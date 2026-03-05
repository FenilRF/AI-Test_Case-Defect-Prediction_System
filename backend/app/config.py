"""
Application Configuration Module
---------------------------------
Centralized configuration using Pydantic BaseSettings.
Loads environment variables from .env file with sensible defaults.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "AI Test Case & Defect Prediction System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./app_database.db"

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── ML Model Paths ───────────────────────────────────────
    ML_MODEL_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ml_models",
        "saved_models",
    )

    # ── Groq LLM API ─────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_TEXT_MODEL: str = "openai/gpt-oss-120b"
    GROQ_VISION_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # ── Logging ──────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — avoids re-reading .env on every call."""
    return Settings()
