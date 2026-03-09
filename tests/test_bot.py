import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


def test_conversation_states_defined():
    from src.bot import GOAL, DUE, REMINDER, CONFIRM
    assert GOAL == 0
    assert DUE == 1
    assert REMINDER == 2
    assert CONFIRM == 3


def test_unknown_message_returns_guidance():
    from src.bot import handle_unknown_message

    class DummyMessage:
        def __init__(self):
            self.calls = []
            self.text = "你好"

        async def reply_text(self, text):
            self.calls.append(text)

    update = SimpleNamespace(message=DummyMessage(), effective_chat=SimpleNamespace(id=123))
    context = SimpleNamespace(user_data={})

    asyncio.run(handle_unknown_message(update, context))

    assert update.message.calls
    assert "/task" in update.message.calls[0]


def test_run_bot_initializes_db():
    from src import bot as bot_module

    mock_app = MagicMock()
    mock_builder = MagicMock()
    mock_builder.token.return_value.build.return_value = mock_app

    with patch.object(bot_module.config, "telegram_bot_token", "token"), \
         patch.object(bot_module, "init_db") as mock_init_db, \
         patch.object(bot_module.Application, "builder", return_value=mock_builder):
        bot_module.run_bot()

    mock_init_db.assert_called_once()
