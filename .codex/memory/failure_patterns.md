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

## FP-16c1fb5aeb
- date: 2026-05-14
- status: active
- project: agent-browser
- task: ad-hoc-session
- symptom: read failed while operating on /home/ke7in/.pi/agent/templates/spec-verification-template.md: ENOENT: no such file or directory, access '/home/ke7in/.pi/agent/templates/spec-verification-template.md'
- failed_approach: Tool invocation failed: read failed while operating on /home/ke7in/.pi/agent/templates/spec-verification-template.md: ENOENT: no such file or directory, access '/home/ke7in/.pi/agent/templates/spec-verification-template.md'
- failure_reason: The attempted tool call or file-targeting approach failed and should be reconsidered before repeating it.
- successful_alternative: Re-read the affected files, verify paths and call sites, then retry with a narrower, evidence-backed change.
- classification: journal-tool_error
- source: tool:read, /home/ke7in/.pi/agent/templates/spec-verification-template.md

## FP-f2d31b05a7
- date: 2026-05-14
- status: active
- project: agent-browser
- task: ad-hoc-session
- symptom: bash failed: no checks reported on the 'spec/001-prd-runtime-foundation' branch
- failed_approach: Tool invocation failed: bash failed: no checks reported on the 'spec/001-prd-runtime-foundation' branch
- failure_reason: The attempted tool call or file-targeting approach failed and should be reconsidered before repeating it.
- successful_alternative: Re-read the affected files, verify paths and call sites, then retry with a narrower, evidence-backed change.
- classification: journal-tool_error
- source: tool:bash
