"""Tests for ingestion service."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest

from knowledgeforge.config import Settings
from knowledgeforge.ingestion.services import IngestionService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
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
    assert service.doc_repo is not None
    assert service.chunk_repo is not None


@patch.object(IngestionService, "_get_by_hash", new_callable=AsyncMock)
@patch.object(IngestionService, "_write_to_es", new_callable=AsyncMock)
async def test_process_duplicate_document(mock_es_write, mock_get_hash, service):
    """Duplicate documents return existing ID."""
    existing_doc = Mock()
    existing_doc.id = uuid4()
    mock_get_hash.return_value = existing_doc

    doc_id = await service.process(b"content", "test.pdf")

    assert doc_id == existing_doc.id
    mock_es_write.assert_not_called()


@patch.object(IngestionService, "_get_by_hash", new_callable=AsyncMock)
async def test_process_creates_document(mock_get_hash, service, mock_session):
    """New document goes through full pipeline."""
    mock_get_hash.return_value = None

    doc_mock = Mock()
    doc_mock.id = uuid4()

    service.doc_repo.create = AsyncMock(return_value=doc_mock)
    service.doc_repo.update_status = AsyncMock()
    service.chunk_repo.create_many = AsyncMock(return_value=[])
    service._write_to_es = AsyncMock()

    with (
        patch("knowledgeforge.ingestion.services.parse_document", return_value="Test content here"),
        patch("langchain_openai.OpenAIEmbeddings.aembed_documents", new_callable=AsyncMock) as mock_embed,
    ):
        mock_embed.return_value = [[0.1] * 1536]

        doc_id = await service.process(b"content", "test.txt")

        assert doc_id == doc_mock.id
        service.doc_repo.create.assert_called_once()
        service.doc_repo.update_status.assert_called()
        service.chunk_repo.create_many.assert_called_once()
        service._write_to_es.assert_called_once()


@patch.object(IngestionService, "_get_by_hash", new_callable=AsyncMock)
async def test_process_failed_document_updates_status(mock_get_hash, service):
    """Failed documents get status 'failed'."""
    mock_get_hash.return_value = None

    doc_mock = Mock()
    doc_mock.id = uuid4()

    service.doc_repo.create = AsyncMock(return_value=doc_mock)
    service.doc_repo.update_status = AsyncMock()

    with patch("knowledgeforge.ingestion.services.parse_document", side_effect=Exception("Parse error")):
        with pytest.raises(Exception, match="Parse error"):
            await service.process(b"content", "test.txt")

        service.doc_repo.update_status.assert_any_call(doc_mock.id, "failed")
