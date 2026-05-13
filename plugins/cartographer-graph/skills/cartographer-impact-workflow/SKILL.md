---
name: cartographer-impact-workflow
description: The always-run-impact-before-edit workflow with cartographer. Real impact tool output shape (depthUsed, risk, byDepth), how to interpret each risk tier (CRITICAL/HIGH/MEDIUM/LOW/UNKNOWN), depth semantics (direct callers will break, depth-2 likely, depth-3 may), and the safe-edit sequence. Use before editing any symbol in an indexed repository.
---

# Cartographer Impact Workflow

The impact workflow is the safety harness for every edit in a cartographer-indexed repo. The graph encodes the call structure of the code; impact analysis tells you who will break before you change anything.

## The Safe-Edit Sequence

```
1. repo_status                              // staleness.statusLabel must be "fresh"; else re-index
2. context({"target": "X"})                 // understand the symbol
3. impact({"target": "X", "max_depth": 3})  // who calls; what will break
4. (decide: proceed, scope-limit, or abort)
5. edit the code
6. detect_changes                           // confirm scope matches the impact prediction
7. commit
```

Skip any step at your peril. The most common bug is editing a function with depth-1 callers and only discovering it through a test failure or a user report.

## Real Impact Tool Output

```json
{
  "depthUsed": 3,
  "risk": "HIGH",
  "byDepth": {
    "1": [ { "depth": 1, "node": ..., "file": ..., "name": ... }, ... ],
    "2": [ ... ],
    "3": [ ... ]
  },
  "staleness": { "statusLabel": "fresh", ... }
}
```

Two signals to surface to the user: the overall `risk` classification and the count of `byDepth["1"]` entries.

## Risk Tiers (from the tool)

| Risk | Trigger | Default action |
|------|---------|----------------|
| `CRITICAL` | Direct callers >= 30, or affected processes >= 5, or affected modules >= 5, or total impacted >= 200 | **Block.** Refactor in stages; surface plan to user. |
| `HIGH` | Approaching CRITICAL thresholds | **Surface count and top hits.** Confirm intent before editing. |
| `MEDIUM` | Notable blast radius | Surface in report; user decides. |
| `LOW` | Local-only impact | Proceed; note in summary. |
| `UNKNOWN` | Could not classify | Treat as MEDIUM until clarified. |

## Depth Semantics

| Depth | Meaning | Action on signature change | Action on behavior change |
|-------|---------|----------------------------|---------------------------|
| `byDepth["1"]` | Direct callers | WILL break | LIKELY break (depending on contract) |
| `byDepth["2"]` | One indirection away | LIKELY break | MAY break if state propagates |
| `byDepth["3"]` and beyond | Distant | MAY surface | Usually safe |

Use this vocabulary in user-facing reports: "5 direct callers (will break on signature change), 12 second-degree (likely on behavior change)".

## Signature Change vs Behavior Change

- **Signature change** (rename, parameter add/remove/reorder, return type): all direct callers WILL break. Use the `rename` MCP tool to plan the cascade.
- **Behavior change** (logic edit, new branch, error path): direct callers LIKELY break depending on contract preservation; second-degree may break if state propagates.

When in doubt, treat the entire `byDepth["1"]` array as blocking and surface the count plus top file:line hits to the user.

## When the Graph Is Stale

`staleness.statusLabel` values:
- `"fresh"`: trust the answer
- `"stale (HEAD moved)"`: working tree has commits the graph has not indexed; check `aheadBy`. For impact analysis, re-index unless `aheadBy` is 1 or 2 and the recent commits are unrelated.
- `"not indexed"`: run `cartographer index .` first
- `"unknown"`: git unavailable; the staleness signal is missing, treat results with caution

```bash
cartographer index .
```

Re-index when in doubt. Impact analysis is the load-bearing safety check; an out-of-date graph defeats the point.

## Examples

### Adding a parameter to a public function

```
1. impact({"target": "ParseRequest", "max_depth": 3})
   -> risk: HIGH; byDepth[1] has 8 callers across 5 files
2. Surface: "ParseRequest has 8 direct callers (HIGH risk). Adding a parameter
   requires updating all of them. Proceed?"
3. (user says yes; or limits scope to a new function name)
4. (apply the edit + all 8 caller updates)
5. detect_changes -> confirms all 8 files are in the expected set
6. cargo nextest run
7. commit
```

### Internal helper refactor

```
1. impact({"target": "_compute_offset", "max_depth": 3})
   -> risk: LOW; byDepth[1] has 1 caller (the file's own public function)
2. Local refactor; no need to surface
3. detect_changes -> only this file affected
4. commit
```

### Renaming a type

```
1. impact({"target": "OldName", "max_depth": 3})
   -> risk: CRITICAL; 50 direct callers in 12 files
2. rename({"from": "OldName", "to": "NewName"})
   -> returns the planned diff
3. (review and apply the diff)
4. cartographer index .
5. detect_changes -> verifies the rename closed everything out
6. cargo nextest run
7. commit
```

### Editing without impact (when it is acceptable)

- Code in `tests/`, `benches/`, or `examples/` (no downstream consumers)
- Doc comments that do not affect type signatures
- Trivially-scoped private function with no callers (`impact` returns empty `byDepth`)

In every other case, run `impact` first.

## Reporting Findings

When surfacing impact results to the user, use this format:

```
Impact analysis for `ParseRequest`:
- Risk: HIGH
- Direct callers (depth=1):    8 in 5 files (will break on signature change)
- Second-degree (depth=2):     12 in 9 files (likely on behavior change)
- Third-degree (depth=3):      27 in 18 files (may surface)
- Staleness: fresh

Top direct callers:
- src/handler.rs:42 process_request
- src/middleware.rs:88 auth_check
- ...
```

Lead with the `risk` classification, follow with depth-1 counts and file:line hits.

## Common Misuses

| Misuse | Why it fails | Fix |
|--------|--------------|-----|
| Skipping `impact` for "small" changes | A one-line behavior change can still affect direct callers | Always run impact |
| Trusting impact when `statusLabel != "fresh"` | The graph predates your changes; answer is incomplete | Re-index first |
| Treating second-degree like direct | Over-conservative; surfaces false positives | Direct: WILL break on signature. Second-degree: LIKELY on behavior. |
| Renaming with sed | Misses generic constraints, macros, string-typed refs | Use the `rename` MCP tool |
| Not calling `detect_changes` before commit | You may have edited more than you intended | Always confirm scope before committing |
| Reading `risk` without reading `byDepth[1]` count | The risk tier hides specifics | Surface both: "HIGH risk, 8 direct callers" |
