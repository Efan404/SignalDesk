"""Database functions for SignalDesk."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator

from src.config import config
from src.models import EmailEvent, TriageDecision


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection."""
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database operations."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Email events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_events (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                sender_email TEXT NOT NULL,
                snippet TEXT,
                received_at TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                labels TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Triage decisions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triage_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                importance INTEGER NOT NULL,
                urgency INTEGER NOT NULL,
                delegatable INTEGER NOT NULL,
                needs_user_decision INTEGER NOT NULL,
                reasons TEXT NOT NULL,
                evidence_refs TEXT NOT NULL,
                route TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES email_events (id)
            )
        """)

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_email_received_at ON email_events(received_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_triage_event_id ON triage_decisions(event_id)"
        )

        conn.commit()


def save_email_event(event: EmailEvent) -> None:
    """Save an email event to the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO email_events
            (id, thread_id, subject, sender, sender_email, snippet, received_at, is_read, labels)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.thread_id,
                event.subject,
                event.sender,
                event.sender_email,
                event.snippet,
                event.received_at.isoformat(),
                1 if event.is_read else 0,
                ",".join(event.labels),
            ),
        )
        conn.commit()


def get_email_event(event_id: str) -> EmailEvent | None:
    """Get an email event by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM email_events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        return EmailEvent(
            id=row["id"],
            thread_id=row["thread_id"],
            subject=row["subject"],
            sender=row["sender"],
            sender_email=row["sender_email"],
            snippet=row["snippet"],
            received_at=datetime.fromisoformat(row["received_at"]),
            is_read=bool(row["is_read"]),
            labels=row["labels"].split(",") if row["labels"] else [],
        )


def save_triage_decision(decision: TriageDecision) -> None:
    """Save a triage decision to the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO triage_decisions
            (event_id, importance, urgency, delegatable, needs_user_decision, reasons, evidence_refs, route, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision.event_id,
                decision.importance,
                decision.urgency,
                1 if decision.delegatable else 0,
                1 if decision.needs_user_decision else 0,
                ",".join(decision.reasons),
                ",".join(decision.evidence_refs),
                decision.route,
                decision.created_at.isoformat() if decision.created_at else datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()


def get_triage_decision(event_id: str) -> TriageDecision | None:
    """Get a triage decision by event ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM triage_decisions WHERE event_id = ? ORDER BY created_at DESC LIMIT 1",
            (event_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        return TriageDecision(
            event_id=row["event_id"],
            importance=row["importance"],
            urgency=row["urgency"],
            delegatable=bool(row["delegatable"]),
            needs_user_decision=bool(row["needs_user_decision"]),
            reasons=row["reasons"].split(","),
            evidence_refs=row["evidence_refs"].split(","),
            route=row["route"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
