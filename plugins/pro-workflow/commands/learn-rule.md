---
description: Capture a correction or lesson as a persistent rule in learnings.json
model: claude-sonnet-4-5
---

# /learn-rule — Extract Correction to Memory

Capture a lesson from this session into persistent memory.

$ARGUMENTS

## Process

### 1. Identify the Lesson

- What mistake was made?
- What should happen instead?

### 2. Format the Rule

```
[LEARN] Category: One-line rule
```

**Categories:**
- **Navigation** — file paths, finding code
- **Editing** — code changes, patterns
- **Testing** — test approaches
- **Git** — commits, branches
- **Quality** — lint, types, style
- **Context** — when to clarify
- **Architecture** — design decisions
- **Performance** — optimization
- **Claude-Code** — sessions, modes, CLAUDE.md, skills, subagents, hooks, MCP
- **Prompting** — scope, constraints, acceptance criteria

### 3. Save to Learnings

After user confirms, append the learning to `.claude/data/learnings.json`:

```bash
# Read existing learnings, append new entry, write back
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

Replace `<CATEGORY>`, `<RULE>`, `<MISTAKE>`, `<CORRECTION>` with actual values.

### 4. Confirm to User

```
Saved as learning #<id>.
Category: <category>
Rule: <rule>
```

## Example

```
Recent mistake: Edited wrong utils.ts file (there were two with the same name)

[LEARN] Navigation: Confirm full path when multiple files share a name.

Add to learnings? (y/n)
→ Saved as learning #7
```

## Claude Code Examples

```
[LEARN] Claude-Code: Use plan mode before multi-file changes.
[LEARN] Claude-Code: Compact context at task boundaries, not mid-work.
[LEARN] Prompting: Always include acceptance criteria in prompts.
[LEARN] Testing: Run tests after every code change, not just at the end.
```

---

**Trigger:** Use when user says "remember this", "add to rules", "learn this", or after making a mistake that should not recur.
