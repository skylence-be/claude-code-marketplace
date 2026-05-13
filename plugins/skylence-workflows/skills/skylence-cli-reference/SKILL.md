---
name: skylence-cli-reference
description: Reference for the Skylence sky CLI (./bin/sky). Covers run, logs, lint, serve, setup, doctor, webhook, learning, codebase, examples, mcp, upgrade. Use when invoking any sky command, registering webhooks, managing learnings, configuring MCP servers, or troubleshooting daemon issues.
---

# Skylence CLI Reference

The `sky` CLI is the single user-facing interface for Skylence. The binary lives at `./bin/sky` after `make build`, or on `$PATH` after install.

## Workflow Operations

```bash
./bin/sky run <name>                # run a workflow by filename (without .sky)
./bin/sky run <name> --vars k=v     # pass vars consumed via {{var}} or $SKY_VAR
./bin/sky logs                      # list recent runs
./bin/sky logs <run-id>             # show a specific run with step status
./bin/sky lint                      # validate all .sky files in .sky/workflows/
./bin/sky lint .sky/workflows/foo.sky    # validate a single file
./bin/sky pause <run-id>            # pause an in-flight run
./bin/sky resume <run-id>           # resume a paused run
./bin/sky stream <run-id>           # tail live events for a run
```

## Daemon Operations

```bash
./bin/sky serve                     # start daemon on :3090 (REST + WebSocket)
./bin/sky setup                     # one-shot: check deps, init SQLite DB
./bin/sky doctor                    # diagnose env (Go version, Claude CLI, ports, tokens)
./bin/sky upgrade                   # self-update via go-selfupdate
```

`serve` runs in the foreground. Background it with `&` for development, or use `make run` which runs it via the platform service manager.

## Webhooks

```bash
./bin/sky webhook list              # list registered webhooks
./bin/sky webhook register <url>    # register a GitHub webhook
./bin/sky webhook update <id> ...   # update fields
./bin/sky webhook delete <id>       # remove a webhook
```

For local development, proxy GitHub deliveries via `smee.io` or `ngrok` to `http://127.0.0.1:3090/api/webhook/github`.

## Learnings

```bash
./bin/sky learning list             # list captured learnings
./bin/sky learning show <id>        # full content
./bin/sky learning delete <id>      # remove
```

Learnings are workflow output annotations the daemon persists for later retrieval. Exclude per workflow via `learnings.exclude = [...]` in `⊕meta⊕`.

## Codebase / Repo Registration

```bash
./bin/sky codebase register <path>  # add a repository the daemon can run workflows in
./bin/sky codebase list             # show registered codebases
./bin/sky codebase show <name>      # full record
```

## MCP Servers

Skylence is itself an MCP server (`sky mcp stdio`) and also manages other MCP servers that workflows can call.

```bash
./bin/sky mcp stdio                 # serve Skylence's own MCP over stdin/stdout (used by the marketplace plugin)
./bin/sky mcp install <name>        # install a known MCP server (uvx / npx managed)
./bin/sky mcp list                  # list managed servers
./bin/sky mcp register <name> ...   # register a custom MCP for workflow use
```

Workflows reference managed MCP servers in their `⊕meta⊕` block via `mcp_servers = { ... }`.

### Auto-Wired via the Marketplace Plugin

When the `skylence-workflows` marketplace plugin is installed, the plugin's bundled `.mcp.json` auto-registers `sky mcp stdio` as a Claude Code MCP server. Tools appear under `mcp__skylence__*`: list_runs, get_run, search_runs, daemon_status, run-tool calls.

**Windows 11:** the `sky` binary must be on PATH. The bundled config calls the bare binary name; Windows resolves to `sky.exe` via PATHEXT. If `where sky` returns nothing, add the install directory to PATH:

```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\path\to\sky", "User")
```

Then restart Claude Code.

## Examples / Templates

```bash
./bin/sky examples list             # browse bundled workflow examples
./bin/sky examples copy <name>      # copy an example into .sky/workflows/
```

## Budget and Audit

```bash
./bin/sky budget                    # show token usage budget and consumption
./bin/sky audit                     # run security/correctness audits on the daemon state
```

## Sentry

```bash
./bin/sky sentry                    # show last N errors reported to Sentry (if configured)
```

## REST API (alternative to CLI)

The daemon exposes the same operations over REST on `:3090`:

```bash
# Trigger a workflow
curl -X POST http://127.0.0.1:3090/api/runs \
  -H "Authorization: Bearer $SKY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"workflow": "<name>", "vars": {}}'

# Stream live events
wscat -c "ws://127.0.0.1:3090/api/ws" \
  -H "Authorization: Bearer $SKY_API_KEY"
```

WebSocket event types: `run.started`, `step.started`, `step.output`, `step.completed`, `run.completed`, `run.failed`.

## Ports

| Port | Service |
|------|---------|
| 3090 | Skylence daemon (REST + WebSocket) |
| 4747 | Gitnexus bridge (when enabled) |

## Repo Init

To add Skylence to a fresh repository:

```bash
mkdir -p .sky/workflows .sky/commands
./bin/sky setup
```

Add `.env` to `.gitignore` if not already present. Commit `.sky/workflows/`.

## Typical Daily Workflow

```bash
./bin/sky lint                          # validate before commit
./bin/sky run smoke-test                # manual test
./bin/sky logs                          # see what happened
./bin/sky logs <run-id>                 # drill into a specific run
./bin/sky stream <run-id>               # watch live events for a running workflow
```
