---
name: cartographer-cli-reference
description: Cartographer CLI: register, index, query, search, mcp, serve, snapshot, drift. Use when invoking CLI subcommands.
---

# Cartographer CLI Reference

The `cartographer` binary is the single CLI entry point for all read and admin operations on the LadybugDB graph. The MCP server is a separate process started via `cartographer mcp`.

## First-Time Setup

```bash
cartographer register .         # register the current dir as a repo
cartographer index .            # build the graph (downloads the embedding model on first run)
cartographer status             # confirm indexing succeeded
cartographer mcp                # start the MCP server (stdio by default)
```

Or in one shot:
```bash
cartographer index .            # register + index implicitly
```

## Repo Management

```bash
cartographer register <path>            # register without indexing
cartographer register . --name foo      # under a custom name
cartographer register . --allow-multi   # allow same name across paths

cartographer list                       # list registered repos
cartographer remove <name-or-path>      # remove from registry (keeps DB)
cartographer remove --all               # remove all repos and groups
cartographer purge <name-or-path>       # delete the local DB (keeps registry entry)
```

## Indexing

```bash
cartographer index                       # current directory
cartographer index <path>                # specific path
cartographer index --all                 # all registered repos
cartographer index --paths a b c         # explicit list
cartographer index --dir ./workspace     # all subdirs of workspace
cartographer index --jobs 2              # max concurrent repos (default: min(4, ncpus/2))
cartographer index --threads-per-job 4   # rayon threads per worker
cartographer index --no-embeddings       # skip ONNX embedding stage (faster; no semantic search)
cartographer index --no-register         # do not add to the global registry
```

On a constrained machine (laptop) keep `--jobs 1` to avoid CPU starvation.

## Querying

```bash
# Run a Cypher query against the graph
cartographer query <repo> "MATCH (f:Function) RETURN f.name LIMIT 10"

# Full-text + semantic search
cartographer search <repo> "parse http request"
cartographer search <repo> "..." --mode bm25       # FTS only
cartographer search <repo> "..." --mode vector     # semantic only
cartographer search <repo> "..." --mode hybrid     # default (reciprocal rank fusion)

# Augment a pattern with graph context (callers, callees, flows)
cartographer augment <repo> "ParseRequest"
```

## MCP Server

```bash
cartographer mcp                        # stdio transport (default; for Claude Code, Cursor, Windsurf)
cartographer mcp --transport http       # HTTP StreamableHTTP transport (default port 7070)
cartographer mcp --port 7070            # custom HTTP port
cartographer mcp --gateway              # enable auth via the SQLite gateway
```

For Claude Code, add the stdio server to project MCP config:

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

## REST API (SPA-facing)

```bash
cartographer serve                       # start the Axum REST API (default :8080)
cartographer serve --port 8080
```

## Groups (cross-repo contracts)

```bash
cartographer group list
cartographer group create <name>
cartographer group add <group> <repo>
cartographer group remove <group> <repo>
cartographer group sync <group>
cartographer group delete <name>
```

## Snapshots (cached results)

```bash
cartographer snapshot list <repo>
cartographer snapshot show <repo> <name>
```

Snapshots are pre-built query results that the MCP server returns instantly. The cache invalidates on HEAD change.

## Drift Detection and Re-indexing

```bash
cartographer drift                       # poll all repos for stale state; reindex if needed
cartographer hooks install               # install git post-commit / post-merge / post-checkout hooks
cartographer hooks uninstall
```

With hooks installed, the graph stays fresh automatically on every commit.

## Wiki and Export

```bash
cartographer wiki <repo>                 # generate a Markdown wiki with Mermaid diagrams
cartographer export <repo> --format jsonl
cartographer export <repo> --format graphml
cartographer export <repo> --format cypher
```

## Service Management

```bash
cartographer service install             # macOS launchd or Linux systemd-user
cartographer service status
cartographer service uninstall

cartographer docker                      # manage the container if running via Docker
cartographer tunnel                      # manage the cloudflared tunnel for remote MCP HTTP
```

## Diagnostics

```bash
cartographer status                      # indexing status for all repos
cartographer doctor                      # check for orphaned WAL files and other local-state issues
cartographer embed "some text"           # diagnostic: embed a string, print dim/norm
cartographer bench-embed                 # benchmark CPU vs CoreML embedding
```

## Gateway (auth for HTTP transport)

```bash
cartographer gateway user create <name>
cartographer gateway user list
cartographer gateway token create <user>
cartographer gateway token revoke <prefix>
cartographer gateway group create <name>
cartographer gateway acl add <group> <repo-pattern>
cartographer gateway tool-deny add <group> <tool>
```

Only needed when running the MCP HTTP server with auth enabled.

## Common Flags

| Flag | Meaning |
|------|---------|
| `--repo <name-or-path>` | Specify the repo for commands that need one |
| `--format json` | Machine-readable output |
| `--quiet` | Suppress progress output |
| `--no-color` | Disable ANSI colors |
