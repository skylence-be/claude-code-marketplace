---
name: cartographer-mcp-tools
description: Cartographer MCP tools reference (query, cypher, context, impact, detect_changes, rename, route_map, api_impact, shape_check, group_*). Use when invoking cartographer MCP tools.
---

# Cartographer MCP Tools

The cartographer MCP server exposes read tools for querying the indexed graph plus admin tools for registry and group management. Every response includes a `staleness` object with `indexedCommit`, `currentCommit`, `indexStale`, `aheadBy`, and `statusLabel` (one of `"fresh"`, `"stale (HEAD moved)"`, `"not indexed"`, `"unknown"`).

## Read Tools (everyday use)

### `list_repos`
List all indexed repositories the server can see.
```json
{}
```
Returns repo names, paths, last-indexed timestamps. Call this first in a fresh session to know what is available.

### `repo_status`
Indexing status of a specific repo.
```json
{"repo": "my-app"}
```
Returns staleness, node/edge counts, last-indexed commit. Call before any other tool to confirm the graph is fresh enough to trust.

### `query`
Natural-language or keyword search across the graph, ranked by relevance plus optional process-flow boosting. Prefer this over `cypher` for everyday symbol lookup.
```json
{
  "repo": "my-app",
  "query": "parse http request",
  "task_context": "adding rate limiting",
  "goal": "find the request validation entry point",
  "limit": 20
}
```
Optional fields: `task_context` and `goal` (ranking hints), `limit` and `max_tokens` (result size), `include_content` (full source per hit), `service` (monorepo scope), `view` (named view from `views.yaml`), `min_confidence` (drop low-confidence graph edges).

### `cypher`
Read-only Cypher against the property graph. Use for ad-hoc analytical queries.
```json
{"repo": "my-app", "query": "MATCH (f:Function)-[:CALLS]->(g:Function) WHERE g.name = $target RETURN f.name, f.file LIMIT 50", "params": {"target": "ParseRequest"}}
```
Never use `CREATE`, `MERGE`, `DELETE`, `REMOVE`, or `SET`. The server rejects writes, but the CLI accepts arbitrary Cypher; do not write to the graph.

### `context`
Get the surrounding context (file, callers, callees, type info) for a symbol.
```json
{"repo": "my-app", "target": "ParseRequest"}
```
Useful as the first read when investigating an unfamiliar symbol.

### `impact`
Blast radius analysis. The most important tool; call before any edit.
```json
{"repo": "my-app", "target": "ParseRequest", "max_depth": 3}
```
Returns:
```json
{
  "depthUsed": 3,
  "risk": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | "UNKNOWN",
  "byDepth": {
    "1": [ { ...impacted symbol, "depth": 1 }, ... ],
    "2": [ ... ],
    "3": [ ... ]
  },
  "staleness": { ... }
}
```
The `risk` field is cartographer's own classification (`CRITICAL` when direct callers >= 30 or process count >= 5 or module count >= 5 or total >= 200; `HIGH`/`MEDIUM`/`LOW` for descending tiers). The `byDepth` map keys callers by BFS depth from the target. Depth-1 callers WILL break on signature changes; treat as blocking.

### `detect_changes`
Compare working-tree changes to the graph; identify affected execution flows.
```json
{"repo": "my-app"}
```
Returns the set of flows / symbols touched by uncommitted edits. Call before committing.

### `rename`
Plan a symbol rename across all call sites.
```json
{"repo": "my-app", "from": "ParseRequest", "to": "ParseHttpRequest"}
```
Returns the list of files and line ranges to edit. Apply the diff after review.

### `route_map`
HTTP route to handler function map.
```json
{"repo": "my-app"}
```
Useful when looking for the handler for `GET /api/users/:id` style routes.

### `tool_map`
For MCP server repos: list every tool the server exposes with its handler.
```json
{"repo": "my-mcp-server"}
```

### `api_impact`
Pre-change impact report for an API route handler.
```json
{"repo": "my-app", "route": "POST /api/users"}
```
Surfaces downstream callees and upstream callers of the route handler.

### `shape_check`
Validate a typed data shape against actual call sites.
```json
{"repo": "my-app", "target": "UserPayload"}
```
Catches drift between a struct definition and its actual usage.

## Group Tools (cross-repo)

### `group_list`
List repo groups and their configurations.
```json
{}
```

### `group_sync`
Sync cross-repo contracts for a group.
```json
{"group": "my-org"}
```

### `group_impact`
Cross-repo impact analysis for a contract change.
```json
{"group": "my-org", "contract": "user.proto"}
```

## Admin Tools

These are for setup, not day-to-day:

- `index_repo` (alternative to CLI `cartographer index`)
- `register_repos`, `unregister_repos`, `purge_repos`
- `group_create`, `group_add`, `group_delete`, `group_remove_repo`
- `gateway_*` (auth, tokens, ACL management; only relevant for HTTP transport with auth enabled)

## Response Format

Every tool's response is a tool-specific JSON payload with a top-level `staleness` object spliced in:
```json
{
  "...tool-specific keys...": "...",
  "staleness": {
    "indexedCommit": "abc123",
    "currentCommit": "def456",
    "indexStale": true,
    "aheadBy": 3,
    "statusLabel": "stale (HEAD moved)"
  }
}
```

Always read `staleness.statusLabel`. Values:
- `"fresh"`: the indexed commit matches `HEAD`; answers are trustworthy
- `"stale (HEAD moved)"`: working tree has commits the graph has not seen yet; check `aheadBy` for how many
- `"not indexed"`: run `cartographer index .` before any other tool
- `"unknown"`: git unavailable; treat the answer with caution

For impact analysis, prefer `"fresh"`; anything stale means the blast radius may underestimate.

## Typical Tool Sequence

For investigating and editing an unfamiliar symbol:

```
1. list_repos                                    // confirm the repo is indexed
2. repo_status({"repo": ...})                    // staleness.statusLabel should be "fresh"
3. context({"target": "X"})                      // understand the symbol
4. impact({"target": "X", "max_depth": 3})       // blast radius before edit
5. (edit the code)
6. detect_changes({"repo": ...})                 // confirm scope matches expectation
7. (commit)
```

For a rename:
```
1. impact({"target": "X", "max_depth": 3})       // who calls it
2. rename({"from": "X", "to": "Y"})              // plan
3. (apply the diff returned by rename)
4. cartographer index .                          // refresh the graph
5. detect_changes({"repo": ...})                 // verify
```
