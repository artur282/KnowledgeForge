"""Tests for RAGAS evaluation service."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from knowledgeforge.eval.services import RAGASEvalService


@pytest.fixture
def mock_settings():
    from knowledgeforge.config import Settings

    return Settings(
        database_url="sqlite+aiosqlite:///test.db",
        elasticsearch_url="http://localhost:9200",
        openai_api_key="sk-test-key",
    )


@pytest.fixture
def mock_eval_repo():
    repo = AsyncMock()
    repo.create.return_value = MagicMock(
        id=uuid4(),
        created_at="2026-05-23T00:00:00Z",
    )
    return repo


@patch("knowledgeforge.eval.services.ChatOpenAI")
@patch("knowledgeforge.eval.services.OpenAIEmbeddings")
def test_service_initialization(mock_embeddings, mock_llm, mock_settings, mock_eval_repo):
    """RAGASEvalService initializes with all components."""
    service = RAGASEvalService(mock_settings, mock_eval_repo)
    assert service.llm is not None
    assert service.embeddings is not None
