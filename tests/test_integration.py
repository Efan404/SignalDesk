import pytest
import uuid
import asyncio
from unittest.mock import patch, MagicMock
from src.main import process_emails
from src.db import save_user_task, get_user_tasks, init_db


def test_process_emails_empty():
    # Mock gws to return empty
    with patch('src.main.GmailIngestor') as MockIngestor:
        mock_instance = MagicMock()
        mock_instance.fetch_recent_emails.return_value = []
        MockIngestor.return_value = mock_instance

        result = asyncio.run(process_emails(max_results=1))
    assert isinstance(result, dict)


def test_task_creation_flow():
    """Test the full task creation flow."""
    init_db()  # Ensure tables exist

    # Create a task
    task_id = str(uuid.uuid4())
    save_user_task(task_id, "测试任务", "2026-03-20", "daily at 9:00")

    # Retrieve it
    tasks = get_user_tasks()
    task = next((t for t in tasks if t.task_id == task_id), None)

    assert task is not None
    assert task.goal == "测试任务"
    assert task.due == "2026-03-20"
    assert task.reminder == "daily at 9:00"
    assert task.status == "pending"
