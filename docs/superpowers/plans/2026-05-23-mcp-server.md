# Sub-proyecto 5: Servidor MCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar servidor MCP que expone `search_knowledge(query)` y `summarize_document(doc_id)` como tools nativas para clientes MCP.

**Architecture:** Módulo MCP que usa el SDK `mcp` para registrar tools. Las tools delegan en los servicios existentes de búsqueda y RAG. El servidor se integra con FastAPI mediante un endpoint SSE/Streamable HTTP. Router expone `GET /mcp/tools` para listar tools disponibles.

**Tech Stack:** FastAPI, MCP SDK Python, LangChain, servicios existentes de búsqueda y chat

---

## Estructura de Archivos

| Archivo | Responsabilidad |
|---------|----------------|
| `src/knowledgeforge/mcp/tools.py` | Definición de MCP tools (search_knowledge, summarize_document) |
| `src/knowledgeforge/mcp/server.py` | Configuración del servidor MCP |
| `src/knowledgeforge/mcp/router.py` | Endpoints HTTP para MCP + lista de tools |
| `src/knowledgeforge/mcp/__init__.py` | Package export |
| `tests/mcp/__init__.py` | Package marker |
| `tests/mcp/test_tools.py` | Tests de MCP tools |
| `tests/mcp/test_router.py` | Tests de endpoints MCP |
| `src/knowledgeforge/main.py` | Registrar MCP router |

---

### Task 1: MCP Tools

**Files:**
- Create: `src/knowledgeforge/mcp/tools.py`
- Test: `tests/mcp/test_tools.py`

- [ ] **Step 1: Crear MCP tools**

```python
"""MCP tool definitions for KnowledgeForge."""

import logging
from uuid import UUID

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP("KnowledgeForge")


@mcp.tool()
async def search_knowledge(query: str, k: int = 10) -> str:
    """Search the knowledge base using hybrid search (BM25 + semantic).

    Args:
        query: The search query.
        k: Number of results to return (default 10, max 100).

    Returns:
        Formatted search results with document content and sources.
    """
    from knowledgeforge.main import app
    from knowledgeforge.config import Settings
    from knowledgeforge.db.engine import get_async_session
    from knowledgeforge.search.services import HybridSearchService

    settings = Settings()
    session_factory = app.state.session_factory

    async with session_factory() as session:
        search_service = HybridSearchService(session, app.state.es_client)
        results = await search_service.search(query=query, k=min(k, 100))

    if not results:
        return "No relevant documents found."

    formatted = []
    for r in results:
        formatted.append(
            f"[{r.filename}] (chunk {r.chunk_index}, score: {r.score:.4f})\n{r.content[:300]}"
        )

    return "\n\n---\n\n".join(formatted)


@mcp.tool()
async def summarize_document(doc_id: str) -> str:
    """Generate a summary of a specific document from the knowledge base.

    Args:
        doc_id: The UUID of the document to summarize.

    Returns:
        A concise summary of the document content.
    """
    from knowledgeforge.main import app
    from knowledgeforge.config import Settings
    from knowledgeforge.db.engine import get_async_session
    from knowledgeforge.db.models import Document
    from knowledgeforge.ingestion.repositories import DocumentRepository
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langfuse.callback import CallbackHandler
    from sqlalchemy import select

    settings = Settings()
    session_factory = app.state.session_factory

    async with session_factory() as session:
        doc_repo = DocumentRepository(session)
        doc = await doc_repo.get_by_id(UUID(doc_id))

        if not doc:
            return f"Document {doc_id} not found."

        if doc.status != "ready":
            return f"Document is not ready for summarization (status: {doc.status})."

        # Get all chunks for this document
        result = await session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == doc.id)
            .order_by(DocumentChunk.chunk_index)
        )
        chunks = result.scalars().all()

        if not chunks:
            return "Document has no content chunks."

        # Combine chunks (truncate if too long)
        full_content = "\n\n".join(c.content for c in chunks)
        max_tokens = 8000
        if len(full_content) > max_tokens * 4:  # Rough char to token ratio
            full_content = full_content[:max_tokens * 4] + "...[truncated]"

        # Generate summary
        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            openai_api_key=settings.openai_api_key,
            temperature=0,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Summarize the following document concisely. Focus on key facts and main points."),
            ("human", "Document: {content}"),
        ])

        chain = prompt | llm
        langfuse_handler = CallbackHandler()

        response = await chain.ainvoke(
            {"content": full_content},
            config={"callbacks": [langfuse_handler]},
        )

        return response.content
```

- [ ] **Step 2: Escribir tests para MCP tools**

```python
"""Tests for MCP tools."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

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


@patch("knowledgeforge.mcp.tools.HybridSearchService")
async def test_search_knowledge_no_results(mock_search_class):
    """search_knowledge returns message when no results."""
    mock_service = AsyncMock()
    mock_service.search.return_value = []
    mock_search_class.return_value = mock_service

    from knowledgeforge.mcp.tools import search_knowledge

    result = await search_knowledge("nonexistent query")
    assert result == "No relevant documents found."
```

- [ ] **Step 3: Commit**

```bash
git add src/knowledgeforge/mcp/tools.py tests/mcp/test_tools.py
git commit -m "feat(mcp): add search_knowledge and summarize_document MCP tools"
```

---

### Task 2: MCP Server y Router

**Files:**
- Create: `src/knowledgeforge/mcp/server.py`
- Create: `src/knowledgeforge/mcp/router.py`
- Create: `src/knowledgeforge/mcp/__init__.py`
- Modify: `src/knowledgeforge/main.py`
- Test: `tests/mcp/test_router.py`

- [ ] **Step 1: Crear MCP server wrapper**

```python
"""MCP server configuration and mounting."""

import logging

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from knowledgeforge.mcp.tools import mcp

logger = logging.getLogger(__name__)


def mount_mcp_server(app: FastAPI) -> None:
    """Mount MCP server as a FastAPI sub-application.

    This exposes MCP tools via Streamable HTTP at /mcp/sse.
    """
    # Mount MCP as a sub-application
    mcp_app = mcp.streamable_http_app()
    app.mount("/mcp", mcp_app)
    logger.info("MCP server mounted at /mcp")
```

- [ ] **Step 2: Crear MCP router**

```python
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
```

- [ ] **Step 3: Actualizar mcp/__init__.py**

```python
"""MCP server module."""

from knowledgeforge.mcp.router import router
from knowledgeforge.mcp.server import mount_mcp_server
from knowledgeforge.mcp.tools import mcp

__all__ = ["router", "mount_mcp_server", "mcp"]
```

- [ ] **Step 4: Registrar MCP en main.py**

Modificar `src/knowledgeforge/main.py`:

```python
# Agregar imports
from knowledgeforge.mcp import mount_mcp_server
from knowledgeforge.mcp import router as mcp_router

# En create_app(), después de incluir otros routers:
app.include_router(mcp_router)

# Después de crear app pero antes del return:
mount_mcp_server(app)
```

- [ ] **Step 5: Escribir tests para router**

```python
"""Tests for MCP endpoints."""

from unittest.mock import patch
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
```

- [ ] **Step 6: Commit**

```bash
git add src/knowledgeforge/mcp/__init__.py src/knowledgeforge/mcp/server.py src/knowledgeforge/mcp/router.py tests/mcp/test_router.py src/knowledgeforge/main.py
git commit -m "feat(mcp): add MCP server mounting and tools listing endpoint"
```

---

### Task 3: Verificación Final

- [ ] **Step 1: Ejecutar tests**

```bash
uv run pytest tests/ -v
```

Esperado: Todos los tests pasan

- [ ] **Step 2: Ejecutar linting**

```bash
uv run ruff check src/ tests/
```

Esperado: 0 issues

- [ ] **Step 3: Commit final si hay cambios**

```bash
git add -A
git commit -m "chore: final verification for MCP server sub-project"
```