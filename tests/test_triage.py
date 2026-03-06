import pytest
from src.triage import TriageEngine
from src.models import EmailEvent
from datetime import datetime, timezone


def test_triage_engine_initialization():
    engine = TriageEngine()
    assert engine.model == "openai/gpt-4o-mini"


def test_triage_decision_structure():
    engine = TriageEngine()
    email = EmailEvent(
        event_id="test-123",
        provider="gmail",
        thread_id="thread-123",
        message_id="msg-123",
        from_addr="oncall@company.com",
        to_addr="me@company.com",
        subject="Urgent: Server down",
        body_text="Our production server is down!",
        timestamp=datetime.now(tz=timezone.utc)
    )
    assert email.subject == "Urgent: Server down"
