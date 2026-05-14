import contextlib
import io

import pytest

from agent_browser import tasks


@pytest.fixture(autouse=True)
def handlers_snapshot():
    original = dict(tasks.HANDLERS)
    yield
    tasks.HANDLERS.clear()
    tasks.HANDLERS.update(original)


@pytest.fixture
def tmp_db_path(monkeypatch, tmp_path):
    db_path = tmp_path / "agent-browser.sqlite3"
    monkeypatch.setenv("AGENT_BROWSER_DB_PATH", str(db_path))
    return db_path


@pytest.fixture
def cli_runner(tmp_db_path):
    from agent_browser import cli

    def run(argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                exit_code = cli.main(argv)
            except SystemExit as exc:
                exit_code = exc.code
        return exit_code, stdout.getvalue(), stderr.getvalue()

    return run
