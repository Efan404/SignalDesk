import pytest
from src.db import save_user_task, get_user_tasks, init_db
import uuid

def test_save_and_get_user_task():
    init_db()  # Ensure tables exist
    task_id = str(uuid.uuid4())

    # Save task
    save_user_task(task_id, "测试任务", "2026-03-15", "daily at 10:00")

    # Get task
    tasks = get_user_tasks()
    task = next((t for t in tasks if t.task_id == task_id), None)

    assert task is not None
    assert task.goal == "测试任务"
    assert task.due == "2026-03-15"
    assert task.reminder == "daily at 10:00"
    assert task.status == "pending"
