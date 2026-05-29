"""Data access layer for documents and chunks."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.models import Document, DocumentChunk


class DocumentRepository:
    """Repository for Document CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, filename: str, content_hash: str) -> Document:
        """Create a new document record."""
        doc = Document(filename=filename, content_hash=content_hash, status="pending")
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def get_by_id(self, doc_id: UUID) -> Document | None:
        """Get document by ID."""
        result = await self.session.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def update_status(self, doc_id: UUID, status: str) -> Document | None:
        """Update document processing status."""
        doc = await self.get_by_id(doc_id)
        if doc:
            doc.status = status
            await self.session.flush()
        return doc

    async def list_all(self) -> list[Document]:
        """List all documents ordered by most recent."""
        result = await self.session.execute(select(Document).order_by(Document.uploaded_at.desc()))
        return list(result.scalars().all())

    async def delete(self, doc_id: UUID) -> bool:
        """Delete document and cascade-delete its chunks. Returns True if found."""
        doc = await self.get_by_id(doc_id)
        if doc:
            await self.session.delete(doc)
            await self.session.flush()
            return True
        return False


class DocumentChunkRepository:
    """Repository for DocumentChunk operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_many(self, chunks: list[dict]) -> list[DocumentChunk]:
        """Bulk create document chunks with embeddings."""
        records = [
            DocumentChunk(
                document_id=c["document_id"],
                chunk_index=c["chunk_index"],
                content=c["content"],
                embedding=c.get("embedding"),
                metadata_=c.get("metadata", {}),
            )
            for c in chunks
        ]
        self.session.add_all(records)
        await self.session.flush()
        return records
