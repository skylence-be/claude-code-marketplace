---
name: archon-mcp-integration
description: Master per-node MCP server integration in Archon DAG workflows — the `mcp:` field pointing at a JSON config, auto-allow wildcards for MCP tools, env var substitution and warnings, Haiku-with-MCP incompatibility warnings, and patterns for wiring up drizzle/nuxt/playwright/web-search MCP servers inside specific workflow nodes. Use when a workflow node needs access to MCP tools (database queries, browser automation, documentation lookup) that aren't in the base Claude toolset.
category: engineering
tags: [archon, mcp, model-context-protocol, tools, drizzle, playwright]
related_skills: [archon-dag-workflow-authoring, archon-github-adapter-patterns]
---

# Archon Per-Node MCP Integration

Archon DAG nodes can declare `mcp:` pointing at a JSON config file of MCP servers. When the node's Claude subprocess starts, Archon loads the config, connects to the servers, and auto-allows their tools via `mcp__<server>__*` wildcards. Based on `packages/workflows/src/schemas/dag-node.ts:127` and `packages/workflows/src/dag-executor.ts:~520`.

## When to Use This Skill

- A workflow node needs to run database queries (Drizzle MCP, SQLite MCP)
- A node needs browser automation (Playwright MCP)
- A node needs documentation lookup (Nuxt Docs MCP, Context7 MCP)
- A node needs Atlassian / Jira / Linear access
- A node needs custom tools from a private MCP server
- Debugging "MCP server not loaded" issues in Archon workflows

## YAML Syntax

```yaml
- id: query-db
  prompt: |
    Count users registered in the last 7 days. Use the drizzle MCP's
    mcp__drizzle__execute_query tool with a Postgres date filter.
  mcp: .archon/mcp/drizzle.json
  depends_on: [fetch-schema]
```

**Single field**: `mcp:` takes a relative path to a JSON file with this shape:

```json
{
  "mcpServers": {
    "drizzle": {
      "command": "node",
      "args": ["node_modules/drizzle-mcp/dist/cli.js", "./drizzle-mcp.config.ts"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

One `mcp:` path per node. Point at the same JSON from multiple nodes if you want them to share a config. Point at different JSONs for nodes that need different tool sets.

## How the Runtime Loads It

From `packages/workflows/src/dag-executor.ts:~520`:

```typescript
if (node.mcp) {
  try {
    const { servers, serverNames, missingVars } = await loadMcpConfig(node.mcp, cwd);
    claudeOptions.mcpServers = servers;
    // Auto-allow all MCP tools via wildcards
    const mcpWildcards = serverNames.map(name => `mcp__${name}__*`);
    claudeOptions.allowedTools = [...(claudeOptions.allowedTools ?? []), ...mcpWildcards];
    getLog().info({ nodeId: node.id, serverNames, mcpPath: node.mcp }, 'dag.mcp_config_loaded');
    // Warn if env vars are missing
    if (missingVars.length > 0) { /* ... */ }
    // Warn if using Haiku with MCP (tool search unsupported)
    if (model?.toLowerCase().includes('haiku')) { /* ... */ }
  } catch (mcpErr) {
    throw new Error(`Node '${node.id}': ${(mcpErr as Error).message}`);
  }
}
```

Three important behaviors:

1. **Auto-allow wildcards** — every MCP server listed gets `mcp__<server>__*` added to `allowedTools`. You don't have to enumerate each tool.
2. **Env var warning** — if the config references `${ENV_VAR}` placeholders and some aren't defined, Archon posts a warning comment on the conversation listing the missing vars.
3. **Haiku warning** — if the node's resolved model contains "haiku", Archon posts a warning because Claude Haiku doesn't support MCP tool search (the lazy-loading mechanism for many tools). The workflow still runs but tool calls may fail unpredictably.

## Env Var Substitution in MCP Config

MCP config files support `${VAR_NAME}` placeholders that Archon expands from the server process environment:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["@atlassian/mcp-server"],
      "env": {
        "JIRA_TOKEN": "${JIRA_TOKEN}",
        "JIRA_BASE_URL": "${JIRA_BASE_URL}"
      }
    }
  }
}
```

**Missing vars are empty strings** — the config still loads, but the MCP server may fail to authenticate at runtime. Archon's warning lets you know to set the vars in `~/.archon/.env`.

## Canonical Patterns

### Pattern 1 — Database queries in a specific node

`.archon/mcp/drizzle.json`:

```json
{
  "mcpServers": {
    "drizzle": {
      "command": "node",
      "args": ["node_modules/drizzle-mcp/dist/cli.js", "./drizzle-mcp.config.ts"]
    }
  }
}
```

Workflow:

```yaml
- id: preflight
  bash: |
    if [ ! -d node_modules ]; then pnpm install --frozen-lockfile 2>&1 | tail -5; fi
  timeout: 300000

- id: query-freshness
  prompt: |
    Use the drizzle MCP to check the scanner data freshness.

    1. Call mcp__drizzle__execute_query with:
       SELECT MAX(scanned_at) as last_scan,
              COUNT(*) FILTER (WHERE scanned_at > NOW() - INTERVAL '30 minutes') as fresh_count
       FROM scanner_results;
    2. If last_scan > 35 minutes ago: output "FAIL"
    3. If last_scan between 0-35 minutes: output "PASS"
    4. If fresh_count == 0: output "WARN"
  mcp: .archon/mcp/drizzle.json
  depends_on: [preflight]
  model: sonnet    # NOT haiku — Haiku doesn't support MCP tool search
  output_format:
    type: object
    properties:
      status: { type: string, enum: [PASS, WARN, FAIL] }
    required: [status]
```

The `preflight` node ensures `node_modules/drizzle-mcp` exists before Claude tries to spawn the drizzle server.

### Pattern 2 — Browser automation for E2E validation

`.archon/mcp/playwright.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

```yaml
- id: e2e-check
  prompt: |
    Navigate to http://localhost:3000/demos/scanner, take a snapshot,
    and verify the "Top Gainers" table has at least 5 rows. Use the
    playwright MCP tools.
  mcp: .archon/mcp/playwright.json
  allowed_tools: [Read]  # NOT Write/Edit — this node is read-only
```

The `allowed_tools: [Read]` restricts the non-MCP toolset while the MCP wildcards (auto-added) still give access to all Playwright tools.

### Pattern 3 — Documentation lookup without cloning

`.archon/mcp/docs.json`:

```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp"
    },
    "nuxt-docs": {
      "type": "sse",
      "url": "https://mcp.nuxt.com/sse"
    }
  }
}
```

```yaml
- id: research
  prompt: |
    Before planning, look up the latest Nuxt 4 server middleware patterns
    via mcp__nuxt-docs__* tools, and cross-reference with mcp__context7__*
    for the `h3` package.
  mcp: .archon/mcp/docs.json
```

External SSE/HTTP MCP servers are ideal for workflows because they don't depend on any local state (no `node_modules`, no running dev server).

### Pattern 4 — Multiple MCP servers in one node

Combine into a single config file:

```json
{
  "mcpServers": {
    "drizzle": {
      "command": "node",
      "args": ["node_modules/drizzle-mcp/dist/cli.js", "./drizzle-mcp.config.ts"]
    },
    "nuxt-docs": {
      "type": "sse",
      "url": "https://mcp.nuxt.com/sse"
    }
  }
}
```

```yaml
- id: feature-design
  prompt: |
    Design a new server route. Use:
    - mcp__drizzle__introspect_schema to see the existing tables
    - mcp__nuxt-docs__search_nuxt_docs to verify route conventions
  mcp: .archon/mcp/design-suite.json
```

Both server wildcards (`mcp__drizzle__*` and `mcp__nuxt-docs__*`) are added to `allowedTools`.

### Pattern 5 — Separate MCP per node, not per workflow

```yaml
nodes:
  - id: query-db
    prompt: "SELECT COUNT(*) from users"
    mcp: .archon/mcp/drizzle.json       # only drizzle here

  - id: browser-check
    prompt: "Visit /health and verify 200"
    mcp: .archon/mcp/playwright.json    # only playwright here
    depends_on: [query-db]
```

Each node gets its own isolated MCP server set. Downstream nodes don't see the upstream's servers. This is **by design** — keeps the tool surface tight per node and prevents noise from servers the node doesn't need.

## Env Var Gotcha

Archon's env var substitution reads from the **server process environment**, which includes variables loaded from `~/.archon/.env` at startup. It does **not** read from the repo's `.env` file unless that was manually copied in via `.archon/config.yaml` `worktree.copyFiles`.

If your MCP config needs `GITHUB_TOKEN` or `JIRA_TOKEN`, put them in `~/.archon/.env` (global, picked up automatically) rather than the project's `.env` (worktree-local, not seen by the Archon server).

Check for missing vars with:

```bash
grep -E '^(GITHUB_TOKEN|JIRA_TOKEN|etc)' ~/.archon/.env
```

## Haiku + MCP Warning Explained

Claude Haiku doesn't support the **tool search** mechanism used for lazy-loading large tool sets. When you specify many MCP tools (hundreds, across several servers), Sonnet and Opus use tool search to find relevant ones for each turn without inflating every API call. Haiku doesn't — it must see every tool definition up front, which blows past context limits with big MCP server sets.

**Rule of thumb**: if you want Haiku cheap-classifier nodes, don't attach MCP to them. Use Haiku for the classification step and let a downstream Sonnet node do the MCP work.

## Relationship to `allowed_tools` and `denied_tools`

Archon adds MCP wildcards to `allowedTools` **in addition to** whatever you specified. If your node has:

```yaml
allowed_tools: [Read, Grep]
mcp: .archon/mcp/drizzle.json
```

The effective `allowedTools` at runtime becomes `[Read, Grep, mcp__drizzle__*]`.

**`denied_tools`** still applies. If you write:

```yaml
denied_tools: [mcp__drizzle__drizzle_run_migrations]
mcp: .archon/mcp/drizzle.json
```

The wildcard allows all drizzle tools EXCEPT the explicit deny on `drizzle_run_migrations`. Useful for read-only audit nodes that shouldn't mutate the DB.

## Debugging "MCP server didn't load"

### Symptom 1: the tool call fails with "tool not found"

**Check**:
1. Is the `mcp:` path correct? It's relative to the node's working directory (usually the worktree repo root).
2. Run `cat .archon/mcp/<file>.json | jq .` — does it parse as valid JSON?
3. Are the server's binaries/URLs reachable from the worktree? (`node_modules/drizzle-mcp/dist/cli.js` only exists if `pnpm install` ran)
4. Is the model Haiku? Switch to Sonnet for MCP-heavy nodes.

### Symptom 2: the AI ignores the MCP tools

**Check**:
1. Is the prompt explicit enough? Say "use the `mcp__drizzle__execute_query` tool" rather than hoping the model infers it.
2. Did `dag.mcp_config_loaded` appear in the Archon server logs? If not, the config failed to parse — check JSON syntax.
3. Did the env var warning fire? Missing env vars make the server silently fail at connect time.

### Symptom 3: MCP noise in the PR comments

Not really an MCP load failure — it's a side effect of Claude subprocess startup in a fresh worktree where project-local MCP servers (like `drizzle-mcp` before `pnpm install`) can't connect. See `archon-github-adapter-patterns` for mitigation patterns (pre-flight install, scoping dev-state servers to `~/.claude.json`, slimming committed `.mcp.json`).

## Why Per-Node Instead of Per-Workflow?

Archon deliberately scopes MCP to nodes rather than workflows because:

1. **Tool surface discipline** — nodes that don't need a server shouldn't see its tools
2. **Context efficiency** — large MCP tool sets cost tokens per turn; scoping reduces per-node cost
3. **Failure isolation** — if one node's MCP server fails, other nodes aren't affected
4. **Explicit intent** — the YAML makes it clear WHERE each tool set is used

The downside: you sometimes end up with multiple `.archon/mcp/*.json` files. That's a feature, not a bug — they serve as documentation of which nodes need which tools.

## Source of Truth

| Concern | File |
|---|---|
| Node `mcp:` schema | `packages/workflows/src/schemas/dag-node.ts:127` |
| MCP runtime integration | `packages/workflows/src/dag-executor.ts:~520` |
| `loadMcpConfig()` | `packages/workflows/src/utils/mcp-config-loader.ts` (likely) |
| Haiku warning threshold | `packages/workflows/src/dag-executor.ts:~550` |
| Claude Agent SDK MCP type | `@anthropic-ai/claude-agent-sdk` — `WorkflowAssistantOptions['mcpServers']` |
