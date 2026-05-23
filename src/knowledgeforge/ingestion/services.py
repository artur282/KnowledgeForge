"""Ingestion service: parse, chunk, embed, and dual-write."""

import logging
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.config import Settings
from knowledgeforge.db.models import Document
from knowledgeforge.ingestion.parsers import compute_hash, parse_document
from knowledgeforge.ingestion.repositories import DocumentChunkRepository, DocumentRepository

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


class IngestionService:
    """Orchestrates document ingestion pipeline."""

    def __init__(
        self,
        session: AsyncSession,
        es_client: AsyncElasticsearch,
        settings: Settings,
    ) -> None:
        self.doc_repo = DocumentRepository(session)
        self.chunk_repo = DocumentChunkRepository(session)
        self.es_client = es_client
        self.settings = settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key,
        )

    async def process(self, file_bytes: bytes, filename: str) -> UUID:
        """Full ingestion pipeline."""
        content_hash = compute_hash(file_bytes)

        existing = await self._get_by_hash(content_hash)
        if existing:
            logger.info("Duplicate document detected: %s", filename)
            return existing.id

        doc = await self.doc_repo.create(filename, content_hash)
        await self.doc_repo.update_status(doc.id, "processing")

        try:
            text = parse_document(file_bytes, filename)
            chunks = self.text_splitter.split_text(text)
            chunk_embeddings = await self.embeddings.aembed_documents(chunks)

            chunk_records = [
                {
                    "document_id": doc.id,
                    "chunk_index": i,
                    "content": chunk,
                    "embedding": embedding,
                    "metadata": {"filename": filename, "chunk_size": len(chunk)},
                }
                for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings, strict=False))
            ]

            await self.chunk_repo.create_many(chunk_records)
            await self._write_to_es(doc.id, filename, chunk_records)

            await self.doc_repo.update_status(doc.id, "ready")
            logger.info("Document %s ingested successfully (%d chunks)", filename, len(chunks))

        except Exception:
            await self.doc_repo.update_status(doc.id, "failed")
            logger.exception("Failed to ingest document %s", filename)
            raise

        return doc.id

    async def _get_by_hash(self, content_hash: str):
        """Get document by content hash."""
        result = await self.doc_repo.session.execute(select(Document).where(Document.content_hash == content_hash))
        return result.scalar_one_or_none()

    async def _write_to_es(self, doc_id: UUID, filename: str, chunks: list[dict]) -> None:
        """Write chunks to Elasticsearch for BM25 search."""
        from elasticsearch.helpers import async_bulk

        async def chunk_generator():
            for chunk in chunks:
                yield {
                    "_index": "knowledgeforge",
                    "_id": f"{doc_id}-{chunk['chunk_index']}",
                    "_source": {
                        "document_id": str(doc_id),
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "filename": filename,
                        "metadata": chunk["metadata"],
                    },
                }

        await async_bulk(self.es_client, chunk_generator())
