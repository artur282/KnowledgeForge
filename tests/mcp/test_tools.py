"""Tests for MCP tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_search_knowledge_tool_exists():
    """search_knowledge tool is registered."""
    from knowledgeforge.mcp.tools import mcp

    tool_names = [tool.name for tool in mcp._tool_manager.list_tools()]
    assert "search_knowledge" in tool_names


def test_summarize_document_tool_exists():
    """summarize_document tool is registered."""
    from knowledgeforge.mcp.tools import mcp

    tool_names = [tool.name for tool in mcp._tool_manager.list_tools()]
    assert "summarize_document" in tool_names


@pytest.mark.asyncio
@patch("knowledgeforge.search.services.HybridSearchService")
@patch("knowledgeforge.main.app")
@patch("knowledgeforge.config.Settings")
async def test_search_knowledge_no_results(mock_settings, mock_app, mock_search_class):
    """search_knowledge returns message when no results."""
    mock_session = AsyncMock()

    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)
    mock_app.state.session_factory = mock_session_factory
    mock_app.state.es_client = AsyncMock()

    mock_service = AsyncMock()
    mock_service.search.return_value = []
    mock_search_class.return_value = mock_service

    mock_settings.return_value.openai_api_key = "sk-test"

    from knowledgeforge.mcp.tools import search_knowledge

    result = await search_knowledge("nonexistent query")
    assert result == "No relevant documents found."
