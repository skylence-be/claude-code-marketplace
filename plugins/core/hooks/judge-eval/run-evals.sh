#!/bin/bash
# run-evals.sh — runs each fixture through judge-hook.sh and asserts the
# resulting exit code matches the fixture's _expected_exit field.
#
# Usage:
#   ./run-evals.sh                    # regex cases only
#   RUN_LLM_EVALS=1 ./run-evals.sh    # also run escalate cases (costs money)
#   ./run-evals.sh fixtures/foo.json  # run a single fixture

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/../judge-hook.sh"
RULES="$SCRIPT_DIR/../judge-rules.example.json"

[ -x "$HOOK" ] || { echo "FATAL: $HOOK not found or not executable"; exit 1; }
[ -f "$RULES" ] || { echo "FATAL: $RULES not found"; exit 1; }

if [ $# -gt 0 ]; then
  FIXTURES=("$@")
else
  FIXTURES=("$SCRIPT_DIR"/fixtures/*.json)
fi

pass=0
fail=0
skip=0

for fixture in "${FIXTURES[@]}"; do
  [ -f "$fixture" ] || continue

  name=$(basename "$fixture" .json)
  expected=$(jq -r '._expected_exit // 0' "$fixture")
  is_llm=$(jq -r '._requires_llm // false' "$fixture")
  description=$(jq -r '._description // ""' "$fixture")

  if [ "$is_llm" = "true" ] && [ "${RUN_LLM_EVALS:-0}" != "1" ]; then
    printf "SKIP  %-40s  (LLM eval; set RUN_LLM_EVALS=1)\n" "$name"
    skip=$((skip + 1))
    continue
  fi

  # Strip _-prefixed meta keys before piping.
  payload=$(jq 'with_entries(select(.key | startswith("_") | not))' "$fixture")

  # Run the hook with the example rules file.
  output=$(JUDGE_RULES_FILE="$RULES" echo "$payload" | JUDGE_RULES_FILE="$RULES" "$HOOK" 2>&1)
  actual=$?

  if [ "$actual" = "$expected" ]; then
    printf "PASS  %-40s  %s\n" "$name" "$description"
    pass=$((pass + 1))
  else
    printf "FAIL  %-40s  expected exit %s, got %s\n" "$name" "$expected" "$actual"
    [ -n "$output" ] && printf "        output: %s\n" "$output"
    fail=$((fail + 1))
  fi
done

echo
echo "results: $pass pass, $fail fail, $skip skip"
[ "$fail" = "0" ]
