---
artifact: bug-analysis
bug_name: <bug-name>
status: draft
updated: YYYY-MM-DD
approval: pending
---

# Bug Analysis

## Metadata

- **Bug**: `<bug-name>`
- **Status**: `draft | reviewed | approved`

## Root Cause Analysis

### Investigation Summary

[Overview of the investigation process and findings]

### Observed Facts

- [Verified runtime or code facts]

### Hypotheses Considered

- [Hypothesis and whether it was ruled out or confirmed]

### Root Cause

[The underlying cause of the bug]

### Contributing Factors

[Any secondary factors that led to or exacerbated the issue]

### Why Existing Tests Missed It

[Why the current test suite did not catch the failure]

## Technical Details

### Affected Code Locations

[List specific files, functions, or code sections involved]

- **File**: `path/to/file`
  - **Function/Method**: `functionName()`
  - **Lines**: `123-145`
  - **Issue**: [Description of the problem in this location]

### Data Flow Analysis

[How data moves through the system and where it breaks]

### Dependencies

[External libraries, services, or components involved]

## Impact Analysis

### Direct Impact

[Immediate effects of the bug]

### Indirect Impact

[Secondary effects or potential cascading issues]

### Risk Assessment

[Risks if the bug is not fixed]

## Solution Approach

### Fix Strategy

[High-level approach to solving the problem]

### Alternative Solutions

[Other possible approaches considered]

### Risks and Trade-offs

[Potential risks of the chosen solution]

### Smoke Test Classification

- **Smoke lane**: `automatable | operator-only | unknown`
- **Smoke steps**: [Exact smoke path to run after the fix]

## Implementation Plan

### Changes Required

[Specific modifications needed]

1. **Change 1**: [Description]
   - File: `path/to/file`
   - Modification: [What needs to be changed]

2. **Change 2**: [Description]
   - File: `path/to/file`
   - Modification: [What needs to be changed]

### Testing Strategy

[How to verify the fix works]

- Run the project's declared validation gates (format, lint, typecheck, test).
- [Additional targeted tests for the specific bug scenario]

## Steering Updates Required

- [ ] No steering doc updates expected
- [ ] Update `steering/product.md`
- [ ] Update `steering/tech.md`
- [ ] Update `steering/structure.md`
- Notes: [What changed and why]

### Prevention Plan

[How to prevent this class of bug from recurring — tests, guards, lint rules, invariants]

### Rollback Plan

[How to revert if the fix causes issues]
