"""Integration tests using Docker Compose services (PostgreSQL + Elasticsearch).

Run with Docker Compose:
    docker compose run test

Or manually:
    docker compose up -d postgres elasticsearch
    docker compose run app uv run pytest tests/ -v
"""

import asyncio
import os
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from knowledgeforge.db.models import Base


@pytest.fixture
async def integration_app():
    """Create FastAPI app with real PostgreSQL and Elasticsearch."""
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://knowledgeforge:kf_secret@postgres:5432/knowledgeforge"
    os.environ["ELASTICSEARCH_URL"] = "http://elasticsearch:9200"
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-openrouter-api-key")
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

    from elasticsearch import AsyncElasticsearch

    from knowledgeforge.config import Settings
    from knowledgeforge.db.engine import create_engine, get_session_factory
    from knowledgeforge.main import create_app

    app = create_app()

    settings = Settings()
    app.state.engine = create_engine(settings.database_url)
    app.state.session_factory = get_session_factory(app.state.engine)
    app.state.es_client = AsyncElasticsearch(
        hosts=[settings.elasticsearch_url],
        request_timeout=30,
    )

    async with app.state.engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    es_client = app.state.es_client
    index_name = "knowledgeforge"
    if not await es_client.indices.exists(index=index_name):
        await es_client.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "document_id": {"type": "keyword"},
                        "chunk_index": {"type": "integer"},
                        "content": {"type": "text"},
                        "filename": {"type": "keyword"},
                        "metadata": {"type": "object"},
                        "content_suggest": {
                            "type": "completion",
                            "analyzer": "simple",
                        },
                        "embedding": {"type": "dense_vector", "dims": 1536},
                    }
                }
            },
        )

    yield app

    async with app.state.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await app.state.es_client.indices.delete(index="knowledgeforge", ignore_unavailable=True)
    await app.state.es_client.close()
    await app.state.engine.dispose()


@pytest.fixture
async def integration_client(integration_app):
    """Async HTTP client for integration testing."""
    transport = ASGITransport(app=integration_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestIngestionIntegration:
    """Integration tests for document ingestion endpoints."""

    async def test_upload_document_status(self, integration_client):
        """POST /documents returns 202 with document ID."""
        response = await integration_client.post(
            "/documents",
            files={"file": ("test.txt", b"Hello world integration test", "text/plain")},
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "queued"

    async def test_get_document_status(self, integration_client):
        """GET /documents/{id} returns document details."""
        upload_resp = await integration_client.post(
            "/documents",
            files={"file": ("test.txt", b"Content for status check", "text/plain")},
        )
        assert upload_resp.status_code == 202
        data = upload_resp.json()
        assert data["status"] == "queued"
        doc_id = data["document_id"]

        await asyncio.sleep(3)
        response = await integration_client.get(f"/documents/{doc_id}")
        assert response.status_code == 200
        doc_data = response.json()
        assert doc_data["id"] == doc_id
        assert doc_data["filename"] == "test.txt"

    async def test_delete_document(self, integration_client):
        """DELETE /documents/{id} removes document."""
        upload_resp = await integration_client.post(
            "/documents",
            files={"file": ("test.txt", b"Content to delete", "text/plain")},
        )
        doc_id = upload_resp.json()["document_id"]

        await asyncio.sleep(3)
        response = await integration_client.delete(f"/documents/{doc_id}")
        assert response.status_code == 204

        response = await integration_client.get(f"/documents/{doc_id}")
        assert response.status_code == 404


class TestSearchIntegration:
    """Integration tests for hybrid search endpoints."""

    async def test_search_empty_results(self, integration_client):
        """POST /search returns empty results when no data."""
        response = await integration_client.post(
            "/search",
            json={"query": "nonexistent query", "k": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data

    async def test_search_suggestions(self, integration_client):
        """GET /search/suggest returns suggestions."""
        response = await integration_client.get("/search/suggest?q=test")
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data


class TestChatIntegration:
    """Integration tests for RAG chat endpoints."""

    async def test_chat_creates_session(self, integration_client):
        """POST /chat returns answer and session_id."""
        response = await integration_client.post(
            "/chat",
            json={"question": "What is this?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

    async def test_chat_history_not_found(self, integration_client):
        """GET /chat/{session_id}/history returns 404 for nonexistent session."""
        response = await integration_client.get(f"/chat/{uuid4()}/history")
        assert response.status_code == 404


class TestMCPIntegration:
    """Integration tests for MCP endpoints."""

    async def test_list_mcp_tools(self, integration_client):
        """GET /mcp/tools returns registered tools."""
        response = await integration_client.get("/mcp/tools")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        tool_names = [t["name"] for t in data]
        assert "search_knowledge" in tool_names
        assert "summarize_document" in tool_names


class TestEvalIntegration:
    """Integration tests for evaluation endpoints."""

    async def test_list_eval_reports_empty(self, integration_client):
        """GET /eval/reports returns empty list when no reports."""
        response = await integration_client.get("/eval/reports")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        assert isinstance(data["reports"], list)
        assert len(data["reports"]) == 0
