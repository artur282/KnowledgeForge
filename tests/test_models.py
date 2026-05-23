from knowledgeforge.db.models import Base, ChatMessage, ChatSession, Document, DocumentChunk, EvalReport


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
    expected = {"documents", "document_chunks", "chat_sessions", "chat_messages", "eval_reports"}
    actual = set(Base.metadata.tables.keys())
    assert actual == expected


def test_eval_report_table_name():
    """EvalReport model maps to eval_reports table."""
    assert EvalReport.__tablename__ == "eval_reports"
