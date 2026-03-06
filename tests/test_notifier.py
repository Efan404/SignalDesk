import pytest
from src.notifier import TelegramNotifier


def test_notifier_initialization():
    notifier = TelegramNotifier()
    # Without token configured, should be disabled
    assert notifier.enabled is False
