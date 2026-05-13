---
name: cartographer-rules
description: MUST/MUST NOT rules for Cartographer. Prevents stale-graph errors, destructive writes, bad renames. Read before editing.
---

# Cartographer Rules

These rules are non-negotiable for any repository that has been indexed with Cartographer (the `.cartographer/` directory or a `LadybugDB` graph database exists, or the `cartographer` binary is on `$PATH`).

## MUST

### Run impact before editing any symbol
**Always call the cartographer `impact` MCP tool before editing a function, method, class, or trait.** The blast radius determines whether the edit is local or cascading.

```json
{"target": "ParseRequest", "max_depth": 3}
```

The tool returns `{depthUsed, risk, byDepth, staleness}`. A non-empty `byDepth["1"]` means direct callers WILL break on signature changes. Treat any direct caller as blocking and confirm scope with the user.

### Re-index after a HEAD change
Cartographer's graph is committed-state. If the working tree has uncommitted changes that affect the graph schema (new files, removed functions, renamed types), call `detect_changes` first to see what is stale, or run `cartographer index .` to refresh.

### Use `cartographer rename` (or the `rename` MCP tool) for renames
Find-and-replace breaks call sites that the static parser sees but `sed` does not (string-typed identifiers, generic constraints, macro invocations). The `rename` tool plans the refactor across all call sites and reports any that need manual adjustment.

### Read the `staleness` object on every response
Every MCP tool response includes a `staleness` object: `{indexedCommit, currentCommit, indexStale, aheadBy, statusLabel}`. The `statusLabel` is one of `"fresh"`, `"stale (HEAD moved)"`, `"not indexed"`, `"unknown"`. Anything other than `"fresh"` means the graph is older than the working tree; surface this to the user when the staleness affects the answer.

### Prefer the `query` tool over raw `cypher` for symbol lookup
`query` is a natural-language and keyword search across the graph, ranked by relevance plus optional process-flow boosting. Use `query` for "find the parser entry point" style searches. Use `cypher` only for graph-shape queries (`MATCH (f)-[:CALLS]->(g) ...`) the search tool cannot express.

### Quote symbol names that contain special characters
Generic types (`Vec<u32>`), associated functions (`Foo::new`), trait methods (`Display::fmt`) need exact strings. Pass the fully qualified name when the MCP tool accepts it.

## MUST NOT

### Issue destructive Cypher
Cartographer's `cypher` MCP tool is read-only by contract, but the local CLI accepts arbitrary Cypher against the local DB. Never run `CREATE`, `MERGE`, `DELETE`, `REMOVE`, or `SET` against the graph; the index is the source of truth and writes are silently lost on the next `cartographer index`.

### Assume the graph reflects unwritten code
If you have edits in flight that have not been saved or committed, the graph does not see them. Save the file, run `cartographer index .`, then query.

### Run `cartographer index` concurrently with another cargo job on a constrained machine
Indexing is CPU-bound and memory-hungry. On a laptop, do not start a new index while `cargo nextest run` or another long Rust build is active.

### Rename via find-and-replace
The graph captures references that pure text search misses. Use `rename` (CLI or MCP). If you must use sed, run `detect_changes` afterward to confirm nothing else broke.

### Trust impact analysis when `staleness.statusLabel` is not `"fresh"`
A non-fresh label means the indexed snapshot pre-dates source changes. Re-index first; the blast radius answer is unreliable otherwise. The `aheadBy` field counts how many commits HEAD is ahead.

### Run the MCP server stdio transport from a workflow that also calls `cargo nextest`
On a laptop the kernel will starve one of them. Bring the MCP server up first as a long-running process and keep cargo work serial.

## Always-Run Gates

| Operation | Required gate |
|-----------|---------------|
| Edit any function or method | `impact` (or `cartographer query --impact`) |
| Rename a symbol | `cartographer rename` (or the `rename` MCP tool) |
| Commit a code change | `detect_changes` to verify scope |
| Run a Cypher query | Confirm read-only; never `CREATE`, `MERGE`, `DELETE`, `REMOVE`, `SET` |
| Trust an MCP response | Read `staleness.statusLabel`; re-index if not `"fresh"` |

## Risk and Depth Semantics

The `impact` tool returns a `risk` classification plus a `byDepth` map. Use both.

| `risk` | Trigger | Action |
|--------|---------|--------|
| `CRITICAL` | Direct callers >= 30, processes >= 5, modules >= 5, or total >= 200 | Block; refactor in stages |
| `HIGH` | Approaching CRITICAL thresholds | Surface count plus top hits; confirm intent |
| `MEDIUM` | Notable blast radius | Surface; user decides |
| `LOW` | Local-only impact | Proceed; note in summary |
| `UNKNOWN` | Cannot classify | Treat as MEDIUM |

| Depth bucket | Meaning | Signature change | Behavior change |
|--------------|---------|------------------|------------------|
| `byDepth["1"]` | Direct callers | WILL break | LIKELY breaks |
| `byDepth["2"]` | One step removed | LIKELY breaks | MAY break |
| `byDepth["3"]` and beyond | Distant | MAY surface | Usually safe |

## Detection Heuristics

A repository uses Cartographer when any of these are true:
- A `.cartographer/` directory exists
- A `LadybugDB` graph database lives at `~/.local/share/cartographer/<repo>` or under `XDG_DATA_HOME`
- The `cartographer` binary is on `$PATH`
- The MCP client config lists a `cartographer` server
- `.cartographerignore` exists

When detected, this skill should be the first reference. Other Cartographer skills (`cartographer-mcp-tools`, `cartographer-cli-reference`, `cartographer-impact-workflow`) cover specific tasks.
