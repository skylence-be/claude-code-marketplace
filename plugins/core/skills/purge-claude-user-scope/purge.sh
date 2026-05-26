#!/usr/bin/env bash
set -euo pipefail

BOLD=$'\033[1m'; RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RESET=$'\033[0m'

CLAUDE_DIR="$HOME/.claude"
CLAUDE_BIN=$(command -v claude 2>/dev/null || true)

# Preflight summary
echo ""
echo "${BOLD}Claude Code User-Scope Purge${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "${BOLD}Will remove:${RESET}"
if [ -d "$CLAUDE_DIR" ]; then
    DIR_SIZE=$(du -sh "$CLAUDE_DIR" 2>/dev/null | cut -f1 || echo "?")
    echo "  ${RED}x${RESET} $CLAUDE_DIR  ($DIR_SIZE: settings, memory, plugins, hooks, sessions, history)"
else
    echo "  - $CLAUDE_DIR  (not found, nothing to purge)"
fi
echo ""
echo "${BOLD}Will keep:${RESET}"
if [ -n "$CLAUDE_BIN" ]; then
    echo "  ${GREEN}✓${RESET} $CLAUDE_BIN  (binary stays installed)"
else
    echo "  ${GREEN}✓${RESET} claude binary  (not in PATH, not touched either way)"
fi
echo "  ${GREEN}✓${RESET} shell rc files  (not touched)"

if [ ! -d "$CLAUDE_DIR" ]; then
    echo ""
    echo "Nothing to do."
    exit 0
fi

echo ""
echo "${YELLOW}This cannot be undone. The binary remains; only user-scope state is wiped.${RESET}"
echo ""
printf "Type %sPURGE%s to confirm, or anything else to cancel: " "${BOLD}" "${RESET}"
read -r CONFIRM

if [ "$CONFIRM" != "PURGE" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Removing $CLAUDE_DIR ..."
rm -rf "$CLAUDE_DIR"
echo "  ${GREEN}done${RESET}"

echo ""
echo "${GREEN}${BOLD}Done.${RESET} User-scope state purged. The claude binary is still installed. Next launch starts fresh."
echo ""
