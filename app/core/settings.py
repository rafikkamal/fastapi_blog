from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Database ---
    # Use async driver for app (alembic/env.py will adapt it if needed)
    DATABASE_URL: str  # e.g. postgresql+asyncpg://postgres:postgres@db:5432/blog

    # --- JWT / Auth ---
    JWT_SECRET: str = "change-me-in-.env"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Pydantic v2 config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
