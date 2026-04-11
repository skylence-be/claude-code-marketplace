---
name: archon-architecture-deep-dive
description: End-to-end architecture reference for Archon v0.3+ — the seven core flows (message routing, workflow execution, isolation resolution, session lifecycle, DB layer, config 4-layer merge, web UI SSE) with file:line pointers into the source. Use when debugging cross-system issues, understanding how a request flows from a platform adapter through the orchestrator to the AI client and back, onboarding to the Archon codebase, or planning architectural changes.
category: engineering
tags: [archon, architecture, orchestrator, sessions, database, sse, internals]
related_skills: [archon-dag-workflow-authoring, archon-isolation-and-worktrees, archon-adapter-implementation]
---

# Archon Architecture Deep Dive

Reference for Archon's internals based on `.claude/docs/architecture-deep-dive.md` in the source plus hands-on code reading. Walks the seven major flows with `file:line` pointers so you can jump into the source quickly when debugging.

## 1. Message Flow: The Routing Agent

The orchestrator is a **routing agent** — most messages go through an AI call that decides how to handle them, not a command dispatcher. Only 5 commands are deterministic (`/help`, `/status`, `/reset`, `/workflow`, `/register-project`). Everything else is AI-routed.

```
Platform event (Slack/Telegram/GitHub/Discord/Web)
  → Adapter receives event, checks auth (ALLOWED_USERS env var)
  → void this.messageHandler(event)                       (fire-and-forget)
    → lockManager.acquireLock(conversationId, handler)    (conversation-lock.ts:59)
      → handleMessage(platform, conversationId, text)     (orchestrator-agent.ts:383)
        → db.getOrCreateConversation()
        → inheritThreadContext()                           (if child thread)
        → generateAndSetTitle()                            (fire-and-forget)

        IF message starts with deterministic /command:
          → commandHandler.handleCommand()                 (orchestrator-agent.ts:430)
          → handleWorkflowRunCommand → dispatchOrchestratorWorkflow()
          → Return directly, no AI involved

        ELSE (everything else, including unknown slash commands):
          → codebaseDb.listCodebases() + discoverAllWorkflows()
          → buildFullPrompt() → project-scoped or global orchestrator prompt
          → sessionDb.getActiveSession() → transitionSession if first message
          → getAssistantClient(conversation.ai_assistant_type)
          → handleBatchMode() or handleStreamMode() based on getStreamingMode()

          AI responds with natural language + optional structured commands:
            → filterToolIndicators()                       (strip emoji-prefixed tool noise)
            → parseOrchestratorCommands()
              → /invoke-workflow → dispatchOrchestratorWorkflow()
              → /register-project → handleRegisterProject()
              → Plain text → platform.sendMessage()
```

**Key decision points**:
- `getStreamingMode()` — Slack/GitHub return `'batch'`, Telegram/Discord/Web return `'stream'`
- `buildFullPrompt()` — project-scoped if conversation has codebase attached, otherwise global
- `parseOrchestratorCommands()` — the AI decides whether to dispatch a workflow; the orchestrator doesn't pattern-match user intent
- Session resume: `session.assistant_session_id` passed to SDK's `options.resume`

**Only these slash commands are deterministic**: `help`, `status`, `reset`, `workflow`, `register-project`. Unknown slash commands fall through to the AI router.

## 2. Workflow Execution

```
/workflow run <name> <message>
  → commandHandler.handleCommand()                         (orchestrator-agent.ts:422)
  → discoverWorkflowsWithConfig() finds by name            (loader.ts:1013)
  → handleWorkflowRunCommand()                             (orchestrator-agent.ts:888)
    → dispatchOrchestratorWorkflow()                       (orchestrator-agent.ts:192)
      → validateAndResolveIsolation()                      → see Flow 3
      → For non-web: executeWorkflow() directly
      → For web: dispatchBackgroundWorkflow() → worker conversation + fire-and-forget
```

**Inside `executeWorkflow()` (`executor.ts`)**:

```
→ deps.store.createWorkflowRun()                           (DB row)
→ getWorkflowEventEmitter().registerRun(runId, conversationId)
→ Resolve provider/model from config
→ Create artifactsDir and logDir

Dispatch by mode:
  DAG     → executeDagWorkflow()  (dag-executor.ts)
  Loop    → max_iterations loop with substituteVariables + aiClient.sendQuery
  Steps   → executeStepInternal per step (or Promise.all for parallel blocks)
```

**`executeDagWorkflow()` internals**:

```
→ buildTopologicalLayers() — Kahn's algorithm
→ For each layer: Promise.allSettled(nodes)
  → Per node:
    → checkTriggerRule()    (all_success / one_success / none_failed_min_one_success / all_done)
    → evaluateCondition(when)
    → Node type dispatch:
        bash   → execFileAsync('bash', ['-c', script], { timeout })
        script → execFileAsync('bun' | 'uv', [script, ...], { deps installed first })
        cmd/prompt → resolveNodeProviderAndModel() → aiClient.sendQuery()
                     Load hooks, mcp, skills if specified
        loop   → inline iteration with $ARTIFACTS_DIR support
        approval → wait for user response (send message, suspend)
        cancel → throw CancelWorkflowError to abort the run
    → Store output in nodeOutputs map for $nodeId.output substitution
```

**Event emission**: Each step/node emits `step_started`, `step_completed`, `node_started`, etc. through `WorkflowEventEmitter` → `WorkflowEventBridge` → SSE to web UI.

## 3. Isolation Resolution (7 steps)

See the `archon-isolation-and-worktrees` skill for the full detail. Summary:

```
validateAndResolveIsolation()                              (orchestrator.ts:108)
  → IsolationResolver.resolve(request)                     (resolver.ts:100)

Step 1  Existing env          — store.getById + worktreeExists
Step 2  No codebase           — { status: 'none', cwd: '/workspace' }
Step 3  Workflow reuse        — findActiveByWorkflow(codebaseId, type, id)
Step 4  Linked issue          — scan hints.linkedIssues
Step 5  PR branch adoption    — findWorktreeByBranch + create adopted DB row
Step 6  Limit check           — countActiveByCodebase vs maxWorktrees (25) → makeRoom()
Step 7  Create new            — provider.create → store.create → on failure destroy orphan
```

## 4. Session Lifecycle

**Sessions are immutable** — never mutated, only deactivated and replaced.

```
First message → transitionSession('first-message')
  → INSERT new session (parent_session_id = null)
  → assistant_session_id = null (no SDK session yet)

AI call completes → tryPersistSessionId(session.id, sdkSessionId)
  → UPDATE assistant_session_id for resume on next message

Next message → getActiveSession() returns existing
  → sendQuery(..., session.assistant_session_id) — SDK resumes

/reset → transitionSession('reset-requested')
  → Deactivates current session
  → Next message triggers 'first-message' → new session

Plan → Execute transition:
  → detectPlanToExecuteTransition() on commandName === 'execute' after 'plan-feature'
  → transitionSession('plan-to-execute') — atomic old-deactivate + new-create in one TX
```

**Transition triggers**: `'first-message'`, `'plan-to-execute'`, `'isolation-changed'`, `'codebase-changed'`, `'codebase-cloned'`, `'cwd-changed'`, `'reset-requested'`, `'context-reset'`, `'repo-removed'`, `'worktree-removed'`, `'conversation-closed'`

**Audit trail**: `getSessionChain(sessionId)` walks `parent_session_id` links via recursive CTE.

## 5. Database Layer

**Auto-detection** (`core/src/db/connection.ts:30-46`):

```
DATABASE_URL set     → PostgresAdapter (pg.Pool, max: 10)
Otherwise            → SqliteAdapter (bun:sqlite, WAL mode, busy_timeout: 5000)
```

**Query flow**:
- Postgres: `$1`, `$2` placeholders work natively
- SQLite: `convertPlaceholders()` replaces `$N` with `?` and reorders params; strips `::jsonb` casts

**Namespaced exports pattern**:

```typescript
import * as conversationDb from '@archon/core/db/conversations';
import * as sessionDb from '@archon/core/db/sessions';

await conversationDb.getOrCreateConversation(platformType, conversationId);
await sessionDb.transitionSession(conversationId, trigger, options);
```

**Dialect differences**:

| Feature | SQLite | PostgreSQL |
|---|---|---|
| `now()` | `datetime('now')` | `NOW()` |
| `jsonMerge(col, $N)` | `json_patch(col, $N)` | `col \|\| $N::jsonb` |
| UUID | `crypto.randomUUID()` | `gen_random_uuid()` |

**Why it matters for debugging**: when inspecting `~/.archon/archon.db` directly with `sqlite3`, remember foreign keys are **off** (`PRAGMA foreign_keys = 0`). Stale references to deleted codebases won't block DELETE but will leave orphaned rows. Check dependent tables manually before deleting.

## 6. Configuration: 4-Layer Merge

```
Layer 1: Code defaults                                     (config-loader.ts:165)
  → botName: 'Archon', assistant: 'claude', concurrency.maxConversations: 10

Layer 2: Global config (~/.archon/config.yaml)
  → loadGlobalConfig() — cached after first load
  → Overrides: botName, defaultAssistant, assistants.*, streaming modes

Layer 3: Repo config ({repoPath}/.archon/config.yaml)
  → loadRepoConfig() — read fresh each time (NOT cached)
  → Overrides: assistant, assistants.*, commands.folder, defaults.*, worktree.baseBranch, worktree.copyFiles

Layer 4: Environment variables (highest precedence)
  → BOT_DISPLAY_NAME, DEFAULT_AI_ASSISTANT
  → TELEGRAM_STREAMING_MODE, DISCORD_STREAMING_MODE, SLACK_STREAMING_MODE
  → MAX_CONCURRENT_CONVERSATIONS
```

**Workflow model resolution priority** (highest first):
1. Per-node `model:` in DAG mode
2. Workflow-level `model:` in YAML
3. Config `assistants.{provider}.model`
4. SDK default

**Cached vs fresh**: global config is cached (reload on server restart), repo config is read fresh on every workflow invocation. If you change `.archon/config.yaml` in your repo mid-session, the next workflow run picks it up without restarting Archon.

## 7. Web UI Data Flow: REST + SSE

### REST (TanStack Query v5)

```
React component → useQuery({ queryKey, queryFn })
  → apiClient.listConversations() — fetch('/api/conversations')
  → Server: Hono route handler → DB query → JSON response
  → TanStack Query caches, polls, invalidates
```

### SSE Streaming

```
React: useSSE(conversationId)
  → new EventSource(`/api/stream/${conversationId}`)
  → Server: streamSSE(c, async (stream) => {
      transport.registerStream(conversationId, stream)
      stream.onAbort(() => transport.removeStream(...))
    })

Event flow:
  AI client yields content → WebAdapter.sendMessage()
    → persistence.appendText()                             (buffer for DB)
    → transport.emit(conversationId, { type: 'text', content })
      → stream.writeSSE({ data: JSON.stringify(event) })

  Client receives:
    → eventSource.onmessage → parseSSEEvent()
    → switch(data.type):
      'text'             → 50ms debounce buffer → handlers.onText()
      'tool_call'        → flush text → handlers.onToolCall()
      'tool_result'      → flush text → handlers.onToolResult()
      'conversation_lock'→ handlers.onLockChange()
      'workflow_step'    → handlers.onWorkflowStep()
      'dag_node'         → handlers.onDagNode()
      'retract'          → clear buffer → handlers.onRetract()
```

### Workflow Progress (Background Workflows)

```
Workflow executor emits events → WorkflowEventEmitter singleton
  → WorkflowEventBridge subscribes → mapWorkflowEvent()
  → For background workflows: bridgeWorkerEvents(workerConvId, parentConvId)
    → Routes worker events to parent's SSE stream
  → transport.emitWorkflowEvent(parentConvId, sseEvent)
    → SSE to React → WorkflowProgressCard updates
```

### Reconnect Grace Period

`SSETransport.removeStream()` schedules cleanup after `RECONNECT_GRACE_MS = 5000ms`. If the browser reconnects within 5s (navigation, tab switch), `registerStream()` cancels the cleanup timer and persistence state is preserved.

## 8. Paused Workflow State

Workflows have three success states, not two. The `WorkflowExecutionResult` type from `packages/workflows/src/schemas/workflow.ts` is a discriminated union:

```typescript
type WorkflowExecutionResult =
  | { success: true;  workflowRunId: string; summary?: string }     // completed
  | { success: false; workflowRunId?: string; error: string }        // failed
  | { success: true;  paused: true; workflowRunId: string };         // paused
```

### When Workflows Pause

Two situations trigger `paused`:

1. **An approval node is waiting** — the DAG executor sends the approval message and suspends until the user responds via `/workflow approve` or `/workflow reject`
2. **An interactive loop node is between iterations** — `loop.interactive: true` means the workflow pauses after each iteration and waits for `/workflow approve` before the next one runs

### Database State

The `remote_agent_workflow_runs` table tracks status. Look for `status = 'paused'`:

```sql
SELECT id, workflow_name, status, current_step_index, started_at, last_activity_at
FROM remote_agent_workflow_runs
WHERE status = 'paused'
ORDER BY started_at DESC;
```

### Resume Mechanics

When `/workflow approve <run-id>` fires:

1. `commandHandler.handleCommand()` intercepts the slash command deterministically (no AI router involvement)
2. The paused run's session is fetched via `sessionDb.getActiveSession()`
3. The DAG executor resumes the suspended node (approval or loop iteration)
4. Downstream nodes proceed normally
5. Status transitions: `paused` → `running` → eventually `completed` / `failed` / `cancelled`

Session preservation: `assistant_session_id` on the paused node's session is kept intact across the pause, so the SDK resumes the conversation with full history. See Flow 4 for session lifecycle details.

### Pause-to-Completion Timeline

A workflow with approval gates can have multiple pause/resume cycles:

```
t+0s    running → (approval node fires) → paused
t+300s  user sends /workflow approve → running
t+320s  (interactive loop iteration 1 done) → paused
t+600s  /workflow approve → running
t+640s  (interactive loop iteration 2 done) → paused
...
t+Nh    (all iterations done) → completed
```

Each pause creates a `workflow_paused` event in `remote_agent_workflow_events`. Each resume creates a `workflow_resumed` event. Full audit trail via:

```sql
SELECT event_type, step_name, substr(data, 1, 150) as data, created_at
FROM remote_agent_workflow_events
WHERE workflow_run_id = '<run-id>'
ORDER BY created_at;
```

### Idle Timeout for Paused States

Paused workflows still respect `idle_timeout` (default 300000ms = 5 min). If no response lands within the idle window, the node fails with `workflow_idle_timeout`. Bump `idle_timeout` on approval/interactive-loop nodes when you expect long pauses:

```yaml
- id: overnight-approval
  idle_timeout: 86400000               # 24 hours
  approval:
    message: "Approve overnight deploy?"
```

### Forcing a Paused Run to Complete Without Response

If a paused workflow needs to be terminated without approval:

```bash
# In conversation:
/workflow cancel <run-id>

# Or from outside, via DB + process kill:
sqlite3 ~/.archon/archon.db "UPDATE remote_agent_workflow_runs SET status='cancelled', completed_at=datetime('now') WHERE id='<run-id>'"
ps -ef | grep claude-agent-sdk | grep -v grep
kill <pid>
```

The CLI's `archon workflow status` command shows paused runs alongside running ones — use it to find orphaned paused runs.

## Command Loading Failure Modes

`LoadCommandResult` from `workflow.ts` is a discriminated union that fully enumerates command file load failures:

```typescript
type LoadCommandResult =
  | { success: true; content: string }
  | {
      success: false;
      reason: 'invalid_name' | 'empty_file' | 'not_found' | 'permission_denied' | 'read_error';
      message: string;
    };
```

Failure reasons:

| `reason` | When it fires | Fix |
|---|---|---|
| `invalid_name` | Command name contains `/`, `\`, `..`, starts with `.`, or is empty | Pick a valid name (kebab-case, no special chars) |
| `empty_file` | The `.md` file exists but has zero non-whitespace content | Add at least a minimal prompt body |
| `not_found` | No matching file in any discovery path (repo → repo-defaults → bundled) | Create the file OR use a bundled name that exists |
| `permission_denied` | File exists but OS permissions prevent read | `chmod +r .archon/commands/<name>.md` |
| `read_error` | Unexpected I/O error (disk, corruption, etc.) | Check file integrity, server logs |

Discovery order (from `loader.ts`):

1. `<repo>/.archon/commands/<name>.md` — highest priority
2. `<repo>/.archon/commands/defaults/<name>.md` — repo-level override of bundled defaults
3. `/Users/jv/Archon/.archon/commands/defaults/<name>.md` — bundled default

First match wins. A `not_found` error means all three locations were checked and none had the file.

## Workflow Source Discriminator

`WorkflowSource = 'bundled' | 'project'` — every loaded workflow is tagged with its source. The `WorkflowWithSource` wrapper surfaces this alongside the definition:

```typescript
interface WorkflowWithSource {
  readonly workflow: WorkflowDefinition;
  readonly source: WorkflowSource;
  readonly filepath: string;        // absolute path
}
```

Use cases:
- **Filter the dashboard** to show only `project` workflows (hiding bundled defaults)
- **Distinguish overrides from bundled** when inspecting the workflow list — if two entries share a name, the `project` one wins at load time
- **Debug override failures** — if you expected your override to take effect but the bundled one is running, check `source` for each discovered workflow

Query via `discoverWorkflowsWithConfig()` in `loader.ts:1013`.

## Cross-Cutting Patterns

### Lazy Logger

Every module defers logger creation to avoid test mock timing issues:

```typescript
let cachedLog: ReturnType<typeof createLogger> | undefined;
function getLog() { return (cachedLog ??= createLogger('module')); }
```

Never initialize loggers at module scope. Test mocks must intercept `createLogger` before first use.

### Shell Invocation: `execFileAsync` Only

All git and shell subprocess calls go through `packages/git/src/exec.ts` → `execFileAsync`. This avoids shell interpretation entirely and provides consistent timeout handling. The codebase forbids the shell-interpretation APIs from Node's built-in child process module because they're vulnerable to command injection on any input touched by user content.

### Structured Event Side-Channel

`IPlatformAdapter.sendStructuredEvent?()` is optional. Only `WebAdapter` implements it. The orchestrator and executor check `if (platform.sendStructuredEvent)` before calling. Sends raw SDK tool call objects to SSE separately from formatted text — so the web UI can render tool calls inline with text without the text path needing to know about tools.

### `isWebAdapter()` Type Guard

Narrows `IPlatformAdapter` to `WebAdapter` for web-specific methods: `setConversationDbId()`, `setupEventBridge()`, `emitRetract()`.

### Conversation Locking

`ConversationLockManager` prevents concurrent message handling on the same conversation. GitHub adapter owns its own `lockManager` (injected in constructor). All other adapters share the global singleton instance from `server/src/index.ts`.

## Key File Reference

| Flow | Key files |
|---|---|
| Message entry | `packages/adapters/src/chat/slack/adapter.ts`, `packages/server/src/index.ts` |
| Orchestration | `packages/core/src/orchestrator/orchestrator-agent.ts`, `orchestrator.ts` |
| Locking | `packages/core/src/utils/conversation-lock.ts` |
| AI clients | `packages/core/src/clients/claude.ts`, `clients/factory.ts` |
| Commands | `packages/core/src/handlers/command-handler.ts` |
| Sessions | `packages/core/src/db/sessions.ts`, `state/session-transitions.ts` |
| Workflows | `packages/workflows/src/executor.ts`, `dag-executor.ts`, `loader.ts` |
| Isolation | `packages/isolation/src/resolver.ts`, `providers/worktree.ts` |
| Database | `packages/core/src/db/connection.ts`, `adapters/sqlite.ts`, `postgres.ts` |
| Config | `packages/core/src/config/config-loader.ts` |
| SSE streaming | `packages/server/src/adapters/web/transport.ts`, `workflow-bridge.ts` |
| Web UI hooks | `packages/web/src/hooks/useSSE.ts`, `src/lib/api.ts` |
| Official docs | `.claude/docs/architecture-deep-dive.md` |
