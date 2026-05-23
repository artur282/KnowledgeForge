import json
import os
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

from knowledgeforge.db.models import Base

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


if Vector is not None:

    @compiles(Vector, "sqlite")
    def _compile_vector_sqlite(type_, compiler, **kw):
        return "TEXT"


def _generate_uuid_on_insert(mapper, connection, target):
    mapper_obj = sa_inspect(type(target))
    for col_attr in mapper_obj.attrs:
        if not hasattr(col_attr, "columns"):
            continue
        for col in col_attr.columns:
            if isinstance(col.type, UUID) and getattr(target, col_attr.key) is None:
                setattr(target, col_attr.key, uuid4())


def _serialize_jsonb_on_insert(mapper, connection, target):
    mapper_obj = sa_inspect(type(target))
    for col_attr in mapper_obj.attrs:
        if not hasattr(col_attr, "columns"):
            continue
        for col in col_attr.columns:
            if isinstance(col.type, JSONB):
                val = getattr(target, col_attr.key)
                if val is not None and not isinstance(val, str):
                    setattr(target, col_attr.key, json.dumps(val))


for mapper in Base.registry.mappers:
    event.listen(mapper, "before_insert", _generate_uuid_on_insert)
    event.listen(mapper, "before_insert", _serialize_jsonb_on_insert)


@pytest.fixture(autouse=True)
def _set_test_env():
    """Set minimal env vars for all tests."""
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")
    os.environ.setdefault("ELASTICSEARCH_URL", "http://localhost:9200")
    os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
    yield


@pytest.fixture
async def app(monkeypatch):
    """Create FastAPI app for testing."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///test.db")
    monkeypatch.setenv("ELASTICSEARCH_URL", "http://localhost:9200")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

    from knowledgeforge.config import Settings
    from knowledgeforge.db.engine import create_engine, get_session_factory
    from knowledgeforge.db.models import Base
    from knowledgeforge.main import create_app

    test_app = create_app()

    settings = Settings()
    test_app.state.engine = create_engine(settings.database_url)
    test_app.state.session_factory = get_session_factory(test_app.state.engine)
    test_app.state.es_client = AsyncMock()

    async with test_app.state.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return test_app


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
