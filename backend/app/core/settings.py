from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://talk2db:talk2db@localhost:5432/talk2db"
    rag_database_url: str = "postgresql+asyncpg://talk2db_reader:talk2db_reader@localhost:5432/talk2db"
    llm_base_url: str = "http://host.docker.internal:11434"
    llm_api_key: str = "token-abc123"
    llm_model: str = "qwen2.5-coder:14b"
    llm_temperature: float = 0.0
    llm_top_p: float = 0.9
    llm_max_tokens: int = 512
    embedding_base_url: str = "http://host.docker.internal:11434"
    embedding_model: str = "nomic-embed-text"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "schema_context"
    schema_retrieval_top_k: int = 4
    environment: str = "development"
    jwt_secret_key: str = "dev-secret-change-me-with-32-bytes-min"
    jwt_algorithm: str = "HS256"
    jwt_audience: str | None = None
    jwt_issuer: str | None = None
    jwt_expiration_minutes: int = 60
    database_schema: str = "public"
    cors_origins: list[str] = ["http://localhost:4200"]
    database_connection_retries: int = 10
    database_connection_retry_delay_seconds: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
