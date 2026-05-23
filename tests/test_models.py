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
