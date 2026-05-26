#!/bin/bash
# writing-guard.sh — PostToolUse hook (Write|Edit) that flags AI writing tells in
# artifact content. Fires when Claude writes a file (HTML, Markdown, code with doc
# lines, etc.), not on terminal chat. The CLAUDE.md ## Writing Guidelines layer is
# the primary prevention; this hook is a safety net for what slips through into
# committed artifacts.

set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Write tool uses .content; Edit tool uses .new_string.
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')

[ -z "$FILE_PATH" ] && exit 0
[ -z "$CONTENT" ] && exit 0

# Skip data, config, lock, and binary files where these checks are pure noise.
case "$FILE_PATH" in
  *.json|*.jsonc|*.yaml|*.yml|*.toml|*.xml|*.csv|*.tsv|*.lock|*.lockb|*.lockfile|*.sum|*.mod|*.svg|*.map|*.min.js|*.min.css) exit 0 ;;
  *.png|*.jpg|*.jpeg|*.gif|*.webp|*.ico|*.pdf|*.zip|*.gz|*.tar|*.docx|*.xlsx|*.pptx|*.doc|*.xls|*.ppt|*.key|*.numbers|*.pages) exit 0 ;;
esac

# Identify prose files for the full vocab/phrase scan. Other files (code, configs)
# only get the strict em-dash check, since vocab/phrase regex on identifiers and
# strings is too noisy.
case "$FILE_PATH" in
  *.md|*.mdx|*.markdown|*.html|*.htm|*.txt|*.rst|*.adoc|*.tex|*.rtf) IS_PROSE=1 ;;
  *) IS_PROSE=0 ;;
esac

# Strip code blocks and inline code so quoted code in prose doesn't trip the regex.
STRIPPED=$(echo "$CONTENT" | awk '
  /^```/ { in_code = !in_code; next }
  !in_code { print }
' | sed 's/`[^`]*`//g')

VIOLATIONS=""

# Em dashes: zero allowed everywhere.
EM_COUNT=$(echo "$STRIPPED" | grep -o '—' | wc -l | tr -d ' ')
if [ "$EM_COUNT" -gt 0 ]; then
  VIOLATIONS="${VIOLATIONS}- Em dashes: ${EM_COUNT} found (zero allowed)\n"
fi

# Vocab + phrase checks only on prose files, and only when the content is
# substantial enough that the rule matters.
if [ "$IS_PROSE" -eq 1 ]; then
  WORD_COUNT=$(echo "$STRIPPED" | wc -w | tr -d ' ')
  if [ "$WORD_COUNT" -ge 150 ]; then
    BANNED='delve|tapestry|pivotal|testament|meticulous|nuanced|multifaceted|embark|spearhead|bolster|garner|interplay|nestled|bustling|vibrant|comprehensive|invaluable|reimagine|empower|groundbreaking|transformative|paramount|myriad|cornerstone|catalyst|seamless|seamlessly'
    FOUND=$(echo "$STRIPPED" | grep -oiE "\b(${BANNED})\b" 2>/dev/null | sort -fu | tr '\n' ',' | sed 's/,$//' || true)
    [ -n "$FOUND" ] && VIOLATIONS="${VIOLATIONS}- Banned AI vocabulary: ${FOUND}\n"

    PHRASES='great question!|certainly!|absolutely!|i hope this helps|let'\''s dive in|without further ado|it'\''s worth noting that|in conclusion,|in summary,'
    FOUND_PH=$(echo "$STRIPPED" | grep -oiE "(${PHRASES})" 2>/dev/null | sort -fu | tr '\n' ' / ' | sed 's, / $,,' || true)
    [ -n "$FOUND_PH" ] && VIOLATIONS="${VIOLATIONS}- AI phrases: ${FOUND_PH}\n"
  fi
fi

[ -z "$VIOLATIONS" ] && exit 0

REASON=$(printf "Wrote to %s but content violates ## Writing Guidelines (~/.claude/CLAUDE.md):\n\n%b\nEdit the file to remove these tells. Do not acknowledge or apologize, just produce a corrected version." "$FILE_PATH" "$VIOLATIONS")

jq -n --arg reason "$REASON" '{decision: "block", reason: $reason}'
