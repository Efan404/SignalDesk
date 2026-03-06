import pytest
from src.models import TriageDecision, EmailEvent

def test_triage_decision_creation():
    decision = TriageDecision(
        event_id="test-123",
        importance=2,
        urgency=1,
        delegatable=False,
        needs_user_decision=True,
        reasons=["Test reason"],
        evidence_refs=["ref1"],
        route="DIGEST_EVENING"
    )
    assert decision.event_id == "test-123"
    assert decision.route == "DIGEST_EVENING"
