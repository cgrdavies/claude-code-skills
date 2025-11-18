# Quick Start Guide

## Installation

The skill is already installed at `~/.claude/skills/auto-implement/` and available in all your Claude Code sessions!

## Basic Usage

### 1. Create a Plan First

```
You: /create_plan Add OAuth2 authentication to the app
```

Claude will work with you to create a detailed plan with multiple phases.

### 2. Auto-Implement the Plan

Once the plan is finalized, trigger the skill:

```
You: Auto-implement the plan at thoughts/shared/plans/2025-01-15-oauth.md
```

Or simply:

```
You: Implement the whole plan
```

### 3. Manual Verification Checkpoints

Claude will pause after each phase for manual verification:

```
Claude:
Phase 1 Complete - Manual Verification Required

Automated verification passed:
✓ Tests pass
✓ Linting passes

Please verify manually:
• OAuth flow works in UI
• Tokens are properly stored

Reply with "continue" when ready.

You: continue
```

### 4. Resuming After Interruption

If you need to stop and resume later:

```
You: Resume auto-implementation from phase 3
```

## Common Phrases That Trigger the Skill

- "Auto-implement [plan path]"
- "Automatically implement the plan"
- "Run all phases of the plan"
- "Implement the whole plan"
- "Resume implementation from phase N"
- "Continue implementing from where we left off"

## Example Complete Workflow

```
# 1. Create the plan
You: /create_plan Add rate limiting to API endpoints

Claude: [works with you to create detailed plan]
Plan created at: thoughts/shared/plans/2025-01-15-rate-limiting.md

# 2. Auto-implement
You: Auto-implement that plan

Claude:
Found 4 phases:
- Phase 1: Database Schema ○
- Phase 2: Middleware Implementation ○
- Phase 3: Configuration ○
- Phase 4: Testing ○

Starting implementation...

[Phase 1 completes]

Phase 1 Complete - Manual Verification Required
...

You: continue

[Phase 2 completes]
...

You: continue

[Continues through all phases]

Claude:
✅ All Phases Complete!

Summary:
- Phase 1: Database Schema ✓
- Phase 2: Middleware Implementation ✓
- Phase 3: Configuration ✓
- Phase 4: Testing ✓

Next steps:
- Review the changes
- Run final integration tests
- Create a PR
```

## Advanced Usage

### Implement Specific Phase Range

```
You: Auto-implement phases 2-4 of the plan
```

### Check Plan Status

```
You: What's the status of the plan implementation?
```

Claude will read the plan and show which phases are complete.

### Skip Manual Verification (Not Recommended)

```
You: Continue implementation, skip manual verification
```

⚠️ **Warning**: Only do this if you're confident the feature works.

## Tips

1. **Always review the plan first** - Make sure the phases are well-defined
2. **Keep phases small** - Smaller phases = better context management
3. **Do manual verification** - Don't skip it, it catches issues early
4. **Fix issues before continuing** - If a phase fails, fix it before moving on
5. **Use resuming** - If interrupted, just resume from the last incomplete phase

## Troubleshooting

### "Plan file not found"

Make sure the path is correct:
```
You: Auto-implement thoughts/shared/plans/2025-01-15-myplan.md
```

### "No phases found"

The plan might not use the standard format. Check that phases are marked as:
```markdown
## Phase 1: Name
## Phase 2: Name
```

### Skill doesn't activate

Try being more explicit:
```
You: Use the auto-implement skill for thoughts/shared/plans/myplan.md
```

Or mention it by name:
```
You: I want to auto-implement the plan using the auto-implement skill
```

### Phase fails repeatedly

Stop the automation and debug manually:
```
You: Stop auto-implementation, I need to debug this

[Fix the issue]

You: Resume from phase 3
```

## Comparison: Skill vs Script

### Using the Skill (Recommended)

✅ No setup required - works immediately
✅ Natural conversation flow
✅ Integrated with Claude Code
✅ Can ask questions and adapt

### Using the Python Script

✅ Can run outside of Claude Code
✅ More control over execution
✅ Easier to integrate into CI/CD
✅ Dry-run and verbose modes

To use the script:
```bash
cd ~/.claude/skills/auto-implement
pip install -r requirements.txt
python scripts/auto_implement_plan.py --help
```

## What Happens Behind the Scenes

When you trigger the skill, Claude:

1. Reads the plan file
2. Parses all phases using regex
3. Checks completion status (by looking for `[x]` checkboxes)
4. For each incomplete phase:
   - Runs `/implement_plan [plan] phase [N]`
   - Monitors automated verification
   - Pauses for manual verification
   - Updates plan file with checkmarks
   - Starts fresh for next phase (context clearing)
5. Reports completion summary

This is equivalent to you manually doing:
```
/implement_plan plan.md phase 1
[wait for completion]
/clear
/implement_plan plan.md phase 2
[wait for completion]
/clear
/implement_plan plan.md phase 3
...
```

But automated and hands-free (except for manual verification)!