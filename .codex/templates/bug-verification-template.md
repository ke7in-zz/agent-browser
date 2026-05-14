---
artifact: bug-verification
bug_name: <bug-name>
status: draft
updated: YYYY-MM-DD
closure: pending
---

# Bug Verification

## Metadata

- **Bug**: `<bug-name>`
- **Status**: `draft | pass | fail`

## Fix Implementation Summary

[Brief description of what was changed to fix the bug]

## Smoke Test Gate

- **Smoke test type**: `automated | operator`
- **Executed by**: [agent name or operator]
- **Evidence**: [command output summary, manual confirmation, screenshot note, or session reference]
- [ ] **Smoke gate passed**

## Test Results

### Original Bug Reproduction

- [ ] **Before Fix**: Bug successfully reproduced
- [ ] **After Fix**: Bug no longer occurs

### Reproduction Steps Verification

[Re-test the original steps that caused the bug]

1. [Step 1] — Result
2. [Step 2] — Result
3. [Step 3] — Result
4. [Expected outcome] — Result

### Regression Testing

[Verify related functionality still works]

- [ ] **Related Feature 1**: [Test result]
- [ ] **Related Feature 2**: [Test result]
- [ ] **Integration Points**: [Test result]

### Edge Case Testing

[Test boundary conditions and edge cases]

- [ ] **Edge Case 1**: [Description and result]
- [ ] **Edge Case 2**: [Description and result]
- [ ] **Error Conditions**: [How errors are handled]

## Code Quality Checks

### Automated Gates

- [ ] **Format**: Passes
- [ ] **Lint**: Passes
- [ ] **Type Check**: Passes
- [ ] **Unit Tests**: All passing
- [ ] **Integration Tests**: All passing (if applicable)

### Manual Code Review

- [ ] **Code Style**: Follows project conventions
- [ ] **Error Handling**: Appropriate error handling added
- [ ] **Performance**: No performance regressions
- [ ] **Security**: No security implications

## Closure Checklist

- [ ] **Smoke gate passed**: Required smoke verification completed
- [ ] **Original issue resolved**: Bug no longer occurs
- [ ] **No regressions introduced**: Related functionality intact
- [ ] **All validation gates pass**: Format, lint, typecheck, tests
- [ ] **Documentation updated**: Relevant docs reflect changes (if applicable)

## Notes

[Any additional observations, lessons learned, or follow-up actions needed]

## Steering Updates Confirmed

- [ ] No steering doc updates were needed
- [ ] Relevant steering docs were updated as part of the fix
- Notes: [What changed and why]
