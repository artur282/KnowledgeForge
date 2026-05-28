"""Hybrid search service combining BM25 and semantic search with RRF."""

import logging
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.config import Settings
from knowledgeforge.search.repositories import SearchRepository
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
        repository: SearchRepository | None = None,
    ) -> None:
        self.session = session
        self.es_client = es_client
        self.settings = settings
        self._embeddings = embeddings
        self._repository = repository or SearchRepository(session)

    async def search(self, query: str, k: int = 10, filters: dict | None = None) -> list[SearchResult]:
        """Execute hybrid search and return fused results."""
        import asyncio

        bm25_task = asyncio.create_task(self._bm25_search(query, k * 2, filters))
        semantic_task = asyncio.create_task(self._semantic_search(query, k * 2, filters))

        bm25_results, semantic_results = await asyncio.gather(bm25_task, semantic_task)

        fused = self._rrf_fusion(bm25_results, semantic_results)

        return await self._rerank(query, fused, top_k=k)

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
                    "filter": [{"term": {f"metadata.{fk}": fv}} for fk, fv in filters.items()],
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
        raw_results = await self._repository.semantic_search(
            embedding=query_embedding,
            k=k,
            filters=filters,
        )

        return [
            {
                "doc_id": UUID(r["document_id"]),
                "chunk_index": r["chunk_index"],
                "content": r["content"],
                "score": r["score"],
                "filename": r["metadata"].get("filename", ""),
                "metadata": r["metadata"],
            }
            for r in raw_results
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

    async def _rerank(self, query: str, results: list, top_k: int = 5) -> list:
        """Rerank results using Cohere if available, otherwise return as-is."""
        if not self.settings.cohere_api_key:
            return results[:top_k]

        try:
            import cohere

            co = cohere.AsyncClient(self.settings.cohere_api_key)

            docs = [r.content for r in results]
            reranked = await co.rerank(
                query=query,
                documents=docs,
                top_n=top_k,
                model="rerank-v3.5",
            )

            reranked_results = []
            for item in reranked.results:
                original = results[item.index]
                original.score = item.relevance_score
                reranked_results.append(original)

            return reranked_results
        except Exception:
            return results[:top_k]

    async def get_suggestions(self, query: str) -> list[str]:
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
