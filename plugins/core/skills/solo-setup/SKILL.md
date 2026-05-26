---
name: solo-setup
description: Write Solo-aware guidance to ~/.claude/CLAUDE.md. Adds standard XVE sections (Advisor, Coding Guidelines, Writing Guidelines, etc.) plus a Solo section covering solo-session-handoff, scratchpad use, and todo coordination. Triggers: 'solo setup', 'set up soloterm', 'configure claude for solo'.
disable-model-invocation: true
---

Configure `~/.claude/CLAUDE.md` for SoloTerm. Writes standard guidance sections plus Solo-specific block. Optionally installs safety hooks (judge-hook + writing-guard) and OS notification hooks.

## Step 1: Backup and strip managed sections

```bash
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
touch "$CLAUDE_MD"

BACKUP="$HOME/.claude/CLAUDE.md.bak.$(date +%Y%m%d-%H%M%S)"
cp "$CLAUDE_MD" "$BACKUP"
echo "Backup: $BACKUP"

awk '
  BEGIN {
    managed["## Advisor"] = 1
    managed["## Model Delegation"] = 1
    managed["## Verify Before Asserting"] = 1
    managed["## Perspectives"] = 1
    managed["## Delegating to Agents"] = 1
    managed["## LLM Council"] = 1
    managed["## Decisive Thinking"] = 1
    managed["## Coding Guidelines"] = 1
    managed["## Review Mindset"] = 1
    managed["## Writing Guidelines"] = 1
    managed["## Solo"] = 1
    in_strip = 0
  }
  $0 in managed { in_strip = 1; next }
  in_strip && /^## / { in_strip = 0 }
  !in_strip { print }
' "$CLAUDE_MD" > "$CLAUDE_MD.tmp" && mv "$CLAUDE_MD.tmp" "$CLAUDE_MD"
```

## Step 2: Install judge-hook (opt-in)

Ask the user:

> "Install judge-hook? Wires two hooks:
> - **judge-hook** (PreToolUse): pattern-matches risky commands against `~/.claude/judge-rules.json`; can escalate ambiguous patterns to a Haiku LLM call. `.env` file blocking is handled here via rules; no separate env-guard script needed.
> - **writing-guard** (PostToolUse on Write/Edit): flags AI writing tells in artifact content; blocks and asks Claude to revise.
>
> Requires `jq`. Rules file created from example if not present.
>
> Install? [y/N]"

Default to **No**. If yes:

```bash
SETTINGS="$HOME/.claude/settings.json"
PLUGIN_HOOKS="${CLAUDE_PLUGIN_ROOT}/hooks"

# 1. Copy scripts
cp "$PLUGIN_HOOKS/writing-guard.sh" ~/.claude/writing-guard.sh && chmod +x ~/.claude/writing-guard.sh
cp "$PLUGIN_HOOKS/judge-hook.sh"    ~/.claude/judge-hook.sh   && chmod +x ~/.claude/judge-hook.sh

# 2. Rules file: don't clobber an existing one
if [ ! -f ~/.claude/judge-rules.json ]; then
  cp "$PLUGIN_HOOKS/judge-rules.example.json" ~/.claude/judge-rules.json
  echo "Wrote ~/.claude/judge-rules.json from example. Review and customize before relying on it."
else
  echo "~/.claude/judge-rules.json already exists: left untouched."
fi

# 3. Wire into settings.json (idempotent)

# writing-guard: PostToolUse on Write|Edit
if ! jq -e '.hooks.PostToolUse // [] | map(.hooks // [] | map(.command // "")) | flatten | any(contains("writing-guard.sh"))' "$SETTINGS" >/dev/null 2>&1; then
  jq '.hooks //= {} | .hooks.PostToolUse //= [] | .hooks.PostToolUse += [{
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "bash ~/.claude/writing-guard.sh"}]
  }]' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
  echo "writing-guard wired."
fi

# judge-hook: PreToolUse (covers env-guard-style blocking via rules)
if ! jq -e '.hooks.PreToolUse // [] | map(.hooks // [] | map(.command // "")) | flatten | any(contains("judge-hook.sh"))' "$SETTINGS" >/dev/null 2>&1; then
  jq '.hooks //= {} | .hooks.PreToolUse //= [] | .hooks.PreToolUse += [{
    "matcher": "Bash|Write|Edit|NotebookEdit|mcp__",
    "hooks": [{"type": "command", "command": "bash ~/.claude/judge-hook.sh", "statusMessage": "Judging tool call..."}]
  }]' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
  echo "judge-hook wired."
fi
```

Then ask:

> "Set `defaultMode` to `bypassPermissions`? With judge-hook active the hook is the safety gate; per-call prompts add friction without adding protection. [Y/n]"

If yes:
```bash
jq '.permissions.defaultMode = "bypassPermissions"' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
echo "defaultMode set to bypassPermissions."
```

Tell the user to review `~/.claude/judge-rules.json` before the next session; the example ships `.env` blocking rules but they should add any environment-specific deny patterns. Restart Claude Code for hooks to take effect.

---

## Step 3: Install notification hooks (opt-in)

Ask the user:

> "Install OS notification hooks? Fires native desktop notifications on key lifecycle events so you can step away during long runs:
> - **PreCompact**: context window about to compact
> - **PostCompact**: compaction done, context reset
> - **Stop**: Claude finished a turn (can be noisy; disable if unwanted)
> - **StopFailure**: Claude stopped due to an API error
> - **TeammateIdle**: a teammate agent is going idle
> - **Notification** (idle_prompt only): Claude has gone idle and is waiting for input
>
> Works on macOS (osascript), Windows (PowerShell NotifyIcon), and Linux (notify-send). Requires `jq`.
>
> Install? [Y/n]"

If yes:

```bash
SETTINGS="$HOME/.claude/settings.json"
PLUGIN_HOOKS="${CLAUDE_PLUGIN_ROOT}/hooks"

cp "$PLUGIN_HOOKS/notify.sh" ~/.claude/notify.sh && chmod +x ~/.claude/notify.sh

if jq -e '
  [.hooks // {} | to_entries[] | .value[] | .hooks // [] | .[] | .command // ""]
  | flatten | any(contains("notify.sh"))
' "$SETTINGS" >/dev/null 2>&1; then
  echo "notify.sh already wired: skipping."
else
  jq '
    .hooks //= {}
    | .hooks.PreCompact //= []
    | .hooks.PreCompact += [{"hooks": [{"type": "command", "command": "bash ~/.claude/notify.sh"}]}]
    | .hooks.PostCompact //= []
    | .hooks.PostCompact += [{"hooks": [{"type": "command", "command": "bash ~/.claude/notify.sh"}]}]
    | .hooks.Stop //= []
    | .hooks.Stop += [{"hooks": [{"type": "command", "command": "bash ~/.claude/notify.sh"}]}]
    | .hooks.StopFailure //= []
    | .hooks.StopFailure += [{"hooks": [{"type": "command", "command": "bash ~/.claude/notify.sh"}]}]
    | .hooks.TeammateIdle //= []
    | .hooks.TeammateIdle += [{"hooks": [{"type": "command", "command": "bash ~/.claude/notify.sh"}]}]
    | .hooks.Notification //= []
    | .hooks.Notification += [{"matcher": "idle_prompt", "hooks": [{"type": "command", "command": "bash ~/.claude/notify.sh"}]}]
  ' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
  echo "Notification hooks wired (6 events)."
fi
```

If Stop is too noisy after install, remove the `.hooks.Stop` entry from `~/.claude/settings.json`. Restart Claude Code for hooks to take effect.

---

## Step 4: Append standard sections

```bash
cat >> "$CLAUDE_MD" << 'EOF'

## Advisor

Call advisor() BEFORE substantive work: before writing, before committing to an approach. Reading files to orient is fine first.

Also call when:
- Stuck (errors recurring, approach not converging)
- Changing approach
- Task complete: but first make deliverables durable (write file, commit)

Skip when:
- You are already running as Opus; advisor() would be Opus consulting itself.
- This turn immediately follows a completed /plan session; the plan output already serves as the advisor input.

On longer tasks: once before committing to approach, once before declaring done. Don't call after every step: advisor adds most value before the approach crystallizes.

Give advice serious weight. If data and advice conflict, don't silently switch: make one more advisor call: "I found X, you suggest Y, which breaks the tie?"

## Model Delegation

When running as Opus, act as orchestrator. Match each subtask to cheapest model that can do it well; keep expensive reasoning where it pays off.

- Opus (you): planning, architecture, ambiguous or high-stakes decisions, reviewing risky changes, final verification. Keep on main thread.
- Sonnet: most implementation, well-specified coding, refactors, research, writing. Spawn Sonnet subagents for sizable implementation; run independent pieces in parallel.
- Haiku: mechanical, deterministic work with clear spec. Renames, formatting, simple lookups, file moves, boilerplate.

Don't burn Opus on grunt work cheaper model handles. Don't push judgment-heavy decisions onto model that will miss what matters. Plan, review, verify on main thread; delegate doing.

## Verify Before Asserting

When about to state or act on load-bearing factual claim while hedging (may, might, probably, likely, I think, should be), treat hedge as signal to verify, not ship. Confirm before you assert:

- Read actual source: code, file, config, API response.
- Run it: reproduce behavior rather than predict it.
- Search web (WebSearch / WebFetch) for anything outside codebase: library behavior, error text, version specifics.

State what you verified and how. If you genuinely can't confirm, say so and label it guess; don't dress hunch as fact. Hedging is fine for real uncertainty you've named, not as substitute for checking.

## Perspectives

Hold two perspectives the developer in front of you won't voice.

**The end user.** Build for the human who uses the end product, not for developer convenience. Optimize for their experience, correctness, and safety. Don't ship shortcuts that only ease the current task (quick-and-dirty SQL, skipped edge cases, convenience hacks) unless the developer explicitly asks for them.

**The attacker.** Review your own changes like a penetration tester: assume hostile input on every field, header, cookie, param, and upload; re-authorize at every trust boundary; write the abuse case before the feature. Highest-leverage checks:
- Access control: every endpoint and object reference verifies this user owns this resource, not just that they're logged in (IDOR/BOLA). Swap an ID, expect 403.
- Injection: trace every user value to its sink (SQL, shell, template, HTML); parameterize queries, encode output.
- Auth and sessions: tokens invalidated on logout, strong password hashing (bcrypt/argon2), reject JWT alg:none, lockout on repeated failures.
- Mass assignment: allowlist bindable fields; role, isAdmin, price, balance are never client-settable.
- Secrets and crypto: no hardcoded keys/tokens, TLS everywhere, no MD5/SHA1 for passwords, no sensitive data in client storage.
- Supply chain: run npm audit / pip-audit / bundle audit in CI, commit lockfiles, use npm ci, watch for typosquatting.

This mindset is for hardening your own product; don't write exploit code against third-party systems. Reference: OWASP Top 10 and API Security Top 10.

## Delegating to Agents

When delegating to subagents (especially parallel agents in git worktrees), the orchestrator owns prevention and verification. Executors fail less when the brief is tight and the result is checked.

Brief each task as a contract:
- Objective, exact files and interfaces, and explicit out-of-scope list.
- A runnable acceptance check (test, lint, or build command) the agent must pass.
- Forbid scope creep: if a change beyond scope seems needed, STOP and report, don't do it.

Require proof, not claims:
- Agent returns the diff and what it changed, not "done".
- Don't gate each returned task on a full build/test/lint. With Rust and cargo that per-task compile cost is brutal. Run the full build, tests, and lint once at the end of a feature, not after every delegated task.
- Review the diff against the spec in a fresh pass; flag correctness gaps only. A reviewer told to "find problems" invents them.

Worktree hygiene:
- Be deliberate about each worktree's base. `worktree.baseRef` in settings.json defaults to `"fresh"` (branch from `origin/HEAD`); set `"head"` only when an agent must build on unpushed local commits. Fetch first so the base is current; a stale base means conflicts before a line is written.
- One file or bounded area per agent. If two tasks' `git diff --name-only` share any file, serialize them.
- Sequential-only: schema migrations, shared config/types/routes, lockfiles. Lockfile owned by one agent or regenerated after merge.
- Rebase remaining worktrees after each merge. Integrate multi-agent work on a staging branch and run the full lint/test suite there once, at feature end, rather than gating every branch.
- Propagate gitignored files agents need (e.g. `.env`) via a `.worktreeinclude` file (gitignore syntax); Claude Code copies them into each new worktree. Assign distinct ports, use relative build-cache paths, clean artifacts before rebuild.

## LLM Council

Use `council this` when the cost of a bad call is high and there are real tradeoffs between options.

Good fit:
- Genuine uncertainty with meaningful options (architecture choices, hiring, pricing, strategy)
- Decision you keep going back and forth on

Not a good fit:
- Factual lookups: just ask directly
- Creation tasks (write a tweet, summarise this)
- Already decided: don't run council to validate

## Decisive Thinking

When deciding how to approach a problem, choose an approach and commit to it.
Avoid revisiting decisions unless you encounter new information that directly
contradicts your reasoning. If weighing two approaches, pick one and see it
through: you can course-correct later if it fails.

Thinking adds latency and should only be used when it will meaningfully
improve answer quality. When in doubt, respond directly.

State conclusions, not deliberation. If you reconsider, do it once and move
on: don't loop. If you catch yourself revisiting the same decision a second
time, call advisor() before continuing rather than spiraling further.

## Coding Guidelines

### Think Before Coding
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them: don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### Simplicity First
- Minimum code that solves the problem. No speculative features.
- No abstractions for single-use code, no unrequested "flexibility".
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### Surgical Changes
- Touch only what the request requires. Don't improve adjacent code.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it: don't delete it.
- Every changed line should trace directly to the user's request.

### Goal-Driven Execution
- Transform tasks into verifiable goals before starting.
- For multi-step tasks, state a brief plan with verification steps.
- Define success criteria upfront so you can loop independently.

## Review Mindset

Treat every output: code, prose, decisions: as if a senior engineer will review it line by line and catch sloppy work. Not a hypothetical: assume it.

This isn't about being defensive or hedging. It's about the bar: would this hold up under scrutiny by someone who knows the domain better than you? If not, fix it before shipping.

## Writing Guidelines

Write like a human, not a language model. These rules apply to all output: responses, docs, messages, anything.

**Banned vocabulary (never use):** delve, tapestry, landscape (abstract), pivotal, underscore (verb), testament, meticulous, nuanced, multifaceted, embark, spearhead, bolster, garner, realm, robust, seamless, groundbreaking, transformative, paramount, myriad, cornerstone, catalyst, nestled, bustling, vibrant, comprehensive, invaluable, reimagine, empower.

**Structural tells to avoid:**
- Em dashes as a stylistic habit: use commas, periods, or parentheses instead. Max one per 500 words.
- Parallel negation: "Not X, but Y" → just state the positive.
- Rule of three: forcing ideas into trios. Pick one or two.
- Inflation of importance: "pivotal moment", "testament to", "crucial development" → delete. State facts.
- Signposting: "Let's dive in", "Here's what you need to know" → drop it, start with the substance.
- Neat endings on every paragraph → let some thoughts just stop.
- Sycophantic openers: "Great question!", "Certainly!" → cut entirely.

**Always do:**
- Vary sentence length. Short. Then a longer one. Then a fragment. AI writes at a steady rhythm; don't.
- Have opinions. Remove "it could be argued" and say the thing.
- Use specific details: numbers, names, dates: over vague claims.
- Start some sentences with "And" or "But."
- Don't dumb it down. "Human" isn't "simplistic."

## Solo

This machine runs SoloTerm. Use Solo MCP tools for cross-session state, todos, and agent coordination.

### Planning to delegation (Opus)

When you plan on Opus in Solo project, persist plan and work breakdown so cheaper models can execute it:

1. Write plan to scratchpad named with `PRD:` prefix, e.g. `scratchpad_write("PRD: checkout refactor", content)`.
2. Break work into todos via `todo_create` (Solo MCP), one per delegatable unit.
3. In PRD, annotate each todo with its delegation target: which model (Sonnet for implementation, Haiku for mechanical work), whether it goes to its own agent or is batched with others into one agent, and which todos run in parallel versus must be sequential.
4. Hand off with minimal instruction: tell agent to follow todos in `PRD: <name>`. It reads todos and executes; it does not need your full reasoning, only breakdown.

Keep planning, review, and final verification on Opus main thread. PRD scratchpad plus todo list is contract between you and executing agents.

### Deferred and out of scope

Keep one standing scratchpad per project for work cut from scope or pushed to later, named with `DEFERRED:` prefix (e.g. `DEFERRED: <project>`). When planning, append anything you defer there with date and source PRD, so nothing is lost. Check it at start of planning. Never delete or archive this scratchpad; it is the running backlog.

### Handoffs

Use `core:solo-session-handoff` when ending session or handing off to another agent. Skill:
1. Calls `whoami()` to verify Solo MCP server reachable.
2. If online: writes scratchpad with session state, open todos, suggested skills, and pick-up notes.
3. If offline: falls back to `core:session-handoff` (chat-only summary for /clear).

### When to use what

| Need | Tool |
|---|---|
| Persist notes for next session | `scratchpad_write` / `scratchpad_append` |
| Shared task list | `todo_create` / `todo_list` |
| Mark work done | `todo_complete` |
| Prevent concurrent writes | `lock_acquire` / `lock_release` |
| In-conversation tracking only | TaskCreate (not Solo) |

### Scratchpad discipline

- Include `## Handoff` section when writing pick-up notes.
- Include `## Suggested skills` list naming skills next agent should invoke.
- Reference existing plans, PRDs, or diffs by absolute path; don't restate them inline.
- Redact API keys, passwords, and PII; write `[REDACTED]` in place.
EOF

echo "CLAUDE.md updated. Backup: $BACKUP"
```

## Step 5: Summary

```
Solo Setup
──────────────────────────────
CLAUDE.md sections written:
  Advisor                  ✓
  LLM Council              ✓
  Decisive Thinking        ✓
  Coding Guidelines        ✓
  Review Mindset           ✓
  Writing Guidelines       ✓
  Solo (SoloTerm)          ✓
Backup: ~/.claude/CLAUDE.md.bak.<timestamp>

Safety hooks:
  writing-guard.sh         ✓ / ✗ skipped
  judge-hook.sh            ✓ / ✗ skipped  (covers .env blocking via rules)
  judge-rules.json         ✓ created / already existed / ✗ skipped
  defaultMode              bypassPermissions / unchanged

Notification hooks:
  notify.sh (6 events)     ✓ / ✗ skipped
```

Restart Claude Code for any hook changes to take effect.
