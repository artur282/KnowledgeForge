"""Tests for chat endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

from httpx import AsyncClient


@patch("knowledgeforge.chat.router.RAGChatService")
async def test_chat(mock_service, client: AsyncClient):
    """POST /chat returns answer with sources."""
    mock_instance = AsyncMock()
    mock_instance.chat.return_value = (
        "Based on the documents, the answer is...",
        [{"doc_id": uuid4(), "chunk_index": 0, "score": 0.9}],
        uuid4(),
    )
    mock_service.return_value = mock_instance

    response = await client.post("/chat", json={"question": "What is the policy?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "session_id" in data


@patch("knowledgeforge.chat.router.RAGChatService")
async def test_chat_with_session_id(mock_service, client: AsyncClient):
    """POST /chat accepts optional session_id."""
    session_id = uuid4()
    mock_instance = AsyncMock()
    mock_instance.chat.return_value = ("Answer", [], session_id)
    mock_service.return_value = mock_instance

    response = await client.post(
        "/chat",
        json={"session_id": str(session_id), "question": "Follow up?"},
    )
    assert response.status_code == 200


async def test_get_history_not_found(client: AsyncClient):
    """GET /chat/{session_id}/history returns 404 for nonexistent session."""
    response = await client.get(f"/chat/{uuid4()}/history")
    assert response.status_code == 404
