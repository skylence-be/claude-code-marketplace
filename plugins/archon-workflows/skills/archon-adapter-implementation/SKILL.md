---
name: archon-adapter-implementation
description: Complete guide to implementing a new platform adapter for Archon — the IPlatformAdapter interface, the lazy logger pattern, constructor-time auth allowlist parsing, message splitting, the ensureThread convention, and per-platform details for Slack, Telegram, GitHub, Discord, and Web. Use when adding a new chat/forge adapter to Archon, debugging adapter behavior, or understanding how messages flow from a platform into the orchestrator.
category: engineering
tags: [archon, adapters, slack, telegram, github, discord, web, platform]
related_skills: [archon-architecture-deep-dive, archon-github-adapter-patterns]
---

# Archon Adapter Implementation Guide

Build a new platform adapter (Mattermost, IRC, MS Teams, custom REST, etc.) or understand how the existing ones work. Based on `.claude/docs/adapter-implementation-guide.md` in the Archon source.

## The Interface: `IPlatformAdapter`

Defined at `packages/core/src/types/index.ts:106-151`.

| Method | Signature | Required |
|---|---|---|
| `sendMessage` | `(conversationId: string, message: string, metadata?: MessageMetadata): Promise<void>` | Yes |
| `ensureThread` | `(originalConversationId: string, messageContext?: unknown): Promise<string>` | Yes |
| `getStreamingMode` | `(): 'stream' \| 'batch'` | Yes |
| `getPlatformType` | `(): string` | Yes |
| `start` | `(): Promise<void>` | Yes |
| `stop` | `(): void` | Yes |
| `sendStructuredEvent` | `(conversationId: string, event: MessageChunk): Promise<void>` | Optional (web only) |
| `emitRetract` | `(conversationId: string): Promise<void>` | Optional (web only) |

`IWebPlatformAdapter` (`types/index.ts:158`) extends this with web-only methods: `sendStructuredEvent` (required), `setConversationDbId`, `setupEventBridge`, `emitLockEvent`, `registerOutputCallback`, `removeOutputCallback`. Type guard: `isWebAdapter()` checks `getPlatformType() === 'web'`.

## Common Template (All Adapters Share)

### 1. Lazy Logger Pattern

Every adapter file uses this at module scope:

```typescript
let cachedLog: ReturnType<typeof createLogger> | undefined;
function getLog(): ReturnType<typeof createLogger> {
  if (!cachedLog) cachedLog = createLogger('adapter.<name>');
  return cachedLog;
}
```

**Never** initialize the logger at module scope — test mocks must intercept `createLogger` before first use.

### 2. Auth: Constructor Whitelist + Silent Rejection

Every adapter reads its env var in the constructor and stores the parsed whitelist:

| Adapter | Env Var | ID Type | Auth File |
|---|---|---|---|
| Slack | `SLACK_ALLOWED_USER_IDS` | `string[]` (regex `/^[UW][A-Z0-9]+$/`) | `chat/slack/auth.ts` |
| Telegram | `TELEGRAM_ALLOWED_USER_IDS` | `number[]` (positive integers) | `chat/telegram/auth.ts` |
| GitHub | `GITHUB_ALLOWED_USERS` | `string[]` (lowercase normalized) | `forge/github/auth.ts` |
| Discord | `DISCORD_ALLOWED_USER_IDS` | `string[]` (numeric snowflakes) | `community/chat/discord/auth.ts` |

Each auth module exports:
- `parseAllowedXxx(envValue)` — parse from env string to typed array
- `isXxxAuthorized(userId, allowedIds)` — check auth

**Empty whitelist** = open access.

**On failure**: log with `userId.slice(0, 4) + '***'` masking, then `return` silently. **No error sent to user** — this is intentional anti-reconnaissance behavior.

### 3. Message Handler Registration

```typescript
class MyAdapter implements IPlatformAdapter {
  private messageHandler?: MessageHandler;

  onMessage(handler: MessageHandler): void {
    this.messageHandler = handler;
  }

  async start(): Promise<void> {
    // Wire up platform events
    this.client.on('message', async (event) => {
      if (!isMyPlatformAuthorized(event.userId, this.allowed)) {
        getLog().info({ maskedUser: mask(event.userId) }, 'myplatform.unauthorized');
        return; // silent reject
      }
      void this.messageHandler?.(event); // fire-and-forget
    });
  }
}
```

### 4. Message Splitting

All adapters use `splitIntoParagraphChunks(message, maxLength)` from `packages/adapters/src/utils/message-splitting.ts`:

| Platform | Limit | Buffer | Effective split |
|---|---|---|---|
| Slack | 12,000 | 500 | 11,500 |
| Telegram | 4,096 | 200 | 3,896 |
| GitHub | 65,000 | 500 | 64,500 |
| Discord | 2,000 | 100 | 1,900 |

Two-pass algorithm: split on `\n\n+` first, then `\n` for oversized paragraphs.

### 5. `ensureThread()` is Usually a No-op

Only Discord creates real threads. Slack's `channel:ts` format already ensures threading. Telegram and GitHub have no thread concept.

```typescript
async ensureThread(conversationId: string): Promise<string> {
  return conversationId; // no-op default
}
```

## Per-Adapter Deep Dive

### Slack (`SlackAdapter`)

**File**: `packages/adapters/src/chat/slack/adapter.ts`

- **Transport**: Socket Mode (WebSocket) via `@slack/bolt`
- **Events**: `app_mention` (line 246), `message` (line 269 — DMs only via `channel_type === 'im'`, skips bot messages via `bot_id`)
- **Conversation ID**: `channel:thread_ts` or `channel:ts`. `getConversationId()` at line 190 encodes both into one string. `sendMessage()` splits on `:` for `chat.postMessage`.
- **Sending**: `sendWithMarkdownBlock()` — posts via `chat.postMessage` with a `markdown` block type. Falls back to plain text on error.
- **Streaming**: `'batch'` by default, overridden via `SLACK_STREAMING_MODE`
- **Unique helpers**: `stripBotMention(text)` strips `<@USERID>` prefixes, `fetchThreadHistory(event)` fetches up to 100 replies via `conversations.replies`

### Telegram (`TelegramAdapter`)

**File**: `packages/adapters/src/chat/telegram/adapter.ts`

- **Transport**: Long polling via Telegraf `bot.launch()`
- **Critical config**: `handlerTimeout: Infinity` (line 31) — avoids the 90s Telegraf default timeout killing long AI operations. `dropPendingUpdates: true` on launch discards offline messages.
- **Conversation ID**: numeric chat ID as string (`ctx.chat.id.toString()`)
- **Sending**: Two-stage markdown — converts to MarkdownV2 via `convertToTelegramMarkdown()`, sends with `parse_mode: 'MarkdownV2'`, falls back to `stripMarkdown()` on rejection. Helpers in `chat/telegram/markdown.ts`.
- **Streaming**: `'stream'` by default, overridden via `TELEGRAM_STREAMING_MODE`
- **Auth IDs**: `number[]` (Telegram user IDs are numeric)

### GitHub (`GitHubAdapter`)

**File**: `packages/adapters/src/forge/github/adapter.ts`

- **Transport**: Webhooks. `start()` is a no-op. Server registers `POST /webhooks/github` → `handleWebhook(payload, signature)`. Fire-and-forget (returns 200 immediately).
- **Processing flow** (`handleWebhook()`, line 677):
  1. HMAC-SHA256 signature verify via `timingSafeEqual`
  2. Auth check against `GITHUB_ALLOWED_USERS` (from `event.sender.login`)
  3. `parseEvent()` — **only handles** `issue_comment.created`, `issues.closed`, `pull_request.closed`. **NOT** `issues.opened` or `pull_request.opened` (descriptions contain docs, not commands — see issue #96)
  4. Self-loop prevention: ignores comments containing `<!-- archon-bot-response -->`
  5. Bot mention check via `hasMention()`
  6. `getOrCreateCodebaseForRepo()` upserts codebase record
  7. `ensureRepoReady()` clones (new) or syncs (existing) the repo
  8. Builds `IsolationHints` for PR/issue workflows
- **Conversation ID**: `owner/repo#number` (e.g., `acme/api#42`)
- **Sending**: `octokit.rest.issues.createComment` with retry logic (3 attempts, exponential backoff). Appends `<!-- archon-bot-response -->` marker to every comment.
- **Streaming**: Always `'batch'` (hardcoded at line 225)
- **Unique**: only adapter with its own `ConversationLockManager` (injected in constructor). Only adapter that calls `handleMessage()` directly (not via `server.ts`). Has `ensureRepoReady()` for on-demand clone/sync. Builds `IsolationHints` with PR branch, SHA, fork detection.

### Discord (`DiscordAdapter`)

**File**: `packages/adapters/src/community/chat/discord/adapter.ts`

- **Transport**: discord.js WebSocket via `client.login()`
- **Gateway intents**: `Guilds`, `GuildMessages`, `MessageContent`, `DirectMessages`. `Partials.Channel` required for DM support.
- **Event**: `Events.MessageCreate` listener in `start()`
- **Conversation ID**: Channel ID string (Discord snowflake). Thread messages use the thread's own channel ID, so each thread is a separate conversation automatically.
- **`ensureThread()`** — **The only adapter with a real implementation** (line 195):
  1. If already in a thread → return thread's `channelId`
  2. If in a DM → no threading, return unchanged
  3. Dedup via `this.pendingThreads` map to prevent double creation
  4. Creates thread via `message.startThread()` with `autoArchiveDuration: OneDay`
  5. Thread name: first 97 chars of message content, fallback `'Bot Response'`
- **Streaming**: `'stream'` by default, overridden via `DISCORD_STREAMING_MODE`
- **Character limit**: 2,000 (smallest of all platforms)

### Web (`WebAdapter`)

**File**: `packages/server/src/adapters/web.ts`

- **Transport**: None — purely output-driven. Messages arrive via REST API (`POST /api/conversations/:id/message`). Adapter's job is SSE streaming + message persistence.
- **Architecture**: Facade over three injected components:
  - `SSETransport` (`web/transport.ts`): manages `Map<string, SSEWriter>` of active connections
  - `MessagePersistence` (`web/persistence.ts`): buffers text + tool calls, flushes to DB
  - `WorkflowEventBridge` (`web/workflow-bridge.ts`): forwards workflow events from workers to parent SSE
- **`sendMessage()`** (line 44):
  1. Calls `persistence.appendText()` first (always buffer for DB)
  2. Skips SSE for `tool_call_formatted` and `isolation_context` categories
  3. Emits `{ type: 'text', content, isComplete: true }` via `SSETransport.emit()`
  4. Forces immediate `persistence.flush()` for `workflow_result` category
- **`sendStructuredEvent()`** (line 81): Handles `'tool'`, `'result'` (session info), `'workflow_dispatch'` message chunks
- **`emitRetract()`** (line 212): Removes last buffered segment from persistence, emits `{ type: 'retract' }` over SSE
- **Streaming**: Always `'stream'` (hardcoded)
- **Unique**: No auth (single-developer tool on local machine). No polling/WebSocket — output-only. Message persistence layer (other adapters don't persist). `emitLockEvent()` for UI lock indicators. `setupEventBridge()` for workflow worker → parent SSE forwarding. `SSETransport.scheduleCleanup()` with `RECONNECT_GRACE_MS = 5000ms`.

## How Adapters Are Registered (`server/src/index.ts`)

```typescript
1. Check env var: Boolean(process.env.XYZ_BOT_TOKEN)
2. Instantiate: new XyzAdapter(token, streamingMode)
3. Register handler: adapter.onMessage(async event => {
     const conversationId = getConversationId(event);
     const threadId = await ensureThread(conversationId, event);
     const history = await fetchThreadHistory(event); // optional
     await lockManager.acquireLock(threadId, async () => {
       await handleMessage(adapter, threadId, content, context);
     });
   });
4. Start: await adapter.start();
```

**Exceptions**:
- **GitHub** is different — self-contained, handles its own lock acquisition internally
- **Web** is always enabled (not conditional on env vars)

## Building a New Adapter: Checklist

1. Create `packages/adapters/src/{category}/{platform}/adapter.ts`
2. Create `packages/adapters/src/{category}/{platform}/auth.ts` with `parseAllowedXxx()` + `isXxxAuthorized()`
3. Implement `IPlatformAdapter` — all 6 required methods
4. Use the lazy logger pattern (never module-scope init)
5. Parse auth whitelist in constructor from env var
6. Check auth in message handler before calling `onMessage` callback; silent-reject unauthorized
7. Use `splitIntoParagraphChunks()` from `../../utils/message-splitting`
8. Register in `packages/server/src/index.ts` following the env-check → instantiate → onMessage → start pattern
9. Add the platform type string to any switch/if chains that check `getPlatformType()`
10. Export from `packages/adapters/src/index.ts`

## What NOT to Do

- **Don't** initialize logger at module scope — use the lazy pattern
- **Don't** send error messages to unauthorized users — silently drop the event
- **Don't** call `handleMessage` directly without acquiring a conversation lock first (except GitHub, which owns its own lock)
- **Don't** store bot session state on the adapter — put it in the DB via `sessionDb`
- **Don't** assume messages have line breaks — always run through `splitIntoParagraphChunks`
- **Don't** use shell-interpretation APIs for subprocess calls — always use `execFileAsync` from `packages/git/src/exec.ts` which uses the safer execFile semantics

## Debug Flow

1. **Event not reaching Archon**: Is the adapter started? Check `archon workflow status` and `launchctl list | grep archon` (macOS) or your service manager.
2. **Event received but user not authorized**: Check `${PLATFORM}_ALLOWED_USER_IDS` env var. Log line: `adapter.<name>: unauthorized_webhook` with masked user.
3. **Authorization passes but no workflow dispatches**: Check `parseOrchestratorCommands()` — the AI router may not have emitted a structured command. Enable stdout logging on the Archon server to see the full AI response.
4. **Messages split incorrectly**: Check the character limit for your platform and the `buffer` value. Adjust if the platform's API rejects at a different boundary than documented.
