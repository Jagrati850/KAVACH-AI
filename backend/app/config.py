"""
KAVACH AI — Configuration Management
Centralized configuration using pydantic-settings with .env support.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────
    app_name: str = "KAVACH AI"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Database ────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./kavach.db"

    # ── JWT Authentication ──────────────────────────────
    jwt_secret_key: str = "kavach-hackathon-secret-key-2026-et-ai"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── CORS ────────────────────────────────────────────
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:5500"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # ── File Upload ─────────────────────────────────────
    max_upload_size_mb: int = 10
    upload_dir: str = "./uploads"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    # ── AI Models ───────────────────────────────────────
    ai_model_dir: str = "./data/models"
    scam_patterns_dir: str = "./data/scam_patterns"

    # ── RAG Module ──────────────────────────────────────
    rag_enabled: bool = True

    # ── Logging ─────────────────────────────────────────
    log_level: str = "DEBUG"
    log_file: str = "./logs/kavach.log"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
