"""FastAPI application with lifespan management."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from knowledgeforge import __version__
from knowledgeforge.chat import router as chat_router
from knowledgeforge.config import Settings
from knowledgeforge.db.engine import create_engine, get_session_factory
from knowledgeforge.eval import router as eval_router
from knowledgeforge.ingestion import router as ingestion_router
from knowledgeforge.mcp import mount_mcp_server
from knowledgeforge.mcp import router as mcp_router
from knowledgeforge.search import router as search_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize and shutdown application resources."""
    logger.info("Starting KnowledgeForge...")

    settings = Settings()
    app.state.settings = settings
    app.state.engine = create_engine(settings.database_url)
    app.state.session_factory = get_session_factory(app.state.engine)

    app.state.es_client = AsyncElasticsearch(
        hosts=[settings.elasticsearch_url],
        request_timeout=30,
    )
    info = await app.state.es_client.info()
    logger.info("Elasticsearch connected: %s", info["version"]["number"])

    app.state.embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    app.state.llm = ChatOpenAI(
        model=settings.llm_model,
        openai_api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0,
    )

    logger.info("Database engine initialized")
    logger.info("Elasticsearch URL: %s", settings.elasticsearch_url)

    yield

    logger.info("Shutting down KnowledgeForge...")
    await app.state.engine.dispose()
    await app.state.es_client.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = Settings()

    app = FastAPI(
        title="KnowledgeForge",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error occurred"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    class HealthResponse(BaseModel):
        status: str
        version: str

    @app.get("/health", response_model=HealthResponse)
    async def health():
        return {"status": "ok", "version": __version__}

    app.include_router(eval_router)
    app.include_router(ingestion_router)
    app.include_router(search_router)
    app.include_router(chat_router)
    app.include_router(mcp_router)

    mount_mcp_server(app)

    return app


app = create_app()


def main():
    """CLI entry point."""
    import uvicorn

    uvicorn.run("knowledgeforge.main:app", host="0.0.0.0", port=8000, reload=True)
