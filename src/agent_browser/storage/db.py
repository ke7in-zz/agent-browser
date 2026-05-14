import sqlite3
from pathlib import Path

from agent_browser.config import ensure_db_parent

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id          TEXT PRIMARY KEY,
    task_name   TEXT NOT NULL,
    prompt      TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    result      TEXT,
    error       TEXT
);
"""


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA_SQL)
    return conn


def open_db(path: Path) -> sqlite3.Connection:
    ensure_db_parent(path)
    return connect(path)
