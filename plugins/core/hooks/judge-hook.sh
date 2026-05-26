#!/bin/bash
# judge-hook.sh — PreToolUse judge for Claude Code.
#
# Reads stdin JSON ({tool_name, tool_input}), evaluates against a rules file,
# and decides allow / deny / escalate-to-LLM. Implements the LLM-as-judge
# pattern as a Claude Code hook.
#
# Rules file: ~/.claude/judge-rules.json (override with $JUDGE_RULES_FILE).
# If the file is missing or empty, the hook exits 0 silently (no-op).
#
# Per-rule behavior:
#   class=deny     → exit 2 with reason on stdout (Claude Code blocks the call)
#   class=allow    → exit 0 (used for allowlist patterns that override later rules)
#   class=escalate → spawn `claude -p` with judge_prompt; LLM returns ALLOW/BLOCK
#
# The hook fails *open* on infrastructure errors (missing jq, missing claude CLI,
# LLM timeout) — this is a usability tradeoff, not a security guarantee. Use
# `class=deny` rules for anything that must block deterministically.

set -euo pipefail

RULES_FILE="${JUDGE_RULES_FILE:-$HOME/.claude/judge-rules.json}"
LLM_TIMEOUT_SECONDS="${JUDGE_LLM_TIMEOUT:-10}"
LLM_MODEL="${JUDGE_LLM_MODEL:-claude-haiku-4-5-20251001}"

# Missing rules file → no-op (opt-in by file presence).
[ -f "$RULES_FILE" ] || exit 0

# jq is required to iterate rules. Without it, fail open silently.
command -v jq >/dev/null 2>&1 || exit 0

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT_JSON=$(echo "$INPUT" | jq -c '.tool_input // {}')

[ -z "$TOOL_NAME" ] && exit 0

# Evaluate rules in declaration order. First match wins.
RULE_COUNT=$(jq '.rules | length' "$RULES_FILE" 2>/dev/null || echo 0)
[ "$RULE_COUNT" = "0" ] && exit 0

for i in $(seq 0 $((RULE_COUNT - 1))); do
  RULE=$(jq ".rules[$i]" "$RULES_FILE")
  R_TOOL=$(echo "$RULE" | jq -r '.tool // "*"')
  R_PATTERN=$(echo "$RULE" | jq -r '.pattern // ""')
  R_CLASS=$(echo "$RULE" | jq -r '.class // "allow"')
  R_REASON=$(echo "$RULE" | jq -r '.reason // ""')

  # Tool match: exact, or "*" for any.
  if [ "$R_TOOL" != "*" ] && [ "$R_TOOL" != "$TOOL_NAME" ]; then
    continue
  fi

  # Pattern match against tool_input JSON. Empty pattern = match all inputs.
  if [ -n "$R_PATTERN" ]; then
    echo "$TOOL_INPUT_JSON" | grep -qE "$R_PATTERN" || continue
  fi

  case "$R_CLASS" in
    deny)
      echo "judge-hook: blocked — ${R_REASON:-no reason given}"
      exit 2
      ;;
    allow)
      exit 0
      ;;
    escalate)
      JUDGE_PROMPT=$(echo "$RULE" | jq -r '.judge_prompt // ""')
      if [ -z "$JUDGE_PROMPT" ]; then
        # Misconfigured escalate rule — fail open with a warning to stderr.
        echo "judge-hook: escalate rule missing judge_prompt; allowing" >&2
        exit 0
      fi
      # claude CLI required for escalate. Without it, fail open.
      command -v claude >/dev/null 2>&1 || {
        echo "judge-hook: claude CLI not found; escalate rule fails open" >&2
        exit 0
      }

      # Build judge input: prompt + the actual proposal.
      FULL_PROMPT=$(printf '%s\n\nTool: %s\nInput: %s\n\nRespond with exactly one word: ALLOW or BLOCK. Then on a new line, a one-sentence reason.' \
        "$JUDGE_PROMPT" "$TOOL_NAME" "$TOOL_INPUT_JSON")

      # Call the LLM judge with a hard timeout. macOS lacks GNU timeout; use perl.
      DECISION=$(perl -e '
        $SIG{ALRM} = sub { die "timeout\n" };
        alarm $ARGV[0];
        open(my $fh, "-|", "claude", "-p", "--model", $ARGV[1], $ARGV[2]) or die "spawn: $!";
        local $/; my $out = <$fh>; close($fh);
        print $out;
      ' "$LLM_TIMEOUT_SECONDS" "$LLM_MODEL" "$FULL_PROMPT" 2>/dev/null) || {
        echo "judge-hook: LLM judge timed out or failed; allowing" >&2
        exit 0
      }

      VERDICT=$(echo "$DECISION" | head -1 | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')
      LLM_REASON=$(echo "$DECISION" | sed -n '2p')

      if [ "$VERDICT" = "BLOCK" ]; then
        echo "judge-hook: LLM judge blocked — ${LLM_REASON:-no reason given}"
        exit 2
      fi
      # ALLOW or unparseable → allow (fail open on the LLM path).
      exit 0
      ;;
  esac
done

# No rule matched.
exit 0
