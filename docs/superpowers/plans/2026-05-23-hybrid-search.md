# Sub-proyecto 3: Búsqueda Híbrida Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar búsqueda híbrida combinando BM25 (Elasticsearch) + semántica (pgvector) con Reciprocal Rank Fusion (RRF) para ranking unificado.

**Architecture:** Servicio de búsqueda que ejecuta queries en paralelo contra Elasticsearch (BM25) y PostgreSQL (cosine similarity), luego fusiona resultados con RRF. Router expone `POST /search` y `GET /search/suggest`.

**Tech Stack:** FastAPI, Elasticsearch async, SQLAlchemy async, pgvector cosine similarity, Reciprocal Rank Fusion

---

## Estructura de Archivos

| Archivo | Responsabilidad |
|---------|----------------|
| `src/knowledgeforge/search/schemas.py` | Pydantic schemas para search request/response |
| `src/knowledgeforge/search/services.py` | Lógica de búsqueda híbrida + RRF |
| `src/knowledgeforge/search/router.py` | Endpoints HTTP: POST /search, GET /search/suggest |
| `src/knowledgeforge/search/__init__.py` | Package export |
| `tests/search/__init__.py` | Package marker |
| `tests/search/test_services.py` | Tests de búsqueda híbrida y RRF |
| `tests/search/test_router.py` | Tests de endpoints |
| `src/knowledgeforge/main.py` | Registrar search router |

---

### Task 1: Schemas de Búsqueda

**Files:**
- Create: `src/knowledgeforge/search/schemas.py`

- [ ] **Step 1: Crear schemas de búsqueda**

```python
"""Pydantic schemas for search endpoints."""

from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request schema for hybrid search."""

    query: str = Field(..., min_length=1, max_length=500)
    k: int = Field(default=10, ge=1, le=100)
    filters: dict | None = None


class SearchResult(BaseModel):
    """Single search result with source info."""

    doc_id: UUID
    chunk_index: int
    content: str
    score: float
    filename: str
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response schema for hybrid search."""

    results: list[SearchResult]
    total: int


class SuggestResponse(BaseModel):
    """Response schema for autocomplete suggestions."""

    suggestions: list[str]
```

- [ ] **Step 2: Commit**

```bash
git add src/knowledgeforge/search/schemas.py
git commit -m "feat(search): add Pydantic schemas for search request/response"
```

---

### Task 2: Servicio de Búsqueda Híbrida con RRF

**Files:**
- Create: `src/knowledgeforge/search/services.py`
- Test: `tests/search/test_services.py`

- [ ] **Step 1: Crear servicio de búsqueda híbrida**

```python
"""Hybrid search service combining BM25 and semantic search with RRF."""

import logging
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.models import DocumentChunk
from knowledgeforge.search.schemas import SearchResult

logger = logging.getLogger(__name__)

RRF_K = 60  # RRF constant


class HybridSearchService:
    """Performs hybrid search with Reciprocal Rank Fusion."""

    def __init__(
        self,
        session: AsyncSession,
        es_client: AsyncElasticsearch,
    ) -> None:
        self.session = session
        self.es_client = es_client

    async def search(self, query: str, k: int = 10, filters: dict | None = None) -> list[SearchResult]:
        """Execute hybrid search and return fused results.

        1. Query Elasticsearch for BM25 results
        2. Query pgvector for semantic results
        3. Fuse results with RRF
        4. Return top-k unified results
        """
        # Run both searches in parallel
        import asyncio

        bm25_task = asyncio.create_task(self._bm25_search(query, k * 2, filters))
        semantic_task = asyncio.create_task(self._semantic_search(query, k * 2, filters))

        bm25_results, semantic_results = await asyncio.gather(bm25_task, semantic_task)

        # Fuse with RRF
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
            es_query["query"]["bool"] = {
                "must": es_query["query"],
                "filter": [{"term": {f"metadata.{k}": v}} for k, v in filters.items()],
            }
            del es_query["query"]["multi_match"]

        response = await self.es_client.search(index="knowledgeforge", body=es_query)

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append({
                "doc_id": UUID(source["document_id"]),
                "chunk_index": source["chunk_index"],
                "content": source["content"],
                "score": hit["_score"],
                "filename": source.get("filename", ""),
                "metadata": source.get("metadata", {}),
            })

        return results

    async def _semantic_search(self, query: str, k: int, filters: dict | None) -> list[dict]:
        """Search pgvector with cosine similarity."""
        from langchain_openai import OpenAIEmbeddings
        from knowledgeforge.config import Settings

        settings = Settings()
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key,
        )

        query_embedding = await embeddings.aembed_query(query)
        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"

        # Build query with optional filters
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
        """Fuse results using Reciprocal Rank Fusion.

        RRF score = sum(1 / (k + rank)) for each result across lists.
        """
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

        # Sort by RRF score descending
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
```

- [ ] **Step 2: Escribir tests para RRF fusion**

```python
"""Tests for hybrid search service."""

from uuid import uuid4

from knowledgeforge.search.services import HybridSearchService, RRF_K


def test_rrf_fusion_basic():
    """RRF fusion combines results from both sources."""
    service = HybridSearchService(None, None)

    doc_id = uuid4()
    bm25 = [
        {"doc_id": doc_id, "chunk_index": 0, "content": "BM25 result", "score": 0.9, "filename": "test.pdf", "metadata": {}},
    ]
    semantic = [
        {"doc_id": doc_id, "chunk_index": 0, "content": "Semantic result", "score": 0.85, "filename": "test.pdf", "metadata": {}},
    ]

    results = service._rrf_fusion(bm25, semantic)
    assert len(results) == 1
    assert results[0].doc_id == doc_id
    # Score should be sum of both RRF scores
    expected_score = round(1.0 / (RRF_K + 1) + 1.0 / (RRF_K + 1), 6)
    assert results[0].score == expected_score


def test_rrf_fusion_different_results():
    """RRF fusion handles non-overlapping results."""
    service = HybridSearchService(None, None)

    doc1 = uuid4()
    doc2 = uuid4()
    bm25 = [
        {"doc_id": doc1, "chunk_index": 0, "content": "BM25 only", "score": 0.9, "filename": "test.pdf", "metadata": {}},
    ]
    semantic = [
        {"doc_id": doc2, "chunk_index": 0, "content": "Semantic only", "score": 0.85, "filename": "test.pdf", "metadata": {}},
    ]

    results = service._rrf_fusion(bm25, semantic)
    assert len(results) == 2
    assert results[0].doc_id == doc1  # BM25 rank 1
    assert results[1].doc_id == doc2  # Semantic rank 1


def test_rrf_fusion_empty_lists():
    """RRF fusion handles empty input."""
    service = HybridSearchService(None, None)
    results = service._rrf_fusion([], [])
    assert results == []


def test_rrf_fusion_preserves_content():
    """RRF fusion preserves result content."""
    service = HybridSearchService(None, None)

    doc_id = uuid4()
    bm25 = [
        {"doc_id": doc_id, "chunk_index": 0, "content": "Test content", "score": 0.9, "filename": "test.pdf", "metadata": {"page": 1}},
    ]

    results = service._rrf_fusion(bm25, [])
    assert len(results) == 1
    assert results[0].content == "Test content"
    assert results[0].filename == "test.pdf"
    assert results[0].metadata == {"page": 1}
```

- [ ] **Step 3: Commit**

```bash
git add src/knowledgeforge/search/services.py tests/search/test_services.py
git commit -m "feat(search): add hybrid search service with BM25 + pgvector RRF fusion"
```

---

### Task 3: Router de Búsqueda

**Files:**
- Create: `src/knowledgeforge/search/router.py`
- Create: `src/knowledgeforge/search/__init__.py`
- Modify: `src/knowledgeforge/main.py`
- Test: `tests/search/test_router.py`

- [ ] **Step 1: Crear router de búsqueda**

```python
"""HTTP endpoints for hybrid search."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.engine import get_async_session
from knowledgeforge.search.schemas import SearchRequest, SearchResponse, SuggestResponse
from knowledgeforge.search.services import HybridSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


def get_search_service(
    session: AsyncSession = Depends(get_async_session),
) -> HybridSearchService:
    """Dependency injection for HybridSearchService."""
    from knowledgeforge.main import app

    return HybridSearchService(session, app.state.es_client)


@router.post(
    "",
    response_model=SearchResponse,
    operation_id="hybridSearch",
)
async def hybrid_search(
    request: SearchRequest,
    service: HybridSearchService = Depends(get_search_service),
):
    """Execute hybrid search with BM25 + semantic fusion."""
    results = await service.search(
        query=request.query,
        k=request.k,
        filters=request.filters,
    )
    return SearchResponse(results=results, total=len(results))


@router.get(
    "/suggest",
    response_model=SuggestResponse,
    operation_id="searchSuggestions",
)
async def search_suggestions(
    q: str = Query(..., min_length=1, max_length=100),
    service: HybridSearchService = Depends(get_search_service),
):
    """Get autocomplete suggestions from Elasticsearch."""
    suggestions = await service._get_suggestions(q)
    return SuggestResponse(suggestions=suggestions)
```

- [ ] **Step 2: Agregar método de sugerencias al servicio**

Agregar a `src/knowledgeforge/search/services.py`:

```python
async def _get_suggestions(self, query: str) -> list[str]:
    """Get autocomplete suggestions from Elasticsearch."""
    response = await self.es_client.search(
        index="knowledgeforge",
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
```

- [ ] **Step 3: Actualizar search/__init__.py**

```python
"""Hybrid search module."""

from knowledgeforge.search.router import router

__all__ = ["router"]
```

- [ ] **Step 4: Registrar router en main.py**

Agregar a `src/knowledgeforge/main.py`:

```python
from knowledgeforge.search import router as search_router

# En create_app():
app.include_router(search_router)
```

- [ ] **Step 5: Escribir tests para router**

```python
"""Tests for search endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


@patch("knowledgeforge.search.router.HybridSearchService")
async def test_hybrid_search(mock_service, client: AsyncClient):
    """POST /search returns fused results."""
    from knowledgeforge.search.schemas import SearchResult

    mock_instance = AsyncMock()
    mock_instance.search.return_value = [
        SearchResult(
            doc_id=uuid4(),
            chunk_index=0,
            content="Test result",
            score=0.016,
            filename="test.pdf",
            metadata={},
        )
    ]
    mock_service.return_value = mock_instance

    response = await client.post("/search", json={"query": "test query", "k": 5})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert data["total"] == 1


async def test_search_suggestions(mock_service, client: AsyncClient):
    """GET /search/suggest returns suggestions."""
    mock_instance = AsyncMock()
    mock_instance._get_suggestions.return_value = ["test", "testing", "tested"]
    mock_service.return_value = mock_instance

    response = await client.get("/search/suggest?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
```

- [ ] **Step 6: Commit**

```bash
git add src/knowledgeforge/search/__init__.py src/knowledgeforge/search/router.py tests/search/test_router.py src/knowledgeforge/main.py
git commit -m "feat(search): add HTTP endpoints for hybrid search and autocomplete suggestions"
```

---

### Task 4: Verificación Final

- [ ] **Step 1: Ejecutar tests**

```bash
uv run pytest tests/ -v
```

Esperado: Todos los tests pasan

- [ ] **Step 2: Ejecutar linting**

```bash
uv run ruff check src/ tests/
```

Esperado: 0 issues

- [ ] **Step 3: Commit final si hay cambios**

```bash
git add -A
git commit -m "chore: final verification for hybrid search sub-project"
```