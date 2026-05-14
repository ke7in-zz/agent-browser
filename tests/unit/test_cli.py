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
