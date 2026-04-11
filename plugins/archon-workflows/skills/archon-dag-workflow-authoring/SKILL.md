---
name: archon-dag-workflow-authoring
description: Master Archon workflow YAML authoring — all three execution modes (steps, loop, DAG), all seven DAG node types (command, prompt, bash, loop, script, approval, cancel), trigger rules, conditional routing, structured output, Codex-specific fields, validation rules, and the gotchas the public docs don't cover. Based on Archon v0.3.5 source (packages/workflows/src/schemas/dag-node.ts). Use when authoring or debugging .archon/workflows/*.yaml files.
category: engineering
tags: [archon, workflow, dag, yaml, ai-agents, claude-code, codex]
related_skills: [archon-github-adapter-patterns, archon-pr-review-patterns]
---

# Archon Workflow Authoring

Authoritative guide for writing `.archon/workflows/*.yaml` files against Archon v0.3+. Draws from the live schema in `packages/workflows/src/schemas/dag-node.ts`, the workflow YAML reference at `.claude/docs/workflow-yaml-reference.md` in the Archon repo, and hands-on experience with v0.3.5.

## Three Execution Modes

A workflow file must declare exactly one top-level execution mode:

| Mode | Discriminator | Use case |
|---|---|---|
| **Steps** | `steps:` array | Sequential workflow with optional `parallel:` blocks. Simple pipelines. |
| **Loop** | top-level `loop:` + `prompt:` | Pure ralph-style single-loop. Stateless iteration until signal. |
| **DAG** | `nodes:` array | Graph with dependencies, conditions, multiple node types. The most powerful. |

## Top-Level Schema (all modes)

```yaml
name: my-workflow                 # required — kebab-case, unique
description: |                    # required — multiline, router-facing
  Use when: <one-sentence problem>
  Triggers: "phrase 1", "phrase 2", "phrase 3"
  NOT for: <anti-patterns>

  <body>

  Suggested branch: <prefix>/<slug>

provider: claude                  # optional — 'claude' | 'codex', default: config
model: sonnet                     # optional — sonnet|opus|haiku|inherit|claude-*|codex-model

# Codex-only top-level fields:
modelReasoningEffort: medium      # 'minimal'|'low'|'medium'|'high'|'xhigh'
webSearchMode: cached             # 'disabled'|'cached'|'live'
additionalDirectories:            # string[] of absolute paths to other repos
  - /path/to/sibling-repo
```

## Steps Mode

Sequential command execution with optional parallel sub-blocks.

```yaml
name: my-feature-flow
description: Sequential plan → implement → review pipeline.
steps:
  - command: archon-plan
  - command: archon-implement
    clearContext: true            # fresh AI session for this step
    allowed_tools: [Read, Edit, Bash]
  - parallel:                     # concurrent sub-block (no nesting allowed)
      - command: archon-review-code
      - command: archon-review-tests
  - command: archon-create-pr
```

| Step field | Type | Default | Description |
|---|---|---|---|
| `command` | string | required | Command file name (no `.md` extension) |
| `clearContext` | bool | `false` | `true` = fresh AI session for this step |
| `allowed_tools` | string[] | all | Claude only. `[]` = MCP-only |
| `denied_tools` | string[] | none | Claude only. Remove named tools |
| `idle_timeout` | number (ms) | 300000 | Per-step inactivity timeout |

**Parallel block**: all children run concurrently via `Promise.all()`, each in a fresh session. Nested `parallel:` blocks are rejected.

**Steps vs DAG**: steps mode is linear + sub-parallel; DAG is a full graph with conditions and per-node types. Pick steps when you don't need conditional branching or structured output passing between nodes.

## Loop Mode (top-level)

Single autonomous loop. For multi-step loops use a DAG with a loop node instead.

```yaml
name: ralph-my-workflow
description: Iterative autonomous execution
loop:
  until: COMPLETE                 # required — completion signal
  max_iterations: 15              # required — integer ≥ 1
  fresh_context: true             # optional — default false (threaded)
prompt: |                         # required — supports $VARIABLE substitution
  Work on the next unfinished item in $ARTIFACTS_DIR/plan.md.
  When all done: <promise>COMPLETE</promise>
```

Completion detection: the AI emits `<promise>SIGNAL</promise>` (preferred, case-insensitive) or the signal on its own line at end of output.

## DAG Mode

The richest mode. Nodes are sorted topologically (Kahn's algorithm) and the same layer runs concurrently (`Promise.allSettled`).

```yaml
name: my-dag
description: Directed acyclic graph execution
nodes:
  - id: classify
    prompt: "Is this a bug? Answer JSON."
    model: haiku
    allowed_tools: []
    output_format:
      type: object
      properties:
        type: { type: string, enum: [BUG, FEATURE] }
      required: [type]

  - id: implement
    command: archon-implement
    depends_on: [classify]
    when: "$classify.output.type == 'BUG'"

  - id: lint
    bash: "pnpm lint"
    depends_on: [implement]
    timeout: 600000
```

### Node Fields (All Types Share These)

Base schema from `packages/workflows/src/schemas/dag-node.ts:113` (`dagNodeBaseSchema`):

| Field | Type | Default | Description |
|---|---|---|---|
| `id` | string | required | Unique. Used in `$<id>.output` references |
| `depends_on` | string[] | `[]` | Upstream node IDs — determines order |
| `when` | string | — | Condition expression (see below) |
| `trigger_rule` | string | `all_success` | Join semantics for deps |
| `provider` | `claude` \| `codex` | inherited | Per-node provider override |
| `model` | string | inherited | Per-node model override |
| `context` | `fresh` \| `shared` | — | `fresh` = new AI session; `shared` = inherit from upstream |
| `idle_timeout` | number (ms) | 300000 | Inactivity timeout (per-iteration on loop nodes) |
| `retry` | object | — | Retry config (not valid on loop nodes — hard error) |
| `output_format` | object | — | JSON Schema for structured output (Claude only) |
| `allowed_tools` | string[] | all | Tool whitelist (Claude only). `[]` = MCP-only |
| `denied_tools` | string[] | none | Tool blacklist (Claude only) |
| `hooks` | object | — | Per-node SDK hooks — see `archon-hooks-system` skill |
| `mcp` | string (path) | — | Relative path to MCP config JSON — see `archon-mcp-integration` skill |
| `skills` | string[] | — | Skill names to load into the node's AI session |
| `effort` | `low`\|`medium`\|`high`\|`max` | — | Claude reasoning effort level |
| `thinking` | string \| object | — | Claude `ThinkingConfig` shorthand or full object |
| `maxBudgetUsd` | number | — | Per-node USD budget cap |
| `systemPrompt` | string | — | Custom system prompt override |
| `fallbackModel` | string | — | Backup model if primary fails |
| `betas` | string[] | — | Array of beta feature flags to enable |
| `sandbox` | object | — | `SandboxSettings` — command + args for sandboxed execution |

## The Seven DAG Node Types

Exactly ONE of these fields must be set per node. Mutual exclusivity is enforced at parse time. From `packages/workflows/src/schemas/dag-node.ts`.

### 1. Command Node

Loads `.archon/commands/<name>.md` (user override) or `.archon/commands/defaults/<name>.md` (bundled). Same-named file in repo wins.

```yaml
- id: investigate
  command: investigate-bug
  context: fresh                  # optional — new AI session
  allowed_tools: [Read, Grep, Bash]
```

### 2. Prompt Node

Inline AI prompt. Good for short workflow-specific prompts.

```yaml
- id: classify
  prompt: |
    Classify this issue: $ARGUMENTS
  model: haiku
  allowed_tools: []
  output_format:
    type: object
    properties:
      issue_type: { type: string, enum: [bug, feature] }
    required: [issue_type]
```

### 3. Bash Node

Shell script, **no AI**. `stdout` → `$<id>.output`. `stderr` logged as warning.

```yaml
- id: fetch-data
  bash: |
    set -e
    gh issue view $ARGUMENTS --json title,body
  timeout: 30000                  # ms, default 120000 (2 min)
```

### 4. Loop Node

AI prompt that iterates until a signal or external check.

```yaml
- id: implement
  depends_on: [plan]
  idle_timeout: 600000            # per-iteration
  loop:
    prompt: |
      Read plan, work next unchecked item. Signal <promise>DONE</promise>.
    until: DONE                   # required
    max_iterations: 15            # required
    fresh_context: true           # false = threaded, true = ralph-stateless
    until_bash: "pnpm test"       # optional — exit 0 = done (alternate signal)
```

**Never set `retry:` on a loop node** — hard parse error. Loop nodes have their own retry via `max_iterations`.

### 5. Script Node (v0.3.3+)

TypeScript or Python via `bun` or `uv`. **Not** AI — deterministic like bash, but with dependency installation.

```yaml
- id: parse-diff
  script: |
    // TypeScript inline — runs under bun
    const diff = await Bun.file(`${process.env.ARTIFACTS_DIR}/pr.diff`).text();
    console.log(JSON.stringify({ lineCount: diff.split("\n").length }));
  runtime: bun                    # required — 'bun' | 'uv'
  deps: ["@octokit/rest@21"]      # optional — installed before run
  timeout: 60000
```

Or reference a file:

```yaml
- id: parse-diff
  script: parse-diff.ts           # resolves to .archon/scripts/parse-diff.ts
  runtime: bun
```

Script node semantics are the same as bash: stdout → `$<id>.output`, AI-specific fields are ignored with a warning.

### 6. Approval Node

Pauses workflow execution and waits for human input. The message is shown in the UI / CLI / GitHub comment.

```yaml
- id: gate
  approval:
    message: "Deploy to production?"
    capture_response: true        # optional — true = record reviewer response
    on_reject:                    # optional — run this prompt if rejected
      prompt: "Explain why deployment should wait and draft a fix plan."
      max_attempts: 3
  depends_on: [build, test]
```

On approval → workflow continues with downstream nodes. On rejection without `on_reject` → workflow cancels. With `on_reject` → the rejection prompt runs, user can re-approve.

### 7. Cancel Node

Terminates the workflow run with a reason. Useful as a conditional endpoint.

```yaml
- id: abort-if-draft
  cancel: "PR is in draft state — won't review until ready"
  depends_on: [fetch-pr]
  when: "$fetch-pr.output.isDraft == 'true'"
```

## Trigger Rules

| Rule | Behavior |
|---|---|
| `all_success` (default) | All upstreams must be `completed` |
| `one_success` | At least one upstream `completed` |
| `none_failed_min_one_success` | No upstream `failed` AND ≥1 `completed` (skipped OK) |
| `all_done` | All upstreams terminal (completed, failed, or skipped all count) |

Use `all_done` on cleanup/reporting nodes that should run even if upstream failed.

## Conditions (`when:`)

Pattern: `$nodeId.output[.field] OPERATOR 'value'`

- **Operators**: `==`, `!=` only
- **Field access**: dot-notation into JSON from `output_format` nodes
- **Values**: single-quoted string literals
- **Fail behavior**: unparseable → `false` → node skipped (fail-closed)

```yaml
when: "$classify.output.issue_type == 'bug'"
when: "$scope.output.complexity != 'trivial'"
```

## Structured Output (`output_format`)

Command/prompt nodes only. Enables typed field access downstream.

```yaml
- id: classify
  prompt: "Classify: $ARGUMENTS"
  model: haiku
  allowed_tools: []
  output_format:
    type: object
    properties:
      issue_type:
        type: string
        enum: [bug, feature, enhancement]
    required: [issue_type]
```

Downstream `$classify.output.issue_type` resolves to the JSON field, not the raw text.

## Complete Variable Substitution Reference

### Standard variables (all modes)

| Variable | Replaced with |
|---|---|
| `$ARGUMENTS` | Full user message string |
| `$USER_MESSAGE` | Alias for `$ARGUMENTS` |
| `$WORKFLOW_ID` | Workflow run UUID |
| `$ARTIFACTS_DIR` | Absolute path to run artifacts directory (pre-created) |
| `$BASE_BRANCH` | Base branch from config or auto-detected |
| `$CONTEXT` | GitHub issue/PR context (empty string if none) |
| `$EXTERNAL_CONTEXT` | Same as `$CONTEXT`, explicit external-context form |
| `$ISSUE_CONTEXT` | GitHub issue-specific context |
| `$PLAN` | Previous plan from session metadata |
| `$IMPLEMENTATION_SUMMARY` | Previous execution summary |

### Positional (command handler)

| Variable | Replaced with |
|---|---|
| `$1`..`$9` | Positional args split from user message |
| `$ARGUMENTS` | All args joined |
| `\$` | Literal `$` (escape) |

### DAG node output references

| Variable | Replaced with |
|---|---|
| `$nodeId.output` | Full stdout/text output |
| `$nodeId.output.field` | JSON field (requires upstream `output_format`) |

In bash scripts, substituted values are **auto shell-quoted** for safety.

## Validation Rules (Load-Time Errors)

From `packages/workflows/src/loader.ts:370-439`:

1. **Unique node IDs** — no duplicates
2. **Valid `depends_on`** — all referenced IDs must exist
3. **No cycles** — Kahn's algorithm; cycles fail with involved IDs
4. **Valid `$nodeId.output` references** — scanned in `when:`, `prompt:`, and `loop.prompt:` fields. The word must match a real node ID.
5. **Exactly one node type per node** — command/prompt/bash/loop/script/approval/cancel are mutually exclusive
6. **`retry:` on loop node** = hard error
7. **`steps:` + `nodes:` together** = error
8. **Model validation** — invalid provider/model combos fail at load
9. **`script:` nodes must have `runtime:`** — `'bun' | 'uv'`
10. **`approval.message` / `cancel` cannot be empty strings**

Run `archon validate workflows <name>` after every edit.

## Discovery and Loading

From `loader.ts:discoverWorkflows()`:

1. Searches `.archon/workflows/` recursively for `*.yaml` and `*.yml`
2. Merges bundled defaults (`/Users/jv/Archon/.archon/workflows/defaults/*.yaml`) with repo-specific workflows
3. Repo workflows **override** bundled defaults when names match
4. One broken YAML doesn't abort discovery — errors appear in `WorkflowLoadResult.errors`
5. Opt-out bundled defaults via `.archon/config.yaml`:
   ```yaml
   defaults:
     loadDefaultWorkflows: false
     loadDefaultCommands: false
   ```

## Traps the Public Docs Don't Warn About

### Trap #1 — Literal `$nodeId.output` in prompt text

The validator greps `prompt:`, `loop.prompt:`, and `when:` fields for the `$<word>.output` pattern and demands the word be a real node. If you write a prompt containing instructional text like *"reject any dangling `$nodeId.output` reference"*, the validator treats `$nodeId.output` as a real reference and fails.

**Workaround**: describe the pattern in prose. Write "output reference (dollar-sign plus node id plus .output)" instead of the literal.

### Trap #2 — `context: fresh` on loop nodes is ignored

Loop nodes accept `context: fresh` at the node level but **ignore it**. Use `loop.fresh_context: true` instead. Silent trap.

### Trap #3 — `provider` / `model` on loop nodes are accepted but ignored

Loop node prompts inherit the workflow-level provider/model. Overrides at the loop node silently do nothing.

### Trap #4 — Bash/script timeout default is 120 seconds

`pnpm install`, `pnpm typecheck`, and full builds routinely blow past this. Bump bash/script node `timeout:` to 600000–1200000 ms for install/build steps.

### Trap #5 — `--resume` skips completed loop iterations

`archon workflow run <wf> --resume` skips already-completed nodes, including loop nodes whose outer run completed. If you wanted a loop to re-iterate on resume, don't use `--resume`.

### Trap #6 — Angle brackets in prompt text survive into generated files

If a prompt instructs the AI to write Vue templates with literal `<` characters ("Float < 20M"), Vue's parser rejects them as `invalid-first-character-of-tag-name`. Tell the AI to escape as `&lt;`.

### Trap #7 — Parallel in steps mode vs DAG layers

Steps mode has an explicit `parallel:` sub-block. DAG mode has implicit concurrency via same-layer nodes (two nodes with no dep between them run in parallel). These are different mechanisms. Don't confuse the two.

### Trap #8 — Script nodes don't get AI-field warnings at the right level

If you put `allowed_tools:` or `model:` on a script node, it loads fine but those fields are silently ignored. The loader emits a warning log (`script_node_ai_fields_ignored`) but validation still passes.

## Canonical DAG Patterns

### Pattern A — Scan → Analyze → Implement → Validate → PR

```yaml
nodes:
  - id: preflight
    bash: |
      set -e
      if [ ! -d node_modules ]; then pnpm install --frozen-lockfile 2>&1 | tail -5; fi
      if [ ! -f .nuxt/eslint.config.mjs ]; then pnpm nuxi prepare 2>&1 | tail -10; fi
    timeout: 600000

  - id: scan
    bash: |
      set -e
      grep -rl "pattern" server/
    depends_on: [preflight]

  - id: plan
    prompt: "Design the fix. Context: $scan.output"
    depends_on: [scan]

  - id: implement
    prompt: "Execute plan in $ARTIFACTS_DIR/plan.md"
    depends_on: [plan]
    context: fresh

  - id: validate
    bash: |
      pnpm lint 2>&1 | tail -30 || true
      pnpm typecheck 2>&1 | tail -30 || true
    depends_on: [implement]
    timeout: 900000

  - id: create-pr
    prompt: "Create draft PR via `gh pr create --draft`. Report URL."
    depends_on: [validate]
    context: fresh
```

### Pattern B — Read-only audit / report

```yaml
nodes:
  - id: scan
    bash: "grep -rn 'pattern' app/"
  - id: analyze
    prompt: "Classify $scan.output"
    depends_on: [scan]
  - id: report
    prompt: "Write $ARTIFACTS_DIR/report.md. DO NOT edit source files."
    depends_on: [analyze]
    allowed_tools: [Read, Grep, Glob, Write, Bash]
```

### Pattern C — Ralph-style stateless loop

```yaml
nodes:
  - id: setup
    bash: "echo 'ready' > $ARTIFACTS_DIR/state.txt"
  - id: implement
    depends_on: [setup]
    idle_timeout: 600000
    loop:
      prompt: |
        FRESH session — no memory. Read $ARTIFACTS_DIR/plan.md,
        do one unchecked task, mark it done. When all done:
        <promise>COMPLETE</promise>
      until: COMPLETE
      max_iterations: 20
      fresh_context: true
      until_bash: "grep -qE '^- \\[ \\]' $ARTIFACTS_DIR/plan.md && exit 1 || exit 0"
```

### Pattern D — Approval gate

```yaml
nodes:
  - id: plan
    command: archon-plan
  - id: review-plan
    approval:
      message: "Approve the plan above? (yes/no)"
      capture_response: true
      on_reject:
        prompt: "Revise the plan addressing the reviewer's concerns, then present again."
        max_attempts: 3
    depends_on: [plan]
  - id: implement
    command: archon-implement
    depends_on: [review-plan]
```

### Pattern E — Conditional routing with cancel

```yaml
nodes:
  - id: fetch-pr
    bash: "gh pr view $ARGUMENTS --json isDraft,number"
    output_format:
      type: object
      properties:
        isDraft: { type: boolean }
      required: [isDraft]

  - id: abort
    cancel: "PR is in draft state — won't review until ready"
    depends_on: [fetch-pr]
    when: "$fetch-pr.output.isDraft == 'true'"

  - id: review
    command: archon-smart-pr-review
    depends_on: [fetch-pr]
    when: "$fetch-pr.output.isDraft == 'false'"
```

## Description Conventions (Critical for Router)

The Archon router picks workflows by asking an AI (via `packages/workflows/src/router.ts`) to match user messages against workflow descriptions. Description quality is the most important performance tuning knob.

Always include:

- **Use when**: one-sentence problem statement
- **Triggers**: 4-6 natural phrases the user might say (these carry weight in the router prompt)
- **NOT for**: 2-3 anti-patterns, each pointing at the correct alternative workflow
- **Body**: 2-4 lines on what the workflow actually does end-to-end
- **Suggested branch**: `<prefix>/<slug>` — helps invoking agents pick meaningful branch names

## Testing and Validation

```bash
# Validate one
archon validate workflows <name>

# Validate all
archon validate workflows

# Validate command files
archon validate commands <command-name>

# Run with explicit worktree branch
archon workflow run <name> --branch <suggested_branch> "<message>"

# Run without worktree isolation
archon workflow run <name> --no-worktree "<message>"

# Resume a failed run
archon workflow run <name> --resume
```

When a workflow silently fails via the GitHub adapter, inspect the DB:

```sql
-- ~/.archon/archon.db
SELECT id, platform_type, platform_conversation_id, title, created_at
FROM remote_agent_conversations WHERE platform_type='github'
ORDER BY created_at DESC LIMIT 5;

SELECT workflow_name, status, started_at, completed_at, working_path
FROM remote_agent_workflow_runs ORDER BY started_at DESC LIMIT 5;

SELECT event_type, step_name, substr(data, 1, 200) as data, created_at
FROM remote_agent_workflow_events
WHERE workflow_run_id = '<run-id>' ORDER BY created_at;
```

## Source of Truth References

| Concern | File in Archon repo |
|---|---|
| Node type schemas | `packages/workflows/src/schemas/dag-node.ts` |
| Loop config schema | `packages/workflows/src/schemas/loop.ts` |
| YAML parsing + validation | `packages/workflows/src/loader.ts` |
| Steps + loop execution | `packages/workflows/src/executor.ts` |
| DAG execution | `packages/workflows/src/dag-executor.ts` |
| Condition evaluation | `packages/workflows/src/condition-evaluator.ts` |
| Model compatibility | `packages/workflows/src/model-validation.ts` |
| Variable substitution | `packages/workflows/src/utils/variable-substitution.ts` |
| Workflow router | `packages/workflows/src/router.ts` |
| Official reference | `.claude/docs/workflow-yaml-reference.md` |
