"""Data models for SignalDesk."""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class RouteType(str, Enum):
    """Routing types for triage decisions."""

    DIGEST_EVENING = "DIGEST_EVENING"
    DIGEST_MORNING = "DIGEST_MORNING"
    IMMEDIATE = "IMMEDIATE"
    DELEGATE = "DELEGATE"
    ARCHIVE = "ARCHIVE"


@dataclass
class EmailEvent:
    """Email event from Gmail API."""

    id: str
    thread_id: str
    subject: str
    sender: str
    sender_email: str
    snippet: str
    received_at: datetime
    is_read: bool = False
    labels: list[str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = []


@dataclass
class TriageDecision:
    """Triage decision for an email event."""

    event_id: str
    importance: int  # 1-5 scale
    urgency: int  # 1-5 scale
    delegatable: bool
    needs_user_decision: bool
    reasons: list[str]
    evidence_refs: list[str]
    route: str  # RouteType value
    created_at: datetime | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
