import sqlite3

import pytest

from agent_browser.storage.db import open_db
from agent_browser.storage.repositories import TaskRepository


def test_open_db_creates_tasks_table(tmp_path):
    db_path = tmp_path / "db.sqlite3"

    with open_db(db_path) as conn:
        columns = conn.execute("PRAGMA table_info(tasks)").fetchall()

    assert [row[1] for row in columns] == [
        "id",
        "task_name",
        "prompt",
        "status",
        "started_at",
        "ended_at",
        "result",
        "error",
    ]


def test_repository_completed_row_is_visible_after_commit(tmp_path):
    db_path = tmp_path / "db.sqlite3"
    with open_db(db_path) as conn:
        repo = TaskRepository(conn)
        with conn:
            repo.insert_running("task-1", "noop", "hello", "start")
            repo.mark_completed("task-1", "end", "done")

    with open_db(db_path) as second:
        row = TaskRepository(second).get("task-1")

    assert row["status"] == "completed"
    assert row["result"] == "done"
    assert row["ended_at"] == "end"


def test_repository_failed_row_persists_error(tmp_path):
    db_path = tmp_path / "db.sqlite3"
    with open_db(db_path) as conn:
        repo = TaskRepository(conn)
        with conn:
            repo.insert_running("task-1", "noop", "hello", "start")
            repo.mark_failed("task-1", "end", "TypeError: bad")
        row = repo.get("task-1")

    assert row["status"] == "failed"
    assert row["error"] == "TypeError: bad"
    assert row["ended_at"] == "end"


def test_status_check_rejects_invalid_status(tmp_path):
    with open_db(tmp_path / "db.sqlite3") as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO tasks (id, task_name, prompt, status, started_at) VALUES (?, ?, ?, ?, ?)",
                ("bad", "noop", "hello", "unknown", "start"),
            )
