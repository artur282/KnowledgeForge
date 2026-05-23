import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from knowledgeforge.db.models import Base


@pytest.fixture(autouse=True)
def _set_test_env():
    """Set minimal env vars for all tests."""
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")
    os.environ.setdefault("ELASTICSEARCH_URL", "http://localhost:9200")
    os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
    yield


@pytest.fixture
def app(monkeypatch):
    """Create FastAPI app for testing."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///test.db")
    monkeypatch.setenv("ELASTICSEARCH_URL", "http://localhost:9200")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

    from knowledgeforge.main import create_app

    return create_app()


@pytest.fixture
async def client(app):
    """Async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def db_session():
    """Database session for tests."""
    engine = create_async_engine("sqlite+aiosqlite:///test.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
