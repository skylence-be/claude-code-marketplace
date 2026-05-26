#!/bin/bash
# Claude Code SessionStart hook — injects context based on env var config
# Set vars in ~/.zshrc; see .env.example for full template

CONTEXT=""

# Advisor (default: enabled)
if [ "${DISABLE_ADVISOR:-0}" = "1" ]; then
    CONTEXT="${CONTEXT}Advisor is DISABLED (DISABLE_ADVISOR=1). Do not call advisor() under any circumstances. "
fi


[ -z "$CONTEXT" ] && exit 0

CONTEXT_JSON=$(printf '%s' "$CONTEXT" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))")
echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":$CONTEXT_JSON}}"
