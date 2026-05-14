---
artifact: tasks
spec_name: <NNN-spec-name>
status: draft
updated: YYYY-MM-DD
approval: pending
generated_from: design.md
---

# Tasks

## Metadata

- **Spec**: `<NNN-spec-name>`
- **Status**: `draft | approved | in_progress | complete`
- **Canonical task IDs**: Use stable IDs like `T-001`, `T-002`; do not renumber existing IDs after execution starts.

## Batch 1 — [Batch title]

Rationale: [Why this batch comes first; what foundation it establishes]

- [ ] T-001: [Concise task title]
  - Objective: [one sentence]
  - Files (create/modify):
    - `[path/to/file]`
    - `[path/to/test]`
  - _Requirements: [requirement refs, e.g. R-01, R-02]_
  - _Leverage: [existing file:Symbol or path to reuse]_
  - Validation:
    - [project format/lint/typecheck/test commands]
  - Result: [fill after completion]

- [ ] T-002: [Concise task title]
  - Objective: [one sentence]
  - Files (create/modify):
    - `[path/to/file]`
  - _Requirements: [requirement refs]_
  - _Leverage: [existing file:Symbol or path to reuse]_
  - Validation:
    - [project format/lint/typecheck/test commands]
  - Result: [fill after completion]

Batch validation:

- [broader validation commands that must pass before starting the next batch]

## Batch 2 — [Batch title]

Rationale: [Why this batch follows Batch 1; what it builds on]

- [ ] T-003: [Concise task title]
  - Objective: [one sentence]
  - Files (create/modify):
    - `[path/to/file]`
    - `[path/to/test]`
  - _Requirements: [requirement refs]_
  - _Leverage: [existing file:Symbol or path to reuse]_
  - Validation:
    - [project format/lint/typecheck/test commands]
  - Result: [fill after completion]

Batch validation:

- [broader validation commands that must pass before starting the next batch]

## Steering Updates Required

- [ ] No steering doc updates expected
- [ ] Update `steering/product.md`
- [ ] Update `steering/tech.md`
- [ ] Update `steering/structure.md`
- Notes: [What changed and why]
