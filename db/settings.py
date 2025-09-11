# db/settings.py
from typing import Optional

# ✅ Pydantic v2 (pydantic-settings) + fallback на v1
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict  # v2

    class Settings(BaseSettings):
        # --- DB ---
        DATABASE_URL: str

        # --- Security / Auth ---
        SECRET_KEY: str
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

        # --- Server ---
        UVICORN_HOST: str = "0.0.0.0"
        UVICORN_PORT: int = 8000

        # --- Config ---
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
        )

except Exception:
    from pydantic import BaseSettings  # v1

    class Settings(BaseSettings):
        # --- DB ---
        DATABASE_URL: str

        # --- Security / Auth ---
        SECRET_KEY: str
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

        # --- Server ---
        UVICORN_HOST: str = "0.0.0.0"
        UVICORN_PORT: int = 8000

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
