import typing

from src.models import EmailEvent, TriageDecision

def test_user_task_creation():
    from src.models import UserTask
    import uuid
    task = UserTask(
        task_id=str(uuid.uuid4()),
        goal="完成 README 撰写",
        due="2026-03-13",
        reminder="daily at 15:00"
    )
    assert task.goal == "完成 README 撰写"
    assert task.status == "pending"

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


def test_triage_decision_type_hints_resolve():
    hints = typing.get_type_hints(TriageDecision)
    assert hints["created_at"] is not None
