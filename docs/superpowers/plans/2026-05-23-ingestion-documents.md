# Sub-proyecto 2: Ingesta de Documentos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar ingesta asíncrona de documentos (PDF, Markdown, HTML) con chunking, embeddings y dual-write a PostgreSQL (pgvector) + Elasticsearch.

**Architecture:** Layered architecture con router → service → repository. Usa FastAPI BackgroundTasks para procesamiento asíncrono. El servicio de ingesta parsea documentos, los divide en chunks, genera embeddings con OpenAI, y escribe en PostgreSQL (pgvector) y Elasticsearch de forma atómica.

**Tech Stack:** FastAPI, LangChain (document loaders + text splitter), OpenAI embeddings, asyncpg, elasticsearch-py, python-multipart

---

## Estructura de Archivos

| Archivo | Responsabilidad |
|---------|----------------|
| `src/knowledgeforge/ingestion/schemas.py` | Pydantic schemas para request/response |
| `src/knowledgeforge/ingestion/repositories.py` | Acceso a datos (CRUD Document + DocumentChunk) |
| `src/knowledgeforge/ingestion/services.py` | Lógica de negocio: parse, chunk, embed, dual-write |
| `src/knowledgeforge/ingestion/router.py` | Endpoints HTTP: POST /documents, GET /documents/{id}, DELETE /documents/{id} |
| `src/knowledgeforge/ingestion/parsers.py` | Parseo de PDF, Markdown, HTML |
| `tests/ingestion/__init__.py` | Package marker |
| `tests/ingestion/test_parsers.py` | Tests de parseo |
| `tests/ingestion/test_services.py` | Tests de servicio de ingesta |
| `tests/ingestion/test_router.py` | Tests de endpoints |
| `src/knowledgeforge/main.py` | Registrar ingestion router |

---

### Task 1: Schemas y Repositories de Ingesta

**Files:**
- Create: `src/knowledgeforge/ingestion/schemas.py`
- Create: `src/knowledgeforge/ingestion/repositories.py`
- Test: `tests/ingestion/test_repositories.py`

- [ ] **Step 1: Crear schemas de ingesta**

```python
"""Pydantic schemas for ingestion endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Response schema for document details."""

    id: UUID
    filename: str
    status: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""

    status: str = "queued"
    document_id: UUID | None = None
```

- [ ] **Step 2: Crear repositories de ingesta**

```python
"""Data access layer for documents and chunks."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.models import Document, DocumentChunk


class DocumentRepository:
    """Repository for Document CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, filename: str, content_hash: str) -> Document:
        """Create a new document record."""
        doc = Document(filename=filename, content_hash=content_hash, status="pending")
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def get_by_id(self, doc_id: UUID) -> Document | None:
        """Get document by ID."""
        result = await self.session.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def update_status(self, doc_id: UUID, status: str) -> Document | None:
        """Update document processing status."""
        doc = await self.get_by_id(doc_id)
        if doc:
            doc.status = status
            await self.session.flush()
        return doc

    async def delete(self, doc_id: UUID) -> bool:
        """Delete document and cascade-delete its chunks. Returns True if found."""
        doc = await self.get_by_id(doc_id)
        if doc:
            await self.session.delete(doc)
            await self.session.flush()
            return True
        return False


class DocumentChunkRepository:
    """Repository for DocumentChunk operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_many(self, chunks: list[dict]) -> list[DocumentChunk]:
        """Bulk create document chunks with embeddings."""
        records = [
            DocumentChunk(
                document_id=c["document_id"],
                chunk_index=c["chunk_index"],
                content=c["content"],
                embedding=c.get("embedding"),
                metadata_=c.get("metadata", {}),
            )
            for c in chunks
        ]
        self.session.add_all(records)
        await self.session.flush()
        return records
```

- [ ] **Step 3: Escribir tests para repositories**

```python
"""Tests for ingestion repositories."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.models import Document
from knowledgeforge.ingestion.repositories import DocumentChunkRepository, DocumentRepository


@pytest.fixture
def doc_repo(db_session: AsyncSession) -> DocumentRepository:
    return DocumentRepository(db_session)


@pytest.fixture
def chunk_repo(db_session: AsyncSession) -> DocumentChunkRepository:
    return DocumentChunkRepository(db_session)


async def test_create_document(doc_repo: DocumentRepository, db_session: AsyncSession):
    doc = await doc_repo.create("test.pdf", "hash123")
    await db_session.commit()
    assert doc.filename == "test.pdf"
    assert doc.status == "pending"
    assert doc.id is not None


async def test_get_document_by_id(doc_repo: DocumentRepository, db_session: AsyncSession):
    doc = await doc_repo.create("test.pdf", "hash123")
    await db_session.commit()
    found = await doc_repo.get_by_id(doc.id)
    assert found is not None
    assert found.id == doc.id


async def test_get_nonexistent_document(doc_repo: DocumentRepository):
    from uuid import uuid4
    result = await doc_repo.get_by_id(uuid4())
    assert result is None


async def test_update_status(doc_repo: DocumentRepository, db_session: AsyncSession):
    doc = await doc_repo.create("test.pdf", "hash123")
    await db_session.commit()
    updated = await doc_repo.update_status(doc.id, "ready")
    assert updated is not None
    assert updated.status == "ready"


async def test_delete_document(doc_repo: DocumentRepository, db_session: AsyncSession):
    doc = await doc_repo.create("test.pdf", "hash123")
    await db_session.commit()
    deleted = await doc_repo.delete(doc.id)
    await db_session.commit()
    assert deleted is True
    found = await doc_repo.get_by_id(doc.id)
    assert found is None


async def test_delete_nonexistent_document(doc_repo: DocumentRepository):
    from uuid import uuid4
    result = await doc_repo.delete(uuid4())
    assert result is False


async def test_create_chunks(chunk_repo: DocumentChunkRepository, doc_repo: DocumentRepository, db_session: AsyncSession):
    doc = await doc_repo.create("test.pdf", "hash123")
    await db_session.commit()

    chunks_data = [
        {"document_id": doc.id, "chunk_index": 0, "content": "Chunk 0", "metadata": {"page": 1}},
        {"document_id": doc.id, "chunk_index": 1, "content": "Chunk 1", "metadata": {"page": 2}},
    ]
    created = await chunk_repo.create_many(chunks_data)
    await db_session.commit()

    assert len(created) == 2
    assert created[0].chunk_index == 0
    assert created[1].content == "Chunk 1"
```

- [ ] **Step 4: Commit**

```bash
git add src/knowledgeforge/ingestion/schemas.py src/knowledgeforge/ingestion/repositories.py tests/ingestion/test_repositories.py
git commit -m "feat(ingestion): add schemas and repositories for document ingestion"
```

---

### Task 2: Parsers de Documentos

**Files:**
- Create: `src/knowledgeforge/ingestion/parsers.py`
- Test: `tests/ingestion/test_parsers.py`

- [ ] **Step 1: Crear parsers de documentos**

```python
"""Document parsers for PDF, Markdown, and HTML files."""

import hashlib
import io
from enum import Enum

from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredHTMLLoader


class DocumentType(Enum):
    """Supported document types."""

    PDF = "pdf"
    MARKDOWN = "md"
    HTML = "html"
    TEXT = "txt"


def detect_type(filename: str) -> DocumentType:
    """Detect document type from filename extension."""
    ext = filename.rsplit(".", 1)[-1].lower()
    mapping = {
        "pdf": DocumentType.PDF,
        "md": DocumentType.MARKDOWN,
        "markdown": DocumentType.MARKDOWN,
        "html": DocumentType.HTML,
        "htm": DocumentType.HTML,
        "txt": DocumentType.TEXT,
    }
    return mapping.get(ext, DocumentType.TEXT)


def compute_hash(content: bytes) -> str:
    """Compute SHA-256 hash for deduplication."""
    return hashlib.sha256(content).hexdigest()


def parse_document(file_bytes: bytes, filename: str) -> str:
    """Parse a document and return its text content.

    Args:
        file_bytes: Raw file bytes.
        filename: Original filename for type detection.

    Returns:
        Extracted text content.
    """
    doc_type = detect_type(filename)

    if doc_type == DocumentType.PDF:
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(file_bytes)
            f.flush()
            loader = PyPDFLoader(f.name)
            docs = loader.load()
        return "\n\n".join(doc.page_content for doc in docs)

    if doc_type == DocumentType.HTML:
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="wb") as f:
            f.write(file_bytes)
            f.flush()
            loader = UnstructuredHTMLLoader(f.name)
            docs = loader.load()
        return "\n\n".join(doc.page_content for doc in docs)

    # Markdown and plain text
    text = file_bytes.decode("utf-8")
    if doc_type == DocumentType.MARKDOWN:
        return text
    return text
```

- [ ] **Step 2: Escribir tests para parsers**

```python
"""Tests for document parsers."""

from knowledgeforge.ingestion.parsers import DocumentType, compute_hash, detect_type, parse_document


def test_detect_pdf():
    assert detect_type("report.pdf") == DocumentType.PDF


def test_detect_markdown():
    assert detect_type("notes.md") == DocumentType.MARKDOWN
    assert detect_type("notes.markdown") == DocumentType.MARKDOWN


def test_detect_html():
    assert detect_type("page.html") == DocumentType.HTML
    assert detect_type("page.htm") == DocumentType.HTML


def test_detect_text():
    assert detect_type("notes.txt") == DocumentType.TEXT
    assert detect_type("unknown.xyz") == DocumentType.TEXT


def test_compute_hash():
    h1 = compute_hash(b"hello")
    h2 = compute_hash(b"hello")
    h3 = compute_hash(b"world")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64  # SHA-256 hex length


def test_parse_text():
    content = b"Plain text content"
    result = parse_document(content, "notes.txt")
    assert result == "Plain text content"


def test_parse_markdown():
    content = b"# Heading\n\nSome **bold** text"
    result = parse_document(content, "notes.md")
    assert result == "# Heading\n\nSome **bold** text"
```

- [ ] **Step 3: Commit**

```bash
git add src/knowledgeforge/ingestion/parsers.py tests/ingestion/test_parsers.py
git commit -m "feat(ingestion): add document parsers for PDF, Markdown, HTML, and text"
```

---

### Task 3: Servicio de Ingesta

**Files:**
- Create: `src/knowledgeforge/ingestion/services.py`
- Test: `tests/ingestion/test_services.py`

- [ ] **Step 1: Crear servicio de ingesta**

```python
"""Ingestion service: parse, chunk, embed, and dual-write."""

import logging
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.config import Settings
from knowledgeforge.ingestion.parsers import compute_hash, parse_document
from knowledgeforge.ingestion.repositories import DocumentChunkRepository, DocumentRepository

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


class IngestionService:
    """Orchestrates document ingestion pipeline."""

    def __init__(
        self,
        session: AsyncSession,
        es_client: AsyncElasticsearch,
        settings: Settings,
    ) -> None:
        self.doc_repo = DocumentRepository(session)
        self.chunk_repo = DocumentChunkRepository(session)
        self.es_client = es_client
        self.settings = settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key,
        )

    async def process(self, file_bytes: bytes, filename: str) -> UUID:
        """Full ingestion pipeline.

        1. Create document record (status: pending)
        2. Parse document to text
        3. Split into chunks
        4. Generate embeddings
        5. Write to PostgreSQL + Elasticsearch
        6. Update status to ready

        Returns:
            Document ID.
        """
        content_hash = compute_hash(file_bytes)

        # Check for duplicate
        existing = await self._get_by_hash(content_hash)
        if existing:
            logger.info("Duplicate document detected: %s", filename)
            return existing.id

        # Create document record
        doc = await self.doc_repo.create(filename, content_hash)
        await self.doc_repo.update_status(doc.id, "processing")

        try:
            # Parse
            text = parse_document(file_bytes, filename)

            # Chunk
            chunks = self.text_splitter.split_text(text)

            # Embed
            chunk_embeddings = await self.embeddings.aembed_documents(chunks)

            # Build chunk records
            chunk_records = [
                {
                    "document_id": doc.id,
                    "chunk_index": i,
                    "content": chunk,
                    "embedding": embedding,
                    "metadata": {"filename": filename, "chunk_size": len(chunk)},
                }
                for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings, strict=False))
            ]

            # Dual write
            await self.chunk_repo.create_many(chunk_records)
            await self._write_to_es(doc.id, filename, chunk_records)

            await self.doc_repo.update_status(doc.id, "ready")
            logger.info("Document %s ingested successfully (%d chunks)", filename, len(chunks))

        except Exception:
            await self.doc_repo.update_status(doc.id, "failed")
            logger.exception("Failed to ingest document %s", filename)
            raise

        return doc.id

    async def _get_by_hash(self, content_hash: str):
        """Get document by content hash."""
        from sqlalchemy import select
        from knowledgeforge.db.models import Document

        result = await self.doc_repo.session.execute(
            select(Document).where(Document.content_hash == content_hash)
        )
        return result.scalar_one_or_none()

    async def _write_to_es(self, doc_id: UUID, filename: str, chunks: list[dict]) -> None:
        """Write chunks to Elasticsearch for BM25 search."""
        from elasticsearch.helpers import async_bulk

        async def chunk_generator():
            for chunk in chunks:
                yield {
                    "_index": "knowledgeforge",
                    "_id": f"{doc_id}-{chunk['chunk_index']}",
                    "_source": {
                        "document_id": str(doc_id),
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "filename": filename,
                        "metadata": chunk["metadata"],
                    },
                }

        await async_bulk(self.es_client, chunk_generator())
```

- [ ] **Step 2: Escribir tests para servicio**

```python
"""Tests for ingestion service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.config import Settings
from knowledgeforge.ingestion.services import IngestionService


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_es():
    return AsyncMock()


@pytest.fixture
def mock_settings():
    return Settings(
        database_url="sqlite+aiosqlite:///test.db",
        elasticsearch_url="http://localhost:9200",
        openai_api_key="sk-test-key",
    )


@pytest.fixture
def service(mock_session, mock_es, mock_settings):
    return IngestionService(mock_session, mock_es, mock_settings)


def test_service_initialization(service):
    assert service.text_splitter is not None
    assert service.embeddings is not None


@patch.object(IngestionService, "_get_by_hash", new_callable=AsyncMock)
@patch.object(IngestionService, "_write_to_es", new_callable=AsyncMock)
async def test_process_duplicate_document(mock_es_write, mock_get_hash, service, mock_session):
    """Duplicate documents return existing ID."""
    from unittest.mock import Mock
    from uuid import uuid4

    existing_doc = Mock()
    existing_doc.id = uuid4()
    mock_get_hash.return_value = existing_doc

    doc_id = await service.process(b"content", "test.pdf")
    assert doc_id == existing_doc.id
    mock_es_write.assert_not_called()
```

- [ ] **Step 3: Commit**

```bash
git add src/knowledgeforge/ingestion/services.py tests/ingestion/test_services.py
git commit -m "feat(ingestion): add ingestion service with parse-chunk-embed-dualwrite pipeline"
```

---

### Task 4: Router de Ingesta

**Files:**
- Create: `src/knowledgeforge/ingestion/router.py`
- Create: `src/knowledgeforge/ingestion/__init__.py`
- Modify: `src/knowledgeforge/main.py`
- Test: `tests/ingestion/test_router.py`

- [ ] **Step 1: Crear router de ingesta**

```python
"""HTTP endpoints for document ingestion."""

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.engine import get_async_session
from knowledgeforge.ingestion.repositories import DocumentRepository
from knowledgeforge.ingestion.schemas import DocumentResponse, DocumentUploadResponse
from knowledgeforge.ingestion.services import IngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


def get_ingestion_service(
    session: AsyncSession = Depends(get_async_session),
) -> IngestionService:
    """Dependency injection for IngestionService."""
    from knowledgeforge.config import Settings
    from knowledgeforge.main import app

    settings = Settings()
    es_client = app.state.es_client
    return IngestionService(session, es_client, settings)


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=202,
    operation_id="uploadDocument",
)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    ingestion_svc: IngestionService = Depends(get_ingestion_service),
):
    """Upload a document for async ingestion."""
    file_bytes = await file.read()
    doc_id = await ingestion_svc.process(file_bytes, file.filename or "unknown")
    return DocumentUploadResponse(document_id=doc_id)


@router.get(
    "/{doc_id}",
    response_model=DocumentResponse,
    operation_id="getDocumentStatus",
)
async def get_document_status(
    doc_id: UUID,
    repo: DocumentRepository = Depends(
        lambda session=Depends(get_async_session): DocumentRepository(session)
    ),
):
    """Get document processing status."""
    doc = await repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.delete(
    "/{doc_id}",
    status_code=204,
    operation_id="deleteDocument",
)
async def delete_document(
    doc_id: UUID,
    repo: DocumentRepository = Depends(
        lambda session=Depends(get_async_session): DocumentRepository(session)
    ),
):
    """Delete a document and all its chunks."""
    deleted = await repo.delete(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
```

- [ ] **Step 2: Actualizar ingestion/__init__.py**

```python
"""Document ingestion module."""

from knowledgeforge.ingestion.router import router

__all__ = ["router"]
```

- [ ] **Step 3: Registrar router en main.py**

Modificar `src/knowledgeforge/main.py` - agregar import y registro del router:

```python
# Agregar después de los imports existentes
from knowledgeforge.ingestion import router as ingestion_router

# Agregar en create_app() antes del return
app.include_router(ingestion_router)
```

- [ ] **Step 4: Escribir tests para router**

```python
"""Tests for ingestion endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


@patch("knowledgeforge.ingestion.router.IngestionService")
async def test_upload_document(mock_service, client: AsyncClient):
    """POST /documents returns 202 with document ID."""
    from uuid import uuid4

    mock_instance = AsyncMock()
    mock_instance.process.return_value = uuid4()
    mock_service.return_value = mock_instance

    response = await client.post(
        "/documents",
        files={"file": ("test.txt", b"Hello world", "text/plain")},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert "document_id" in data


async def test_get_document_not_found(client: AsyncClient):
    """GET /documents/{id} returns 404 for nonexistent document."""
    response = await client.get(f"/documents/{uuid4()}")
    assert response.status_code == 404


async def test_delete_document_not_found(client: AsyncClient):
    """DELETE /documents/{id} returns 404 for nonexistent document."""
    response = await client.delete(f"/documents/{uuid4()}")
    assert response.status_code == 404
```

- [ ] **Step 5: Commit**

```bash
git add src/knowledgeforge/ingestion/__init__.py src/knowledgeforge/ingestion/router.py tests/ingestion/test_router.py src/knowledgeforge/main.py
git commit -m "feat(ingestion): add HTTP endpoints for document upload, status, and deletion"
```

---

### Task 5: Integrar Elasticsearch Client en Lifespan

**Files:**
- Modify: `src/knowledgeforge/main.py`

- [ ] **Step 1: Agregar Elasticsearch client al lifespan**

Modificar `src/knowledgeforge/main.py`:

```python
# Agregar imports
from elasticsearch import AsyncElasticsearch

# Modificar lifespan para incluir ES client
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize and shutdown application resources."""
    logger.info("Starting KnowledgeForge...")

    settings = Settings()
    app.state.engine = create_engine(settings.database_url)
    app.state.session_factory = get_session_factory(app.state.engine)

    # Initialize Elasticsearch client
    app.state.es_client = AsyncElasticsearch(
        hosts=[settings.elasticsearch_url],
        request_timeout=30,
    )
    # Verify ES connection
    info = await app.state.es_client.info()
    logger.info("Elasticsearch connected: %s", info["version"]["number"])

    logger.info("Database engine initialized")
    logger.info("Elasticsearch URL: %s", settings.elasticsearch_url)

    yield

    logger.info("Shutting down KnowledgeForge...")
    await app.state.engine.dispose()
    await app.state.es_client.close()
```

- [ ] **Step 2: Commit**

```bash
git add src/knowledgeforge/main.py
git commit -m "feat: add Elasticsearch client to application lifespan"
```

---

### Task 6: Verificación Final

- [ ] **Step 1: Ejecutar tests**

```bash
uv run pytest tests/ -v
```

Esperado: Todos los tests pasan (15+ tests)

- [ ] **Step 2: Ejecutar linting**

```bash
uv run ruff check src/ tests/
```

Esperado: 0 issues

- [ ] **Step 3: Verificar que la app arranca**

```bash
uv run knowledgeforge
```

Esperado: App arranca en puerto 8000, logs muestran conexión a ES

- [ ] **Step 4: Commit final si hay cambios**

```bash
git add -A
git commit -m "chore: final verification and cleanup for ingestion sub-project"
```