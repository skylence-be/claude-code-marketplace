---
description: Wire the cartographer MCP server into a Claude Code project or verify the marketplace plugin has auto-wired it
---

# Cartographer MCP Setup

If the `cartographer-graph` marketplace plugin is installed, the MCP server is **already wired** via the plugin's bundled `.mcp.json`. This command verifies that setup or wires it manually for projects that do not use the plugin.

## Specification

$ARGUMENTS

## Process

1. **Confirm cartographer is installed**: `command -v cartographer` (or `where cartographer` on Windows). If missing, install per the project's README (typically `cargo install --path crates/cartographer-cli` from the source repo)
2. **Confirm the repo is indexed**: `cartographer status`; if not, run `cartographer index .` first
3. **If the marketplace plugin is installed**: restart Claude Code; the MCP tools should appear under `mcp__cartographer__*` automatically. No `.mcp.json` edit needed.
4. **If using cartographer standalone**: add the MCP server to the project's `.mcp.json` manually (template below)
5. **Verify**: the tools should appear as `mcp__cartographer__*` when listed

## Auto-Configuration via the Marketplace Plugin

When the `cartographer-graph` plugin is installed, the bundled `.mcp.json` registers the server automatically. The configuration shipped with the plugin is:

```json
{
  "cartographer": {
    "command": "cartographer",
    "args": ["mcp"]
  }
}
```

No further setup is required. After installing the plugin, restart Claude Code; the tools appear under `mcp__cartographer__*`.

**Windows 11:** make sure the `cartographer` binary is on PATH after installation. The bundled `.mcp.json` calls the bare binary name; Windows resolves it through `PATHEXT` to `cartographer.exe`. If `where cartographer` returns nothing, add the install directory to `PATH` via System Properties or PowerShell:

```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\path\to\cartographer", "User")
```

Then restart Claude Code.

## Manual stdio Transport (standalone, without the plugin)

Add to `.mcp.json` at the project root:

```json
{
  "mcpServers": {
    "cartographer": {
      "command": "cartographer",
      "args": ["mcp"]
    }
  }
}
```

The server runs as a subprocess of the Claude Code session and shuts down when the session ends.

## HTTP Transport (for shared / remote)

Start the server once as a background process:

```bash
cartographer mcp --transport http --port 7070 &
```

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "cartographer": {
      "url": "http://127.0.0.1:7070",
      "transport": "http"
    }
  }
}
```

For team / remote use with auth, enable the gateway:

```bash
cartographer mcp --transport http --port 7070 --gateway
```

Then create a user and token:

```bash
cartographer gateway user create alice
cartographer gateway token create alice
# print: tok_abc123...
```

Pass the token via the `Authorization` header on each request (depends on your client's HTTP MCP config).

## Verifying the Tools Are Loaded

After restart, in the Claude Code session, the tools appear under the prefix `mcp__cartographer__`. Test with:

```
list_repos
```

Should return JSON with at least one repo.

## Initial Tool Sequence

Once wired, the typical first-session sequence is:

```
1. list_repos                          // see what is indexed
2. repo_status({"repo": "..."})        // confirm staleness=fresh
3. context({"repo": "...", "target": "<symbol>"})   // investigate a symbol
4. impact({"target": "...", "direction": "upstream"})  // before any edit
```

## Project Hooks

For project-local MCP, prefer `.mcp.json` over `~/.claude.json`. Commit `.mcp.json` so teammates get the same configuration. The server's local DB is per-machine; the config is portable.
