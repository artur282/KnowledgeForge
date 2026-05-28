"""Database engine configuration."""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def create_engine(database_url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine."""
    return create_async_engine(database_url, echo=False)


def get_session_factory(engine):
    """Create a session factory bound to the engine."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
