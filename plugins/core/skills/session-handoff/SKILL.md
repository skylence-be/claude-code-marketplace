---
name: session-handoff-skill
description: Produce a structured end-of-session handoff (decisions, shipped changes, key files, running state, deferrals, open questions) for /clear. Triggers "session handoff", "wrap up session", "hand off", "handoff summary".
---

# Session Handoff

End-of-session summary for `/clear`. Audience is the next agent, not a stakeholder. Output in chat only.

## Sources to pull from

1. Plan files referenced this session
2. TodoWrite state (in-progress or pending tasks)
3. Background processes started with `run_in_background`; shell IDs matter
4. Files created or modified this session
5. Memory files written or updated
6. Unresolved questions from the conversation

Do NOT grep or `git log` to rediscover state. Synthesize what happened in this session only.

## Output template

```
# Session Handoff — <one-line title>

## Where it started
<2-3 sentences: what was asked, key constraints>

## Decisions locked + what shipped
- <change> — <why, absolute path>

## Key files for next session
- `<absolute path>` — <why read first>
- Plan file: `<path>` (if applicable)
- Memory files touched: `<paths>` (if any)

## Running state
- Background processes: <shell IDs + command + how to kill> — or "none"
- Dev servers: <url:port> — or "none"
- Open worktrees: <paths> — or "none"

## Verification
- `<command>` — <expected outcome>

## Deferred + open questions
- Deferred: <item> — <why>
- Open: <question> — <context>

## Suggested skills
- <skill-name>: <one line on why the next agent should invoke it>

## Pick up here
<1-2 sentences: single most likely next action>
```

## Rules

1. Chat only; never write to a file, never update memory.
2. Never invent state; write "none" for any section or bullet without real content; never omit a section.
3. Absolute paths always.
4. Plan file goes first in "Key files".
5. No emojis, no hype, no retrospectives.
6. Background process IDs must include the kill command.
7. Redact API keys, passwords, and PII; write `[REDACTED]` in place.
8. Don't re-state content already captured in plans, PRDs, ADRs, issues, or diffs; reference by absolute path or URL instead.

## Anti-patterns

- Summarizing only the last few turns
- Relative paths
- Omitting "Running state" because nothing is running; write "none"
- Writing the handoff to a file
- Steps beyond "Pick up here"; the next agent decides
