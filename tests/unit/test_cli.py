import os
import subprocess
import sys

import pytest

from agent_browser import cli


def run_cli(argv):
    with pytest.raises(SystemExit) as exc_info:
        cli.main(argv)
    return exc_info.value.code


def test_help_works_for_module_entrypoint(capsys):
    exit_code = run_cli(["--help"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage: agent-browser" in captured.out


def test_python_module_entrypoint_help_runs():
    completed = subprocess.run(
        [sys.executable, "-m", "agent_browser", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )

    assert completed.returncode == 0
    assert completed.stdout.startswith("usage: agent-browser")


def test_parser_uses_agent_browser_prog(capsys):
    run_cli(["--help"])

    captured = capsys.readouterr()
    assert captured.out.startswith("usage: agent-browser")

import json
import sqlite3

from agent_browser.tasks import TaskOutcome, register_handler


def row_count(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]


def test_missing_task_exits_2_and_does_not_open_db(cli_runner, tmp_db_path):
    exit_code, stdout, stderr = cli_runner(["run", "--prompt", "hello"])

    assert exit_code == 2
    assert stdout == ""
    assert "--task" in stderr
    assert not tmp_db_path.exists()


def test_missing_prompt_exits_2_and_does_not_open_db(cli_runner, tmp_db_path):
    exit_code, stdout, stderr = cli_runner(["run", "--task", "noop"])

    assert exit_code == 2
    assert stdout == ""
    assert "--prompt" in stderr
    assert not tmp_db_path.exists()


def test_unknown_task_exits_4_and_writes_no_row(cli_runner, tmp_db_path):
    exit_code, stdout, stderr = cli_runner(["run", "--task", "missing", "--prompt", "hello"])

    assert exit_code == 4
    assert stdout == ""
    assert "unknown task 'missing'" in stderr
    assert "noop" in stderr
    assert row_count(tmp_db_path) == 0


def test_invalid_relative_db_env_exits_3(cli_runner, monkeypatch):
    monkeypatch.setenv("AGENT_BROWSER_DB_PATH", "relative.sqlite3")

    exit_code, stdout, stderr = cli_runner(["run", "--task", "noop", "--prompt", "hello"])

    assert exit_code == 3
    assert stdout == ""
    assert "AGENT_BROWSER_DB_PATH" in stderr


def test_run_noop_end_to_end_human_output(cli_runner, tmp_db_path):
    exit_code, stdout, stderr = cli_runner(["run", "--task", "noop", "--prompt", "hello"])

    assert exit_code == 0
    assert stderr == ""
    assert "task_id:" in stdout
    assert "task_name: noop" in stdout
    assert "status: completed" in stdout
    assert "result: noop completed: hello" in stdout
    assert row_count(tmp_db_path) == 1


def test_json_success_stdout_is_exact_payload(cli_runner, tmp_db_path):
    exit_code, stdout, stderr = cli_runner(["run", "--task", "noop", "--prompt", "hello", "--json"])

    assert exit_code == 0
    assert stderr == ""
    payload = json.loads(stdout)
    assert list(payload) == ["task_id", "task_name", "prompt", "status", "started_at", "ended_at", "result", "error"]
    assert payload["task_name"] == "noop"
    assert payload["prompt"] == "hello"
    assert payload["status"] == "completed"
    assert payload["result"] == "noop completed: hello"
    assert payload["error"] is None

    with sqlite3.connect(tmp_db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (payload["task_id"],)).fetchone()
    assert row["task_name"] == payload["task_name"]
    assert row["prompt"] == payload["prompt"]
    assert row["status"] == payload["status"]
    assert row["started_at"] == payload["started_at"]
    assert row["ended_at"] == payload["ended_at"]
    assert row["result"] == payload["result"]
    assert row["error"] == payload["error"]


def test_json_handler_failure_stdout_is_exact_payload(cli_runner, handlers_snapshot):
    def broken(request):
        raise RuntimeError("boom")

    register_handler("broken", broken)

    exit_code, stdout, stderr = cli_runner(["run", "--task", "broken", "--prompt", "hello", "--json"])

    assert exit_code == 1
    assert stderr == ""
    payload = json.loads(stdout)
    assert payload["status"] == "failed"
    assert payload["result"] is None
    assert payload["error"] == "RuntimeError: boom"


def test_db_open_errors_leave_stdout_empty(cli_runner, monkeypatch, tmp_path):
    blocked = tmp_path / "parent"
    blocked.write_text("not a directory")
    monkeypatch.setenv("AGENT_BROWSER_DB_PATH", str(blocked / "db.sqlite3"))

    exit_code, stdout, stderr = cli_runner(["run", "--task", "noop", "--prompt", "hello"])

    assert exit_code == 3
    assert stdout == ""
    assert f"cannot open database at {blocked / 'db.sqlite3'}" in stderr
