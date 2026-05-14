# Technical Architecture -- agent-browser

## Stack

- **Language**: Python for MVP.
- **Runtime entrypoint**: Pi-invoked Python command/module first; daemon or durable runner later.
- **Browser control**: Playwright over CDP to a Windows-hosted Chrome/Edge instance.
- **Agent layer**: `browser-use` as the first browser-agent integration, behind an adapter so direct Playwright flows remain possible.
- **Persistence**: SQLite for local task logs and approval records.
- **Configuration**: Local `.env` for paths, CDP endpoint, database path, and provider settings. `.env` must not be committed.

## Architecture Overview

The system is split across WSL and the Windows host. WSL owns orchestration, task execution, LLM/agent integration, approvals, and SQLite persistence. The Windows host owns the real browser process, persistent profile, GPU acceleration, and native browser environment. WSL connects to the Windows browser through CDP and executes one task at a time for MVP.

Pi is the command/control surface. A Pi-triggered task enters the Python runtime, loads local configuration, connects to the Windows browser via Playwright/CDP, executes through an agent/workflow adapter, pauses for approval when required, and records structured status/results in SQLite.

## Key Decisions

- Use a real Windows Chrome/Edge browser instead of headless-first automation because logged-in browser state, native profile behavior, GPU support, and desktop browser fidelity are core constraints.
- Use Python-only for MVP to keep the runtime small and align with browser-use, Playwright Python, SQLite, and local orchestration.
- Keep `browser-use` behind an adapter so the project can use direct Playwright workflows where agent autonomy is unnecessary.
- Start with one task at a time and one browser profile; queueing, concurrency, and multi-profile support are post-MVP.
- Treat CDP as privileged access because it can control logged-in browser sessions.

## Performance Requirements

- MVP targets a single local operator on one machine.
- Task startup should be fast enough for interactive Pi use; optimize correctness and safety before throughput.
- Long-lived Windows browser sessions are preferred; the Python runtime may connect per task.
- Parallel task execution is out of scope for MVP.

## Security Requirements

- CDP must never be exposed to a public network.
- Bind CDP as narrowly as feasible: Windows localhost when possible, or a Windows host address reachable only from WSL/local machine.
- Store secrets in local `.env` or Pi/provider configuration; never hardcode credentials, tokens, or profile-specific secrets.
- Logs must avoid sensitive page contents and message bodies by default.
- High-risk actions require explicit operator approval before execution.

## Constraints

- Local-first, single-operator deployment for MVP.
- Windows host is required for the real browser runtime.
- WSL is required for orchestration and Pi integration.
- Browser-dependent integration tests may require the Windows browser to be running with CDP enabled and should be opt-in.
- Multi-user, hosted, multi-account, and anti-detection/evasion capabilities are not part of the product direction.
