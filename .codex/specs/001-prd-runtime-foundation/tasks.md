---
artifact: tasks
spec_name: 001-prd-runtime-foundation
status: approved
updated: 2026-05-15
approval: approved
generated_from: design.md
---

# Tasks

## Metadata

- **Spec**: `001-prd-runtime-foundation`
- **Status**: `approved`
- **Canonical task IDs**: Use stable IDs like `T-001`, `T-002`; do not renumber existing IDs after execution starts.
- **Minimum gate**: `pytest -q` from `.codex/testing.md`.
- **E2E gate**: Not required; this spec does not touch CDP, Playwright, approval-gated external actions, or site-specific workflows.

## Batch 1 — Package shell and configuration

Rationale: Establish the Python package, import surface, entrypoints, and deterministic local DB path resolution before adding persistence or runtime orchestration.

- [x] T-001: Add Python package metadata and empty importable package
  - Objective: Create the `src/` package skeleton, project metadata, console script declaration, and module entrypoint shell without task logic.
  - Files (create/modify):
    - `pyproject.toml`
    - `src/agent_browser/__init__.py`
    - `src/agent_browser/__main__.py`
    - `src/agent_browser/cli.py`
    - `tests/__init__.py`
    - `tests/unit/test_cli.py`
  - _Requirements: R-01_
  - _Leverage: `steering/structure.md`; `.codex/specs/001-prd-runtime-foundation/design.md` Components and Interfaces_
  - Tests:
    - Unit: `tests/unit/test_cli.py::test_help_works_for_module_entrypoint` for `cli.main(["--help"])` via a `SystemExit`-capturing helper.
    - Unit: `tests/unit/test_cli.py::test_parser_uses_agent_browser_prog` to pin the shared help banner.
    - Integration: N/A — package shell only; console script smoke is in T-008 after editable install.
  - Validation:
    - `pytest -q`
  - Result: Added src-layout package metadata, module entrypoint shell, CLI help parser, and package import tests.

- [x] T-002: Implement database path resolution
  - Objective: Resolve `AGENT_BROWSER_DB_PATH` and default DB path exactly as designed, including empty-string fallback, absolute-path validation, and parent directory creation.
  - Files (create/modify):
    - `src/agent_browser/config.py`
    - `tests/unit/test_config.py`
  - _Requirements: R-05_
  - _Leverage: `design.md` `config.py` interface; `.gitignore` local data exclusions_
  - Tests:
    - Unit: env override returns the exact absolute path.
    - Unit: empty `AGENT_BROWSER_DB_PATH` falls through to default.
    - Unit: relative `AGENT_BROWSER_DB_PATH` raises `ValueError` with an actionable message.
    - Unit: default path uses patched `Path.home()` and does not touch the real home directory.
    - Unit: `ensure_db_parent` creates missing parent directories and re-raises `OSError` without `RuntimeError` wrapping.
    - Integration: N/A — no DB connection yet.
  - Validation:
    - `pytest -q`
  - Result: Implemented safe DB path resolution, absolute-path validation, default path handling, and parent directory creation tests.

Batch validation:

```bash
pytest -q
```

Focus Gate:

- No speculative behavior beyond approved requirements: only package shell and DB path resolution.
- New abstractions are justified by design complexity accounting: entrypoint shell and config helper are required by R-01/R-05.
- Replaced paths are deleted or explicitly deferred: no pre-existing source paths exist.
- User-facing concepts remain aligned with the Product Spine: Pi/shell invocation and safe local persistence setup only.

## Batch 2 — SQLite persistence and task lifecycle core

Rationale: Build the durable task substrate and lifecycle orchestrator before exposing the full CLI run flow, so persistence semantics and transaction behavior are tested independently.

- [x] T-003: Implement SQLite connection helper and repository
  - Objective: Create the idempotent `tasks` schema, connection helper, and repository methods without orchestration logic.
  - Files (create/modify):
    - `src/agent_browser/storage/__init__.py`
    - `src/agent_browser/storage/db.py`
    - `src/agent_browser/storage/repositories.py`
    - `tests/unit/test_storage.py`
  - _Requirements: R-04_
  - _Leverage: Python stdlib `sqlite3`; `design.md` `tasks` schema and repository interface_
  - Tests:
    - Unit: `open_db(tmp_path / "db.sqlite3")` creates the `tasks` table.
    - Unit: repository `insert_running` + `mark_completed` round-trips through a committed transaction and a second connection.
    - Unit: repository `insert_running` + `mark_failed` persists status `failed`, `ended_at`, and error.
    - Unit: invalid status is rejected by the SQLite CHECK constraint.
    - Integration: repository transaction boundary exercised by reading committed rows from a second connection.
  - Validation:
    - `pytest -q`
  - Result: Added SQLite schema initialization, connection helper, repository persistence methods, and storage tests.

- [x] T-004: Implement task dataclasses, handler registry, and transaction-owned orchestration
  - Objective: Add `TaskRequest`, `TaskOutcome`, `TaskResult`, `UnknownTaskError`, handler registration helpers, deterministic test seams, and `run_task` with atomic SQLite transaction semantics.
  - Files (create/modify):
    - `src/agent_browser/tasks.py`
    - `src/agent_browser/handlers.py`
    - `src/agent_browser/__init__.py`
    - `tests/conftest.py`
    - `tests/unit/test_tasks.py`
  - _Requirements: R-02, R-03, R-04_
  - _Leverage: `design.md` adversarial findings F-01/F-02; `TaskRepository` from T-003_
  - Tests:
    - Unit: default handler registry includes `noop` after importing `agent_browser`.
    - Unit: `noop` returns `TaskOutcome(result="noop completed: <prompt>")` and writes nothing to stdout.
    - Unit: `run_task` with injected `clock` and `id_factory` returns deterministic metadata and status `completed`.
    - Unit: handler exception persists a `failed` row with `TypeError: ...`-style error summary truncated to 1024 chars and no traceback.
    - Unit: unknown task raises `UnknownTaskError` and writes no row.
    - Unit: `handlers_snapshot` restores registry mutations after each test.
    - Integration: `run_task` commits the final row so it is visible through a second SQLite connection.
  - Validation:
    - `pytest -q`
  - Result: Added task dataclasses, noop handler registration, atomic run_task orchestration, failure persistence, and deterministic tests.

Batch validation:

```bash
pytest -q
```

Focus Gate:

- No speculative behavior beyond approved requirements: one table, one handler, one registry, no events/approvals/browser code.
- New abstractions are justified by design complexity accounting: registry, dataclasses, transaction ownership, and repository boundary are required for safe extension by later specs.
- Replaced paths are deleted or explicitly deferred: no duplicate storage/task paths introduced.
- User-facing concepts remain aligned with the Product Spine: persisted task lifecycle for a single local operator.

## Batch 3 — CLI run flow and machine-readable output

Rationale: Wire the already-tested task core into the operator-facing command, then prove human and JSON output contracts through end-to-end CLI tests.

- [x] T-005: Implement `run` command argument handling and exit-code mapping
  - Objective: Parse `run --task --prompt [--json]`, open the configured DB, dispatch `run_task`, and map usage/DB/unknown/handler outcomes to the approved exit codes.
  - Files (create/modify):
    - `src/agent_browser/cli.py`
    - `src/agent_browser/__main__.py`
    - `tests/conftest.py`
    - `tests/unit/test_cli.py`
  - _Requirements: R-01, R-02, R-05, R-06_
  - _Leverage: `resolve_db_path`, `open_db`, `TaskRepository`, `run_task`; `design.md` CLI orchestration sequence_
  - Tests:
    - Unit: missing `--task` exits 2 and does not open the DB.
    - Unit: missing `--prompt` exits 2 and does not open the DB.
    - Unit: unknown task exits 4, reports known tasks, and writes no row.
    - Unit: invalid relative DB env exits 3 with an actionable error.
    - Integration: CLI `run --task noop --prompt hello` against `tmp_db_path` creates exactly one completed row.
  - Validation:
    - `pytest -q`
  - Result: Implemented run command parsing, DB opening, task dispatch, exit-code mapping, and error-path tests.

- [x] T-006: Implement human and JSON result formatting
  - Objective: Print concise human output by default and stable JSON-only stdout for `--json` success/handler-failure paths.
  - Files (create/modify):
    - `src/agent_browser/cli.py`
    - `tests/unit/test_cli.py`
  - _Requirements: R-03, R-06_
  - _Leverage: `TaskResult` JSON output schema in `design.md`; handler stdout discipline from `design.md`_
  - Tests:
    - Unit: human output contains task id, task name, status, and result.
    - Unit: `--json` success stdout is exactly one JSON object with keys `task_id`, `task_name`, `prompt`, `status`, `started_at`, `ended_at`, `result`, `error`.
    - Unit: `--json` handler failure stdout is exactly one JSON object with `status="failed"` and non-empty `error`.
    - Unit: argparse and DB-open errors leave stdout empty and write actionable text to stderr.
    - Integration: JSON output parses and matches the committed SQLite row for the same task id.
  - Validation:
    - `pytest -q`
  - Result: Added human output, stable JSON serialization, handler-failure JSON behavior, and SQLite row matching tests.

Batch validation:

```bash
pytest -q
```

Focus Gate:

- No speculative behavior beyond approved requirements: no extra commands such as `tasks list`, no queueing, no browser connection, no approval prompts.
- New abstractions are justified by design complexity accounting: formatting helpers only support R-06 and must stay inside `cli.py` unless duplication appears.
- Replaced paths are deleted or explicitly deferred: no alternate JSON/human output path exists.
- User-facing concepts remain aligned with the Product Spine: operator can run a no-op task and consume structured output.

## Batch 4 — Packaging smoke and final hardening

Rationale: Verify the package is usable the way Pi/shell will invoke it, then complete final contract checks and documentation consistency without adding new feature scope.

- [x] T-007: Add final edge-case tests and contract assertions
  - Objective: Cover remaining design review edge cases before packaging smoke: no browser dependency imports, no stdout pollution from handlers, status CHECK evolution note remains documented, and repository methods do not commit outside orchestrator ownership.
  - Files (create/modify):
    - `tests/unit/test_cli.py`
    - `tests/unit/test_tasks.py`
    - `tests/unit/test_storage.py`
  - _Requirements: R-01, R-03, R-04, R-06_
  - _Leverage: `context.md` carry-forward warnings; `design.md` adversarial findings_
  - Tests:
    - Unit: `python -m agent_browser --help` path can be exercised without importing future `browser`, `agents`, or `workflows` modules (guard as import-surface assertion using current module set).
    - Unit: repository method calls are not assumed durable until committed, while `run_task` output is durable.
    - Unit: `noop` and handler-failure path produce no handler-originated stdout before CLI formatting.
    - Integration: N/A — edge assertions remain in-process with temp SQLite.
  - Validation:
    - `pytest -q`
  - Result: Added final contract tests for import surface, repository commit ownership, and handler stdout suppression.

- [x] T-008: Run editable-install smoke and final repo gate
  - Objective: Prove both entrypoints work after editable installation and the full validation gate passes with no browser/CDP prerequisite.
  - Files (create/modify):
    - `pyproject.toml`
    - `tests/unit/test_cli.py`
    - `.codex/specs/001-prd-runtime-foundation/context.md`
  - _Requirements: R-01, R-02, R-03, R-04, R-05, R-06_
  - _Leverage: `.codex/testing.md` minimum gate; `requirements.md` manual verification checks_
  - Tests:
    - Unit: existing CLI tests cover command behavior under `pytest`.
    - Integration: manual smoke after editable install: `python -m agent_browser --help`, `agent-browser --help`, and a no-op JSON run against a temp DB path.
  - Validation:
    - `pytest -q`
    - `python -m agent_browser --help`
    - `agent-browser --help`
    - `AGENT_BROWSER_DB_PATH=$(mktemp -u).sqlite3 agent-browser run --task noop --prompt "test" --json`
  - Result: Validated editable install, both help entrypoints (using a temporary python→python3 PATH shim for the documented `python -m` smoke because this WSL image lacks a `python` alias), no-op JSON execution, and full pytest gate without browser/CDP prerequisites.

Batch validation:

```bash
pytest -q
python -m agent_browser --help
agent-browser --help
AGENT_BROWSER_DB_PATH=$(mktemp -u).sqlite3 agent-browser run --task noop --prompt "test" --json
```

Focus Gate:

- No speculative behavior beyond approved requirements: final smoke only proves approved entrypoints and no-op path.
- New abstractions are justified by design complexity accounting: no new abstractions should be introduced in this batch.
- Replaced paths are deleted or explicitly deferred: if implementation created one-use helpers beyond the design, collapse them before completion.
- User-facing concepts remain aligned with the Product Spine: local CLI task execution, SQLite persistence, structured result.

## Steering Updates Required

- [x] No further steering doc updates expected
- [ ] Update `steering/product.md`
- [ ] Update `steering/tech.md`
- [ ] Update `steering/structure.md`
- Notes: `steering/structure.md` was already updated during spec creation to capture the dual-entrypoint decision. Implementation should not change durable steering decisions.

## Lifecycle

- Follow `~/.pi/agent/rules/spec-lifecycle.md`.
- `context.md` is the carry-forward source for design-review decisions and warnings.
- `spec-execute` should auto-run `spec-init` if harness state is missing or stale.
- Browser/CDP, approval gates, queues, and SoundCloud workflows are explicitly deferred to later specs and must not be pulled into execution tasks.
