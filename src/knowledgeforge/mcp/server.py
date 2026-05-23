"""MCP server configuration and mounting."""

import logging

from fastapi import FastAPI

from knowledgeforge.mcp.tools import mcp

logger = logging.getLogger(__name__)


def mount_mcp_server(app: FastAPI) -> None:
    """Mount MCP server as a FastAPI sub-application.

    This exposes MCP tools via Streamable HTTP at /mcp/stream.
    """
    mcp_app = mcp.streamable_http_app()
    app.mount("/mcp/stream", mcp_app)
    logger.info("MCP server mounted at /mcp/stream")
