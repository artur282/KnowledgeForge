"""Tests for RAG chat service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.chat.services import RAGChatService


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    from knowledgeforge.config import Settings

    return Settings(
        database_url="sqlite+aiosqlite:///test.db",
        elasticsearch_url="http://localhost:9200",
        openai_api_key="sk-test-key",
    )


@pytest.fixture
def mock_search_service():
    service = AsyncMock()
    service.search.return_value = []
    return service


@patch("knowledgeforge.chat.services.CallbackHandler")
@patch("knowledgeforge.chat.services.ChatOpenAI")
def test_service_initialization(mock_llm, mock_handler, mock_session, mock_settings, mock_search_service):
    """RAGChatService initializes with all components."""
    service = RAGChatService(mock_session, mock_settings, mock_search_service)
    assert service.chain is not None
    assert service.langfuse_handler is not None
