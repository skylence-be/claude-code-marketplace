#!/usr/bin/env bash
set -euo pipefail

BOLD=$'\033[1m'; RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RESET=$'\033[0m'

CLAUDE_DIR="$HOME/.claude"
CLAUDE_BIN=$(command -v claude 2>/dev/null || true)
SHELL_NAME=$(basename "${SHELL:-bash}")

# Detect install method
INSTALL_METHOD="unknown"
if [ -n "$CLAUDE_BIN" ]; then
    if command -v brew >/dev/null 2>&1 && brew list --formula 2>/dev/null | grep -q "^claude$"; then
        INSTALL_METHOD="brew"
    elif command -v npm >/dev/null 2>&1 && npm list -g @anthropic-ai/claude-code 2>/dev/null | grep -q claude-code; then
        INSTALL_METHOD="npm"
    else
        INSTALL_METHOD="direct"
    fi
fi

# Shell rc files to scan
RC_FILES=()
case "$SHELL_NAME" in
    zsh)  RC_FILES+=("$HOME/.zshrc" "$HOME/.zprofile") ;;
    bash) RC_FILES+=("$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile") ;;
    fish) RC_FILES+=("$HOME/.config/fish/config.fish") ;;
esac

# Collect rc lines that reference claude-specific paths
RC_MATCHES=()
for f in "${RC_FILES[@]}"; do
    [ -f "$f" ] || continue
    while IFS= read -r line; do
        if echo "$line" | grep -qE '\.claude[/"]|anthropic-ai[/-]claude'; then
            RC_MATCHES+=("  $f: $line")
        fi
    done < "$f"
done

# Preflight summary
echo ""
echo "${BOLD}Claude Code Uninstaller${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Shell: $SHELL_NAME"
echo ""
echo "${BOLD}Will remove:${RESET}"
if [ -d "$CLAUDE_DIR" ]; then
    echo "  ${RED}x${RESET} $CLAUDE_DIR  (settings, memory, history, plugins)"
else
    echo "  - $CLAUDE_DIR  (not found)"
fi
if [ -n "$CLAUDE_BIN" ]; then
    echo "  ${RED}x${RESET} $CLAUDE_BIN  (binary, install method: $INSTALL_METHOD)"
else
    echo "  - claude binary  (not found in PATH)"
fi
if [ ${#RC_MATCHES[@]} -gt 0 ]; then
    echo "  ${RED}x${RESET} Shell rc entries referencing claude:"
    printf '%s\n' "${RC_MATCHES[@]}"
else
    echo "  - no shell rc entries referencing claude found"
fi

echo ""
echo "${YELLOW}This cannot be undone.${RESET}"
echo ""
printf "Type %sDELETE%s to confirm, or anything else to cancel: " "${BOLD}" "${RESET}"
read -r CONFIRM

if [ "$CONFIRM" != "DELETE" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""

# Uninstall binary
if [ -n "$CLAUDE_BIN" ]; then
    case "$INSTALL_METHOD" in
        brew)
            echo "Uninstalling via homebrew..."
            brew uninstall claude
            ;;
        npm)
            echo "Uninstalling via npm..."
            npm uninstall -g @anthropic-ai/claude-code
            ;;
        *)
            echo "Removing $CLAUDE_BIN ..."
            rm -f "$CLAUDE_BIN"
            ;;
    esac
    echo "  ${GREEN}done${RESET}"
fi

# Remove ~/.claude
if [ -d "$CLAUDE_DIR" ]; then
    echo "Removing $CLAUDE_DIR ..."
    rm -rf "$CLAUDE_DIR"
    echo "  ${GREEN}done${RESET}"
fi

# Clean shell rc files
for f in "${RC_FILES[@]}"; do
    [ -f "$f" ] || continue
    BEFORE=$(wc -l < "$f")
    TMP=$(mktemp)
    grep -vE '\.claude[/"]|anthropic-ai[/-]claude' "$f" > "$TMP" && mv "$TMP" "$f"
    AFTER=$(wc -l < "$f")
    REMOVED=$(( BEFORE - AFTER ))
    if [ "$REMOVED" -gt 0 ]; then
        echo "  ${GREEN}Removed $REMOVED line(s) from $f${RESET}"
    fi
done

echo ""
echo "${GREEN}${BOLD}Done.${RESET} Restart your terminal to complete cleanup."
echo ""
