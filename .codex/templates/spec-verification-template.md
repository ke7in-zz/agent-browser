---
artifact: spec-verification
spec_name: <NNN-spec-name>
status: draft
updated: YYYY-MM-DD
closure: pending
---

# Spec Verification

## Metadata

- **Spec**: `<NNN-spec-name>`
- **Status**: `draft | pass | fail`

## Outcome

- **Result**: PASS | FAIL
- **Spec**: `[spec-name]`
- **Verified on**: [date]

## Requirement Verification Matrix

| Requirement | Status | Evidence type | Evidence |
| ----------- | ------ | ------------- | -------- |
| R-01 | Pass / Fail / Pending | automated / operator / missing | [test, command, manual note, or file ref] |
| R-02 | Pass / Fail / Pending | automated / operator / missing | [test, command, manual note, or file ref] |

## Design Conformance

- **Implemented as designed**:
  - [key design element]
- **Intentional deviations**:
  - [what changed and why]
- **Blocking mismatches**:
  - [anything preventing closure]

## Validation Gates Run

- [ ] Format
- [ ] Lint / Analyze
- [ ] Unit / Integration tests
- [ ] Additional project gates

## Smoke / Integration Checks

- [ ] **Smoke lane 1**: [result]
- [ ] **Integration lane 1**: [result]

## Operator Checks

- [ ] No operator-only checks required
- [ ] Operator check 1 completed: [evidence]
- [ ] Operator check 2 completed: [evidence]

## Deviations and Follow-ups

- [Non-blocking debt, follow-up work, or documentation updates]

## Steering Updates Confirmed

- [ ] No steering doc updates were needed
- [ ] Relevant steering docs were updated during implementation or verification
- Notes: [What changed and why]

## Closure Recommendation

- [ ] Ready for `/codex-archive spec <spec_name>`
- [ ] Not ready for archival

### Notes

[Any extra context that a future operator or agent should know]
