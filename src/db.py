"""Database functions for SignalDesk."""
import datetime
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager

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
                event_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                from_addr TEXT NOT NULL,
                to_addr TEXT NOT NULL,
                cc_addr TEXT,
                subject TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                body_text TEXT,
                permalink TEXT,
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
                FOREIGN KEY (event_id) REFERENCES email_events (event_id)
            )
        """)

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                source_event_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                goal TEXT NOT NULL,
                constraints TEXT,
                inputs TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                bub_session_ref TEXT,
                outputs TEXT,
                user_feedback TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_event_id) REFERENCES email_events (event_id)
            )
        """)

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_email_timestamp ON email_events(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_triage_event_id ON triage_decisions(event_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_source_event_id ON tasks(source_event_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)"
        )

        conn.commit()


def save_email_event(event: EmailEvent) -> None:
    """Save an email event to the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO email_events
            (event_id, provider, thread_id, message_id, from_addr, to_addr, cc_addr, subject, timestamp, body_text, permalink)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.provider,
                event.thread_id,
                event.message_id,
                event.from_addr,
                event.to_addr,
                event.cc_addr,
                event.subject,
                event.timestamp.isoformat(),
                event.body_text,
                event.permalink,
            ),
        )
        conn.commit()


def get_email_event(event_id: str) -> EmailEvent | None:
    """Get an email event by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM email_events WHERE event_id = ?", (event_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        return EmailEvent(
            event_id=row["event_id"],
            provider=row["provider"],
            thread_id=row["thread_id"],
            message_id=row["message_id"],
            from_addr=row["from_addr"],
            to_addr=row["to_addr"],
            cc_addr=row["cc_addr"],
            subject=row["subject"],
            timestamp=datetime.datetime.fromisoformat(row["timestamp"]),
            body_text=row["body_text"],
            permalink=row["permalink"],
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
                decision.created_at.isoformat() if decision.created_at else datetime.datetime.now(tz=datetime.UTC).isoformat(),
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
            created_at=datetime.datetime.fromisoformat(row["created_at"]),
        )
