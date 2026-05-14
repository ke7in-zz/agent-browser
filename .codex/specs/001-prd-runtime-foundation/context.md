# Execution Context — 001-prd-runtime-foundation

## Status

Last completed batch: 4
Remaining batches: none
Next exact step: Run spec verification
Next command: /skill:spec-verify 001-prd-runtime-foundation
Resume from (file:line): .codex/specs/001-prd-runtime-foundation/harness/progress.md:4

## Key Discoveries

- Repository has steering docs and bootstrap scaffold, but no source package, tests, or Python tooling yet.
- `.codex/testing.md` declares `pytest -q` as the minimum gate; it currently exits with no-tests status until the first tests are added.
- No existing implementation covers CLI entrypoints, task lifecycle, SQLite persistence, or runtime result formatting.

- [Batch 1] `pyproject.toml` uses a src layout with pytest `pythonpath = ["src"]`; no runtime dependencies are declared.
- [Batch 1] `resolve_db_path` treats empty `AGENT_BROWSER_DB_PATH` as unset and rejects relative overrides before any DB open.

- [Batch 2] `open_db(path)` creates parent directories, opens SQLite, sets `sqlite3.Row`, and applies the `tasks` schema idempotently.
- [Batch 2] Repository methods intentionally do not commit; `run_task` owns durability with `with repo.conn:` and commits terminal task rows.
- [Batch 2] Unknown task names fail before row insertion; handler exceptions return a failed `TaskResult` and persist a truncated error summary without traceback.

- [Batch 3] CLI `run` opens the configured SQLite database before dispatch and maps unknown tasks to exit 4, DB/path errors to exit 3, handler failures to exit 1, and completions to exit 0.
- [Batch 3] JSON output is generated with `dataclasses.asdict(TaskResult)`, preserving dataclass field order for the approved schema.

- [Batch 4] Editable install succeeded with hatchling and exposed `agent-browser`; both module and console help entrypoints work after installation. This WSL image lacks a `python` alias, so the documented `python -m agent_browser --help` smoke was run with a temporary PATH shim pointing `python` to `python3`.
- [Batch 4] `run_task` redirects Python-level handler `sys.stdout`/`print` output during invocation so normal handler prints do not pollute CLI JSON stdout; file-descriptor/subprocess stdout remains a future adapter concern.
- [Smoke] Automated smoke verified `pytest -q`, module help, console help, and no-op JSON execution against a temp SQLite DB. No manual checks remain.

## Decisions Made

- [Create] Decision: Frame this spec as a walking skeleton — Rationale: proves CLI, task lifecycle, SQLite logging, and output formatting without mixing in CDP/browser concerns.
- [Create] Decision: Expose both `python -m agent_browser` and `agent-browser` — Rationale: supports development fallback and Pi/shell invocation.
- [Create] Decision: Use a `noop` handler that echoes prompt plus generated metadata — Rationale: makes runtime behavior debuggable before real browser tasks exist.
- [Create] Decision: Start with a minimal `tasks` table only — Rationale: avoids premature event/approval schema design.
- [Create] Decision: Default DB path is `~/.local/share/agent-browser/agent-browser.sqlite3`, overrideable with `AGENT_BROWSER_DB_PATH` — Rationale: keeps local data outside the repo while making tests deterministic.
- [Create] Decision: Human-readable CLI output by default, `--json` for machine parsing — Rationale: supports terminal use and stable Pi/script integration.
- [Design] Decision: `run_task` owns the transaction boundary via `with repo.conn:` so the entire lifecycle commits atomically — Rationale: adversarial review F-01 caught that `contextlib.closing` rolls back uncommitted DML on close.
- [Design] Decision: Handler registry bootstrap moves to `agent_browser/__init__.py` — Rationale: breaks `tasks ↔ handlers` circular import (adversarial F-02).
- [Design] Decision: `ensure_db_parent` re-raises `OSError` unchanged; CLI catches `OSError` only — Rationale: collapses error funnel; `RuntimeError` would have escaped (adversarial F-03).
- [Design] Decision: `AGENT_BROWSER_DB_PATH` empty-string treated as unset; non-absolute paths rejected with `ValueError` — Rationale: prevents silent cwd/empty-path footguns (adversarial F-04).
- [Design] Decision: Pin JSON output schema (key names, order, nullability) and document handler-side stdout discipline — Rationale: keep Pi/script consumer contract stable from foundation onward (adversarial F-07, F-15).
- [Design] Decision: Document that `status` CHECK extension requires SQLite 12-step table rebuild — Rationale: future approval/queue states (003, 006) inherit a known cost rather than a surprise (adversarial F-05).
- [Tasks] Decision: Generated 8 implementation tasks across 4 batches and marked design/tasks approved — Rationale: stage package/config before persistence, persistence before CLI wiring, CLI before final packaging smoke.

- [Batch 1] Decision: Amend DB-open error design to catch `sqlite3.Error` separately from `OSError` — Rationale: implementation must satisfy R-05 AC4 because `sqlite3.OperationalError` is not an `OSError` subclass.

## Carry-forward Warnings

- Future sensitive workflows must not log sensitive prompt/message/page contents by default; the `noop` echo behavior is only for the non-sensitive foundation handler.
- Browser/CDP integration remains out of scope for this spec and belongs in `002-prd-cdp-browser-connection`.
- **R-01 AC2 carry-forward**: `python -m agent_browser --help` must not transitively import browser/agent deps. Future `browser/`, `agents/`, `workflows/` modules must be imported lazily inside CLI dispatch handlers, not at package or `cli.py` import time.
- **Sensitive-data redaction carry-forward**: Foundation persists `prompt` and `result` as plain text. `004+` handlers operating on sensitive page content must redact at the handler boundary before constructing `TaskOutcome`.
- **Queue-era schema carry-forward**: `006-prd-task-queue` will need `created_at` distinct from `started_at`, and likely `pid`/`hostname` for the reaper. SQLite `ALTER TABLE ADD COLUMN` handles this; foundation deliberately does not pre-allocate.
- **Status CHECK carry-forward**: Adding a new status value (e.g. `awaiting_approval` for 003) requires the SQLite 12-step table rebuild, not a simple ALTER. Acknowledged design cost.
