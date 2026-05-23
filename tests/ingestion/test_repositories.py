"""Tests for ingestion repositories."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

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
    result = await doc_repo.delete(uuid4())
    assert result is False


async def test_create_chunks(
    chunk_repo: DocumentChunkRepository,
    doc_repo: DocumentRepository,
    db_session: AsyncSession,
):
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
