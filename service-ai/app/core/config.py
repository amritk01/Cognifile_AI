
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Cognifile AI Service"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Gemini
    GOOGLE_API_KEY: str
    PRIMARY_MODEL: str = "gemini-3.8-flash"
    FALLBACK_MODEL: str = "gemini-3.8-flash"

    # Production settings
    RATE_LIMIT: str = "20/minute"
    CACHE_TTL_SECONDS: int = 300
    MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
