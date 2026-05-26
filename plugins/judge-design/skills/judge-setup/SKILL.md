---
name: judge-setup
description: "Write judge-layer guidance to ~/.claude/CLAUDE.md. Adds a ## Judge section covering when to proactively invoke the judge-design workflow and the anti-theater rules that make a judge layer real rather than decorative. Triggers: 'judge setup', 'set up judge layer guidance', 'configure claude for judge design', 'add judge section to CLAUDE.md'."
disable-model-invocation: true
---

Configure `~/.claude/CLAUDE.md` with a `## Judge` section. This section tells Claude when to reach for judge-design workflow automatically, and what makes a judge layer work versus what makes it theater.

## Step 1: Backup and strip the ## Judge section

```bash
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
touch "$CLAUDE_MD"

BACKUP="$HOME/.claude/CLAUDE.md.bak.$(date +%Y%m%d-%H%M%S)"
cp "$CLAUDE_MD" "$BACKUP"
echo "Backup: $BACKUP"

awk '
  BEGIN {
    managed["## Judge"] = 1
    in_strip = 0
  }
  $0 in managed { in_strip = 1; next }
  in_strip && /^## / { in_strip = 0 }
  !in_strip { print }
' "$CLAUDE_MD" > "$CLAUDE_MD.tmp" && mv "$CLAUDE_MD.tmp" "$CLAUDE_MD"
```

## Step 2: Append the ## Judge section

```bash
cat >> "$CLAUDE_MD" << 'EOF'

## Judge

Use judge-design workflow before shipping any agent or automation that takes consequential autonomous actions. Design gate before agent goes live.

### When to invoke the workflow

If agent can do any of following without human in the loop, run workflow first:

- Merge PRs or push to protected branches
- Deploy or restart services
- Run DB migrations or write to production databases
- Send external messages (Slack, email, webhooks, SMS)
- Spend money or authorize purchases
- Change infrastructure, permissions, or access controls

Chain: `judge-design:action-surface-audit-skill` to map action surface, then `judge-design:judge-criteria-skill` to design criteria and structured proposal format actor must submit, then `judge-design:judge-prompt-writer-skill` to produce judge system prompt, then `judge-design:judge-eval-suite-skill` to validate it. Before scaling (more actions, more agents, higher stakes), run `judge-design:judge-architecture-review-skill`.

### Anti-theater rules

Judge that looks like control layer but catches nothing is worse than no judge. It adds latency, creates false confidence, and delays finding real gap.

**Different failure modes, or it does not count.** Actor and judge using same model, same prompt context, and same reasoning style will share same blind spots. They fail on same inputs. Use different prompt with tighter criteria for judge. Smaller, cheaper model (Haiku is runtime default in `judge-hook.sh`) often diverges usefully from actor. Goal is not a second opinion from a copy of yourself.

**No eval suite, no deployment.** Run `judge-design:judge-eval-suite-skill` before any judge goes live. Suite must cover all four outcomes: allow, block, revise, escalate. Weight toward mundane boundary failures (one step too far, authorization scope creep, stale evidence) rather than adversarial red-team. Judge with no passing eval suite is another model call, not a control layer.

**Hard blocks need deterministic rules.** LLM judges fail open on infra errors, timeouts, and ambiguous inputs. Anything that must block reliably belongs in `~/.claude/judge-rules.json` as a `class=deny` rule, enforced by `judge-hook.sh` PreToolUse hook from `core` plugin. Design skills define what those rules should contain and verify they actually fire.

**Judge that never blocks in testing is not working; it is unconfigured.** Verify during eval that block and revise cases are caught. If every test case returns ALLOW, criteria are too loose or judge is ignoring proposal format.

EOF

echo "CLAUDE.md updated. Backup: $BACKUP"
```

## Step 3: Summary

```
Judge Setup
-----------------------------------------
CLAUDE.md section written:
  Judge (when to invoke + anti-theater)   done
Backup: ~/.claude/CLAUDE.md.bak.<timestamp>

Covered in the ## Judge section:
  Trigger conditions (PR merge, deploy,
  DB writes, external messages, money,
  infra/permissions)                       yes
  Workflow chain (audit -> criteria ->
  prompt -> eval -> architecture review)   yes
  Different failure modes rule             yes
  Eval suite required before deploy        yes
  Deterministic rules via judge-hook.sh    yes
  Judge-never-blocks = unconfigured        yes
```

Review `~/.claude/judge-rules.json` if you have `core` plugin's `judge-hook.sh` installed. Hook fails open on infrastructure errors; deterministic deny rules are hard boundary.
