---
artifact: requirements
spec_name: 001-prd-runtime-foundation
status: approved
updated: 2026-05-14
approval: approved
---

# Requirements Document

## Metadata

- **Spec**: `001-prd-runtime-foundation`
- **Status**: `approved`
- **Related steering docs**: `steering/product.md`, `steering/tech.md`, `steering/structure.md`

## Product Spine

This spec helps the single local operator run the first Pi/shell-triggered automation task by creating a minimal Python runtime that accepts a task prompt, executes a registered no-op handler, records the task in SQLite, and returns a structured result. It strengthens the product by establishing the smallest reusable foundation that later CDP, approval, agent, and site-specific workflow specs can extend.

## Introduction

The repository currently has product steering and workflow scaffold, but no runnable Python package. This spec creates the walking skeleton for `agent-browser`: package metadata, CLI entrypoints, task lifecycle primitives, a minimal no-op task handler, SQLite task persistence, and result formatting.

The goal is not to build browser automation yet. The goal is to prove the runtime path from operator command to persisted task result without requiring Windows Chrome, CDP, browser-use, or external services.

## Alignment with Product Vision

This spec supports the product goals for Pi-triggered automation, reusable runtime foundation, and local persistence. It deliberately defers logged-in browser control and approval-aware browser actions so the first implementation remains small, testable, and independent of Windows browser availability.

## Approach

### Chosen approach: walking skeleton

Create the smallest Python runtime that can:

- expose both `python -m agent_browser` and `agent-browser` entrypoints;
- accept a task name and prompt;
- dispatch a registered `noop` task handler;
- persist task execution to a local SQLite `tasks` table;
- print a human-readable result by default or JSON when requested.

### Rejected alternatives

- **Full foundation upfront**: rejected because config, event logs, approvals, browser artifacts, and extensibility layers would force design decisions before real workflows validate them.
- **Foundation plus CDP smoke test**: rejected because browser connectivity belongs in `002-prd-cdp-browser-connection` and should not make the runtime foundation depend on Windows browser availability.
- **Skip foundation and start with CDP**: rejected because browser connection work would need to invent runtime plumbing as a side-effect.

## Scope

### In scope

- Python package scaffold for `agent_browser`.
- `python -m agent_browser` development entrypoint.
- `agent-browser` console script entrypoint.
- `run` command accepting `--task`, `--prompt`, and `--json`.
- Registered `noop` task handler.
- Minimal task lifecycle: create, start, complete, fail.
- SQLite initialization with a minimal `tasks` table.
- Default database path: `~/.local/share/agent-browser/agent-browser.sqlite3`.
- `AGENT_BROWSER_DB_PATH` override for tests and local development.
- Human-readable CLI output by default; JSON output with `--json`.
- Unit tests for CLI, task execution, DB path resolution, persistence, and JSON output.

### Out of scope

- CDP, Playwright, Windows browser startup, or browser session validation.
- LLM/browser-use integration.
- Approval gates or approval persistence.
- Task queueing, concurrency, retries, scheduling, or daemon mode.
- Multi-profile/account support.
- Site-specific workflows, including SoundCloud.
- Screenshot, trace, browser artifact, or page-content capture.
- Event-sourced task logs or separate `task_events` table.

## Non-Goals

- Do not create a general plugin system beyond what is needed for a single registered `noop` handler.
- Do not add browser automation dependencies in this spec.
- Do not store sensitive browser/page/message contents beyond the intentionally non-sensitive `noop` prompt used to prove plumbing.
- Do not add environment file parsing unless required by implementation; `AGENT_BROWSER_DB_PATH` is sufficient for this spec.
- Do not implement Pi-specific integration beyond shell-friendly entrypoints and JSON output.

## Product Focus Risks

- **New user-facing concepts**: The CLI introduces `run`, `--task`, `--prompt`, and `--json`; keep these stable and minimal.
- **Duplicate flows/concepts**: Avoid creating both task service and workflow abstractions before real workflows exist.
- **Speculative configuration**: Only support database path override now; defer CDP endpoint, provider config, profiles, and approval settings.
- **Replaced/deletable behavior**: The `noop` handler is proof plumbing and may remain only as a smoke/test utility after real workflows exist.

## Dependencies

- Python packaging/tooling to be introduced by this spec.
- Standard-library SQLite is acceptable for MVP persistence.
- `pytest` is the canonical minimum test gate per `.codex/testing.md`.
- No Windows browser, CDP endpoint, LLM provider, or network access is required.

## Requirements

### R-01 Python package and entrypoints

**User Story:** As the local operator, I want both module and console-script entrypoints, so that I can invoke the runtime from Pi, shell scripts, or development commands.

#### Acceptance Criteria

1. WHEN the package is installed in editable mode THEN the system SHALL expose an `agent-browser` console script.
2. WHEN `python -m agent_browser --help` is run THEN the system SHALL display CLI help without importing browser automation dependencies.
3. WHEN `agent-browser --help` is run THEN the system SHALL display the same command family as the module entrypoint.
4. WHEN implementation adds packaging metadata THEN it SHALL define dependencies only required by this foundation spec.

### R-02 Run command

**User Story:** As the local operator, I want to submit a named task with a prompt, so that the runtime can execute a first deterministic task path.

#### Acceptance Criteria

1. WHEN `agent-browser run --task noop --prompt "test task"` is run THEN the system SHALL execute the registered `noop` handler.
2. WHEN the `run` command is invoked without `--task` THEN the system SHALL return a non-zero exit and explain the missing argument.
3. WHEN the `run` command is invoked without `--prompt` THEN the system SHALL return a non-zero exit and explain the missing argument.
4. IF an unknown task name is provided THEN the system SHALL return a non-zero exit, record the task failure when possible, and report that the task is unsupported.

### R-03 No-op task handler

**User Story:** As the local operator, I want a deterministic no-op task, so that I can prove runtime plumbing without controlling a browser or calling an LLM.

#### Acceptance Criteria

1. WHEN the `noop` handler runs THEN the system SHALL complete without external service, browser, CDP, or network access.
2. WHEN the `noop` handler succeeds THEN the system SHALL include the task name, prompt, task id, timestamps, status, and result in the returned task result.
3. WHEN the `noop` handler succeeds THEN the system SHALL mark the task status as `completed`.
4. IF the handler raises an exception THEN the system SHALL mark the task status as `failed` and persist an error summary.

### R-04 SQLite task persistence

**User Story:** As the local operator, I want task executions recorded locally, so that later specs can inspect and build on task history.

#### Acceptance Criteria

1. WHEN the runtime starts a task THEN the system SHALL initialize the SQLite database if it does not exist.
2. WHEN initializing SQLite THEN the system SHALL create a minimal `tasks` table with fields for id, task name, prompt, status, started timestamp, ended timestamp, result, and error.
3. WHEN a task is started THEN the system SHALL persist a row with status `running` and a started timestamp.
4. WHEN a task completes THEN the system SHALL update the same row with status `completed`, an ended timestamp, and the result.
5. IF a task fails THEN the system SHALL update the same row with status `failed`, an ended timestamp, and an error summary.
6. WHEN tests run THEN they SHALL use a temporary database path and SHALL NOT write to the operator's default local database.

### R-05 Database path resolution

**User Story:** As the local operator, I want a safe default database location with an override, so that normal use does not dirty the repo and tests remain isolated.

#### Acceptance Criteria

1. WHEN `AGENT_BROWSER_DB_PATH` is set THEN the system SHALL use that exact path for SQLite persistence.
2. WHEN `AGENT_BROWSER_DB_PATH` is not set THEN the system SHALL use `~/.local/share/agent-browser/agent-browser.sqlite3`.
3. WHEN the selected database parent directory does not exist THEN the system SHALL create it before opening SQLite.
4. WHEN the selected path is invalid or not writable THEN the system SHALL fail with a clear error and a non-zero exit.

### R-06 CLI result formatting

**User Story:** As the local operator, I want friendly output by default and JSON for automation, so that both humans and Pi/scripts can consume task results.

#### Acceptance Criteria

1. WHEN `agent-browser run --task noop --prompt "test task"` succeeds without `--json` THEN the system SHALL print a concise human-readable summary containing task id, task name, status, and result.
2. WHEN the same command includes `--json` THEN the system SHALL print valid JSON containing task id, task name, prompt, status, timestamps, result, and error fields.
3. WHEN JSON output is requested THEN stdout SHALL contain only the JSON payload for successful task execution.
4. IF command execution fails THEN the system SHALL return a non-zero exit and provide an actionable error message.

## Validation Plan

Per `.codex/testing.md`, the minimum repo gate is:

```bash
pytest -q
```

No E2E gate is required for this spec because it does not touch CDP connection behavior, Playwright browser session control, approval-gated external actions, or site-specific workflows.

### Acceptance tests

| ID   | Given                                                    | When                                                            | Then                                                                                                     |
| ---- | -------------------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| T-01 | Package installed in editable mode                       | `agent-browser --help` and `python -m agent_browser --help` run | Both commands show CLI help and exit successfully                                                        |
| T-02 | Temporary `AGENT_BROWSER_DB_PATH`                        | `agent-browser run --task noop --prompt "hello"` runs           | A `tasks` row is created and completed in SQLite                                                         |
| T-03 | Temporary `AGENT_BROWSER_DB_PATH`                        | `agent-browser run --task noop --prompt "hello" --json` runs    | stdout is parseable JSON with task metadata and status `completed`                                       |
| T-04 | Temporary `AGENT_BROWSER_DB_PATH`                        | Unknown task name is submitted                                  | Command exits non-zero and reports unsupported task                                                      |
| T-05 | No DB env override in a unit-scoped path-resolution test | DB path is resolved                                             | Default path expands to `~/.local/share/agent-browser/agent-browser.sqlite3` without opening the real DB |

### Manual verification checks

- [ ] Run `python -m agent_browser --help`.
- [ ] Run `agent-browser --help` after editable install.
- [ ] Run `AGENT_BROWSER_DB_PATH=$(mktemp -u).sqlite3 agent-browser run --task noop --prompt "test" --json` and inspect JSON.
- [ ] Confirm no browser/CDP prerequisite is needed.

### Success metrics

- `pytest -q` passes.
- Both entrypoints execute successfully.
- A no-op task creates exactly one task record and completes it.
- JSON output can be parsed by downstream scripts.

## Non-Functional Requirements

### Performance

- No-op task execution should complete quickly enough for interactive terminal use; no external service waits are allowed.

### Security

- The implementation SHALL NOT read browser profiles, CDP endpoints, or provider secrets.
- The implementation SHALL NOT commit or require `.env` files.
- The `noop` prompt may be persisted for this non-sensitive foundation test path, but future sensitive workflows must avoid logging sensitive contents by default.

### Reliability

- Task lifecycle updates SHALL leave a persisted terminal status for completed or failed task execution.
- Tests SHALL isolate database state per test.

### Usability

- CLI errors SHALL be actionable and concise.
- Human-readable output SHALL be useful in a terminal.
- JSON output SHALL be stable enough for Pi/script parsing.

## Assumptions

- **A-01**: Python packaging/tooling will be introduced in this spec because none exists yet.
- **A-02**: `pytest` is the first validation gate and will be made runnable by this spec.
- **A-03**: The default database path is acceptable for Linux/WSL local use.
- **A-04**: The no-op prompt used in this spec is non-sensitive test input.

## Open Questions

None.

## Steering Updates Required

- [ ] No steering doc updates expected
- [ ] Update `steering/product.md`
- [ ] Update `steering/tech.md`
- [x] Update `steering/structure.md`
- Notes: `steering/structure.md` was updated to record the dual entrypoint decision: `python -m agent_browser` plus `agent-browser` console script.
