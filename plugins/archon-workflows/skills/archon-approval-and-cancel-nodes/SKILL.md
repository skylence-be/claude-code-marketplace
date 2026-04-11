---
name: archon-approval-and-cancel-nodes
description: Master Archon's human-in-the-loop and workflow-termination node types — the approval node (message, capture_response, on_reject prompt + max_attempts retry loop), the cancel node (reason string, CancelWorkflowError propagation, downstream node fate), session resume across approval pauses, and how the approval message lands in each platform adapter (Slack, Telegram, GitHub, Discord, Web). Use when building workflows that need human gates before proceeding, terminating early on conditional state, or debugging why an approval didn't surface in the expected UI.
category: engineering
tags: [archon, approval, cancel, human-in-the-loop, workflow-control]
related_skills: [archon-dag-workflow-authoring, archon-architecture-deep-dive]
---

# Archon Approval and Cancel Nodes

Two DAG node types that control workflow flow without invoking the AI. Approval nodes pause for human input; cancel nodes terminate the run with a reason. Both schemas are defined in `packages/workflows/src/schemas/dag-node.ts`.

## When to Use This Skill

- Building a workflow that needs a human gate before destructive actions (deploys, merges, schema migrations)
- Adding a plan-review checkpoint between planning and implementation phases
- Terminating a workflow early when a precondition fails (PR is draft, CI failing, etc.)
- Understanding how approval messages surface differently per adapter
- Debugging why an approval loop retries indefinitely or a cancel skips too many downstream nodes

## Approval Node

### Schema

From `packages/workflows/src/schemas/dag-node.ts:247`:

```yaml
- id: gate
  approval:
    message: "Approve the plan?"       # required, non-empty string
    capture_response: true             # optional — record reviewer response
    on_reject:                         # optional — retry loop on rejection
      prompt: |                        # required if on_reject is set
        Revise addressing the reviewer's concerns, then present again.
      max_attempts: 3                  # optional — default 3, range 1-10
  depends_on: [plan]
```

**Fields**:

| Field | Type | Default | Description |
|---|---|---|---|
| `approval.message` | string | **required** | The prompt shown to the human reviewer |
| `approval.capture_response` | boolean | `false` | Record reviewer's free-form response (stored on session, usable downstream) |
| `approval.on_reject` | object | — | Retry loop config for rejection case |
| `approval.on_reject.prompt` | string | **required if `on_reject` set** | Prompt re-sent to the AI to revise and re-present |
| `approval.on_reject.max_attempts` | integer (1-10) | 3 | Max revision attempts before workflow cancels |

### Behavior

1. Node runs → Archon sends `approval.message` to the platform adapter via `platform.sendMessage()`.
2. Workflow **suspends** — the DAG executor halts this node's layer and waits.
3. User responds. Recognized responses:
   - **Approve**: `yes`, `y`, `approve`, `approved`, `lgtm`, `looks good`, `ok`, `okay` (case-insensitive)
   - **Reject**: `no`, `n`, `reject`, `rejected`, `deny`, `denied` (case-insensitive)
   - **Freeform with `capture_response: true`**: any other response is stored as the reviewer's comment and treated as an approval with context
4. **On approve** → workflow resumes with downstream nodes.
5. **On reject with no `on_reject`** → workflow cancels (treated as `CancelWorkflowError`).
6. **On reject with `on_reject`**:
   - The `on_reject.prompt` is dispatched to the AI with the rejection context
   - AI produces a revised output
   - Approval message re-sent
   - Counter increments
   - After `max_attempts` consecutive rejections → workflow cancels

### Canonical Patterns

**Pattern 1 — Plan review checkpoint**:

```yaml
nodes:
  - id: plan
    command: archon-create-plan

  - id: review-plan
    approval:
      message: |
        Plan draft ready. Approve to continue to implementation?
        Review $ARTIFACTS_DIR/plan.md before deciding.
      capture_response: true
      on_reject:
        prompt: |
          The reviewer rejected the plan. Read their feedback in the
          conversation history and revise $ARTIFACTS_DIR/plan.md to address
          the concerns. Then present the revised plan.
        max_attempts: 3
    depends_on: [plan]

  - id: implement
    command: archon-implement
    depends_on: [review-plan]
```

**Pattern 2 — Destructive action gate**:

```yaml
- id: confirm-deploy
  approval:
    message: |
      ⚠️ About to deploy to production.
      Commit: $git-info.output.sha
      Changed files: $git-info.output.changedFiles
      Approve?
    capture_response: false
  depends_on: [git-info, preflight-checks]

- id: deploy
  bash: "bun run deploy:prod"
  depends_on: [confirm-deploy]
  timeout: 1200000
```

Cancels the workflow if the reviewer rejects — without `on_reject`, there's no retry loop, it's a hard gate.

**Pattern 3 — Freeform response capture**:

```yaml
- id: get-priority
  approval:
    message: "What priority should this fix have? (P0/P1/P2/P3 or freeform)"
    capture_response: true
  depends_on: [classify]

- id: route-by-priority
  prompt: |
    Reviewer said: <reviewer response from $get-priority>
    Route to the appropriate workflow based on stated priority.
  depends_on: [get-priority]
```

With `capture_response: true`, the reviewer's freeform text becomes available as conversation context in downstream AI nodes.

### Per-Adapter Behavior

How the approval message surfaces in each platform:

| Adapter | Presentation | User responds via |
|---|---|---|
| **Slack** | Single message via `chat.postMessage`. No button UI. | Reply in the same thread (channel:ts lookup) |
| **Telegram** | Single message via `sendMessage`. | Reply in the same chat |
| **GitHub** | Single comment via `gh pr comment`. Must be `@archon`-mentioned in response. | Reply on the PR/issue with `@archon approved` or `@archon rejected: <reason>` |
| **Discord** | Single message in the conversation channel | Reply in the same channel |
| **Web** | Message with a visual approve/reject button pair in the UI | Click button OR type response |

**Web is the only adapter with native button UI.** All other platforms rely on text responses that Archon pattern-matches.

### Timeout Behavior

Approval nodes inherit the node-level `idle_timeout` (default 300000ms = 5 minutes). If no response lands within the idle timeout, the node times out and the workflow cancels with a `workflow_idle_timeout` error.

For long approval gates (waiting overnight for a human), bump explicitly:

```yaml
- id: gate
  idle_timeout: 86400000              # 24 hours
  approval:
    message: "Approve overnight deploy?"
```

### Limitations

- **No multi-reviewer approval**: first response wins. You can't require 2-of-3 approvers.
- **No scheduled approval reminders**: if no one responds in `idle_timeout`, the node times out — no reminder pings.
- **Session resume after long pauses**: the SDK session is preserved across approval waits via `assistant_session_id`. See `archon-architecture-deep-dive` for how session lifecycle handles pauses.
- **Can't resume after workflow cancel**: if `max_attempts` exhausts and the workflow cancels, you can't "reopen" the same run — invoke the workflow again from scratch.

## Cancel Node

### Schema

From `packages/workflows/src/schemas/dag-node.ts:269`:

```yaml
- id: abort-if-draft
  cancel: "PR is in draft state — won't review until ready"   # required, non-empty string
  depends_on: [fetch-pr]
  when: "$fetch-pr.output.isDraft == 'true'"
```

**Fields**: Just `cancel:` — a non-empty string used as the termination reason. That's it. All base node fields (`depends_on`, `when`, etc.) work normally.

### Behavior

When a cancel node fires:

1. Archon throws `CancelWorkflowError` with the provided reason
2. The DAG executor catches it and marks the current layer as **cancelled**
3. All **downstream** nodes that depend (directly or transitively) on the cancel node are **skipped** with status `cancelled`
4. Nodes in **parallel layers** (not depending on the cancel node) **continue to run** to completion
5. The workflow run status becomes `cancelled` (not `failed`)
6. A message is sent to the user with the cancel reason via `platform.sendMessage()`
7. Post-cancel cleanup (worktree removal, session closure) runs as normal

**Key mental model**: cancel is like `return` inside a function — it stops further progress on the current path but doesn't abort the whole workflow run unless everything depends on it. Use `trigger_rule: all_done` on terminal cleanup/report nodes if you want them to run even when a cancel fires upstream.

### Canonical Patterns

**Pattern 1 — Precondition gate**:

```yaml
nodes:
  - id: fetch-pr
    bash: |
      gh pr view $ARGUMENTS --json isDraft,mergeable
    output_format:
      type: object
      properties:
        isDraft: { type: boolean }
        mergeable: { type: string }
      required: [isDraft, mergeable]

  - id: abort-draft
    cancel: "PR #$ARGUMENTS is draft — will review once marked ready"
    depends_on: [fetch-pr]
    when: "$fetch-pr.output.isDraft == 'true'"

  - id: abort-conflict
    cancel: "PR #$ARGUMENTS has merge conflicts — resolve before review"
    depends_on: [fetch-pr]
    when: "$fetch-pr.output.mergeable == 'CONFLICTING'"

  - id: review
    command: archon-smart-pr-review
    depends_on: [fetch-pr]
    when: "$fetch-pr.output.isDraft == 'false'"
```

Three conditional paths. One of the cancel nodes fires based on PR state; the review node runs only if the PR is ready.

**Pattern 2 — Cleanup that still runs on cancel**:

```yaml
- id: implement
  command: archon-implement
  depends_on: [plan]

- id: abort-if-tests-fail
  cancel: "Tests failed — aborting before PR creation"
  depends_on: [implement]
  when: "$implement.output.testsPass == 'false'"

- id: cleanup
  bash: "pnpm clean"
  depends_on: [implement]
  trigger_rule: all_done                # runs even if abort-if-tests-fail fired
```

`trigger_rule: all_done` on `cleanup` ensures it executes whether or not the cancel fired.

**Pattern 3 — Orchestrator bail-out**:

```yaml
- id: check-budget
  script: |
    const usage = await Bun.file(`${process.env.ARTIFACTS_DIR}/budget.json`).json();
    if (usage.usedUsd > 10) process.exit(1);
    console.log('OK');
  runtime: bun

- id: cancel-over-budget
  cancel: "Workflow over budget ($10 threshold). Escalating to human review."
  depends_on: [check-budget]
  trigger_rule: all_done                # cancel fires when check-budget EXIT non-zero
  when: "$check-budget.output != 'OK'"
```

Combines a deterministic check with a cancel node for budget enforcement.

## Approval vs Cancel — Decision Table

| Need | Use |
|---|---|
| Wait for human before proceeding | **Approval** |
| Give human a way to veto | **Approval** (with default reject = cancel) |
| Give human option to reject with revision loop | **Approval** with `on_reject` |
| Terminate conditionally based on upstream output | **Cancel** with `when:` |
| Fail-closed on precondition check | **Cancel** |
| Budget/quota enforcement | **Cancel** after script check |
| Pause and later resume | **Approval** (workflow stays alive) |
| Stop permanently | **Cancel** (workflow run marked cancelled) |

## Limitations of Both

- **No audit trail UI**: approvals and cancels land in the workflow event log (`remote_agent_workflow_events`) but there's no dedicated audit view in the web UI
- **No conditional approval branching**: you can't say "if reviewer approves, go to A; if reviewer rejects with comment X, go to B". Use freeform response + `when:` conditions on downstream nodes as a workaround.
- **No cancel-with-follow-up**: a cancel node terminates the run. To "cancel this path but continue another", use `trigger_rule: all_done` on unaffected nodes as shown in Pattern 2.
- **Cancel reason is static**: the `cancel:` string is baked into the YAML. It doesn't support variable substitution in v0.3.5 (only `when:` conditions do).

## Source of Truth

| Concern | File |
|---|---|
| Approval node schema | `packages/workflows/src/schemas/dag-node.ts:247` |
| `approvalOnRejectSchema` | `packages/workflows/src/schemas/dag-node.ts:236` |
| Cancel node schema | `packages/workflows/src/schemas/dag-node.ts:269` |
| Approval runtime handling | `packages/workflows/src/dag-executor.ts` (search `isApprovalNode`) |
| Cancel runtime handling | `packages/workflows/src/dag-executor.ts` (search `isCancelNode`) |
| Type guards | `packages/workflows/src/schemas/dag-node.ts:580-620` (`isApprovalNode`, `isCancelNode`) |
| CancelWorkflowError | `packages/workflows/src/errors.ts` |
| Session resume across pauses | `packages/core/src/db/sessions.ts` (see `archon-architecture-deep-dive` skill) |
