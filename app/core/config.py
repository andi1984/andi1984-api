"""Application configuration loaded from environment variables / .env."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    app_name: str = "andi1984 API"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # Domain settings
    birth_year: int = Field(default=1984, ge=1900, le=2100)
    timezone: str = "UTC"
    writing_feed_url: str = "https://andi1984.dev/rss.xml"
    writing_cache_ttl_seconds: int = Field(default=3600, ge=0)

    # Follower counts. YouTube and dev.to are skipped (null) unless their API key is set.
    followers_cache_ttl_seconds: int = Field(default=3600, ge=0)
    github_username: str = "andi1984"
    mastodon_instance_url: str = "https://dibbelabb.es"
    mastodon_account: str = "andi1984dev"
    youtube_handle: str = "@andi1984dev"
    youtube_api_key: SecretStr | None = None
    devto_api_key: SecretStr | None = None

    # CORS: comma-separated list of allowed origins, e.g. "https://a.com,https://b.com"
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance. Use as a FastAPI dependency."""
    return Settings()
