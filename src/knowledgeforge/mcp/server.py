"""MCP server configuration and mounting."""

import logging

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def mount_mcp_server(app: FastAPI) -> None:
    """Mount MCP server as a FastAPI sub-application.

    This exposes MCP tools via Streamable HTTP at /mcp/stream.
    Tools are registered with dependencies injected from app.state.
    """
    from knowledgeforge.mcp.tools import create_mcp_tools

    mcp = FastMCP("KnowledgeForge")

    tools = create_mcp_tools(
        session_factory=app.state.session_factory,
        es_client=app.state.es_client,
        settings=app.state.settings,
        embeddings=getattr(app.state, "embeddings", None),
        llm=getattr(app.state, "llm", None),
    )

    for tool_name, tool_func in tools.items():
        mcp.tool(name=tool_name)(tool_func)

    mcp_app = mcp.streamable_http_app()
    app.state.mcp = mcp
    app.mount("/mcp/stream", mcp_app)
    logger.info("MCP server mounted at /mcp/stream")
