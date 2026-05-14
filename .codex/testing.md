# Testing Contract -- agent-browser

Use this file as the canonical repo-level testing and validation contract when generating spec artifacts, bug artifacts, or executing changes.

## Minimum Gates

```bash
pytest -q
```

Coverage target: >=80% for touched modules once coverage tooling is configured.

## End-to-End Gate

No default E2E command exists yet. Browser/CDP E2E tests should be opt-in and require a Windows Chrome/Edge process with CDP enabled.

<!-- TODO: replace with actual command when browser integration tooling exists. -->

## When E2E Is Required

E2E or operator smoke validation is required when a change touches:

- CDP connection behavior
- Playwright browser session control
- approval-gated send/post/purchase/delete/account-change flows
- site-specific workflows such as SoundCloud automation

## Preferred Helpers

No project helper scripts exist yet.

<!-- TODO: add scripts/test/*.sh or equivalent once created. -->

## Spec Artifact Rules

For `.codex/specs/<spec-name>/design.md`:

- The `Testing Strategy` section should reference the relevant commands from this file instead of generic phrases like "run tests".
- If the spec touches an E2E-required surface, explicitly call out the E2E command and any CI E2E workflow.

For `.codex/specs/<spec-name>/tasks.md`:

- Every task must include exact `Validation:` commands.
- Every batch must include a batch-level validation gate.
- If a task or batch touches an E2E-required surface, include the E2E command or operator smoke gate in the relevant validation gate.
- Prefer repo helper scripts over ad hoc command variants when a helper exists.

## Bug Artifact Rules

For `.codex/bugs/<bug-name>/analysis.md`:

- Include at least one targeted regression test command.
- Include the relevant full repo gates from this file for the touched surface area.
- If the bug touches an E2E-required surface, include the E2E command or operator smoke gate in verification or smoke planning.
- Classify the smoke lane as `automatable`, `operator-only`, or `unknown`.

For `.codex/bugs/<bug-name>/context.md` or fix execution notes:

- Record which targeted tests, full gates, and E2E gates were run.

## CI Notes

No CI workflows exist yet.

<!-- TODO: add CI workflow names and enforced gates when CI is configured. -->

## Test Infrastructure

This section maps the repo's existing test fixtures, harness entry points, and E2E orchestration so agents reuse them instead of reinventing. For general test design principles (isolation, factories, deterministic time, mock boundaries), see `~/.pi/agent/rules/test_harness_guidelines.md`.

### Unit / Integration Tests

- Entry point: `tests/` once the Python package is created.
- Runner: `pytest`.
- Browser/CDP integration tests should be isolated from default unit tests unless the Windows browser prerequisite is satisfied.

<!-- TODO: document conftest.py fixtures, factories, environment handling, and singleton resets once they exist. -->

### E2E Tests

No E2E harness exists yet.

<!-- TODO: document Windows browser startup, CDP endpoint, readiness checks, seed data, artifact handling, and operator smoke steps when implemented. -->

### Adding New Tests

- Prefer unit tests for approval policy, task orchestration, configuration, and storage logic.
- Add integration tests for CDP/Playwright behavior only behind explicit opt-in markers or commands.
- Add workflow smoke coverage when implementing site-specific automation.
- Avoid recording sensitive logged-in page contents, message bodies, screenshots, or traces unless explicitly needed and kept local.

## Default Principle

When in doubt, prefer the smallest relevant targeted test first, then the full applicable gate for the touched layer, then E2E or operator smoke validation when the change matches the trigger list above.
