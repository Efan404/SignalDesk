"""Data models for SignalDesk."""
import datetime
from dataclasses import dataclass
from enum import StrEnum, Enum


class RouteType(StrEnum, Enum):
    """Routing types for triage decisions."""

    PUSH_HIGH = "PUSH_HIGH"
    PUSH_NORMAL = "PUSH_NORMAL"
    DIGEST_EVENING = "DIGEST_EVENING"
    SILENT = "SILENT"
    DELEGATE = "DELEGATE"


@dataclass
class EmailEvent:
    """Email event from Gmail API."""

    event_id: str
    provider: str  # e.g., "gmail"
    thread_id: str
    message_id: str
    from_addr: str
    to_addr: str
    subject: str
    timestamp: datetime
    cc_addr: str | None = None
    body_text: str | None = None
    permalink: str | None = None


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
            self.created_at = datetime.datetime.now(tz=datetime.UTC)


@dataclass
class Task:
    """Task created from a triage decision."""

    task_id: str
    source_event_id: str
    thread_id: str
    goal: str
    status: str = "pending"  # pending, in_progress, completed, failed
    constraints: str | None = None
    inputs: str | None = None
    bub_session_ref: str | None = None
    outputs: str | None = None
    user_feedback: str | None = None


@dataclass
class UserTask:
    """Task created by user via Telegram."""

    task_id: str
    goal: str
    due: str | None = None
    reminder: str | None = None
    status: str = "pending"
    created_at: datetime | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now(tz=datetime.UTC)
