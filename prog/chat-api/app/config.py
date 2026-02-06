"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://chatuser:chatpass@localhost:5432/chatdb"
    TEST_DATABASE_URL: str = "postgresql+asyncpg://chatuser:chatpass@db:5432/chatdb_test"
    
    # Application
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # API
    API_V1_PREFIX: str = ""
    PROJECT_NAME: str = "Chat API"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()
