---
description: Run cartographer impact analysis on a symbol and report the risk tier and depth-grouped blast radius
---

# Cartographer Impact

Run impact analysis on a target symbol (function, method, class, trait) via the cartographer MCP `impact` tool. Report the `risk` tier, the direct-caller count, and top file:line hits.

## Specification

$ARGUMENTS

## Process

1. **Identify the target** from the specification (a symbol name; quoted if it contains generics or path components)
2. **Confirm the graph is fresh**: call MCP `repo_status` or run `cartographer status`; if `staleness.statusLabel != "fresh"`, re-index first
3. **Run the impact tool**: MCP `impact({"target": "...", "max_depth": 3})`
4. **Report findings**: the `risk` classification plus depth-1 count and top hits
5. **Decide next action**: proceed (LOW risk), surface to user (HIGH or CRITICAL), or scope-limit

## MCP Tool Invocation

```json
{
  "tool": "impact",
  "params": {
    "repo": "my-app",
    "target": "ParseRequest",
    "max_depth": 3
  }
}
```

Returns:
```json
{
  "depthUsed": 3,
  "risk": "HIGH",
  "byDepth": {
    "1": [ ... direct callers ... ],
    "2": [ ... ],
    "3": [ ... ]
  },
  "staleness": { "statusLabel": "fresh", ... }
}
```

## CLI Fallback (Cypher)

If the MCP server is not wired up, run a Cypher query against the graph directly. The query depends on the actual graph schema; this is an approximation:

```bash
cartographer query my-app "
  MATCH (caller)-[:CALLS*1..3]->(target {name: 'ParseRequest'})
  RETURN caller.name, caller.file, length(rel) as depth
  ORDER BY depth
  LIMIT 50
"
```

The MCP `impact` tool is preferred; it returns the same depth grouping plus the `risk` classification and applies the depth-halving logic for high-fanout symbols.

## Report Format

```
Impact analysis for `ParseRequest`:
- Risk: HIGH
- Direct callers (depth=1):    8 in 5 files (will break on signature change)
- Second-degree (depth=2):     12 in 9 files (likely on behavior change)
- Third-degree (depth=3):      27 in 18 files (may surface)
- Staleness: fresh
- Depth used: 3

Top direct callers:
- src/handler.rs:42 process_request
- src/middleware.rs:88 auth_check
- src/router.rs:120 route_handler
```

## Decision Tree

| Result | Action |
|--------|--------|
| `risk: CRITICAL` | **Block.** Refactor in stages; surface plan to user. |
| `risk: HIGH` plus signature change | **Surface count and top hits.** Confirm intent before editing. |
| `risk: HIGH` plus behavior change | Surface; proceed if contract is preserved. |
| `risk: MEDIUM` | Note in report; user decides. |
| `risk: LOW` | Proceed; mention in summary. |
| Empty `byDepth` | Truly local; proceed without surfacing. |
| `staleness.statusLabel != "fresh"` | **Stop.** Re-index first; answer is unreliable. |

## Signature Change vs Behavior Change

A signature change (rename, parameter add/remove/reorder, return type) breaks every `d=1` caller. Use `rename` (CLI or MCP tool) to plan the cascade instead of editing manually.

A behavior change (logic edit, new branch) usually preserves callers if the contract is the same. The risk is in `d=1` and `d=2` callers that depend on side effects.

## Always Pair with `detect_changes`

After applying the edit:

```json
{
  "tool": "detect_changes",
  "params": {"repo": "my-app"}
}
```

This confirms the actual changeset matches the impact prediction. Surface any unexpected file in the diff.
