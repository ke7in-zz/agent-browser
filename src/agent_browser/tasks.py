from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Literal
from uuid import uuid4

from agent_browser.storage.repositories import TaskRepository


@dataclass(frozen=True)
class TaskRequest:
    task_name: str
    prompt: str


@dataclass(frozen=True)
class TaskOutcome:
    result: str


@dataclass(frozen=True)
class TaskResult:
    task_id: str
    task_name: str
    prompt: str
    status: Literal["completed", "failed"]
    started_at: str
    ended_at: str
    result: str | None
    error: str | None


class UnknownTaskError(Exception):
    pass


Handler = Callable[[TaskRequest], TaskOutcome]
Clock = Callable[[], datetime]
HANDLERS: dict[str, Handler] = {}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def register_handler(name: str, fn: Handler) -> None:
    HANDLERS[name] = fn


def unregister_handler(name: str) -> None:
    HANDLERS.pop(name, None)


def summarize_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"[:1024]


def run_task(
    request: TaskRequest,
    *,
    repo: TaskRepository,
    clock: Clock = utc_now,
    id_factory: Callable[[], str] = lambda: uuid4().hex,
) -> TaskResult:
    handler = HANDLERS.get(request.task_name)
    if handler is None:
        raise UnknownTaskError(request.task_name)

    task_id = id_factory()
    started_at = clock().isoformat()
    with repo.conn:
        repo.insert_running(task_id, request.task_name, request.prompt, started_at)
        try:
            outcome = handler(request)
        except Exception as exc:  # noqa: BLE001 - task failures are persisted as data.
            ended_at = clock().isoformat()
            error = summarize_error(exc)
            repo.mark_failed(task_id, ended_at, error)
            return TaskResult(task_id, request.task_name, request.prompt, "failed", started_at, ended_at, None, error)
        ended_at = clock().isoformat()
        repo.mark_completed(task_id, ended_at, outcome.result)
        return TaskResult(task_id, request.task_name, request.prompt, "completed", started_at, ended_at, outcome.result, None)
