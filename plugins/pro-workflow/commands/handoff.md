---
description: Generate a session handoff document for the next session to continue seamlessly
model: claude-sonnet-4-5
---

# /handoff — Session Handoff Document

Generate a structured handoff document that another Claude session (or your future self) can consume immediately to continue where you left off.

$ARGUMENTS

## Process

### 1. Gather Current State

```bash
git status
git diff --stat
git log --oneline -5
```

- Current branch and uncommitted work
- Recent commits this session
- Files modified

### 2. Check Learnings

Read any learnings captured this session from `.claude/data/learnings.json`:

```bash
python3 -c "
import json, os
from datetime import datetime, timedelta
path = '.claude/data/learnings.json'
if os.path.exists(path):
    with open(path) as f:
        data = json.load(f)
    cutoff = (datetime.now() - timedelta(hours=4)).isoformat()
    recent = [l for l in data if l.get('date', '') >= cutoff]
    for l in recent:
        print(f\"  [{l['category']}] {l['rule']}\")
    if not recent:
        print('  No learnings this session')
else:
    print('  No learnings file found')
"
```

### 3. Generate Handoff Document

Produce the following markdown document:

```markdown
# Session Handoff — [date] [time]

## Status
- **Branch**: [current branch]
- **Commits this session**: [count]
- **Uncommitted changes**: [count] files modified
- **Tests**: passing / failing / not run

## What's Done
- [completed task 1]
- [completed task 2]

## What's In Progress
- [current task with context on where you stopped]
- [file:line that needs attention next]

## What's Pending
- [next task that hasn't been started]
- [blocked items with reason]

## Key Decisions Made
- [decision 1 and why]
- [decision 2 and why]

## Learnings Captured
- [Category] Rule (from this session)

## Files Touched
- `path/to/file1.ext` — [what changed]
- `path/to/file2.ext` — [what changed]

## Gotchas for Next Session
- [thing that tripped you up]
- [non-obvious behavior discovered]

## Resume Command
Copy this into your next session:
> Continue working on [branch]. [1-2 sentence context]. Next step: [specific action].
```

### 4. Save the Handoff

Save to `.claude/data/handoffs/[date]-[branch].md`:

```bash
mkdir -p .claude/data/handoffs
```

## Options

- **default**: Standard handoff with all sections
- **--full**: Include full git diff in the document
- **--compact**: Just the resume command and key context (for pasting into next session)

## Why This Is Different from /wrap-up

`/wrap-up` is a checklist to close a session properly. `/handoff` is a document designed to be consumed by the next session — it's written for the reader, not the writer.

## Related Commands

- `/pro-workflow:wrap-up` — End-of-session checklist (do this first, then handoff)
- `/pro-workflow:learn` — Best practices guide
- `/pro-workflow:learn-rule` — Capture specific learnings

---

**Trigger:** Use when user says "handoff", "hand off", "pass to next session", "create handoff", "session transfer", "continue later", or when ending a session and wants to resume smoothly.
