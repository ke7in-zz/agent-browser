# Project Structure -- agent-browser

## Directory Layout

```text
agent-browser/
  src/
    agent_browser/
      __init__.py
      cli.py                 # Pi/script entrypoint
      config.py              # local config loading
      tasks.py               # task model and execution orchestration
      approvals.py           # approval policy and prompts
      browser/
        cdp.py               # CDP connection helpers
        playwright_client.py # Playwright adapter
      agents/
        browser_use.py       # browser-use adapter
      storage/
        db.py                # SQLite connection/schema
        repositories.py      # task/log persistence
      workflows/
        soundcloud.py        # first proof workflow
  tests/
    unit/
    integration/
  scripts/
    start_windows_chrome.ps1 # optional Windows helper script
  steering/
  .codex/
```

## Naming Conventions

- Python package name: `agent_browser`.
- Python modules use `snake_case.py`.
- Classes use `PascalCase`; functions, variables, and module-level constants use idiomatic Python naming.
- Workflow modules should be named after the target workflow or site only when they contain workflow-specific behavior.
- Test files should use `test_<module_or_behavior>.py`.

## Module / Package Boundaries

- `cli.py` is a thin entrypoint; it parses intent/config and delegates to orchestration.
- `tasks.py` owns task lifecycle and orchestration flow.
- `approvals.py` owns action-risk classification and approval decisions.
- `browser/` owns Playwright and CDP mechanics.
- `agents/` owns LLM/browser-agent integrations and hides provider-specific APIs behind adapters.
- `storage/` owns SQLite schema, connections, repositories, and persistence behavior.
- `workflows/` composes task, browser, agent, approval, and storage services; it must not talk directly to raw SQLite or CDP.

## Quality Standards

- Use `pytest` for unit and integration tests.
- Unit-test approval policy, task orchestration, configuration parsing, and storage behavior.
- Keep browser/CDP integration tests opt-in so normal WSL gates do not require a running Windows browser.
- Prefer small modules and functions; avoid speculative abstractions before the first workflow proves the runtime.
- Keep logs structured and avoid sensitive logged-in page data unless explicitly enabled for debugging.
