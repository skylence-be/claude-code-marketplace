---
name: skylence-debugging-runs
description: Debug Skylence runs: sky logs, failure modes (lint, when, chain_from). Use when a run fails or hangs.
---

# Debugging Skylence Runs

When a workflow run fails or behaves unexpectedly, this is the diagnostic flow.

## Step 1: Read the Log

```bash
./bin/sky logs                  # list recent runs with status
./bin/sky logs <run-id>         # full run record + per-step status
```

Output sections to look at:
- **Run summary**: status (`completed`, `failed`, `cancelled`, `running`), duration, trigger
- **Step list**: each node's status (`pending`, `running`, `completed`, `failed`, `skipped`, `cancelled`)
- **Step output**: stdout (Claude response, bash output, script output)
- **Step error**: stderr or daemon-captured error

A `skipped` status means the node's `when` condition evaluated to `false` (or its trigger rule was not met).

## Step 2: Stream Live Events

For a still-running workflow:

```bash
./bin/sky stream <run-id>
```

Or via WebSocket:

```bash
wscat -c "ws://127.0.0.1:3090/api/ws" -H "Authorization: Bearer $SKY_API_KEY"
```

Event types: `run.started`, `step.started`, `step.output` (per chunk), `step.completed`, `run.completed`, `run.failed`.

## Common Failure Modes

### `when` condition silently never fires

**Symptom:** Node status is `skipped` and you expected it to run.

**Cause:** RHS is a bareword instead of a quoted value.

```
# WRONG: bareword, always evaluates false
when = "$classify.output.type == bug"

# CORRECT:
when = "$classify.output.type == 'bug'"
```

Verify the upstream output matches by reading `$SKY_OUTPUT_CLASSIFY` from the previous step's output.

### `chain_from` rejects at lint

**Symptom:** `SKY-WF-040` from `./bin/sky lint`.

**Cause:** `chain_from = "X"` without `"X"` in `depends_on`.

**Fix:** Add the chain target to `depends_on`:

```
§self-fix§
chain_from = "implement"
depends_on = ["synthesize", "implement"]
§§
```

### `bash` node fails on a variable

**Symptom:** `parameter not set` or weird shell injection.

**Cause:** Variable was unquoted, contained a space, or `{{var}}` was used (which does not expand in `bash`).

**Fix:** Always quote, always use `$SKY_*`:

```bash
# WRONG
echo {{issue.number}}
echo $SKY_ISSUE_NUMBER

# CORRECT
echo "$SKY_ISSUE_NUMBER"
```

### `${env:NAME}` reference does not resolve

**Symptom:** Lint error `SKY-WF-055`, or MCP server fails to start.

**Cause:** `NAME` is not declared in the workflow's `secrets` array.

**Fix:**

```
⊕meta⊕
secrets = ["GITHUB_TOKEN"]
⊕⊕

§call§
mcp_servers = { gh = { command = "...", env = { GITHUB_TOKEN = "${env:GITHUB_TOKEN}" } } }
§§
```

Also confirm the actual env var is set in the daemon's environment (`./bin/sky doctor` checks the most common ones).

### Workflow does not trigger on webhook

**Symptom:** `gh api ...` shows the webhook delivery succeeded but no run was created.

**Cause one:** Trigger filter mismatch. `trigger.github.event = "issues"` only matches issue events, not pull requests.

**Cause two:** A `cancel` guard fired before any real work. Read the run log; a cancelled run with one `cancel` step is the smoking gun.

**Cause three:** The daemon was not running. `./bin/sky doctor` will report.

### `output_format` schema validation fails

**Symptom:** Claude returns JSON that does not match the schema; downstream node consuming `$SKY_OUTPUT_X` parses garbage.

**Cause:** Schema and prompt drifted.

**Fix:** Re-read the `∆` prompt block and confirm it explicitly instructs Claude to produce the schema. Belt-and-suspenders: keep the schema in the prompt as well.

### `emit` triggers nothing

**Symptom:** A node emits `deploy.completed` but no subscriber workflow runs.

**Causes (in order):**
1. The subscriber workflow's `trigger.sky_event.event` does not exactly match the emit name.
2. Chain depth exceeded 5 (cycle guard or deep recursion).
3. The subscriber workflow is in the ancestor chain (cycle guard skipped it).

## Step 3: Diagnose with `doctor`

```bash
./bin/sky doctor
```

Checks: Go version, Claude CLI version, daemon process, port 3090 binding, SQLite DB integrity, `$SKY_API_KEY`, common env vars. Output is a checklist with `OK` / `FAIL` per item.

## Step 4: Re-run with a Smaller Slice

If the run hits a complex DAG and you cannot isolate the failure:
1. Copy the workflow to `.sky/workflows/<name>-minimal.sky`.
2. Strip all but the failing node and its direct dependencies.
3. Lint and run with `--vars k=v` to reproduce the failure.

## Step 5: Consult the Runbook

The repo's own `docs/runbook.md` covers operational failure modes (daemon crash, SQLite corruption, port collision, Claude CLI auth expiry). Read it before opening an issue.
