# agent-browser: Agent Notes

## Start Here

- Confirm branch + destination: `main` is the protected branch when protection is configured; changes to protected branches must land via pull request.
- Read `steering/product.md`, `steering/tech.md`, and `steering/structure.md` before planning changes.
- Treat Chrome DevTools Protocol access as privileged control over logged-in browser sessions.

## Non-Negotiables (repo-specific)

- Python orchestration runs in WSL; real Chrome/Edge runs on the Windows host and is controlled over CDP.
- No direct browser, CDP, LLM, or storage calls from workflow logic when a service/adapter boundary exists.
- High-risk browser actions such as send, post, purchase, delete, or account changes require explicit operator approval.
- Do not build bot-detection evasion, account farming, spam scaling, or deceptive automation features.
- Keep browser-dependent integration tests opt-in so default gates can run without a Windows browser session.

## Validation Gates (minimum before "done")

<!-- Keep commands below in sync with .codex/testing.md -- that file is authoritative -->

See `.codex/testing.md` for the canonical command matrix and artifact-generation rules.

```bash
pytest -q
```

After Python tooling is added, keep this section synchronized with `.codex/testing.md` and prefer project helper scripts when available.

## Environment / Local-Only Files (avoid committing)

- `.env`, `.env.local`
- `__pycache__/`, `.pytest_cache/`, `.venv*/`, `venv/`
- local SQLite databases such as `*.db`, `*.sqlite`, `*.sqlite3`
- browser profiles, screenshots, traces, and task artifacts containing logged-in page data
- `.DS_Store`

## References

- Steering: `steering/product.md`, `steering/tech.md`, `steering/structure.md`
- Testing contract: `.codex/testing.md`
- Specs: `.codex/specs/`
- Session: `SESSION.md`
