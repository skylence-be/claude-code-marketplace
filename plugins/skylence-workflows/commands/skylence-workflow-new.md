---
description: Scaffold a new .sky workflow with valid four-delimiter format, a chosen trigger, and a starter node DAG
---

# New Skylence Workflow

Scaffold a new `.sky` workflow file in `.sky/workflows/` with valid format, a chosen trigger, and one or more starter nodes.

## Specification

$ARGUMENTS

## Process

1. **Determine the workflow name** from the specification (kebab-case, must match the filename without `.sky`)
2. **Choose exactly one trigger**: `manual`, `github`, `sky_event`, or `cron`
3. **Identify required secrets** if any `${env:NAME}` references will be needed in `mcp_servers` or HTTP fields
4. **Decide the node DAG**: claude prompt, bash, script, http, invoke, or a mix; map `depends_on` between them
5. **Write the `.sky` file** in `.sky/workflows/<name>.sky` with `⊕meta⊕`, `§<id>§`, and `∆<id>∆` blocks
6. **Run `./bin/sky lint .sky/workflows/<name>.sky`** and fix every reported error
7. **Manual trigger workflow only**: run `./bin/sky run <name>` to smoke-test

## Examples

### Manual smoke test

```
⊕meta⊕
name = "smoke-test"
description = "Manual smoke test"
trigger.manual = true
output_style = "terse"
⊕⊕

§work§
bash = "echo 'smoke work done'"
§§
```

### GitHub issue triage with structured output

```
⊕meta⊕
name = "triage-issue"
description = "Classify a new GitHub issue and add a label"
trigger.github.event = "issues"
secrets = ["GITHUB_TOKEN"]
⊕⊕

§classify§
model = "sonnet"
output_format = {"type": "object", "properties": {"issue_type": {"type": "string", "enum": ["bug", "feature", "question"]}, "reasoning": {"type": "string"}}, "required": ["issue_type", "reasoning"]}
§§

∆classify∆
Classify this GitHub issue. Return JSON with `issue_type` and `reasoning`.

Title: {{issue.title}}
Body: {{issue.body}}
∆∆

§label§
bash = """
curl -sS -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$SKY_REPO_FULL_NAME/issues/$SKY_ISSUE_NUMBER/labels" \
  -d "{\"labels\":[\"$(echo "$SKY_OUTPUT_CLASSIFY" | jq -r '.issue_type')\"]}"
"""
depends_on = ["classify"]
§§
```

### Chained workflow via emit

```
⊕meta⊕
name = "deploy"
description = "Run deploy script then emit completion event"
trigger.manual = true
⊕⊕

§run§
bash = "./scripts/deploy.sh"
emit = {"name": "deploy.completed", "payload": {"env": "prod"}}
§§
```

The subscriber workflow lives in a separate `.sky` file:

```
⊕meta⊕
name = "notify-on-deploy"
description = "Slack notify when deploy completes"
trigger.sky_event.event = "deploy.completed"
secrets = ["SLACK_WEBHOOK_URL"]
⊕⊕

§notify§
http = {"url": "${env:SLACK_WEBHOOK_URL}", "method": "POST", "body": "{\"text\": \"deploy complete in prod\"}"}
§§
```

### Invoke: synchronous sub-workflow call

Parent workflow blocks until the child finishes; the child's leaf output becomes the invoke node's output.

```
⊕meta⊕
name = "parent-workflow"
description = "Calls a child workflow and verifies its output"
trigger.manual = true
⊕⊕

§call-child§
invoke.target = "child-workflow"
invoke.vars = {"greeting": "hello from parent"}
§§

§verify§
eval = {"source": "$call-child.output", "contains": "expected text"}
depends_on = ["call-child"]
§§
```

The child workflow must have exactly one leaf node (a node nothing else depends on). Use `invoke.target` and `invoke.vars` (not `invoke = "name"` or `invoke_vars`). Lint both files together: `./bin/sky lint parent.sky child.sky`.

### Cancel guard for label-gated workflows

```
⊕meta⊕
name = "review-on-ready"
description = "Run review when ready-for-sky label is set"
trigger.github.event = "pull_request"
⊕⊕

§guard§
cancel = {"reason": "label mismatch; skipping"}
when = "{{label}} != 'ready-for-sky'"
§§

§review§
model = "sonnet"
depends_on = ["guard"]
§§

∆review∆
Review PR #{{pull_request.number}}.
∆∆
```

After writing the file, always run `./bin/sky lint` and fix every error before committing.
