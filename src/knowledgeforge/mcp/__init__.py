"""MCP server module."""

from knowledgeforge.mcp.router import router
from knowledgeforge.mcp.server import mount_mcp_server

__all__ = ["router", "mount_mcp_server"]
