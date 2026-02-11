---
description: Claude Code best practices guide and persistent learning capture
model: claude-sonnet-4-5
---

# /learn — Claude Code Best Practices & Learning Capture

Learn Claude Code best practices and capture lessons into persistent memory.

## Usage

- `/learn` — Show best practices guide
- `/learn <topic>` — Show practices for a specific topic (e.g., `/learn context`, `/learn prompting`)
- `/learn save` — Capture a lesson from this session

$ARGUMENTS

## Best Practices

### Sessions & Context
- Every Claude Code invocation is a session. Claude reads your project on start.
- Context window is finite (200k tokens). Use `/context` to check usage.
- Use `/compact` at task boundaries — after planning, after a feature, when >70%.
- Don't compact mid-task. You lose working context.

### CLAUDE.md & Memory
- CLAUDE.md is persistent project memory. It loads every session.
- Put: project structure, build commands, conventions, constraints, gotchas.
- Don't put: entire file contents, obvious things, rapidly changing info.
- For complex projects, split into AGENTS.md, SOUL.md, LEARNED.md.

### Modes
- **Normal** — Claude asks before edits (default)
- **Auto-Accept** — Claude edits without asking (trusted iteration)
- **Plan** — Research first, then propose plan (complex tasks)
- Use Plan mode when: >3 files, architecture decisions, multiple approaches, unclear requirements.
- Toggle with `Shift+Tab`.

### CLI Shortcuts
| Shortcut | Action |
|----------|--------|
| `Shift+Tab` | Cycle modes (Normal/Auto-Accept/Plan/Delegate) |
| `Ctrl+L` | Clear screen |
| `Ctrl+C` | Cancel generation |
| `Ctrl+B` | Run task in background |
| `Ctrl+T` | Toggle task list (agent teams) |
| `Up/Down` | Prompt history |
| `/compact` | Compact context |
| `/context` | Check context usage |
| `/clear` | Clear conversation |

### Prompting
Good prompts have four parts:
1. **Scope** — What files/area to work in
2. **Context** — Background info Claude needs
3. **Constraints** — What NOT to do
4. **Acceptance criteria** — How to know it's done

Bad: "Add rate limiting"
Good: "In src/auth/, add rate limiting to the login endpoint. We use Express with Redis. Don't change session middleware. Return 429 after 5 failed attempts per IP in 15 min."

### Writing Rules
Rules in CLAUDE.md prevent Claude from going off-track.
- Good: "Always use snake_case for database columns"
- Good: "Run pytest -x after any Python file change"
- Bad: "Write good code"
- Bad: "Be careful"

### Subagents
- Use for: parallel exploration, background tasks, independent research
- Avoid for: single-file reads, tasks needing conversation context
- Press `Ctrl+B` to send tasks to background
- Create custom subagents in `.claude/agents/` (project) or `~/.claude/agents/` (user)

### Hooks
Hooks run scripts on events to automate quality enforcement:
- PreToolUse, PostToolUse, SessionStart, Stop, UserPromptSubmit, PreCompact
- Pro-Workflow ships hooks for edit tracking, quality gates, and learning capture

### Security
- Review permission requests carefully
- Don't auto-approve shell commands you don't understand
- Keep secrets out of CLAUDE.md
- Use `.gitignore` and `.claudeignore` for sensitive files

## Learning Path

**Beginner:** Sessions, CLI shortcuts, context management, modes
**Intermediate:** CLAUDE.md, writing rules, prompting, skills
**Advanced:** Subagents, hooks, MCP, GitHub Actions, Pro-Workflow patterns

## Saving Learnings

When the user runs `/learn save`, capture a lesson from this session.

### Step 1: Identify the Learning

Ask the user what they learned, or extract it from the conversation:

```
Category: <category>
Rule: <one-line description of the correct behavior>
Mistake: <what went wrong>
Correction: <how it was fixed>
```

### Categories
Navigation, Editing, Testing, Git, Quality, Context, Architecture, Performance, Claude-Code, Prompting

### Step 2: Save to JSON

After the user confirms, append the learning to `.claude/data/learnings.json`:

```bash
python3 -c "
import json, os
from datetime import datetime
path = '.claude/data/learnings.json'
os.makedirs(os.path.dirname(path), exist_ok=True)
data = []
if os.path.exists(path):
    with open(path) as f:
        data = json.load(f)
data.append({
    'date': datetime.now().isoformat(),
    'project': os.path.basename(os.getcwd()),
    'category': '<CATEGORY>',
    'rule': '<RULE>',
    'mistake': '<MISTAKE>',
    'correction': '<CORRECTION>',
    'times_applied': 0
})
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
print(f'Saved as learning #{len(data)}')
"
```

### Step 3: Confirm

```
Saved as learning #<id>.
Category: <category>
Rule: <rule>
```

### Auto-Capture via [LEARN] Tags

You can also emit `[LEARN]` blocks in your response, which the Stop hook will auto-capture:

```
[LEARN] Category: Rule text here
Mistake: What went wrong
Correction: How it was fixed
```

## Related Commands

- `/pro-workflow:learn-rule` — Capture a specific correction
- `/pro-workflow:wrap-up` — End-of-session checklist with learning capture
- `/pro-workflow:handoff` — Generate handoff with learnings included

---

**Trigger:** Use when user says "learn", "teach me", "best practices", "how do I use Claude Code", or after making a mistake.
