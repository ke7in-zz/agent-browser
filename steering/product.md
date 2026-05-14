# Product -- agent-browser

## Vision

Build a personal, local-first browser automation runtime that lets a single operator initiate tasks from Pi and execute them against real logged-in Windows browser sessions from WSL.

## Goals

1. **Pi-triggered automation**: Start browser automation tasks from Pi with a clear task prompt and execution status.
2. **Real logged-in browser control**: Connect from WSL to Windows-hosted Chrome/Edge via Chrome DevTools Protocol (CDP) using an existing persistent browser profile.
3. **Reusable runtime foundation**: Provide task orchestration, browser session control, local persistence, structured logging, and structured task results.
4. **Approval-aware execution**: Pause for operator approval before sensitive actions such as sending messages, posting, purchases, account changes, or destructive actions.
5. **First workflow proof**: Complete logged-in SoundCloud messaging tasks with approval before sending messages.

## Target Users

- **Primary user**: The repository operator, running automation locally from WSL and controlling it through Pi.
- **Initial workflow context**: Repetitive logged-in browser work where manual navigation, message drafting, and form interaction are tedious.
- **Future-adjacent users**: Other operators or team usage are not targeted for MVP.

## Non-goals

- No SaaS product or hosted multi-tenant platform.
- No bot-detection evasion, account farming, spam scaling, or deceptive automation.
- No headless-only automation as the primary path.
- No general-purpose RPA studio UI; Pi is the command/control interface.
- No autonomous execution of sensitive external actions without an explicit approval policy.

## Key Constraints

- WSL runs orchestration, LLM/browser-use integration, workflows, queues, SQLite/CRM/logging, and Pi-facing command handling.
- Windows host runs real Chrome/Edge with a persistent logged-in profile, GPU acceleration, and native browser environment.
- WSL connects to the Windows browser over CDP.
- Design is local-first and single-operator for MVP.
- Approval requirements depend on task/action risk.

## Spec Roadmap

### MVP

1. `001-prd-runtime-foundation` -- Python package scaffold, config loading, task model, SQLite task log, and Pi-invoked CLI entrypoint. Estimated size: M
2. `002-prd-cdp-browser-connection` -- Connect from WSL to Windows Chrome/Edge over CDP through Playwright and verify basic navigation/session access. Estimated size: M
3. `003-prd-approval-gates` -- Define action-risk policy and operator approval checkpoints for sensitive browser actions. Estimated size: S
4. `004-prd-browser-agent-adapter` -- Wrap browser-use/agent execution behind a local adapter that can run one task at a time and report structured results. Estimated size: M
5. `005-prd-soundcloud-workflow` -- First real logged-in workflow: navigate SoundCloud, draft/prepare messages, and require approval before send. Estimated size: M

### Post-MVP

6. `006-prd-task-queue` -- Add durable queue/workflow runner for queued local tasks. Estimated size: M
7. `007-prd-artifacts-and-observability` -- Optional screenshots, trace files, richer logs, and task replay/debug tooling with sensitive-data controls. Estimated size: M
8. `008-prd-multi-profile-support` -- Manage multiple browser profiles/accounts with isolated config and safety limits. Estimated size: L

### Dependencies

- 002 depends on 001.
- 003 depends on 001.
- 004 depends on 001 and 002.
- 005 depends on 002, 003, and 004.
- 006-008 are post-MVP and should not block the first usable product.
