#!/bin/bash
# env-guard-tests.sh — regression tests for env-guard.sh.
#
# Run from the repo:
#   ./hooks/env-guard-tests.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/env-guard.sh"

[ -x "$HOOK" ] || { echo "FATAL: $HOOK not found or not executable"; exit 1; }

pass=0
fail=0

test_case() {
  local name="$1" expected="$2" input="$3"
  local out actual
  out=$(echo "$input" | bash "$HOOK" 2>&1)
  actual=$?
  if [ "$actual" = "$expected" ]; then
    printf "PASS  %-45s  exit=%s\n" "$name" "$actual"
    pass=$((pass + 1))
  else
    printf "FAIL  %-45s  expected=%s got=%s output=%s\n" "$name" "$expected" "$actual" "$out"
    fail=$((fail + 1))
  fi
}

# --- Bash branch: real file access blocks (exit 2) ---
test_case "cat secret file"         2 '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}'
test_case "vim secret file"         2 '{"tool_name":"Bash","tool_input":{"command":"vim .env"}}'
test_case "cat path/secret"         2 '{"tool_name":"Bash","tool_input":{"command":"cat /tmp/foo/.env"}}'
test_case "redirect from secret"    2 '{"tool_name":"Bash","tool_input":{"command":"cat < .env"}}'
test_case "tee into secret"         2 '{"tool_name":"Bash","tool_input":{"command":"echo X | tee .env"}}'

# --- Bash branch: safe templates allow (exit 0) ---
test_case "example template"        0 '{"tool_name":"Bash","tool_input":{"command":"cat .env.example"}}'
test_case "sample template"         0 '{"tool_name":"Bash","tool_input":{"command":"cat .env.sample"}}'

# --- Bash branch: mentions inside quotes allow (the bug being fixed) ---
test_case "double-quoted commit -m" 0 '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"docs: write .env handler\""}}'
test_case "single-quoted echo"      0 "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"echo 'set .env var'\"}}"
test_case "heredoc commit body"     0 '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"$(cat <<EOF\nfix: .env handler\nEOF\n)\""}}'

# --- Bash branch: unrelated commands allow ---
test_case "plain ls"                0 '{"tool_name":"Bash","tool_input":{"command":"ls /tmp"}}'
test_case "git status"              0 '{"tool_name":"Bash","tool_input":{"command":"git status"}}'

# --- File-tool branches still work ---
test_case "Read secret via tool"    2 '{"tool_name":"Read","tool_input":{"file_path":"/tmp/.env"}}'
test_case "Read template via tool"  0 '{"tool_name":"Read","tool_input":{"file_path":"/tmp/.env.example"}}'
test_case "Write secret via tool"   2 '{"tool_name":"Write","tool_input":{"file_path":"/x/.env","content":"k=v"}}'
test_case "Edit secret via tool"    2 '{"tool_name":"Edit","tool_input":{"file_path":"/x/.env","old_string":"a","new_string":"b"}}'
test_case "Grep on secret dir"      2 '{"tool_name":"Grep","tool_input":{"path":"/x/.env"}}'

echo
echo "results: $pass pass, $fail fail"
[ "$fail" = "0" ]
