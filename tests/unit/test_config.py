from pathlib import Path

import pytest

from agent_browser.config import ensure_db_parent, resolve_db_path


def test_env_override_returns_exact_absolute_path(tmp_path):
    db_path = tmp_path / "custom.sqlite3"

    assert resolve_db_path({"AGENT_BROWSER_DB_PATH": str(db_path)}) == db_path


def test_empty_env_value_falls_back_to_default(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))

    assert resolve_db_path({"AGENT_BROWSER_DB_PATH": ""}) == tmp_path / ".local" / "share" / "agent-browser" / "agent-browser.sqlite3"


def test_relative_env_value_raises_actionable_error():
    with pytest.raises(ValueError, match="must be an absolute path"):
        resolve_db_path({"AGENT_BROWSER_DB_PATH": "relative.sqlite3"})


def test_default_path_uses_home_without_creating_it(monkeypatch, tmp_path):
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))

    path = resolve_db_path({})

    assert path == home / ".local" / "share" / "agent-browser" / "agent-browser.sqlite3"
    assert not home.exists()


def test_ensure_db_parent_creates_missing_parents(tmp_path):
    db_path = tmp_path / "nested" / "data" / "db.sqlite3"

    ensure_db_parent(db_path)
    ensure_db_parent(db_path)

    assert db_path.parent.is_dir()


def test_ensure_db_parent_reraises_oserror(monkeypatch, tmp_path):
    db_path = tmp_path / "blocked" / "db.sqlite3"

    def raise_oserror(*args, **kwargs):
        raise OSError("nope")

    monkeypatch.setattr(Path, "mkdir", raise_oserror)

    with pytest.raises(OSError, match="nope"):
        ensure_db_parent(db_path)
