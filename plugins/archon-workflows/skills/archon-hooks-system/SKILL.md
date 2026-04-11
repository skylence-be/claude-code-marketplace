---
name: archon-hooks-system
description: Master Archon's per-node hooks system — all 21 hook events (PreToolUse, PostToolUse, PostToolUseFailure, Notification, UserPromptSubmit, SessionStart, SessionEnd, Stop, SubagentStart, SubagentStop, PreCompact, PermissionRequest, Setup, TeammateIdle, TaskCompleted, Elicitation, ElicitationResult, ConfigChange, WorktreeCreate, WorktreeRemove, InstructionsLoaded), matcher patterns, response JSON, and the quality-loop workflow pattern used by archon-architect. Use when building self-correcting workflows, injecting pre/post-tool behavior, enforcing quality gates at the node level, or adding per-node permission overrides.
category: engineering
tags: [archon, hooks, quality-gates, sdk, pre-tool-use, post-tool-use]
related_skills: [archon-dag-workflow-authoring, archon-bundled-workflows]
---

# Archon Per-Node Hooks System

Archon DAG nodes can declare **hooks** that intercept the Claude Agent SDK's lifecycle events. Hooks enable self-correcting workflows — `archon-architect` uses PostToolUse hooks to type-check after every edit, PreToolUse hooks to inject architectural principles before writes, and so on. Based on `packages/workflows/src/schemas/hooks.ts`.

## When to Use This Skill

- Building workflows that self-correct (type-check after every edit, etc.)
- Enforcing coding rules at the tool-call level
- Adding permission overrides (block dangerous Bash commands, require approval for certain file writes)
- Injecting context into prompts just-in-time (SessionStart hooks)
- Running cleanup after workflow completion (Stop, SessionEnd hooks)
- Understanding how `archon-architect` achieves its "self-review loops"

## The 21 Hook Events

Each event fires at a specific point in the SDK session lifecycle. Named identically to Claude Agent SDK's `HookEvent` type.

| Event | When It Fires |
|---|---|
| `PreToolUse` | Before the AI invokes any tool (Read, Write, Bash, etc.) |
| `PostToolUse` | After a tool completes successfully |
| `PostToolUseFailure` | After a tool call fails |
| `Notification` | AI emits a UI notification |
| `UserPromptSubmit` | A new user prompt is submitted to the session |
| `SessionStart` | New AI session begins |
| `SessionEnd` | AI session ends |
| `Stop` | Workflow or session explicitly stops |
| `SubagentStart` | A sub-agent spawn begins |
| `SubagentStop` | A sub-agent spawn ends |
| `PreCompact` | Before SDK compacts conversation history to stay under context limit |
| `PermissionRequest` | AI asks for permission to perform a sensitive action |
| `Setup` | One-time setup phase before the main interaction |
| `TeammateIdle` | A teammate agent has been idle (used for coordination) |
| `TaskCompleted` | A task marked complete in the SDK's task tracker |
| `Elicitation` | The AI asks the user for input mid-session |
| `ElicitationResult` | User responds to an elicitation |
| `ConfigChange` | SDK config changes mid-session |
| `WorktreeCreate` | A new git worktree is created |
| `WorktreeRemove` | A git worktree is removed |
| `InstructionsLoaded` | CLAUDE.md / instructions files have been loaded |

Strict validation — typos like `preToolUse` (camelCase) get rejected at parse time. Only the exact PascalCase forms above are accepted.

## Hook Matcher Schema

Each event maps to an **array of matchers**. A matcher is:

```yaml
matcher: "<regex>"      # optional — filters which tools/events trigger this hook
response:               # required — the SDK SyncHookJSONOutput to return
  <free-form JSON>
timeout: 60             # optional — seconds (default: 60)
```

- **`matcher`**: regex pattern matching tool names (for `PreToolUse` / `PostToolUse`) or event subtypes. Omit to match all events of this type.
- **`response`**: arbitrary JSON returned to the SDK. The shape depends on the event — see the Claude Agent SDK docs for the `SyncHookJSONOutput` spec.
- **`timeout`**: seconds the hook has to respond. Default 60.

## Basic YAML Structure

```yaml
- id: implement-with-guards
  command: archon-implement
  depends_on: [plan]
  hooks:
    PreToolUse:
      - matcher: "Write|Edit"
        response:
          permissionDecision: "allow"
          systemPromptAddition: |
            Before editing, make sure the change:
            - Does not introduce new abstractions
            - Keeps the function under 50 lines
            - Matches existing patterns in the same directory
    PostToolUse:
      - matcher: "Write|Edit"
        response:
          systemPromptAddition: "Now run `pnpm typecheck` to verify the change compiles."
        timeout: 30
    Stop:
      - response:
          summary: "Implementation phase complete. Review the diff before proceeding."
```

The whole `hooks:` block sits on a DAG node. It's completely optional. When present, Archon builds SDK hook callbacks from the matcher array via `buildSDKHooksFromYAML(node.hooks)` in `packages/workflows/src/dag-executor.ts`.

## What Responses Can Do

Each hook's `response` is passed back to the SDK as `SyncHookJSONOutput`. Depending on the event, the SDK interprets it differently. Most common fields:

| Field | Works for | Effect |
|---|---|---|
| `permissionDecision` | `PreToolUse`, `PermissionRequest` | `"allow"` / `"deny"` / `"ask"` — override the default permission |
| `systemPromptAddition` | Most events | Text appended to the system prompt before the AI acts |
| `messageAddition` | Most events | Message injected into the conversation |
| `summary` | `Stop`, `SessionEnd` | Final summary shown to the user |
| `retry` | `PostToolUseFailure` | `true` / `false` — whether the SDK should retry the failed tool call |
| `abort` | Any | If `true`, the SDK terminates the session with an error |

The full shape is defined by the Claude Agent SDK's type `SyncHookJSONOutput`. Archon validates the field presence (as `z.record(z.unknown())`) but not the semantics — if you pass an unknown field, the SDK silently ignores it.

## Canonical Patterns

### Pattern 1 — Type-check after every edit

The cornerstone of `archon-architect` and `archon-refactor-safely`:

```yaml
- id: refactor
  command: archon-refactor-step
  hooks:
    PostToolUse:
      - matcher: "Write|Edit|MultiEdit"
        response:
          messageAddition: |
            File modified. Run `pnpm typecheck` and confirm no new errors
            before making another edit.
        timeout: 30
```

The AI sees the injected message after every file edit and types-checks before moving on. Creates an organic quality loop.

### Pattern 2 — Block dangerous Bash commands

```yaml
- id: execute
  command: archon-execute-plan
  hooks:
    PreToolUse:
      - matcher: "Bash"
        response:
          permissionDecision: "ask"
          systemPromptAddition: |
            About to run a Bash command. If the command contains any of:
            - rm -rf
            - git reset --hard
            - git push --force
            - DELETE FROM (SQL)
            - DROP TABLE
            DO NOT PROCEED without explicit user approval.
```

Forces the AI through a permission gate for every bash invocation. Users can configure `permissionDecision: "deny"` outright for hard blocks.

### Pattern 3 — Inject project principles before writes

```yaml
- id: implement
  command: archon-implement
  hooks:
    PreToolUse:
      - matcher: "Write|Edit"
        response:
          systemPromptAddition: |
            Project principles to respect:
            - No new abstractions without approval
            - Keep files under 500 LOC
            - Match existing directory patterns
            - Read CLAUDE.md before writing new files
```

Lighter weight than re-stating principles in the main prompt — the AI sees them only when actually about to write, not when planning or reading.

### Pattern 4 — Auto-summary on stop

```yaml
- id: investigate
  command: archon-investigate-issue
  hooks:
    Stop:
      - response:
          summary: |
            Investigation complete. Check $ARTIFACTS_DIR/investigation.md for:
            - Root cause analysis
            - Reproduction steps
            - Scope boundaries
            - Recommended fix approach
```

The `summary` is shown to the user when the node finishes, providing a structured "what to look at" signal without the AI having to repeat it.

### Pattern 5 — Retry failed tests automatically

```yaml
- id: run-tests
  command: archon-run-tests
  hooks:
    PostToolUseFailure:
      - matcher: "Bash"
        response:
          retry: true
          systemPromptAddition: |
            Test run failed. Read the error output carefully and retry with
            the fix applied. Maximum 3 retries per test file.
```

The AI sees a clear retry signal, the SDK automatically repeats the failed invocation.

### Pattern 6 — Filter sensitive paths

```yaml
- id: cleanup
  command: archon-cleanup
  hooks:
    PreToolUse:
      - matcher: "Write|Edit|Bash"
        response:
          permissionDecision: "deny"
          reason: |
            Cleanup node cannot modify lib/auth/, server/utils/db/, or any
            .env* file. Ask the user before touching these paths.
```

Combined with the SDK's own file-path awareness, this effectively carves out untouchable zones.

### Pattern 7 — Self-review on completion

```yaml
- id: implement
  command: archon-implement
  hooks:
    PostToolUse:
      - matcher: "Write|Edit"
        response:
          systemPromptAddition: |
            Before your next action, ask yourself:
            1. Does this edit match the plan?
            2. Did I introduce any new types that should go in shared/?
            3. Is this function testable in isolation?
            If any answer is no, revise BEFORE continuing.
```

Uses hooks to enforce a self-questioning pattern after each edit. `archon-architect` uses something similar.

## How It Works Internally

From `packages/workflows/src/dag-executor.ts`:

```typescript
if (node.hooks) {
  const builtHooks = buildSDKHooksFromYAML(node.hooks);
  if (Object.keys(builtHooks).length > 0) claudeOptions.hooks = builtHooks;
}
```

`buildSDKHooksFromYAML` walks the typed YAML structure, converts each matcher array into the SDK's expected `HookCallbackMatcher[]` shape, and passes it to the Claude Agent SDK as `claudeOptions.hooks`. The SDK then registers the callbacks at session startup and invokes them when the corresponding events fire.

**Important**: hooks are **per-node** — they don't apply to the whole workflow. Each node's hooks are built and passed only for that node's AI call. Downstream nodes start fresh without the previous node's hooks.

## Limitations

1. **Only command and prompt nodes** get hooks applied. Bash, script, loop, approval, and cancel nodes don't trigger SDK events, so their hook config is silently ignored.
2. **No dynamic hook responses** — the `response` is static JSON in the YAML. You can't compute a response from runtime state; it's pre-baked.
3. **No hook chaining** — if multiple matchers match the same event, all their responses fire, but there's no defined order-of-merging for conflicting fields (e.g., two matchers both setting `permissionDecision`). Avoid overlapping matchers when possible.
4. **Claude only** — hooks are a Claude Agent SDK feature. Codex nodes don't support them. The loader emits a warning if you set `hooks:` on a node running under Codex.

## Debugging Hooks

### Enable verbose logging

Temporarily unset `/dev/null` stdout in Archon's launchd plist (or run `archon serve --verbose`) to see `dag.hooks_built` and `dag.hook_fired` log lines.

### Test hook fires

Add a no-op hook with a distinctive message addition to confirm the hook is being loaded:

```yaml
hooks:
  PreToolUse:
    - matcher: ".*"
      response:
        systemPromptAddition: "HOOK_TEST_MARKER_123"
```

If you see `HOOK_TEST_MARKER_123` in the AI output, the hook fired. If not, check YAML syntax and verify the node type supports hooks (command or prompt only).

### Schema validation errors

`archon validate workflows <name>` catches:
- Unknown hook event names (typos like `preToolUse`)
- Missing `response` field
- Negative `timeout` values
- Non-regex `matcher` values that break zod parsing

## Source of Truth

| Concern | File |
|---|---|
| Hook event enum (21 events) | `packages/workflows/src/schemas/hooks.ts` |
| Hook matcher schema | `packages/workflows/src/schemas/hooks.ts:42` (`workflowHookMatcherSchema`) |
| Node hooks schema | `packages/workflows/src/schemas/hooks.ts:61` (`workflowNodeHooksSchema`) |
| Runtime integration | `packages/workflows/src/dag-executor.ts:~516` (`buildSDKHooksFromYAML`) |
| SDK `SyncHookJSONOutput` type | See `@anthropic-ai/claude-agent-sdk` type exports |
| Canonical example workflow | `/Users/jv/Archon/.archon/workflows/defaults/archon-architect.yaml` |
