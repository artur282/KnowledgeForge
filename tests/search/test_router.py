"""Tests for search endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

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


@patch("knowledgeforge.search.router.HybridSearchService")
async def test_search_suggestions(mock_service, client: AsyncClient):
    """GET /search/suggest returns suggestions."""
    mock_instance = AsyncMock()
    mock_instance._get_suggestions.return_value = ["test", "testing", "tested"]
    mock_service.return_value = mock_instance

    response = await client.get("/search/suggest?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
