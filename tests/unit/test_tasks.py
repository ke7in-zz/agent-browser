from datetime import datetime, timezone

import pytest

from agent_browser.handlers import noop
from agent_browser.storage.db import open_db
from agent_browser.storage.repositories import TaskRepository
from agent_browser.tasks import (
    HANDLERS,
    TaskOutcome,
    TaskRequest,
    UnknownTaskError,
    register_handler,
    run_task,
)


def fixed_clock():
    times = [
        datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        datetime(2026, 1, 1, 12, 0, 1, tzinfo=timezone.utc),
    ]
    return lambda: times.pop(0)


def test_default_registry_includes_noop():
    assert "noop" in HANDLERS


def test_noop_returns_result_without_stdout(capsys):
    outcome = noop(TaskRequest("noop", "hello"))

    assert outcome == TaskOutcome("noop completed: hello")
    assert capsys.readouterr().out == ""


def test_run_task_completes_with_deterministic_metadata(tmp_path):
    with open_db(tmp_path / "db.sqlite3") as conn:
        result = run_task(
            TaskRequest("noop", "hello"),
            repo=TaskRepository(conn),
            clock=fixed_clock(),
            id_factory=lambda: "task-id",
        )
        row = TaskRepository(conn).get("task-id")

    assert result.task_id == "task-id"
    assert result.status == "completed"
    assert result.started_at == "2026-01-01T12:00:00+00:00"
    assert result.ended_at == "2026-01-01T12:00:01+00:00"
    assert result.result == "noop completed: hello"
    assert row is not None
    assert row["status"] == "completed"


def test_handler_exception_persists_failed_row(tmp_path, handlers_snapshot):
    def broken(request):
        raise TypeError("x" * 1100)

    register_handler("broken", broken)
    with open_db(tmp_path / "db.sqlite3") as conn:
        result = run_task(
            TaskRequest("broken", "hello"),
            repo=TaskRepository(conn),
            clock=fixed_clock(),
            id_factory=lambda: "task-id",
        )
        row = TaskRepository(conn).get("task-id")

    assert result.status == "failed"
    assert result.error is not None
    assert result.error.startswith("TypeError: ")
    assert len(result.error) == 1024
    assert "Traceback" not in result.error
    assert row is not None
    assert row["status"] == "failed"
    assert row["error"] == result.error


def test_unknown_task_writes_no_row(tmp_path):
    with open_db(tmp_path / "db.sqlite3") as conn:
        with pytest.raises(UnknownTaskError):
            run_task(TaskRequest("missing", "hello"), repo=TaskRepository(conn))
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    assert count == 0


def test_run_task_commit_visible_to_second_connection(tmp_path):
    db_path = tmp_path / "db.sqlite3"
    with open_db(db_path) as conn:
        run_task(
            TaskRequest("noop", "hello"),
            repo=TaskRepository(conn),
            clock=fixed_clock(),
            id_factory=lambda: "task-id",
        )

    with open_db(db_path) as second:
        row = TaskRepository(second).get("task-id")

    assert row is not None
    assert row["status"] == "completed"


def test_handler_failure_produces_no_stdout(tmp_path, handlers_snapshot, capsys):
    def broken(request):
        print("leaked")
        raise RuntimeError("boom")

    register_handler("broken", broken)
    with open_db(tmp_path / "db.sqlite3") as conn:
        run_task(TaskRequest("broken", "hello"), repo=TaskRepository(conn), clock=fixed_clock())

    assert capsys.readouterr().out == ""


def test_handler_success_produces_no_stdout(tmp_path, handlers_snapshot, capsys):
    def noisy(request):
        print("leaked")
        return TaskOutcome("done")

    register_handler("noisy", noisy)
    with open_db(tmp_path / "db.sqlite3") as conn:
        result = run_task(TaskRequest("noisy", "hello"), repo=TaskRepository(conn), clock=fixed_clock())

    assert result.status == "completed"
    assert capsys.readouterr().out == ""


def test_stdout_suppression_preserves_text_stream_methods(tmp_path, handlers_snapshot):
    import sys

    def checks_stdout(request):
        assert sys.stdout.isatty() is False
        assert sys.stdout.encoding
        return TaskOutcome("done")

    register_handler("stdout-check", checks_stdout)
    with open_db(tmp_path / "db.sqlite3") as conn:
        result = run_task(TaskRequest("stdout-check", "hello"), repo=TaskRepository(conn), clock=fixed_clock())

    assert result.status == "completed"
