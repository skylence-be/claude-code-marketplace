---
name: archon-codex-provider
description: Master the Codex provider option in Archon (v0.3+) — the modelReasoningEffort flag (minimal/low/medium/high/xhigh), webSearchMode (disabled/cached/live), additionalDirectories for multi-repo context, codexBinaryPath resolution, when to pick Codex over Claude, and the warn-and-ignore semantics for invalid values. Use when writing workflows that should run under Codex instead of Claude, configuring default Codex settings in .archon/config.yaml, debugging Codex-specific execution differences, or tuning reasoning effort for cost-vs-quality tradeoffs.
category: engineering
tags: [archon, codex, provider, reasoning, web-search, multi-repo]
related_skills: [archon-dag-workflow-authoring, archon-architecture-deep-dive]
---

# Archon Codex Provider

Archon supports two AI providers for workflow execution: **Claude** (the default, via Claude Agent SDK) and **Codex** (OpenAI's coding agent, via the Codex CLI). Most workflows default to Claude, but individual nodes or whole workflows can declare `provider: codex` and pick up Codex-specific tuning fields.

## When to Use This Skill

- Running a workflow that needs OpenAI-specific capabilities or pricing
- Configuring `.archon/config.yaml` `assistants.codex.*` defaults
- Picking between Claude and Codex for specific workflow nodes based on cost/quality tradeoff
- Tuning `modelReasoningEffort` for harder problems
- Enabling `webSearchMode` for research nodes
- Loading context from multiple repos via `additionalDirectories`
- Debugging "Codex binary not found" errors

## The Three Codex-Specific Top-Level Fields

These apply to the **workflow** (or inherited by all nodes) when `provider: codex`. None of them do anything for Claude nodes.

### `modelReasoningEffort`

```yaml
provider: codex
model: gpt-5.3-codex
modelReasoningEffort: medium
```

| Value | Use case |
|---|---|
| `minimal` | Simple classifications, quick lookups — cheapest |
| `low` | Short responses, low-complexity edits |
| `medium` | **Default**. General-purpose coding tasks |
| `high` | Complex refactors, architectural decisions |
| `xhigh` | Hardest problems, maximum reasoning depth |

**Warn-and-ignore semantics**: if you pass an invalid value like `modelReasoningEffort: ultra`, the workflow loads successfully but the field is silently dropped and a `dag.invalid_model_reasoning_effort` warning is logged. This is intentional — old workflows shouldn't fail to load when new levels are added.

### `webSearchMode`

```yaml
provider: codex
webSearchMode: cached
```

| Value | Behavior |
|---|---|
| `disabled` | No web searches from this workflow |
| `cached` | **Default**. Use cached results when available, hit the live web otherwise |
| `live` | Always hit the live web, skip cache |

Use `live` for research-heavy workflows where freshness matters (CVE scans, documentation lookups for rapidly-changing libraries). Use `disabled` for deterministic workflows that shouldn't make external calls (compliance-sensitive environments).

### `additionalDirectories`

```yaml
provider: codex
additionalDirectories:
  - /Users/jv/webdev/shared-lib
  - /Users/jv/webdev/design-system
```

Array of **absolute paths** to other directories Codex should have read access to. Useful for monorepo-adjacent workflows that need context from a sibling repo without actually running in it.

Claude doesn't have this — if you need multi-repo context with Claude, you copy files into the worktree via `worktree.copyFiles` in `.archon/config.yaml`.

## Per-Node vs Per-Workflow

These fields can appear at the workflow level (applies to all Codex nodes) or on individual nodes:

```yaml
# Workflow-level: all nodes inherit
provider: codex
modelReasoningEffort: low

nodes:
  - id: classify
    prompt: "Is this a bug?"

  - id: deep-analysis
    prompt: "Trace the root cause"
    modelReasoningEffort: xhigh          # override just for this node
```

Node-level overrides win over workflow-level. If a node doesn't specify, it inherits.

## Switching Between Claude and Codex Within One DAG

You can mix providers within a single workflow by setting `provider:` per node:

```yaml
nodes:
  - id: quick-classify
    provider: claude
    model: haiku
    prompt: "Classify this issue"
    allowed_tools: []

  - id: deep-investigate
    provider: codex
    model: gpt-5.3-codex
    modelReasoningEffort: high
    command: archon-investigate-issue
    depends_on: [quick-classify]
    when: "$quick-classify.output.type == 'bug'"

  - id: implement
    provider: claude                      # back to Claude for the implementation
    model: sonnet
    command: archon-implement
    depends_on: [deep-investigate]
```

Use case: classify cheaply with Haiku, investigate deeply with Codex at high reasoning effort, then implement with Claude Sonnet. Each step picks the optimal provider/model for its task.

## Provider Selection in `.archon/config.yaml`

Global + repo-level defaults:

```yaml
# ~/.archon/config.yaml
defaultAssistant: claude      # 'claude' or 'codex' — workflow default

assistants:
  claude:
    model: sonnet
    settingSources: [user, project]

  codex:
    model: gpt-5.3-codex
    modelReasoningEffort: medium
    webSearchMode: cached
    codexBinaryPath: /opt/homebrew/bin/codex    # optional — auto-resolved if omitted
```

Workflow-level `provider:` overrides the default. Per-node overrides both.

## Codex Binary Resolution

The Codex CLI binary is found in this order:

1. **Config**: `assistants.codex.codexBinaryPath` in `~/.archon/config.yaml` (or repo-level `.archon/config.yaml`)
2. **Env var**: `CODEX_CLI_PATH` (legacy)
3. **PATH lookup**: `which codex` on Unix, `where codex` on Windows
4. **Auto-resolve** (v0.3.3+): Archon checks common install locations

In compiled binaries (v0.3.3+), Archon auto-resolves the Codex binary automatically — no manual `CODEX_CLI_PATH` override needed. If the binary isn't found, workflows that declare `provider: codex` fail at load time with `codex_binary_not_found`.

**Quick verify**:

```bash
which codex                          # should print a path
codex --version                      # should return a version number
```

If both pass, Archon will find it.

## Model Validation

Each provider has a model pattern:

- **Claude models**: `sonnet`, `opus`, `haiku`, `inherit`, or anything matching `claude-*`
- **Codex models**: anything **not** matching Claude patterns (e.g., `gpt-5.3-codex`, `codex-4`, `o1`)

The loader validates provider/model compatibility at load time. Incompatible combinations fail:

```yaml
provider: claude
model: gpt-5.3-codex    # ERROR: incompatible
```

Model inference: if you specify `model: haiku` without `provider:`, Archon infers Claude. If you specify `model: gpt-5.3-codex`, it infers Codex.

## Choosing Claude vs Codex

Pragmatic guide:

| Task | Prefer |
|---|---|
| Short classifications, quick routing | **Claude Haiku** — cheapest and fastest |
| General coding (feature, bug fix) | **Claude Sonnet** — proven, good tool use |
| Complex refactors, architectural work | **Claude Opus** or **Codex xhigh** — both are strong, test both |
| Web research with heavy browsing | **Codex with `webSearchMode: live`** |
| Python-heavy tasks | **Codex** — strong Python training |
| Multi-repo code awareness | **Codex with `additionalDirectories`** |
| Long planning + implementation chain | **Claude Sonnet** — strong session coherence |
| Batch processing many files | **Claude** — faster token throughput |

## Cost Notes

Reasoning effort scales token usage and cost non-linearly:

- `minimal` / `low` — ~1x token baseline
- `medium` — ~1.5x
- `high` — ~3-5x
- `xhigh` — ~10x+ (very expensive — use for hard problems only)

Budget workflows explicitly with `maxBudgetUsd` on individual nodes:

```yaml
- id: deep-reason
  provider: codex
  modelReasoningEffort: xhigh
  maxBudgetUsd: 2.00                   # cap this one node at $2
  command: archon-investigate-complex
```

If the node exceeds the budget, Archon terminates the call and marks the node failed.

## Limitations and Gotchas

### Gotcha 1 — Codex doesn't support MCP servers

As of v0.3.5, the per-node `mcp:` field is **Claude-only**. Codex nodes with `mcp:` set will log a warning and ignore the MCP config. Use Codex for pure reasoning, not tool-heavy work.

### Gotcha 2 — Codex doesn't support SDK hooks

The per-node `hooks:` field is **Claude-only**. Codex nodes with `hooks:` set will log a warning and ignore the hook config. Self-correcting quality loops require Claude.

### Gotcha 3 — Codex output streaming differs

Claude's streaming outputs tool calls interleaved with text. Codex streams text-only; tool calls come at the end of each turn. UI adapters should handle this difference automatically, but if you're writing a custom adapter, test both.

### Gotcha 4 — `modelReasoningEffort` changes session cost unpredictably

Switching mid-session from `medium` to `high` on a subsequent message doesn't "upgrade" the earlier turns — each turn is costed independently. For consistent cost accounting, set the effort at workflow dispatch time and don't change it.

### Gotcha 5 — Codex binary version pinning

Codex CLI is versioned separately from Archon. If Archon's Codex client expects an API that's removed in a newer Codex release, workflows fail with cryptic parser errors. Pin Codex CLI version explicitly in your setup docs.

## Debugging Codex Execution

1. **"Codex binary not found"**: run `which codex`, set `assistants.codex.codexBinaryPath` in `~/.archon/config.yaml`
2. **"Invalid modelReasoningEffort"**: check your YAML for typos — valid values are `minimal`, `low`, `medium`, `high`, `xhigh`. Invalid → warn and drop.
3. **"additionalDirectories doesn't apply"**: verify paths are **absolute**, verify the directories exist, verify they're not gitignored by any parent config
4. **"Codex runs but ignores my hooks/mcp"**: expected — those are Claude-only. Switch the node to `provider: claude` if you need them.
5. **"Web search results look stale"**: set `webSearchMode: live` on the node or workflow

## Source of Truth

| Concern | File |
|---|---|
| Codex workflow-level schemas | `packages/workflows/src/schemas/workflow.ts` (`modelReasoningEffortSchema`, `webSearchModeSchema`) |
| Codex loader validation | `packages/workflows/src/loader.ts:289-330` (warn-and-ignore) |
| Codex client | `packages/core/src/clients/codex.ts` |
| Binary path resolution | `packages/core/src/clients/codex.ts:210` (`getCodex(codexBinaryPath)`) |
| Config schema | `packages/core/src/config/config-types.ts` (`assistants.codex.*`) |
| Codex CLI support commit | CHANGELOG `## [0.3.3]` ("Codex native binary auto-resolution") |
| Related issue | [#561](https://github.com/coleam00/Archon/issues/561) (Codex CLI support) |
