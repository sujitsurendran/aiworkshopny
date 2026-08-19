"""
Application configuration using pydantic-settings.
All environment-specific settings are loaded from environment variables or .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./verizon_credit.db"

    # Security
    secret_key: str = "change-me-in-production"
    token_expiry_seconds: int = 86400  # 24 hours

    # API
    api_port: int = 9000
    debug: bool = True

    # CORS
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
