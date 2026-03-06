"""Configuration for SignalDesk."""
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database
    db_path: Path = Path(__file__).parent.parent / "data" / "signaldesk.db"

    # LLM settings (LiteLLM)
    litellm_base_url: str | None = None
    litellm_api_key: str | None = None
    litellm_model: str = "gpt-4o-mini"

    # Telegram settings
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # Digest settings
    digest_time: str = "20:00"  # HH:MM format


# Global config instance
config = Config()
