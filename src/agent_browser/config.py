import os
from pathlib import Path
from typing import Mapping

DB_ENV_VAR = "AGENT_BROWSER_DB_PATH"


def resolve_db_path(env: Mapping[str, str] | None = None) -> Path:
    values = os.environ if env is None else env
    override = values.get(DB_ENV_VAR)
    if override:
        path = Path(override)
        if not path.is_absolute():
            raise ValueError(f"{DB_ENV_VAR} must be an absolute path; got '{override}'")
        return path
    return Path.home() / ".local" / "share" / "agent-browser" / "agent-browser.sqlite3"


def ensure_db_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
