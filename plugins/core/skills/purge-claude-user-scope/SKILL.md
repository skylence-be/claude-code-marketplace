---
name: purge-claude-user-scope-skill
description: Wipe all Claude Code user-scope files (~/.claude) while leaving the claude binary installed. Less destructive than uninstall.
disable-model-invocation: true
---

Purge Claude Code user-scope state from this machine. This removes `~/.claude/` (settings, memory, plugins, hooks, sessions, history) but leaves the `claude` binary installed and shell rc untouched. To also remove the binary, use the uninstall-claude skill instead.

## Step 1: Detect platform

```bash
uname -s 2>/dev/null || echo "Windows"
```

## Step 2: Run the purge

**macOS / Linux** (`uname` returns Darwin or Linux):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/purge-claude-user-scope/purge.sh"
```

**Windows** (`uname` not found, or running in PowerShell):

```powershell
& "${env:CLAUDE_PLUGIN_ROOT}\skills\purge-claude-user-scope\purge.ps1"
```

Script handles everything: preflight summary, confirmation prompt, and the `~/.claude/` wipe. Relay its output verbatim. Add nothing.
