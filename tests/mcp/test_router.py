"""Tests for MCP endpoints."""

from httpx import AsyncClient


async def test_list_mcp_tools(client: AsyncClient):
    """GET /mcp/tools returns list of available tools."""
    response = await client.get("/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    tool_names = [t["name"] for t in data]
    assert "search_knowledge" in tool_names
    assert "summarize_document" in tool_names
