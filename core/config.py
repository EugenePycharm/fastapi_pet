from functools import lru_cache
from typing import Final

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения с поддержкой .env файлов."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "fastapi_gemini"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    # Application settings
    APP_NAME: str = "FastAPI Gemini Clone"
    DEBUG: bool = False

    # Security settings
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API keys
    API_KEY: str | None = None

    @property
    def database_url(self) -> str:
        """Формирует PostgreSQL URL для asyncpg."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def database_url_sync(self) -> str:
        """Формирует PostgreSQL URL для синхронных операций (Alembic)."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def async_database_url(self) -> PostgresDsn:
        """Валидированный PostgreSQL DSN для asyncpg."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )


@lru_cache
def get_settings() -> Settings:
    """Кэшированный экземпляр настроек."""
    return Settings()


settings: Final[Settings] = get_settings()
