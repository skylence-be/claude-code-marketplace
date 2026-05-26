---
name: uninstall-claude-skill
description: Remove all Claude Code user-scope files and uninstall the claude binary from this machine.
disable-model-invocation: true
---

Uninstall Claude Code from this machine.

## Step 1: Detect platform

```bash
uname -s 2>/dev/null || echo "Windows"
```

## Step 2: Run the uninstaller

**macOS / Linux** (`uname` returns Darwin or Linux):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/uninstall-claude/uninstall.sh"
```

**Windows** (`uname` not found, or running in PowerShell):

```powershell
& "${env:CLAUDE_PLUGIN_ROOT}\skills\uninstall-claude\uninstall.ps1"
```

Script handles everything: install-method detection, confirmation prompt, binary removal, `~/.claude/` wipe, and shell rc cleanup. Relay its output verbatim. Add nothing.
