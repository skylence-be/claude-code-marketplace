---
description: End-of-session checklist — audit changes, verify quality, capture learnings
model: claude-sonnet-4-5
---

# /wrap-up — Session Wrap-Up

End your session with intention. Run through this checklist before closing.

$ARGUMENTS

## Execute This Checklist

### 1. Changes Audit

```bash
git status
git diff --stat
```

- What files were modified?
- Any uncommitted changes?
- Any TODOs left in code?

### 2. Quality Check

Run your project's lint/test commands:

```bash
# Run whatever lint/typecheck/test commands your project uses
# Examples:
#   npm run lint && npm run typecheck && npm test
#   composer test && ./vendor/bin/pint --test
#   python -m pytest && python -m mypy .
#   flutter test && dart analyze
```

- All checks passing?
- Any warnings to address?

### 3. Debug Artifact Scan

Search for leftover debug statements in changed files:

```bash
git diff --name-only | head -20
```

Check for: `console.log`, `debugger`, `dd()`, `dump()`, `var_dump()`, `print()` (debug), `TODO`, `FIXME`, `HACK`

### 4. Learning Capture

- What mistakes were made this session?
- What patterns worked well?
- Any corrections to add?

Format: `[LEARN] Category: Rule`

Categories: Navigation, Editing, Testing, Git, Quality, Context, Architecture, Performance, Claude-Code, Prompting

### 5. Next Session Context

- What's the next logical task?
- Any blockers to note?
- Context to preserve for next time?

### 6. Summary

Write one paragraph:
- What was accomplished
- Current state of the codebase
- What should happen next

---

**After completing checklist, ask:** "Ready to end session?"

## Related Commands

- `/pro-workflow:handoff` — Generate a handoff document for the next session
- `/pro-workflow:commit` — Smart commit with quality gates
- `/pro-workflow:learn-rule` — Capture a specific learning
