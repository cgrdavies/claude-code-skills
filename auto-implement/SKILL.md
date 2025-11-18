---
name: auto-implement
description: Automates multi-phase plan implementation using a Python script that runs each phase with fresh context between phases. Use when user wants to automatically implement all phases of a plan with context clearing between each phase.
---

# Auto-Implement Skill

This skill runs a Python script that automates the complete plan implementation workflow by executing each phase with fresh context, exactly like manually running `/implement_plan phase N`, `/clear`, then repeating for the next phase.

## When to Use This Skill

Use this skill when the user:
- Asks to "auto-implement" a plan
- Wants to "implement all phases" automatically
- Says "run the whole plan" or similar
- Wants context cleared between phases for better performance

## What the Script Does

The `auto_implement_plan.py` script:

1. **Parses the plan** to find all phases (`## Phase N:` headers)
2. **Detects completed work** by checking for `[x]` checkboxes in automated verification sections
3. **Implements each incomplete phase** by running `/implement_plan [plan] phase [N]`
4. **Clears context between phases** by starting a fresh Claude session for each phase
5. **Pauses for manual verification** when phases require human testing
6. **Updates the plan file** with checkmarks as phases complete
7. **Provides progress summaries** throughout the process

## Instructions

When this skill is invoked:

### Step 1: Get the Plan Path

If the user didn't provide a plan path, ask:
```
Which plan would you like to auto-implement?
Please provide the path (usually in thoughts/shared/plans/)
```

### Step 2: Explain What Will Happen

Tell the user:
```
I'll run the auto-implementation script that will:
- Parse your plan and detect completed phases
- Implement each remaining phase with fresh context
- Pause for manual verification when needed
- Update progress in the plan file

This runs each phase in a separate context (like /clear between phases) for optimal performance.
```

### Step 3: Run the Script

Use the Bash tool to run the script from the current working directory (the project directory):

```bash
python ~/.claude/skills/auto-implement/scripts/auto_implement_plan.py --plan [PLAN_PATH] --verbose
```

Replace `[PLAN_PATH]` with the actual plan path provided by the user.

**Important**:
- Always use `--verbose` flag so the user can see progress
- Run from the current working directory so the script can access project files
- Use the full path to the script in the skills directory

### Step 4: Handle Script Output

The script will output:
- Phase status summary
- Implementation progress for each phase
- Prompts for manual verification
- Completion summaries

Show this output to the user in real-time.

### Step 5: Manual Verification

When the script pauses for manual verification, it will prompt:
```
Manual verification needed. Complete? (y/n):
```

The user should perform the manual tests and then type `y` to continue.

### Step 6: Handle Completion or Errors

**If successful:**
```
✅ All phases implemented successfully!

The plan has been fully implemented with all phases complete.
```

**If errors occur:**
```
The script encountered an issue at Phase [N].

You can fix the issue and resume with:
python scripts/auto_implement_plan.py --plan [PLAN_PATH] --start-phase [N]
```

## Script Options

The script supports these options:

- `--plan PATH` - Path to the plan file (required)
- `--start-phase N` - Resume from phase N
- `--end-phase N` - Stop after phase N
- `--verbose` - Show detailed output (always use this)
- `--dry-run` - Preview what would happen without executing

## Example Usage

**User**: "Auto-implement thoughts/shared/plans/2025-01-15-oauth.md"

**You should**:
1. Acknowledge the request
2. Run the script from the current project directory:
```bash
python ~/.claude/skills/auto-implement/scripts/auto_implement_plan.py --plan thoughts/shared/plans/2025-01-15-oauth.md --verbose
```
3. Monitor output and relay it to the user

## Alternative: Manual Phase-by-Phase

If the user prefers manual control or the script isn't working, you can fall back to:
```
Alternatively, I can help you implement phases one at a time:
1. /implement_plan [plan] phase 1
2. /clear
3. /implement_plan [plan] phase 2
4. And so on...

Would you prefer that approach?
```

## Prerequisites

The script requires:
- Python 3.10+
- claude-agent-sdk (installed via requirements.txt)
- Claude Code CLI

If dependencies aren't installed, run:
```bash
cd ~/.claude/skills/auto-implement
pip install -r requirements.txt
```
