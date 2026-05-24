"""Tests for ingestion endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

from httpx import AsyncClient


@patch("knowledgeforge.ingestion.router.IngestionService")
async def test_upload_document(mock_service, client: AsyncClient):
    """POST /documents returns 202 with document ID."""
    from uuid import uuid4

    mock_instance = AsyncMock()
    mock_instance.create_document.return_value = uuid4()
    mock_service.return_value = mock_instance

    response = await client.post(
        "/documents",
        files={"file": ("test.txt", b"Hello world", "text/plain")},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert "document_id" in data


async def test_get_document_not_found(client: AsyncClient):
    """GET /documents/{id} returns 404 for nonexistent document."""
    response = await client.get(f"/documents/{uuid4()}")
    assert response.status_code == 404


async def test_delete_document_not_found(client: AsyncClient):
    """DELETE /documents/{id} returns 404 for nonexistent document."""
    response = await client.delete(f"/documents/{uuid4()}")
    assert response.status_code == 404
