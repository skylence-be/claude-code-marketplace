#!/bin/bash
# Blocks Claude from accessing .env files via Read/Edit/Write/Bash/Grep tools.
#
# For Bash commands, the check is quote-aware: .env mentions inside single- or
# double-quoted strings or heredoc bodies are treated as string content, not
# file paths. This prevents false positives on commit messages, echo strings,
# and similar cases. Real file access (cat .env, vim .env, < .env) still blocks.

INPUT=$(cat)
TOOL=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)

is_env_file() {
  local f="$1"
  echo "$f" | grep -qE '(^|/)\.env(\.|$)' || return 1
  # Allow safe templates
  echo "$f" | grep -qE '(^|/)\.env\.(example|sample|dist|template)$' && return 1
  return 0
}

# Quote-aware Bash check, kept as a separate -c script so it does not steal
# stdin from the echo "$INPUT" pipe (heredoc + pipe conflict on python3 stdin).
BASH_CHECK_PY='
import json
import re
import sys

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")
if not cmd:
    print("allow"); sys.exit(0)

# Strip heredoc bodies. Handles optional quoted delimiter and indent (<<-).
cmd = re.sub(
    r"<<-?\s*[\"\x27]?(\w+)[\"\x27]?[^\n]*\n.*?\n\s*\1\s*(?:\n|$)",
    " ",
    cmd,
    flags=re.DOTALL,
)
# Strip double-quoted strings (handle escaped quotes inside).
cmd = re.sub(r"\"(?:\\\\.|[^\"\\\\])*\"", "\"\"", cmd)
# Strip single-quoted strings (bash single quotes have no escapes inside).
cmd = re.sub(r"\x27[^\x27]*\x27", "\x27\x27", cmd)

if not re.search(r"\.env(\b|\.)", cmd):
    print("allow"); sys.exit(0)
if re.search(r"\.env\.(example|sample|dist|template)", cmd):
    print("allow"); sys.exit(0)
print("block")
'

case "$TOOL" in
  Read|Edit|Write|NotebookEdit)
    FILE=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)
    if is_env_file "$FILE"; then
      echo "env-guard: .env file access blocked ($FILE)"
      exit 2
    fi
    ;;
  Grep)
    PATH_ARG=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('path',''))" 2>/dev/null)
    if is_env_file "$PATH_ARG"; then
      echo "env-guard: grep on .env file blocked ($PATH_ARG)"
      exit 2
    fi
    ;;
  Bash)
    VERDICT=$(echo "$INPUT" | python3 -c "$BASH_CHECK_PY" 2>/dev/null)
    if [ "$VERDICT" = "block" ]; then
      echo "env-guard: bash command references .env file — blocked"
      exit 2
    fi
    ;;
esac

exit 0
