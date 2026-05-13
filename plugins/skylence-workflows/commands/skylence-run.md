---
description: Run a Skylence workflow with live event streaming, reporting the run-id and final status
---

# Run a Skylence Workflow

Trigger a `.sky` workflow via `./bin/sky run` (or the REST API), stream the live event log, and report the final status with the run-id.

## Specification

$ARGUMENTS

## Process

1. **Confirm the workflow exists**: check `.sky/workflows/<name>.sky` (filename without `.sky`)
2. **Lint first**: run `./bin/sky lint .sky/workflows/<name>.sky`; abort if it fails
3. **Confirm the daemon is running**: `./bin/sky doctor` reports the daemon port; start with `./bin/sky serve` if not
4. **Run the workflow**: `./bin/sky run <name>` (add `--vars k=v` for each variable the workflow consumes)
5. **Stream events**: capture the run-id from the output, then `./bin/sky stream <run-id>` for live updates
6. **Report the final status**: read `./bin/sky logs <run-id>` for the per-step breakdown, and identify any failed or skipped node

## Examples

### Manual workflow

```bash
./bin/sky lint .sky/workflows/smoke-test.sky
./bin/sky run smoke-test
# output includes: run-id <id>
./bin/sky logs <id>
```

### With variables

```bash
./bin/sky run triage-issue --vars issue.number=42 --vars issue.title="bug in login"
```

### Streaming the live event feed

```bash
./bin/sky run long-running-flow
# capture run-id
./bin/sky stream <run-id>
# or via WebSocket:
wscat -c "ws://127.0.0.1:3090/api/ws" -H "Authorization: Bearer $SKY_API_KEY"
```

### REST API trigger (alternative)

```bash
curl -X POST http://127.0.0.1:3090/api/runs \
  -H "Authorization: Bearer $SKY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"workflow": "triage-issue", "vars": {"issue": {"number": 42}}}'
```

If the run failed, invoke the `skylence-debugging-runs` skill or the `skylence-workflow-author` agent for diagnosis.
