"""Hybrid search service combining BM25 and semantic search with RRF."""

import logging
import re
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.config import Settings
from knowledgeforge.search.schemas import SearchResult

logger = logging.getLogger(__name__)

RRF_K = 60


class HybridSearchService:
    """Performs hybrid search with Reciprocal Rank Fusion."""

    def __init__(
        self,
        session: AsyncSession,
        es_client: AsyncElasticsearch,
        settings: Settings,
        embeddings=None,
    ) -> None:
        self.session = session
        self.es_client = es_client
        self.settings = settings
        self._embeddings = embeddings

    async def search(self, query: str, k: int = 10, filters: dict | None = None) -> list[SearchResult]:
        """Execute hybrid search and return fused results."""
        import asyncio

        bm25_task = asyncio.create_task(self._bm25_search(query, k * 2, filters))
        semantic_task = asyncio.create_task(self._semantic_search(query, k * 2, filters))

        bm25_results, semantic_results = await asyncio.gather(bm25_task, semantic_task)

        fused = self._rrf_fusion(bm25_results, semantic_results)

        return fused[:k]

    async def _bm25_search(self, query: str, k: int, filters: dict | None) -> list[dict]:
        """Search Elasticsearch with BM25."""
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content"],
                    "type": "best_fields",
                }
            },
            "size": k,
        }

        if filters:
            es_query["query"] = {
                "bool": {
                    "must": [{"multi_match": {"query": query, "fields": ["content"], "type": "best_fields"}}],
                    "filter": [{"term": {f"metadata.{k}": v}} for k, v in filters.items()],
                }
            }

        response = await self.es_client.search(index=self.settings.elasticsearch_index, body=es_query)

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append(
                {
                    "doc_id": UUID(source["document_id"]),
                    "chunk_index": source["chunk_index"],
                    "content": source["content"],
                    "score": hit["_score"],
                    "filename": source.get("filename", ""),
                    "metadata": source.get("metadata", {}),
                }
            )

        return results

    async def _semantic_search(self, query: str, k: int, filters: dict | None) -> list[dict]:
        """Search pgvector with cosine similarity."""
        if self._embeddings is None:
            from knowledgeforge.config import Settings

            settings = Settings()
            from langchain_openai import OpenAIEmbeddings

            self._embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

        query_embedding = await self._embeddings.aembed_query(query)
        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        sql = """
            SELECT dc.id, dc.document_id, dc.chunk_index, dc.content,
                   dc.metadata, d.filename,
                   1 - (dc.embedding <=> :embedding) AS similarity
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE dc.embedding IS NOT NULL
        """
        params = {"embedding": embedding_str}

        if filters:
            for key, value in filters.items():
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    continue
                sql += f" AND dc.metadata->>'{key}' = :filter_{key}"
                params[f"filter_{key}"] = str(value)

        sql += " ORDER BY similarity DESC LIMIT :limit"
        params["limit"] = k

        result = await self.session.execute(text(sql), params)
        rows = result.fetchall()

        return [
            {
                "doc_id": row.document_id,
                "chunk_index": row.chunk_index,
                "content": row.content,
                "score": float(row.similarity),
                "filename": row.filename,
                "metadata": dict(row.metadata) if row.metadata else {},
            }
            for row in rows
        ]

    def _rrf_fusion(self, bm25_results: list[dict], semantic_results: list[dict]) -> list[SearchResult]:
        """Fuse results using Reciprocal Rank Fusion."""
        scores: dict[tuple[UUID, int], tuple[float, dict]] = {}

        for rank, result in enumerate(bm25_results, 1):
            key = (result["doc_id"], result["chunk_index"])
            rrf_score = 1.0 / (RRF_K + rank)
            if key in scores:
                scores[key] = (scores[key][0] + rrf_score, result)
            else:
                scores[key] = (rrf_score, result)

        for rank, result in enumerate(semantic_results, 1):
            key = (result["doc_id"], result["chunk_index"])
            rrf_score = 1.0 / (RRF_K + rank)
            if key in scores:
                scores[key] = (scores[key][0] + rrf_score, result)
            else:
                scores[key] = (rrf_score, result)

        sorted_results = sorted(scores.values(), key=lambda x: x[0], reverse=True)

        return [
            SearchResult(
                doc_id=result["doc_id"],
                chunk_index=result["chunk_index"],
                content=result["content"],
                score=round(rrf_score, 6),
                filename=result["filename"],
                metadata=result["metadata"],
            )
            for rrf_score, result in sorted_results
        ]

    async def _get_suggestions(self, query: str) -> list[str]:
        """Get autocomplete suggestions from Elasticsearch."""
        response = await self.es_client.search(
            index=self.settings.elasticsearch_index,
            body={
                "suggest": {
                    "content-suggest": {
                        "prefix": query,
                        "completion": {
                            "field": "content_suggest",
                            "size": 5,
                        },
                    }
                }
            },
        )

        suggestions = []
        for option in response["suggest"]["content-suggest"][0]["options"]:
            suggestions.append(option["text"])

        return suggestions
