"""
Configuration management for the Todo Backend.

Loads environment variables and provides typed configuration objects
for the FastAPI application.
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql://todouser:todopass@localhost:5432/tododb"

    # JWT Authentication
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Application
    environment: Literal["development", "production", "test"] = "development"
    frontend_url: str = "http://localhost:3000"
    api_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


# Global settings instance
settings = Settings()
