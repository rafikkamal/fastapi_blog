from pydantic_settings import BaseSettings

# Define a settings class that loads from environment
class Settings(BaseSettings):
    DATABASE_URL: str  # Required variable

    class Config:
        env_file = ".env"  # Load variables from this file

settings = Settings()  # Create a global settings object
