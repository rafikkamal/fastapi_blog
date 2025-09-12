# -----------------------------------------------------------------------------
# Enable forward references in type hints
# -----------------------------------------------------------------------------
# - Allows you to reference classes/types before they are defined in the file.
# - Useful in large projects; here it’s harmless but consistent with rest of code.
from __future__ import annotations

# -----------------------------------------------------------------------------
# Import BaseSettings and SettingsConfigDict from pydantic-settings
# -----------------------------------------------------------------------------
# - BaseSettings: lets you define a class where attributes are read from environment variables.
# - SettingsConfigDict: Pydantic v2 way of configuring settings (e.g., which .env file to load).
from pydantic_settings import BaseSettings, SettingsConfigDict


# -----------------------------------------------------------------------------
# Define a Settings class that loads environment variables into attributes
# -----------------------------------------------------------------------------
class Settings(BaseSettings):
    # --- Database -------------------------------------------------------------
    # - DATABASE_URL is required: must be provided via .env or real environment.
    # - Example format for async Postgres:
    #   postgresql+asyncpg://<USER>:<PASSWORD>@<HOST>:<PORT>/<DBNAME>
    DATABASE_URL: str

    # --- JWT / Auth -----------------------------------------------------------
    # - JWT_SECRET: symmetric signing key for JWT tokens.
    #   Should be a long random string. Default is placeholder, overridden in .env.
    JWT_SECRET: str = "change-me-in-.env"

    # - JWT_ALGORITHM: cryptographic algorithm used for JWT signing/verification.
    #   HS256 = HMAC-SHA256. Matches what jose.jwt.encode/decode use.
    JWT_ALGORITHM: str = "HS256"

    # - ACCESS_TOKEN_EXPIRE_MINUTES: default lifetime for issued access tokens.
    #   60 means tokens expire 1 hour after creation unless overridden.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Pydantic v2 model configuration -------------------------------------
    # - env_file=".env" → load variables from project’s .env file automatically.
    # - env_file_encoding="utf-8" ensures file is read correctly.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# -----------------------------------------------------------------------------
# Instantiate the settings object
# -----------------------------------------------------------------------------
# - When this line runs, Pydantic loads variables from environment/.env.
# - The `settings` object is then imported everywhere else in the app.
# - Example usage:
#     from app.core.settings import settings
#     print(settings.DATABASE_URL)
# -----------------------------------------------------------------------------
settings = Settings()
