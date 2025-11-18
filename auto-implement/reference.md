# Auto-Implement Reference

## Plan File Format

Implementation plans follow this structure:

```markdown
# [Feature Name] Implementation Plan

## Overview
[Brief description]

## Current State Analysis
[What exists now]

## Desired End State
[What we want to achieve]

## What We're NOT Doing
[Explicit scope exclusions]

## Phase 1: [Descriptive Name]

### Overview
[What this phase accomplishes]

### Changes Required:

#### 1. [Component/File Group]
**File**: `path/to/file.ext`
**Changes**: [Summary]

### Success Criteria:

#### Automated Verification:
- [ ] Migration applies: `make migrate`
- [ ] Tests pass: `make test`
- [ ] Linting passes: `make lint`

#### Manual Verification:
- [ ] Feature works in UI
- [ ] Performance acceptable

---

## Phase 2: [Next Phase]
...
```

## Phase Detection Regex

To find phases in a plan:

```regex
^## Phase (\d+):\s*(.+?)$
```

This matches lines like:
- `## Phase 1: Database Schema`
- `## Phase 2: Backend API`
- `## Phase 10: Final Integration`

## Completion Detection Algorithm

1. Look for the "#### Automated Verification:" section
2. Scan all checkbox items until reaching "#### Manual Verification:"
3. If any item is `- [ ]` (unchecked), phase is incomplete
4. If all items are `- [x]` (checked), phase is complete

Example:

```markdown
#### Automated Verification:
- [x] Tests pass: `make test`
- [x] Linting passes: `make lint`
- [ ] Migration runs: `make migrate`  ← This makes phase incomplete

#### Manual Verification:
- [ ] UI works correctly  ← Not checked yet, but doesn't count for automated completion
```

## File Locations

Plans are typically stored in:
- `thoughts/shared/plans/YYYY-MM-DD-DESCRIPTION.md`
- `thoughts/shared/plans/YYYY-MM-DD-ENG-XXXX-description.md` (with ticket number)

## Common Commands Referenced in Plans

- `make migrate` - Run database migrations
- `make test` - Run test suite
- `make lint` - Run linters
- `make check` - Often runs both lint and test
- `make -C directory check` - Run checks in specific directory
- `bun run fmt` - Format code (for Node/TypeScript projects)
- `go test ./...` - Run Go tests
- `npm run typecheck` - TypeScript type checking
- `pytest` - Run Python tests

## Workflow States

A plan implementation can be in these states:

1. **Not Started**: No checkboxes are checked
2. **In Progress**: Some checkboxes checked, some unchecked
3. **Awaiting Manual Verification**: All automated verification checked, manual verification unchecked
4. **Complete**: All automated AND manual verification checked

## Error Handling

Common failure scenarios:

### Test Failures
```
Failed: make test
Output: FAILED tests/test_auth.py::test_login

Action: Debug the failing test, fix the code, re-run phase
```

### Migration Failures
```
Failed: make migrate
Output: Error: duplicate key value violates unique constraint

Action: Review migration, fix conflict, re-run phase
```

### Type Errors
```
Failed: npm run typecheck
Output: error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'

Action: Fix type error, re-run phase
```

## Integration Points

### With /create_plan
1. User runs `/create_plan task description`
2. Claude creates plan in `thoughts/shared/plans/`
3. User reviews and approves
4. User invokes auto-implement skill with the plan path

### With /implement_plan
The auto-implement skill calls `/implement_plan` for each phase:
```
/implement_plan thoughts/shared/plans/2025-01-15-oauth.md phase 1
/implement_plan thoughts/shared/plans/2025-01-15-oauth.md phase 2
/implement_plan thoughts/shared/plans/2025-01-15-oauth.md phase 3
```

### Manual Intervention Points

User may need to intervene when:
1. Manual verification is required (expected)
2. Automated verification fails (fix needed)
3. Plan doesn't match reality (plan needs updating)
4. Unexpected errors occur (debugging needed)

## Python Script Alternative

For users who prefer a standalone script, `scripts/auto_implement_plan.py` provides:

```bash
# Install dependencies
pip install -r requirements.txt

# Run automation
python scripts/auto_implement_plan.py --plan path/to/plan.md

# Resume from phase 3
python scripts/auto_implement_plan.py --plan path/to/plan.md --start-phase 3

# Create new plan
python scripts/auto_implement_plan.py --create "Task description"
```

The skill provides the same functionality but integrated directly into Claude Code conversations.