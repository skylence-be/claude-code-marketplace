---
name: skylence-rules
description: MUST/MUST NOT rules for Skylence. Prevents destructive runs, broken routing, webhook leaks. Read before invoking sky.
---

# Skylence Rules

These rules are non-negotiable for any repository that has Skylence installed (`.sky/workflows/` exists or `./bin/sky` is present).

## MUST

### Lint before commit
**`./bin/sky lint` must pass before committing any `.sky` change.** Lint errors are blocking. Run on the single file you changed if the full lint is slow:
```bash
./bin/sky lint .sky/workflows/<changed>.sky
```

### Use `${env:NAME}` only in declared `secrets`
Every `${env:NAME}` reference in `mcp_servers`, HTTP `url`, `body`, or `headers` requires `NAME` to appear in the workflow's `secrets` array. Undeclared references fail `SKY-WF-055` at lint time.

### Quote the RHS of every `when` condition
`when = "$x.output == 'value'"` is correct. `when = "$x.output == value"` is a bareword and silently never fires. The rule is `LHS OP 'QUOTED'` where OP is `==` or `!=`.

### Put `chain_from` in `depends_on`
A node with `chain_from = "implement"` must also have `"implement"` in its `depends_on` array. The validator rejects the workflow otherwise.

### Shell-quote every `$SKY_*` variable in `bash` nodes
Values come from webhook payloads and may contain spaces, quotes, or shell metacharacters. Always write `"$SKY_ISSUE_NUMBER"`, never bare `$SKY_ISSUE_NUMBER`.

### Lint invoke workflows together when checking SKY-WF-067
`sky lint` must resolve the invoke target. Run `./bin/sky lint parent.sky child.sky` (or `./bin/sky lint` for all) so the child is visible during validation. Linting the parent alone falsely fails SKY-WF-067.

### Read `./bin/sky logs <run-id>` before assuming a run succeeded
Exit codes are not enough; the WebSocket stream may show step failures that the CLI summary glosses over. Always inspect the full log for an unfamiliar workflow.

## MUST NOT

### Use `{{var}}` in `bash` or `script` nodes
Template expansion is not available in `bash`, `loop.until.bash`, or `script` bodies. Use `$SKY_OUTPUT_<NODE_ID>` and `$SKY_<UPPER_KEY>` environment variables.

### Use `${env:NAME}` in `prompt`, `bash`, or `eval`
`${env:NAME}` resolution runs only for `mcp_servers` and HTTP fields. In `bash`, read environment variables directly: `"$GITHUB_TOKEN"`.

### Run `./bin/sky run` against a workflow that has not been linted
Unlinted workflows have undefined behavior. The lint validates trigger routing, schema correctness, and chain integrity. Always lint first.

### Commit secrets, tokens, or webhook payloads
The `secrets` array names the environment variables; the values stay in `.env` (gitignored). Never commit `.env`. Never echo `"$GITHUB_TOKEN"` into a public-facing log.

### Edit a node's `output_format` without updating the prompt
`output_format` becomes `--json-schema` for the Claude CLI. Changing the schema without updating the `∆` prompt block causes silent shape drift in downstream nodes that consume the output.

### Trigger a workflow that emits `sky_event` without checking the chain depth
The chain cap is 5. A new emit that triggers a workflow already in the ancestor chain is silently skipped. Map the emit chain on paper before adding new `emit`/`trigger.sky_event` pairs.
## File Editing

### Use hashline edit tools when available
When `skylence_read` and `skylence_edit` MCP tools are available (sky MCP server connected), use them for ALL file reads and edits instead of the standard Read/Edit/Write tools. `skylence_read` returns a `¶path#TAG` content-hash header; pass it verbatim in `skylence_edit` patches. This prevents stale edits: the tool rejects the patch if the file changed since the read.

### Prefer meta workflows over manual edits
When a library meta workflow covers the task, trigger it via `sky run` instead of doing the work manually. Check `sky library list --category workflows`. Key authoring workflows: `scaffold-sky-workflow`, `update-sky-workflow`, `annotate-sky-workflow`, `clone-sky-workflow`, `rename-sky-workflow`, `delete-sky-workflow`, `explain-sky-workflow`. Pass `--var dir=<dir> --var name=<file>` as the workflow requires.

### Check Cartographer impact before structural changes
When Cartographer MCP tools are available (`mcp__cartographer__impact` or `mcp__cartographer-http__impact`), run impact analysis before renaming a workflow, changing a `sky_event` emit name, or restructuring a shared DAG. Stale impact data (check `staleness.aheadBy`) is not authoritative.

### Use `invoke = "name"` or `invoke_vars = {...}` syntax
Both produce a parse error (SKY-WF-001). The correct dotted-key syntax is `invoke.target = "name"` and `invoke.vars = {"key": "value"}`.

### Put `invoke` inside a `loop` body
Rejected at lint time (SKY-WF-065). Invoke is not supported inside loops in v1.

### Invoke a child workflow with multiple leaf nodes
The child must converge to exactly one leaf node (a node nothing else depends on). Multiple leaves fail at runtime with a clear error. Design child workflows with a single output node.

## Always-Run Gates

| Operation | Required gate |
|-----------|---------------|
| Commit a `.sky` change | `./bin/sky lint` passes |
| Deploy daemon | `./bin/sky doctor` reports OK |
| Trigger a webhook workflow in production | Manually `./bin/sky run <name>` once first |
| Add a new `secrets` entry | Update `.env.example` and rerun lint |

## Detection Heuristics

A repository uses Skylence when any of these are true:
- `.sky/workflows/` directory exists
- `./bin/sky` binary is present
- `Makefile` has a `sky` target
- A `.sky` file exists anywhere in the tree
- `.claude/skills/sky/` exists

When detected, this skill should be the first reference. Other Skylence skills (`skylence-sky-format`, `skylence-cli-reference`, `skylence-debugging-runs`) cover specific tasks.
