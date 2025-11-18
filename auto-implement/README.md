# Auto-Implement Skill

Automates the multi-phase plan implementation workflow by executing each phase with fresh context, just like manually running `/implement_plan phase N`, `/clear`, then repeating.

## What This Skill Does

When you have an implementation plan with multiple phases (created via `/create_plan`), this skill:

1. Parses the plan to identify all phases
2. Checks which phases are already complete (by looking for `[x]` checkboxes)
3. Implements each incomplete phase sequentially
4. Clears context between phases (for optimal performance)
5. Pauses for manual verification when needed
6. Updates the plan file as work progresses

## Usage

### Trigger the Skill

Claude will automatically use this skill when you say things like:

- "Auto-implement the plan at thoughts/shared/plans/2025-01-15-oauth.md"
- "Automatically run all phases of the plan"
- "Implement the whole plan"
- "Resume implementation from phase 3"

### Example Session

```
You: Auto-implement thoughts/shared/plans/2025-01-15-feature-x.md

Claude:
Found 3 phases in plan:
- Phase 1: Database Schema ○
- Phase 2: Backend Logic ○
- Phase 3: Frontend UI ○

Starting implementation...

═══════════════════════════════════════════════
Implementing Phase 1/3: Database Schema
═══════════════════════════════════════════════

[Implementation proceeds with /implement_plan]

Phase 1 Complete - Manual Verification Required

Automated verification passed:
✓ Migration runs: make migrate
✓ Tests pass: make test

Please verify manually:
• Database schema looks correct
• Foreign keys are properly set up

Reply with "continue" when ready.

You: continue

Claude:
Moving to Phase 2...

═══════════════════════════════════════════════
Implementing Phase 2/3: Backend Logic
═══════════════════════════════════════════════

[Implementation continues...]
```

## Files in This Skill

- **SKILL.md** - Main skill definition and instructions for Claude
- **reference.md** - Detailed reference about plan formats, detection algorithms, error handling
- **README.md** - This file
- **scripts/auto_implement_plan.py** - Standalone Python script for automation
- **requirements.txt** - Python dependencies for the script

## Using the Python Script

If you prefer a standalone script instead of the skill:

```bash
# Install dependencies
pip install -r requirements.txt

# Auto-implement a plan
python scripts/auto_implement_plan.py --plan thoughts/shared/plans/2025-01-15-feature.md

# Resume from specific phase
python scripts/auto_implement_plan.py --plan path/to/plan.md --start-phase 3

# Create and implement new plan
python scripts/auto_implement_plan.py --create "Add OAuth2 authentication"

# See what would happen without executing
python scripts/auto_implement_plan.py --plan path/to/plan.md --dry-run --verbose
```

## How It Works

### Phase Detection

The skill parses markdown plans looking for:
```markdown
## Phase 1: Some Name
## Phase 2: Another Name
```

### Completion Tracking

Phases are considered complete when all automated verification items are checked:

```markdown
#### Automated Verification:
- [x] Tests pass: make test
- [x] Linting passes: make lint

#### Manual Verification:
- [ ] Works in UI  ← Manual items don't affect automated completion
```

### Context Clearing

Each phase runs in a fresh context, equivalent to:
1. `/implement_plan plan.md phase 1`
2. `/clear`
3. `/implement_plan plan.md phase 2`
4. `/clear`
5. And so on...

This ensures optimal performance and prevents context bloat.

## Benefits

1. **Saves Time**: No need to manually run each phase and clear context
2. **Consistent**: Follows the same process every time
3. **Resumable**: Can pick up from any phase if interrupted
4. **Safe**: Pauses for manual verification, stops on errors
5. **Transparent**: Shows detailed progress throughout

## When to Use

✅ **Good for:**
- Plans with 3+ phases
- Plans where phases are well-defined and independent
- Implementing approved plans without changes
- Resuming interrupted work

❌ **Not ideal for:**
- Plans still being designed (use `/create_plan` first)
- Single-phase implementations (just use `/implement_plan`)
- Plans that need significant adaptation (implement manually)

## Troubleshooting

### Skill doesn't activate

Make sure you're using trigger phrases like "auto-implement" or "implement the whole plan".

### Phase keeps failing

The skill will stop and report the error. Fix the issue, then resume with:
"Resume auto-implementation from phase N"

### Manual verification confusion

The skill will always pause and wait for your "continue" confirmation before moving to the next phase.

## Version History

- v1.0 (2025-01-15): Initial release with phase detection, completion tracking, and manual verification support