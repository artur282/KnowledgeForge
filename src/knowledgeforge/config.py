from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str
    elasticsearch_url: str
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    langfuse_host: str = "http://localhost:3000"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:3000"]
    llm_model: str = "nvidia/nemotron-3-nano-30b-a3b:free"
    embedding_model: str = "text-embedding-3-small"
    elasticsearch_index: str = "knowledgeforge"
    chunk_size: int = 500
    chunk_overlap: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
