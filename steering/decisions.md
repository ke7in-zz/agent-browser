# Decisions

This file records architectural and product decisions for agent-browser.

## Active Decisions

### DEC-001

- **ID**: DEC-001
- **Date**: 2026-05-14
- **Title**: Build a personal local-first browser automation runtime
- **Decision**: agent-browser is a single-operator local tool controlled through Pi, not a hosted SaaS or multi-tenant automation platform.
- **Why**: The primary need is personal logged-in browser automation from WSL with a real Windows browser, not external product distribution.
- **Consequences**: MVP can optimize for local reliability, direct operator approval, and small scope; multi-user auth, hosted deployment, billing, and team collaboration are deferred.
- **Status**: active

### DEC-002

- **ID**: DEC-002
- **Date**: 2026-05-14
- **Title**: Split orchestration and browser runtime across WSL and Windows
- **Decision**: WSL runs orchestration, agents, workflows, approvals, and persistence; Windows runs Chrome/Edge with persistent profile and GPU acceleration; the connection uses CDP.
- **Why**: The browser must use the real Windows desktop environment while the automation/orchestration stack runs naturally in WSL.
- **Consequences**: CDP becomes a privileged local interface that must be protected; integration tests may require a Windows browser process with CDP enabled.
- **Status**: active

### DEC-003

- **ID**: DEC-003
- **Date**: 2026-05-14
- **Title**: Use Python-only for MVP
- **Decision**: The MVP runtime uses Python with Playwright, browser-use adapter boundaries, and SQLite persistence.
- **Why**: Python aligns with browser-use, Playwright Python, simple local orchestration, and fast MVP delivery.
- **Consequences**: TypeScript/UI layers are deferred; Pi remains the control interface rather than a custom web app.
- **Status**: active

### DEC-004

- **ID**: DEC-004
- **Date**: 2026-05-14
- **Title**: Require approval for high-risk browser actions
- **Decision**: Sensitive actions such as sending messages, posting, purchases, deletions, and account changes require explicit operator approval.
- **Why**: Logged-in browser automation can affect external accounts and people; safety must be built into the runtime boundary.
- **Consequences**: Workflows need approval checkpoints and cannot blindly execute all agent-proposed actions.
- **Status**: active

### DEC-005

- **ID**: DEC-005
- **Date**: 2026-05-14
- **Title**: Prove the runtime with SoundCloud messaging
- **Decision**: SoundCloud logged-in messaging is the first proof workflow, with approval before sending messages.
- **Why**: It is a concrete repetitive logged-in browser task that validates Pi-triggered task execution, CDP control, agent/workflow integration, logging, and approvals.
- **Consequences**: The workflow must remain a proof of general browser automation, not a SoundCloud-only product direction or spam automation system.
- **Status**: active

## Archived Decisions

No archived decisions yet.
