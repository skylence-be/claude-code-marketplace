---
name: skylence-sky-format
description: .sky format: Unicode delimiters, trigger routing, node types (claude/bash/script/emit). Use when authoring .sky files.
---

# .sky File Format

A `.sky` file defines a DAG of execution nodes, plus metadata for trigger routing. The parser uses four Unicode delimiter blocks; every opener and closer must be alone on its line.

## Delimiter Blocks

```
⊕meta⊕         ⊕⊕      workflow identity + trigger routing
§<id>§         §§      DAG node config (model, depends_on, when, etc.)
∆<id>∆         ∆∆      Claude prompt body for node <id>
※※             ※※      doc / comment block (parser discards)
```

## Minimal Example

```
⊕meta⊕
name = "smoke-test"
description = "Manual smoke test"
trigger.manual = true
output_style = "terse"
⊕⊕

§work§
bash = "echo 'hello'"
§§
```

## `⊕meta⊕` Block

Required keys:
- `name` (string, kebab-case, matches filename)
- `description` (string)

Trigger options (exactly one required):
- `trigger.manual = true` for CLI-only via `./bin/sky run <name>`
- `trigger.github.event = "issues"` (or `pull_request`, `push`, `issue_comment`, etc.)
- `trigger.sky_event.event = "deploy.completed"` (subscribe to an emit from another workflow)
- `trigger.cron = "0 */6 * * *"` (cron schedule)

Optional:
- `output_style = "terse"` to compress all node responses
- `secrets = ["GITHUB_TOKEN", "OPENAI_API_KEY"]` to declare env vars used in `${env:NAME}` references
- `learnings.exclude = ["execution-rules", "patterns"]` to suppress learnings for the workflow
- `permissions = "interactive"` to gate destructive tool calls through user approval
- `mcp_servers = { name = { command = "...", args = [...], env = { KEY = "${env:KEY}" } } }`

## `§<id>§` Node Config Block

Identifies and configures one DAG node. Common keys:

| Key | Values | Notes |
|-----|--------|-------|
| `model` | `sonnet`, `opus`, `haiku` | Required for Claude prompt nodes |
| `effort` | `max` | Enables extended thinking |
| `depends_on` | `["nodeA", "nodeB"]` | Upstream nodes; output available as `$SKY_OUTPUT_<ID>` |
| `when` | `"$classify.output.type == 'bug'"` | RHS must be quoted; LHS may start with `$` |
| `trigger_rule` | `all_done` (default), `all_success`, `one_success`, `one_failure` | When this node runs relative to deps |
| `isolation` | `worktree`, `worktree-run` | Run in an isolated git worktree |
| `chain_from` | `"implement"` | Resumes prior node's Claude session; must also appear in `depends_on` |
| `output_format` | JSON Schema object | Passed as `--json-schema` to claude CLI |
| `max_turns` | integer >= 1 | Caps Claude reasoning turns |
| `bash` | shell command string | Replaces the Claude prompt; no `∆` block needed |
| `script` | `{"runtime": "bun" or "uv", "deps": [...], "timeout": ms}` | Deterministic data transform; no Claude session |
| `cancel` | `{"reason": "..."}` | Aborts the run; combine with `when` for a guard |
| `emit` | `{"name": "evt.name", "payload": {...}}` | Triggers any workflow with matching `trigger.sky_event` |
| `loop.until.bash` | shell command | Runs the node repeatedly until the command exits 0 |
| `http` | `{"url": "...", "method": "POST", "body": "...", "headers": {...}}` | HTTP call instead of a Claude prompt |

## `∆<id>∆` Prompt Body Block

The body sent to the Claude CLI for a prompt node. Plain markdown; `{{var}}` template expansion works here (unlike `bash` or `script`).

```
∆classify∆
You are a triage bot. Classify the GitHub issue and output JSON:

Issue: {{issue.title}}
Body: {{issue.body}}

Categories: bug, feature, question
∆∆
```

`{{var}}` filters available in HTTP bodies (not prompts):
- `{{var|json}}` injects the value as a JSON-escaped string
- `{{var|urlencode}}` escapes for query strings

## Variable Reference

| In | Use |
|----|-----|
| `prompt` (`∆` block) | `{{issue.title}}`, `{{repo.full_name}}`, `{{label}}` |
| `bash` node | `"$SKY_ISSUE_NUMBER"`, `"$SKY_REPO_FULL_NAME"`, `"$SKY_OUTPUT_CLASSIFY"` |
| `script` node | `process.env.SKY_OUTPUT_CLASSIFY` (or `os.environ` in Python) |
| `mcp_servers` / `http` | `${env:GITHUB_TOKEN}` (declared in `secrets`) |
| `when` condition | `$classify.output.type` (single quotes around the RHS) |

Webhook payload keys are flattened: `issue.number` becomes `$SKY_ISSUE_NUMBER`, `repo.full_name` becomes `$SKY_REPO_FULL_NAME`, etc.

## Node Type Quick Pick

| Want to | Use |
|---------|-----|
| Ask Claude to reason | `model = "sonnet"` plus a `∆` block |
| Run a shell command | `bash = "..."` (no `∆` needed) |
| Transform JSON deterministically | `script = {"runtime": "bun", "deps": [...]}` |
| Call an HTTP API | `http = {"url": "...", "method": "POST", ...}` |
| Loop until condition met | `loop.until.bash = "test -f flag"` |
| Abort the run conditionally | `cancel = {"reason": "..."}` plus `when = "..."` |
| Trigger another workflow | `emit = {"name": "...", "payload": {...}}` |

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Bareword RHS in `when` | Node never fires | Quote: `"$x.output == 'bug'"` |
| `chain_from` not in `depends_on` | Lint error `SKY-WF-040` | Add the chain target to `depends_on` |
| Bare `{{var}}` in `http.body` JSON | Lint error `SKY-WF-047` | Use `{{var|json}}` |
| Undeclared `${env:NAME}` | Lint error `SKY-WF-055` | Add `NAME` to `secrets` array |
| `output_format` schema mismatch | Lint error `SKY-WF-060` | Fix the schema or align the prompt |
| Unquoted `$SKY_*` in bash | Shell injection or whitespace bugs | Always quote: `"$SKY_VAR"` |
| `set_var` reading webhook value | Edition 2024: unsafe | Pass via `$SKY_*` env var instead |
