# Failure Patterns

## FP-cc084182a4
- date: 2026-05-14
- status: active
- project: agent-browser
- task: ad-hoc-session
- symptom: bash failed: no tests ran in 0.00s
- failed_approach: Tool invocation failed: bash failed: no tests ran in 0.00s
- failure_reason: The attempted tool call or file-targeting approach failed and should be reconsidered before repeating it.
- successful_alternative: Re-read the affected files, verify paths and call sites, then retry with a narrower, evidence-backed change.
- classification: journal-tool_error
- source: tool:bash
