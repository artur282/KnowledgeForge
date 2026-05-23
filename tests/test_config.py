import pytest
from pydantic import ValidationError

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

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
