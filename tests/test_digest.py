import pytest
from src.digest import DigestGenerator
from src.models import TriageDecision, EmailEvent, RouteType
from datetime import datetime, timezone


def test_digest_generation():
    generator = DigestGenerator()
    decisions = [
        TriageDecision(
            event_id="1", importance=2, urgency=2,
            delegatable=False, needs_user_decision=True,
            reasons=["Test"], evidence_refs=[], route=RouteType.DIGEST_EVENING
        )
    ]
    events = {
        "1": EmailEvent(
            event_id="1", subject="Test Email",
            from_addr="test@example.com", timestamp=datetime.now(tz=timezone.utc),
            provider="gmail", thread_id="thread1", message_id="msg1", to_addr="me@example.com"
        )
    }
    digest = generator.generate(decisions, events)
    assert "Digest" in digest
