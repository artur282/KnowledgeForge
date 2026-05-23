"""FastAPI application with lifespan management."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from knowledgeforge import __version__
from knowledgeforge.config import Settings
from knowledgeforge.db.engine import create_engine, get_session_factory
from knowledgeforge.ingestion import router as ingestion_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize and shutdown application resources."""
    logger.info("Starting KnowledgeForge...")

    settings = Settings()
    app.state.engine = create_engine(settings.database_url)
    app.state.session_factory = get_session_factory(app.state.engine)

    logger.info("Database engine initialized")
    logger.info("Elasticsearch URL: %s", settings.elasticsearch_url)

    yield

    logger.info("Shutting down KnowledgeForge...")
    await app.state.engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="KnowledgeForge",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": __version__}

    app.include_router(ingestion_router)

    return app


app = create_app()


def main():
    """CLI entry point."""
    import uvicorn

    uvicorn.run("knowledgeforge.main:app", host="0.0.0.0", port=8000, reload=True)
