"""Shared dependencies for all routers."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Get database session from app state."""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_settings(request: Request):
    """Get settings from app state (singleton)."""
    return request.app.state.settings


def get_es_client(request: Request):
    """Get Elasticsearch client from app state."""
    return request.app.state.es_client
