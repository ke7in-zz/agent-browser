import argparse
import json
import sqlite3
import sys
from contextlib import closing
from dataclasses import asdict

from agent_browser.config import resolve_db_path
from agent_browser.storage.db import open_db
from agent_browser.storage.repositories import TaskRepository
from agent_browser.tasks import HANDLERS, TaskRequest, UnknownTaskError, run_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-browser")
    subparsers = parser.add_subparsers(dest="command")
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--task", required=True)
    run_parser.add_argument("--prompt", required=True)
    run_parser.add_argument("--json", action="store_true")
    return parser


def format_human(result) -> str:
    lines = [
        f"task_id: {result.task_id}",
        f"task_name: {result.task_name}",
        f"status: {result.status}",
    ]
    if result.result is not None:
        lines.append(f"result: {result.result}")
    if result.error is not None:
        lines.append(f"error: {result.error}")
    return "\n".join(lines) + "\n"


def emit_result(result, json_output: bool) -> None:
    if json_output:
        print(json.dumps(asdict(result)))
        return
    print(format_human(result), end="")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "run":
        parser.print_help()
        return 0

    db_path = None
    try:
        db_path = resolve_db_path()
        with closing(open_db(db_path)) as conn:
            repo = TaskRepository(conn)
            result = run_task(TaskRequest(args.task, args.prompt), repo=repo)
    except UnknownTaskError as exc:
        known = ", ".join(sorted(HANDLERS)) or "none"
        print(f"Error: unknown task '{exc}'. Known: {known}", file=sys.stderr)
        return 4
    except (OSError, sqlite3.Error, ValueError) as exc:
        target = f" at {db_path}" if db_path is not None else ""
        print(f"Error: cannot open database{target}: {exc}", file=sys.stderr)
        return 3

    emit_result(result, args.json)
    return 0 if result.status == "completed" else 1
