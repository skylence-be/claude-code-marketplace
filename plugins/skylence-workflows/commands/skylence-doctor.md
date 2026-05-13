---
description: Run sky doctor and interpret the diagnostic output, suggesting fixes for any failing checks
---

# Skylence Doctor

Run `./bin/sky doctor` to diagnose the Skylence environment (daemon health, ports, Claude CLI, env vars) and propose a fix for each failing check.

## Specification

$ARGUMENTS

## Process

1. **Run the diagnostic**: `./bin/sky doctor`
2. **For each failing check**, identify what is being tested and the failure cause
3. **Propose a concrete fix** for each `FAIL` entry
4. **Re-run** after each fix to confirm

## Common Checks

| Check | Failure cause | Fix |
|-------|---------------|-----|
| Go version | Go below required minimum | Update Go (`brew install go` on macOS, or download from go.dev) |
| Claude CLI | `claude` not on `$PATH` or auth expired | `npm i -g @anthropic-ai/claude-code`; run `claude` once to authenticate |
| Daemon process | Daemon not running | `./bin/sky serve &` for foreground; `make run` for service manager |
| Port 3090 | Port in use by another process | `lsof -i :3090` to find the process; kill or change the port |
| SQLite DB | Path not writable or corrupt | `./bin/sky setup` to re-init the DB |
| `SKY_API_KEY` | Not set in environment | `export SKY_API_KEY="$(uuidgen)"` and add to `.env` |
| `GITHUB_TOKEN` | Not set; required for github-triggered workflows | `gh auth token` then `export GITHUB_TOKEN=...` |
| Webhook delivery | Webhook misconfigured | `./bin/sky webhook list`; verify the URL is reachable |

## Examples

```bash
./bin/sky doctor
```

Sample output (truncated):

```
OK    Go 1.26.0
OK    Claude CLI 1.0.91
FAIL  Daemon not running on :3090
OK    SQLite DB at ~/.local/share/skylence/sky.db
OK    SKY_API_KEY set
WARN  GITHUB_TOKEN not set (github-triggered workflows will fail)
```

Then act on each `FAIL` / `WARN` in order.
