from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://talk2db:talk2db@localhost:5432/talk2db"
    rag_database_url: str = "postgresql+asyncpg://talk2db_reader:talk2db_reader@localhost:5432/talk2db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4-mini"
    jwt_secret_key: str = "dev-secret-change-me-with-32-bytes-min"
    jwt_algorithm: str = "HS256"
    cors_origins: list[str] = ["http://localhost:4200"]
    database_connection_retries: int = 10
    database_connection_retry_delay_seconds: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
