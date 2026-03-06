def test_conversation_states_defined():
    from src.bot import GOAL, DUE, REMINDER, CONFIRM
    assert GOAL == 0
    assert DUE == 1
    assert REMINDER == 2
    assert CONFIRM == 3
