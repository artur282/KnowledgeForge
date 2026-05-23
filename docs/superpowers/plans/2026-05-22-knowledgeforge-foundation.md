# KnowledgeForge — Fundación: Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear la infraestructura base del proyecto KnowledgeForge con estructura src/, Docker Compose, SQLAlchemy models, Alembic, FastAPI app skeleton y tests.

**Architecture:** Monolito modular con layout src/. FastAPI como gateway con lifespan manager. SQLAlchemy async con pgvector. Docker Compose con 5 servicios (postgres, elasticsearch, langfuse, langfuse-db, app).

**Tech Stack:** Python 3.12, uv, FastAPI 0.115+, SQLAlchemy 2.0 async, Alembic, pgvector, pydantic-settings, pytest, Docker Compose.

---

## File Structure Map

| File | Responsibility |
|------|---------------|
| `pyproject.toml` | Dependencies, build config, pytest config |
| `.env.example` | Template de variables de entorno |
| `docker-compose.yml` | Infraestructura completa |
| `Dockerfile` | Build de la app para Docker |
| `src/knowledgeforge/__init__.py` | Package marker |
| `src/knowledgeforge/__main__.py` | Entry point `python -m` |
| `src/knowledgeforge/config.py` | Settings con pydantic-settings |
| `src/knowledgeforge/main.py` | FastAPI app + lifespan + routers |
| `src/knowledgeforge/db/__init__.py` | DB package marker |
| `src/knowledgeforge/db/engine.py` | Async engine, session factory, lifespan |
| `src/knowledgeforge/db/models.py` | SQLAlchemy declarative models |
| `src/knowledgeforge/ingestion/__init__.py` | Placeholder módulo ingesta |
| `src/knowledgeforge/search/__init__.py` | Placeholder módulo búsqueda |
| `src/knowledgeforge/chat/__init__.py` | Placeholder módulo chat |
| `src/knowledgeforge/mcp/__init__.py` | Placeholder módulo MCP |
| `src/knowledgeforge/eval/__init__.py` | Placeholder módulo evaluación |
| `tests/conftest.py` | Fixtures pytest (app, db, client) |
| `tests/test_health.py` | Smoke test health endpoint |
| `tests/test_config.py` | Test de configuración |
| `alembic.ini` | Alembic config |
| `alembic/env.py` | Alembic environment setup |
| `alembic/versions/` | Migration scripts |
| `docs/openapi.yaml` | Contrato API |

---

### Task 1: pyproject.toml y .env.example

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`

- [ ] **Step 1: Crear pyproject.toml**

```toml
[project]
name = "knowledgeforge"
version = "0.1.0"
description = "Enterprise knowledge management platform with AI-powered RAG"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.13.0",
    "pgvector>=0.3.0",
    "pydantic-settings>=2.0.0",
    "elasticsearch[async]>=8.15.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langfuse>=2.0.0",
    "mcp>=1.0.0",
    "ragas>=0.2.0",
    "python-multipart>=0.0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "ruff>=0.6.0",
    "testcontainers[postgres,elasticsearch]>=4.0.0",
]

[project.scripts]
knowledgeforge = "knowledgeforge.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]
```

- [ ] **Step 2: Crear .env.example**

```env
DATABASE_URL=postgresql+asyncpg://knowledgeforge:kf_secret@localhost:5432/knowledgeforge
ELASTICSEARCH_URL=http://localhost:9200
OPENAI_API_KEY=sk-your-key-here
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

- [ ] **Step 3: Verificar estructura**

Run: `cat pyproject.toml`
Expected: Contenido TOML válido con todas las dependencias listadas.

---

### Task 2: Estructura de directorios y paquetes

**Files:**
- Create: `src/knowledgeforge/__init__.py`
- Create: `src/knowledgeforge/__main__.py`
- Create: `src/knowledgeforge/db/__init__.py`
- Create: `src/knowledgeforge/ingestion/__init__.py`
- Create: `src/knowledgeforge/search/__init__.py`
- Create: `src/knowledgeforge/chat/__init__.py`
- Create: `src/knowledgeforge/mcp/__init__.py`
- Create: `src/knowledgeforge/eval/__init__.py`

- [ ] **Step 1: Crear directorios**

Run:
```bash
mkdir -p src/knowledgeforge/db
mkdir -p src/knowledgeforge/ingestion
mkdir -p src/knowledgeforge/search
mkdir -p src/knowledgeforge/chat
mkdir -p src/knowledgeforge/mcp
mkdir -p src/knowledgeforge/eval
mkdir -p tests
mkdir -p alembic/versions
mkdir -p docs
```

- [ ] **Step 2: Crear __init__.py del paquete principal**

```python
"""KnowledgeForge — Enterprise Knowledge Management Platform."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Crear __main__.py**

```python
"""Entry point for `python -m knowledgeforge`."""

import uvicorn

def main():
    uvicorn.run(
        "knowledgeforge.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Crear __init__.py de submódulos**

`src/knowledgeforge/db/__init__.py`:
```python
"""Database layer."""
```

`src/knowledgeforge/ingestion/__init__.py`:
```python
"""Document ingestion module."""
```

`src/knowledgeforge/search/__init__.py`:
```python
"""Hybrid search module."""
```

`src/knowledgeforge/chat/__init__.py`:
```python
"""RAG chat module."""
```

`src/knowledgeforge/mcp/__init__.py`:
```python
"""MCP server module."""
```

`src/knowledgeforge/eval/__init__.py`:
```python
"""RAG evaluation module."""
```

- [ ] **Step 5: Verificar estructura**

Run: `find src -name "*.py" | sort`
Expected: 8 archivos .py listados en la estructura correcta.

---

### Task 3: Configuración con pydantic-settings

**Files:**
- Create: `src/knowledgeforge/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
import os
import pytest
from knowledgeforge.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("ELASTICSEARCH_URL", "http://localhost:9200")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:3000")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")

    settings = Settings()

    assert settings.database_url == "postgresql+asyncpg://user:pass@localhost/db"
    assert settings.elasticsearch_url == "http://localhost:9200"
    assert settings.openai_api_key == "sk-test-key"
    assert settings.langfuse_host == "http://localhost:3000"


def test_settings_missing_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("ELASTICSEARCH_URL", "http://localhost:9200")

    with pytest.raises(Exception):  # pydantic.ValidationError
        Settings()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL con "ModuleNotFoundError: No module named 'knowledgeforge.config'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/knowledgeforge/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str
    elasticsearch_url: str
    openai_api_key: str
    langfuse_host: str = "http://localhost:3000"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: PASS — 2 tests pass

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .env.example src/ tests/test_config.py
git commit -m "feat: add project structure, config, and dev dependencies"
```

---

### Task 4: Modelos SQLAlchemy

**Files:**
- Create: `src/knowledgeforge/db/models.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_models.py
import pytest
from sqlalchemy import inspect
from knowledgeforge.db.models import Base, Document, DocumentChunk, ChatSession, ChatMessage


def test_document_table_name():
    assert Document.__tablename__ == "documents"


def test_document_chunk_table_name():
    assert DocumentChunk.__tablename__ == "document_chunks"


def test_chat_session_table_name():
    assert ChatSession.__tablename__ == "chat_sessions"


def test_chat_message_table_name():
    assert ChatMessage.__tablename__ == "chat_messages"


def test_all_tables_registered():
    """Verify all models are registered in Base.metadata."""
    expected = {"documents", "document_chunks", "chat_sessions", "chat_messages"}
    actual = set(Base.metadata.tables.keys())
    assert actual == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL con "ModuleNotFoundError: No module named 'knowledgeforge.db.models'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/knowledgeforge/db/models.py
from datetime import datetime, timezone
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship

Base = DeclarativeBase()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    filename = Column(Text, nullable=False)
    content_hash = Column(Text, nullable=False, unique=True)
    status = Column(String(20), nullable=False, default="pending")
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename={self.filename} status={self.status}>"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        CheckConstraint("chunk_index >= 0", name="chk_chunk_index_positive"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    metadata_ = Column("metadata", JSONB, nullable=False, server_default="{}")

    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk id={self.id} doc={self.document_id} idx={self.chunk_index}>"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id}>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="chk_role_valid"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    context_used = Column("context_used", JSONB, nullable=False, server_default="[]")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} role={self.role} session={self.session_id}>"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py -v`
Expected: PASS — 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/knowledgeforge/db/models.py tests/test_models.py
git commit -m "feat: add SQLAlchemy models for documents, chunks, and chat"
```

---

### Task 5: Database Engine y Lifespan

**Files:**
- Create: `src/knowledgeforge/db/engine.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_engine.py
import pytest
from knowledgeforge.db.engine import create_engine, get_async_session


def test_create_engine_returns_async_engine():
    engine = create_engine("postgresql+asyncpg://user:pass@localhost/db")
    assert engine.__class__.__name__ == "AsyncEngine"


def test_create_engine_with_default_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/testdb")
    monkeypatch.setenv("ELASTICSEARCH_URL", "http://localhost:9200")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    from knowledgeforge.config import Settings
    settings = Settings()
    engine = create_engine(settings.database_url)
    assert engine.__class__.__name__ == "AsyncEngine"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_engine.py -v`
Expected: FAIL con "ModuleNotFoundError: No module named 'knowledgeforge.db.engine'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/knowledgeforge/db/engine.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def create_engine(database_url: str, echo: bool = False):
    """Create an async SQLAlchemy engine."""
    return create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
    )


def get_session_factory(engine):
    """Create an async session factory bound to the engine."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_async_session(session_factory):
    """Dependency yielding an async session."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_engine.py -v`
Expected: PASS — 2 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/knowledgeforge/db/engine.py tests/test_engine.py
git commit -m "feat: add async database engine and session factory"
```

---

### Task 6: FastAPI App con Lifespan

**Files:**
- Create: `src/knowledgeforge/main.py`
- Modify: `tests/test_health.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_health.py
import pytest
from httpx import AsyncClient, ASGITransport
from knowledgeforge.main import create_app


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("ELASTICSEARCH_URL", "http://localhost:9200")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    return create_app()


@pytest.mark.asyncio
async def test_health_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_health.py -v`
Expected: FAIL con "ModuleNotFoundError: No module named 'knowledgeforge.main'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/knowledgeforge/main.py
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from knowledgeforge import __version__
from knowledgeforge.config import settings
from knowledgeforge.db.engine import create_engine, get_session_factory

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize and shutdown application resources."""
    logger.info("Starting KnowledgeForge...")

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

    return app


app = create_app()


def main():
    """CLI entry point."""
    import uvicorn
    uvicorn.run("knowledgeforge.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_health.py -v`
Expected: PASS — 1 test passes

- [ ] **Step 5: Commit**

```bash
git add src/knowledgeforge/main.py tests/test_health.py
git commit -m "feat: add FastAPI app with lifespan and health endpoint"
```

---

### Task 7: conftest.py y fixtures de testing

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Write conftest.py**

```python
# tests/conftest.py
import os
from typing import AsyncGenerator

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
```

- [ ] **Step 2: Install aiosqlite para tests SQLite**

Run: `uv add --dev aiosqlite`
Expected: aiosqlite agregado a dev dependencies.

- [ ] **Step 3: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: PASS — todos los tests existentes pasan (config, models, engine, health)

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py pyproject.toml
git commit -m "feat: add test fixtures and SQLite support for testing"
```

---

### Task 8: Docker Compose y Dockerfile

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`

- [ ] **Step 1: Crear Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv sync --frozen

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "knowledgeforge.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 2: Crear docker-compose.yml**

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: knowledgeforge
      POSTGRES_PASSWORD: kf_secret
      POSTGRES_DB: knowledgeforge
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U knowledgeforge"]
      interval: 5s
      timeout: 3s
      retries: 5

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    volumes:
      - esdata:/usr/share/elasticsearch/data
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5

  langfuse:
    image: ghcr.io/langfuse/langfuse:latest
    ports:
      - "3000:3000"
    depends_on:
      - langfuse-db
    environment:
      - DATABASE_URL=postgresql://langfuse:langfuse@langfuse-db:5432/langfuse
      - NEXTAUTH_SECRET=langfuse_secret_change_in_production
      - SALT=langfuse_salt_change_in_production

  langfuse-db:
    image: postgres:16
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse
      POSTGRES_DB: langfuse

  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      elasticsearch:
        condition: service_healthy
      langfuse:
        condition: service_started
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://knowledgeforge:kf_secret@postgres:5432/knowledgeforge
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - LANGFUSE_HOST=http://langfuse:3000
    volumes:
      - ./src:/app/src
      - ./alembic:/app/alembic
      - ./alembic.ini:/app/alembic.ini

volumes:
  pgdata:
  esdata:
```

- [ ] **Step 3: Verificar sintaxis Docker Compose**

Run: `docker compose config`
Expected: YAML parseado correctamente con todos los servicios listados.

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml Dockerfile
git commit -m "feat: add Docker Compose with PG, ES, Langfuse, and app services"
```

---

### Task 9: Alembic inicialización

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/.gitkeep`

- [ ] **Step 1: Crear alembic.ini**

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://knowledgeforge:kf_secret@localhost:5432/knowledgeforge

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 2: Crear alembic/env.py**

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from knowledgeforge.config import settings
from knowledgeforge.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations when connected to a database."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 3: Crear .gitkeep en versions**

Run: `touch alembic/versions/.gitkeep`

- [ ] **Step 4: Generar migración inicial**

Run: `uv run alembic revision --autogenerate -m "initial_schema"`
Expected: Migration file creado en `alembic/versions/` con las 4 tablas.

- [ ] **Step 5: Commit**

```bash
git add alembic.ini alembic/env.py alembic/versions/
git commit -m "feat: add Alembic async migration setup with initial schema"
```

---

### Task 10: OpenAPI Contract

**Files:**
- Create: `docs/openapi.yaml`

- [ ] **Step 1: Crear contrato OpenAPI**

```yaml
openapi: "3.1.0"
info:
  title: KnowledgeForge API
  version: "0.1.0"
  description: Enterprise knowledge management platform with AI-powered RAG

servers:
  - url: http://localhost:8000
    description: Development server

paths:
  /health:
    get:
      summary: Health check
      operationId: healthCheck
      responses:
        "200":
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: ok
                  version:
                    type: string
                    example: "0.1.0"

  /documents:
    post:
      summary: Upload document for ingestion
      operationId: uploadDocument
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        "202":
          description: Document queued for processing
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: queued

  /documents/{id}:
    get:
      summary: Get document status
      operationId: getDocumentStatus
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        "200":
          description: Document details
        "404":
          description: Document not found
    delete:
      summary: Delete document and its chunks
      operationId: deleteDocument
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        "204":
          description: Document deleted
        "404":
          description: Document not found

  /search:
    post:
      summary: Hybrid search
      operationId: hybridSearch
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                k:
                  type: integer
                  default: 10
                filters:
                  type: object
      responses:
        "200":
          description: Search results with sources

  /search/suggest:
    get:
      summary: Autocomplete suggestions
      operationId: searchSuggestions
      parameters:
        - name: q
          in: query
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Suggestion list

  /chat:
    post:
      summary: RAG Q&A
      operationId: chat
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                session_id:
                  type: string
                  format: uuid
                question:
                  type: string
              required:
                - question
      responses:
        "200":
          description: Answer with sources
          content:
            application/json:
              schema:
                type: object
                properties:
                  answer:
                    type: string
                  sources:
                    type: array
                    items:
                      type: object
                      properties:
                        doc_id:
                          type: string
                        chunk_index:
                          type: integer
                        score:
                          type: number

  /chat/{session_id}/history:
    get:
      summary: Chat session history
      operationId: getChatHistory
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        "200":
          description: Message history

  /mcp/tools:
    get:
      summary: List available MCP tools
      operationId: listMcpTools
      responses:
        "200":
          description: MCP tools list

  /eval/run:
    post:
      summary: Run RAGAS evaluation
      operationId: runEvaluation
      responses:
        "200":
          description: Evaluation results

  /eval/reports:
    get:
      summary: List evaluation reports
      operationId: listEvalReports
      responses:
        "200":
          description: Report list
```

- [ ] **Step 2: Validar OpenAPI**

Run: `cat docs/openapi.yaml | python -c "import sys, yaml; yaml.safe_load(sys.stdin); print('Valid YAML')"`
Expected: "Valid YAML"

- [ ] **Step 3: Commit**

```bash
git add docs/openapi.yaml
git commit -m "docs: add OpenAPI contract for all endpoints"
```

---

### Task 11: Verificación final y README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Crear README.md**

```markdown
# KnowledgeForge

Enterprise knowledge management platform with AI-powered RAG.

## Quick Start

```bash
# 1. Copy environment variables
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 2. Start all services
docker compose up -d

# 3. Run migrations
docker compose exec app uv run alembic upgrade head

# 4. Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Langfuse: http://localhost:3000
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Start dev server
uv run knowledgeforge
```

## Architecture

- **FastAPI** — Async web framework
- **SQLAlchemy + pgvector** — Database with vector embeddings
- **Elasticsearch** — Full-text search with BM25
- **LangChain** — RAG pipeline
- **Langfuse** — LLM observability
- **MCP** — Model Context Protocol server
- **RAGAS** — RAG evaluation metrics

## Project Structure

```
src/knowledgeforge/
├── config.py       # Settings
├── main.py         # FastAPI app
├── db/             # Database layer
├── ingestion/      # Document ingestion
├── search/         # Hybrid search
├── chat/           # RAG chat
├── mcp/            # MCP server
└── eval/           # Evaluation
```
```

- [ ] **Step 2: Run all tests final check**

Run: `uv run pytest tests/ -v --tb=short`
Expected: All tests pass

- [ ] **Step 3: Run linter**

Run: `uv run ruff check src/ tests/`
Expected: No linting errors

- [ ] **Step 4: Final commit**

```bash
git add README.md
git commit -m "docs: add README with setup and development instructions"
```
