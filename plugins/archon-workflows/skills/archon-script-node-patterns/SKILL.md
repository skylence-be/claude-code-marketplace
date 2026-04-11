---
name: archon-script-node-patterns
description: Master the Archon script node type (v0.3.3+) — TypeScript via bun and Python via uv, inline vs file-based scripts, the deps field for dependency installation, timeout configuration, stdout capture for $nodeId.output, and patterns for common automation tasks (diff parsing, JSON manipulation, report generation, API calls). Use when writing deterministic script logic that's too complex for bash but shouldn't involve AI, or when porting inline bash heredocs to cleaner TypeScript/Python.
category: engineering
tags: [archon, script, typescript, python, bun, uv, automation]
related_skills: [archon-dag-workflow-authoring, archon-bundled-workflows]
---

# Archon Script Node Patterns

The `script:` node type was added in Archon v0.3.3 (April 10, 2026). It runs **TypeScript via bun** or **Python via uv** — deterministic like bash but with package dependency support. Use it when bash+jq gets awkward, or when you want types, or when you need a mature library ecosystem (HTTP clients, date math, diff parsing).

## When to Use This Skill

- Writing a workflow step that parses complex data structures (diffs, ASTs, JSON)
- Making HTTP API calls with retries and structured error handling
- Generating reports from multiple data sources
- Replacing long bash heredocs with typed code
- Running Python-ecosystem tools (pandas, numpy, transformers) inside a workflow

## Basic Syntax

```yaml
- id: parse-diff
  script: |
    // Inline TypeScript — runs under bun
    const diff = await Bun.file(`${process.env.ARTIFACTS_DIR}/pr.diff`).text();
    const lines = diff.split("\n");
    console.log(JSON.stringify({ lineCount: lines.length }));
  runtime: bun                  # required — 'bun' | 'uv'
  deps:                         # optional — installed before the script runs
    - "@octokit/rest@21"
  timeout: 60000                # optional — milliseconds
  depends_on: [fetch-pr]
```

**Required fields**:
- `script:` — inline code OR a filename relative to `.archon/scripts/`
- `runtime:` — `'bun'` (TypeScript/JavaScript) or `'uv'` (Python)

**Optional fields**:
- `deps:` — array of packages to install before running. Bun: `"package-name@version"`. uv/Python: `"package-name==version"` or any pip-compatible spec.
- `timeout:` — milliseconds; default 120000 (2 min). Bump for long-running tasks.

**Inherited from base node schema**: `id`, `depends_on`, `when`, `trigger_rule`, `idle_timeout`. No `model`, `provider`, `allowed_tools` — script nodes are deterministic, not AI.

## Inline vs File-Based

### Inline script

For short logic (<30 lines). Embeds the code directly in the YAML:

```yaml
- id: classify
  script: |
    const files = JSON.parse(
      await Bun.file(`${process.env.ARTIFACTS_DIR}/pr-files.json`).text()
    );
    const categories = { source: 0, test: 0, docs: 0 };
    for (const f of files) {
      if (f.filename.includes(".test.")) categories.test++;
      else if (f.filename.endsWith(".md")) categories.docs++;
      else categories.source++;
    }
    console.log(JSON.stringify(categories));
  runtime: bun
```

### File-based script

For anything over ~30 lines. Put the file at `.archon/scripts/<name>.{ts|py}` and reference by name:

```yaml
- id: generate-report
  script: generate-report.ts   # resolves to .archon/scripts/generate-report.ts
  runtime: bun
  deps: ["chalk@5", "zod@4"]
  timeout: 120000
```

File in `.archon/scripts/generate-report.ts`:

```typescript
#!/usr/bin/env bun
import { z } from "zod";
import chalk from "chalk";

const FindingSchema = z.object({
  path: z.string(),
  line: z.number(),
  severity: z.enum(["blocker", "suggestion", "nit"]),
});

const findings = z
  .array(FindingSchema)
  .parse(JSON.parse(await Bun.file(`${process.env.ARTIFACTS_DIR}/findings.json`).text()));

console.log(chalk.bold(`Found ${findings.length} findings`));
// ...
```

**Why file-based for non-trivial logic**:
- Actual editor syntax highlighting + type checking in your IDE
- Reusable across workflows (two YAML files can reference the same script)
- Easier to test with `bun run .archon/scripts/generate-report.ts` locally
- No YAML escaping gotchas for backticks, `${...}` interpolation, etc.

## Output Capture

Script nodes work exactly like bash nodes for output. **`stdout` is captured as `$<node-id>.output`**, available for downstream nodes. **`stderr` is forwarded as a warning log**, not captured as output.

For structured handoff between nodes, emit JSON to stdout and consume via `output_format` field access (on the consuming node):

```yaml
- id: classify-pr
  script: |
    console.log(JSON.stringify({
      complexity: "medium",
      hasTests: true,
      fileCount: 12
    }));
  runtime: bun
  output_format:
    type: object
    properties:
      complexity: { type: string, enum: [trivial, small, medium, large] }
      hasTests: { type: boolean }
      fileCount: { type: integer }
    required: [complexity, hasTests, fileCount]

- id: deep-review
  command: archon-code-review-agent
  depends_on: [classify-pr]
  when: "$classify-pr.output.complexity != 'trivial'"
```

## The `deps:` Field

### Bun runtime

```yaml
deps:
  - "@octokit/rest@21"
  - "zod@4"
  - "chalk@5"
  - "date-fns@3"
```

Bun resolves from npm. Pinning major versions is good practice. Packages install to a local cache the first time and persist for subsequent runs in the same worktree.

### uv runtime

```yaml
deps:
  - "httpx==0.27"
  - "pydantic==2.8"
  - "numpy>=2,<3"
  - "pandas"
```

`uv` resolves from PyPI. Pip-style version specifiers work. Install is fast thanks to uv's Rust-based resolver.

## Canonical Patterns

### Pattern 1 — Parse a GitHub PR diff

```yaml
- id: build-diff-map
  script: |
    interface File { filename: string; patch?: string }
    const files: File[] = JSON.parse(
      await Bun.file(`${process.env.ARTIFACTS_DIR}/pr-files.json`).text()
    );
    const valid: string[] = [];
    for (const f of files) {
      if (!f.patch) continue;
      let right = 0;
      for (const line of f.patch.split("\n")) {
        const hunk = line.match(/^@@ -\d+(?:,\d+)? \+(\d+)/);
        if (hunk) { right = parseInt(hunk[1]); continue; }
        if (right === 0) continue;
        if (line.startsWith("+++") || line.startsWith("---")) continue;
        if (line.startsWith("+") || line.startsWith(" ")) {
          valid.push(`${f.filename}:${right}`);
          right++;
        }
      }
    }
    await Bun.write(`${process.env.ARTIFACTS_DIR}/valid-lines.json`, JSON.stringify(valid));
    console.log(`valid=${valid.length}`);
  runtime: bun
  timeout: 30000
```

Replaces 20 lines of awk with 15 lines of typed TypeScript that's easier to maintain.

### Pattern 2 — Structured HTTP call with retries

```yaml
- id: check-ci-status
  script: |
    import httpx
    import os, sys, json

    repo = os.environ["REPO"]          # set via $REPO in bash prep step
    pr   = os.environ["PR_NUM"]
    tok  = os.environ["GITHUB_TOKEN"]

    r = httpx.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr}",
        headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"},
        timeout=30.0,
    )
    r.raise_for_status()
    pr_data = r.json()

    print(json.dumps({
        "mergeable": pr_data.get("mergeable"),
        "merge_state": pr_data.get("mergeable_state"),
        "checks_status": pr_data.get("status"),
    }))
  runtime: uv
  deps: ["httpx==0.27"]
  timeout: 60000
```

Python's `httpx` with automatic retries + timeouts is often cleaner than bash `curl | jq`.

### Pattern 3 — Generate a report from multiple artifacts

```yaml
- id: compile-report
  script: compile-report.ts   # .archon/scripts/compile-report.ts
  runtime: bun
  deps: ["marked@14", "date-fns@3"]
  timeout: 60000
```

`.archon/scripts/compile-report.ts`:

```typescript
import { marked } from "marked";
import { format } from "date-fns";

const dir = process.env.ARTIFACTS_DIR!;
const review = await Bun.file(`${dir}/review.json`).json();
const fixes  = await Bun.file(`${dir}/fix-summary.json`).json();
const stats  = await Bun.file(`${dir}/stats.json`).json();

const markdown = `
# Workflow Report — ${format(new Date(), "yyyy-MM-dd HH:mm")}

## Review
- Findings: ${review.findings.length}
- Verdict: ${review.verdict}

## Fixes
- Files changed: ${fixes.filesChanged}
- Commits: ${fixes.commits}

## Stats
- Total workflow duration: ${stats.durationMs}ms
- Nodes executed: ${stats.nodeCount}
`.trim();

// Write both markdown and pre-rendered HTML
await Bun.write(`${dir}/report.md`, markdown);
await Bun.write(`${dir}/report.html`, marked(markdown));

console.log(`report.md + report.html written`);
```

### Pattern 4 — Seeded randomization for testing

```yaml
- id: generate-fixtures
  script: |
    import random
    import json
    import os

    random.seed(42)
    fixtures = [
        {
            "id": f"test-{i}",
            "value": random.randint(1, 1000),
            "tags": random.sample(["a", "b", "c", "d"], k=2),
        }
        for i in range(100)
    ]
    with open(f"{os.environ['ARTIFACTS_DIR']}/fixtures.json", "w") as f:
        json.dump(fixtures, f)
    print(f"wrote {len(fixtures)} fixtures")
  runtime: uv
```

### Pattern 5 — Data validation before AI node

```yaml
- id: validate-input
  script: |
    import { z } from "zod";
    const Schema = z.object({
      issueNumber: z.number().int().positive(),
      title: z.string().min(1),
      body: z.string(),
      labels: z.array(z.string()),
    });
    const raw = JSON.parse(
      await Bun.file(`${process.env.ARTIFACTS_DIR}/issue.json`).text()
    );
    try {
      Schema.parse(raw);
      console.log("OK");
    } catch (e) {
      console.error("Validation failed:", e);
      process.exit(1);
    }
  runtime: bun
  deps: ["zod@4"]

- id: investigate
  command: archon-investigate-issue
  depends_on: [validate-input]
  when: "$validate-input.output == 'OK'"
```

The script node acts as a cheap gate — if validation fails, the AI node never runs. Saves tokens + time compared to letting the AI handle bad input.

## Environment Variables

Script nodes inherit:
- `ARTIFACTS_DIR` — path to the run's artifacts directory
- `WORKFLOW_ID` — workflow run UUID
- `BASE_BRANCH` — base branch from config or auto-detected
- All other env vars from the Archon server process (including `.env`-loaded secrets)

**Access in Bun**:
```typescript
const dir = process.env.ARTIFACTS_DIR!;
const runId = process.env.WORKFLOW_ID!;
```

**Access in Python**:
```python
import os
dir = os.environ["ARTIFACTS_DIR"]
run_id = os.environ["WORKFLOW_ID"]
```

## Traps and Gotchas

### Trap 1 — AI-specific fields are ignored (with a warning)

Script nodes have `model`, `provider`, `allowed_tools`, `denied_tools`, `output_format` (on the base schema) but they're silently ignored at runtime. The loader emits a `script_node_ai_fields_ignored` warning. Keeps working but feels subtle.

### Trap 2 — `deps:` runs fresh each time unless cached

In a fresh worktree, deps install on every first run. Subsequent runs in the same worktree use the cache. If a workflow creates a fresh worktree every invocation (typical for Archon), expect 5-10 extra seconds per run for dep install. Use the built-in `timeout:` field to accommodate.

### Trap 3 — `deps:` doesn't pin transitive versions

Bun's `bun install <pkg>@<ver>` installs the specified version but transitive deps resolve against the lockfile, or fresh if no lockfile. For reproducibility in production workflows, commit a `.archon/scripts/bun.lockb` (binary lockfile) alongside your `.ts` files and bun will respect it.

### Trap 4 — Python `uv run` script doesn't persist state

Each invocation starts a fresh Python process. There's no hidden global state between script nodes in the same DAG — pass data via `$ARTIFACTS_DIR/*.json` files.

### Trap 5 — Unix shebangs don't help

Don't prefix your script with `#!/usr/bin/env bun` or `#!/usr/bin/env python3`. The runtime is determined by the `runtime:` field. A shebang is just a comment.

### Trap 6 — stdout buffering on failure

If your script crashes mid-write, some stdout may be lost depending on buffering. For critical output, `console.log` line-by-line rather than accumulating a big string and flushing at the end.

### Trap 7 — Relative paths

`script: parse-diff.ts` resolves to `.archon/scripts/parse-diff.ts` relative to **the repo root**, not to the workflow file. Don't try `script: ../../scripts/parse-diff.ts` — path traversal is blocked.

## When to Use Script vs Bash vs AI Node

| Need | Best choice |
|---|---|
| Single command, no parsing | Bash |
| Pipe a few grep/jq/awk calls | Bash |
| Parse complex JSON, build structured output | Script (bun+TS) |
| HTTP API with retries and schema validation | Script (bun or uv) |
| Generate a report from multiple files | Script |
| Install a Python lib (pandas, numpy) | Script (uv) |
| Understand semantic content and make judgment calls | AI node (prompt or command) |
| Long-running AI with progress updates | Loop node |
| Pause for human review | Approval node |
| Fail loudly on invalid input | Script (with `process.exit(1)`) or Cancel node |

Rule of thumb: if the logic is deterministic and you'd write more than ~15 lines of shell + jq, port it to a script node. If it needs to "understand" what code or text means, use an AI node.

## Migration from Inline Bash

Before:

```yaml
- id: parse-findings
  bash: |
    jq -r '.findings[] | "\(.path):\(.line) \(.severity) \(.body)"' \
      $ARTIFACTS_DIR/review.json \
      | awk -F: 'BEGIN { blocker=0; suggestion=0 }
                 /blocker/ { blocker++ }
                 /suggestion/ { suggestion++ }
                 END { printf "{\"blocker\": %d, \"suggestion\": %d}\n", blocker, suggestion }'
```

After:

```yaml
- id: parse-findings
  script: |
    const review = await Bun.file(`${process.env.ARTIFACTS_DIR}/review.json`).json();
    const counts = { blocker: 0, suggestion: 0, nit: 0 };
    for (const f of review.findings ?? []) {
      counts[f.severity] = (counts[f.severity] ?? 0) + 1;
    }
    console.log(JSON.stringify(counts));
  runtime: bun
  output_format:
    type: object
    properties:
      blocker:    { type: integer }
      suggestion: { type: integer }
      nit:        { type: integer }
    required: [blocker, suggestion, nit]
```

Typed, more readable, downstream nodes get structured access via `$parse-findings.output.blocker`.

## Source of Truth

| Concern | File |
|---|---|
| Schema | `packages/workflows/src/schemas/dag-node.ts` (scriptNodeSchema ~line 199) |
| Type guard | `packages/workflows/src/schemas/dag-node.ts:601` (`isScriptNode`) |
| Runtime dispatch | `packages/workflows/src/dag-executor.ts` |
| Added in | CHANGELOG `## [0.3.3] - 2026-04-10` ("Script node type for DAG workflows") |
| Related issue | [#999](https://github.com/coleam00/Archon/issues/999) |
