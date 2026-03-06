"""Configuration for SignalDesk."""
from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    """Application configuration."""

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    db_path: Path = base_dir / "data" / "signaldesk.db"

    # Gmail settings
    gmail_credentials_path: Path = base_dir / "credentials" / "gmail-credentials.json"
    gmail_token_path: Path = base_dir / "credentials" / "gmail-token.json"

    # LLM settings
    llm_provider: str = "openai"  # or "anthropic"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str | None = None
    llm_temperature: float = 0.0

    # Telegram settings
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # Triage settings
    digest_time: str = "20:00"  # HH:MM format
    max_emails_per_digest: int = 10

    # Importance/Urgency scale
    importance_threshold: int = 3  # 1-5 scale, >= 3 means important
    urgency_threshold: int = 3  # 1-5 scale, >= 3 means urgent


# Global config instance
config = Config()
