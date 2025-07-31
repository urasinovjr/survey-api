from pydantic import BaseSettings

class Settings(BaseSettings):
    """Settings for application configuration."""
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"