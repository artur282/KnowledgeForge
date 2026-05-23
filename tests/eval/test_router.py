"""Tests for evaluation endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

from httpx import AsyncClient


@patch("knowledgeforge.eval.router.RAGASEvalService")
async def test_run_evaluation(mock_service, client: AsyncClient):
    """POST /eval/run executes evaluation and returns scores."""
    mock_instance = AsyncMock()
    mock_instance.run_evaluation.return_value = {
        "report_id": uuid4(),
        "name": "test_run",
        "faithfulness": 0.92,
        "answer_relevancy": 0.88,
        "context_precision": 0.85,
        "context_recall": 0.90,
        "created_at": "2026-05-23T00:00:00Z",
    }
    mock_service.return_value = mock_instance

    response = await client.post("/eval/run", json={"name": "test_run"})
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "faithfulness" in data
    assert "answer_relevancy" in data
    assert "context_precision" in data


async def test_list_eval_reports_empty(client: AsyncClient):
    """GET /eval/reports returns empty list when no reports exist."""
    response = await client.get("/eval/reports")
    assert response.status_code == 200
    data = response.json()
    assert "reports" in data
    assert isinstance(data["reports"], list)
