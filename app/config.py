"""Application configuration management."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Almaty Market Research Platform"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_v1_prefix: str = "/api/v1"

    # Database (PostgreSQL)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "almaty_market_research"

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Synchronous URL for Alembic migrations."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Cache
    cache_ttl_analysis: int = 3600  # 1 hour
    cache_ttl_opportunities: int = 1800  # 30 minutes
    cache_ttl_recommendations: int = 900  # 15 minutes
    cache_enabled: bool = True

    # Data collection
    google_maps_api_key: Optional[str] = None
    collection_default_limit: int = 100

    # LLM (OpenAI)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1024

    # Scheduler
    scheduler_enabled: bool = True
    collection_cron_hour: int = 2
    collection_cron_minute: int = 0


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
