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
