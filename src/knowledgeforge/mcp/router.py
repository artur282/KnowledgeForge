"""HTTP endpoints for MCP server."""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get(
    "/tools",
    operation_id="listMcpTools",
)
async def list_mcp_tools():
    """List available MCP tools."""
    from knowledgeforge.mcp.tools import mcp

    tools = mcp._tool_manager.list_tools()
    return [
        {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.parameters,
        }
        for tool in tools
    ]
