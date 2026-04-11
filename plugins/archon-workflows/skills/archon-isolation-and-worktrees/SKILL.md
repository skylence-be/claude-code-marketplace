---
name: archon-isolation-and-worktrees
description: Master Archon's git worktree isolation system — the 7-step resolution order, worktree path layout, creation flow, cleanup lifecycle, port allocation (deterministic MD5 hash per worktree), stale detection, makeRoom strategy, branch adoption patterns, and worktree.copyFiles config. Use when debugging worktree creation failures, understanding how Archon chooses reuse vs create, cleaning up stale environments, or configuring which gitignored files get copied into new worktrees.
category: engineering
tags: [archon, worktree, isolation, git, cleanup, ports]
related_skills: [archon-dag-workflow-authoring, archon-github-adapter-patterns, archon-cli-reference]
---

# Archon Isolation & Worktrees

Complete guide to Archon's worktree-based isolation system. Based on the official `.claude/docs/isolation-and-worktree-guide.md` in the Archon source plus hands-on experience resolving worktree issues on v0.3.5.

## The Big Picture

Every Archon workflow runs in an **isolated environment**. Concrete implementation: a git worktree on a dedicated branch, created under `~/.archon/workspaces/<owner>/<repo>/worktrees/<branch>/`. Multiple workflows can run in parallel on the same repo without stepping on each other.

The isolation system has five concerns:

1. **Request types** — what kind of workflow is asking? (issue, PR, review, thread, task)
2. **Resolution** — reuse an existing worktree or create a new one? 7-step algorithm
3. **Creation** — branch, sync, worktree add, copy gitignored files
4. **Cleanup** — remove worktrees after merge, stale timeout, or limit pressure
5. **Port allocation** — each worktree gets a deterministic port for dev servers

## Branded Types (`packages/git/src/types.ts`)

Three branded string types prevent path confusion at compile time:

| Type | Factory | Rejects |
|---|---|---|
| `RepoPath` | `toRepoPath(s)` | empty string |
| `BranchName` | `toBranchName(s)` | empty string |
| `WorktreePath` | `toWorktreePath(s)` | empty string |

Always use the factories — never pass raw strings where branded types are expected.

## Five Isolation Request Types

All extend `IsolationRequestBase` (carries `codebaseId`, `canonicalRepoPath: RepoPath`, optional `description`):

| Type | `workflowType` | Branch Pattern | When |
|---|---|---|---|
| `IssueIsolationRequest` | `'issue'` | `issue-{identifier}` | Fixing a GitHub issue |
| `PRIsolationRequest` | `'pr'` | actual PR head branch (same-repo) or `pr-{N}-review` (fork) | PR review |
| `ReviewIsolationRequest` | `'review'` | `review-{identifier}` | Standalone review workflow |
| `ThreadIsolationRequest` | `'thread'` | `thread-{8-hex-hash}` | Slack, Telegram, Discord |
| `TaskIsolationRequest` | `'task'` | `task-{slugified}` (max 50 chars) | CLI manual task |

Adapters build the corresponding request type based on where the event came from and pass it through to the resolver via `IsolationHints`.

## The 7-Step Resolution Order

`IsolationResolver.resolve()` in `packages/isolation/src/resolver.ts` executes these steps in strict order. Each step can short-circuit.

### Step 1 — Existing Environment Reference

If the request carries `existingEnvId`, check DB row AND filesystem path via `worktreeExists()`. Both valid → return `resolved`. DB exists but filesystem gone → `stale_cleaned` (caller retries with no reference).

### Step 2 — No Codebase

If `request.codebase` is `null` → return `{ status: 'none', cwd: '/workspace' }`. Workflow runs without isolation.

### Step 3 — Workflow Reuse

`store.findActiveByWorkflow(codebaseId, workflowType, workflowId)` finds an existing environment with the same workflow identity (e.g. same issue number, same PR number). If filesystem valid → reuse. If filesystem gone → mark destroyed, fall through to step 4.

### Step 4 — Linked Issue Sharing

When `hints.linkedIssues` is non-empty (PR references issues via `Closes #42` etc.), iterate issue numbers and try `findActiveByWorkflow(codebaseId, 'issue', issueNum)`. First live match → reuse. This lets a PR review happen in the same worktree as the fix workflow that produced the PR.

### Step 5 — PR Branch Adoption

When `hints.prBranch` is set, call `findWorktreeByBranch(canonicalPath, prBranch)` to scan `git worktree list --porcelain`. If found and path exists → create a DB row with `metadata: { adopted: true, adopted_from: 'skill' }` pointing at the existing worktree. This lets Archon inherit worktrees that external tools (or prior runs) created.

### Step 6 — Limit Check + Auto-cleanup

Compare `store.countActiveByCodebase()` against `maxWorktrees` (default 25). If at limit → call `cleanup.makeRoom()` which removes **merged** branches. If still at limit → `blocked` with a formatted user message explaining the limit and breakdown.

### Step 7 — Create New Environment

1. Construct concrete `IsolationRequest` from `workflowType` + hints
2. Call `provider.create(isolationRequest)`
3. On known error → `blocked` with classified message
4. On unknown error → re-throw (crash)
5. On success → `store.create()` to register in DB
6. If `store.create()` fails → destroy orphaned worktree before re-throwing

## Worktree Creation Flow

`WorktreeProvider.create(request)` in `packages/isolation/src/providers/worktree.ts:56`:

### 1. Generate names + check adoption

- `generateBranchName(request)` → branch name based on request type
- `getWorktreePath(request, branchName)` → filesystem path
- `findExisting()` → check if path already exists OR PR branch has a worktree

### 2. Sync workspace

- Calls `syncWorkspace(repoPath, baseBranch)`
- Runs `git fetch origin <branch>` with 60s timeout
- Auto-detects default branch: `symbolic-ref` → `origin/main` → `master`

### 3. Create worktree

- **Same-repo PRs**: `git fetch origin prBranch` → `git worktree add <path> -b prBranch origin/prBranch`
- **Fork PRs**: fetch `refs/pull/{N}/head` → create at SHA → checkout branch
- **Everything else**: `git worktree add <path> -b <branchName> origin/<baseBranch>`
- Before creation: `cleanOrphanDirectoryIfExists()` removes stale non-worktree directories at the target path

### 4. Copy configured files

- **Default**: always copies `.archon/` directory (so worktrees have the same workflows + commands as the main repo)
- **User config**: additional paths from `.archon/config.yaml` `worktree.copyFiles`
- Supports `"source -> destination"` arrow syntax for renaming during copy
- Path traversal blocked via `isPathWithinRoot()` security check

## Worktree Path Layout

From `getWorktreeBase()` in `packages/git/src/worktree.ts:29`:

### Project-scoped layout (repo under `~/.archon/workspaces/`)

- Base: `~/.archon/workspaces/<owner>/<repo>/worktrees/`
- Path: `<base>/<branchName>`

Example: `/Users/jv/.archon/workspaces/skylence-be/tastytrade.skylence.be/worktrees/refactor/nautilus-route-factory`

### Legacy global layout (repo elsewhere)

- Base: `~/.archon/worktrees/`
- Path: `<base>/<owner>/<repo>/<branchName>`

The project-scoped layout is preferred for new repos. Legacy is kept for backward compatibility with repos registered before the path refactor.

## Cleanup Flow

### `removeEnvironment()` in `packages/core/src/services/cleanup-service.ts:134`

1. Fetch DB row. If `status === 'destroyed'` → return (idempotent)
2. Get `canonicalRepoPath` from codebase record
3. Check `worktreeExists()` for the path
4. If exists and `force` is false → check `hasUncommittedChanges()` (fail-safe: returns `true` on unexpected errors). If changes exist → skip removal
5. Call `provider.destroy(path, options)`

### `WorktreeProvider.destroy()` (`providers/worktree.ts:105`)

Returns `DestroyResult` tracking partial failures:

1. If path already gone → `worktreeRemoved: true`
2. If path exists → `git worktree remove [--force] path`
3. If directory persists after git removal (untracked files) → `rm -rf`
4. If `branchName` provided → `git branch -D branchName`
5. If `deleteRemoteBranch: true` → `git push origin --delete branchName`

## Error Classification

`classifyIsolationError(err)` in `packages/isolation/src/errors.ts`:

| Error pattern | User-friendly message |
|---|---|
| `permission denied` / `eacces` | "Permission denied while creating workspace." |
| `timeout` | "Timed out creating workspace." |
| `no space left` / `enospc` | "No disk space available." |
| `not a git repository` | "Target path is not a valid git repository." |
| `branch not found` | "Branch not found." |

Unknown errors are **re-thrown as crashes**. `IsolationBlockedError` signals that ALL message handling must stop — the user has already been notified via the blocked message.

## The Adoption Pattern

Two entry points for adopting worktrees that Archon didn't create:

### Path-based adoption (in `WorktreeProvider.create()`)

Before any git operations, the provider checks:
- Does the expected worktree path already exist?
- Does `findWorktreeByBranch()` return a match for the PR branch?

If yes → return adopted environment with `metadata: { adopted: true }`.

### DB-level adoption (in `IsolationResolver.tryBranchAdoption()`)

Uses `findWorktreeByBranch()` to scan git's worktree list. Creates a DB row **without** calling `provider.create()` at all. Returns `{ method: { type: 'branch_adoption', branch } }`.

Use case: a workflow externally created a worktree via `git worktree add`, then invokes Archon which needs to own it. Adoption lets Archon pick it up without recreating.

## Port Allocation

`getPort()` in `packages/core/src/utils/port-allocation.ts`:

1. If `PORT` env var is set → use it
2. If CWD is a worktree → `MD5(cwd)`, take `readUInt16BE(0) % 900 + 100` → port = `3090 + offset` (range: 3190-4089)
3. If CWD is NOT a worktree → `3090`

**Key property**: same worktree always gets the same port (deterministic hash). Parallel workflows on different worktrees never collide on dev server ports.

Useful when a workflow spawns a dev server in its worktree — you can reach it predictably from tests.

## Stale Environment Detection

`isEnvironmentStale(env, staleDays)` in `cleanup-service`:

1. Check `getLastCommitDate()` (`git log -1 --format=%ci`)
2. If recent commit exists and within threshold → not stale
3. Otherwise check `env.created_at` against threshold
4. **Default threshold: 14 days** (`STALE_THRESHOLD_DAYS`)

## Scheduled Cleanup

`runScheduledCleanup()` runs on Archon server startup + every 6 hours.

For each active environment:

1. **Filesystem gone** → `removeEnvironment()` (mark destroyed, remove DB row if orphaned)
2. **Branch merged into main** → remove (skipped if uncommitted changes OR other conversations reference it)
3. **Stale (14+ days, non-Telegram)** → remove (same uncommitted-changes check)

After environment cleanup: `sessionDb.deleteOldSessions(30)` (30-day session retention).

## `makeRoom()` Strategy

When at the worktree limit (default 25):

- Only removes **merged** branches (not stale ones — stale might still be in progress)
- For each candidate env:
  - Check `isBranchMerged(repoPath, branchName, mainBranch)`
  - Skip if uncommitted changes OR conversations reference it
  - Remove with `deleteRemoteBranch: true`

If merged cleanup frees space → proceed with creation. If not → block with a formatted message showing breakdown of merged/stale/active counts.

## Worktree Copy Files Configuration

In your repo's `.archon/config.yaml`:

```yaml
worktree:
  # Base branch for new worktrees (optional — auto-detected)
  baseBranch: main

  # Gitignored files to copy from main repo into new worktrees.
  # These are gitignored, so worktrees don't get them automatically.
  copyFiles:
    - .env                              # plain path → copied to same relative path
    - .env.local
    - .env -> .env.archon-debug        # arrow syntax: copy and rename
    - data/fixtures/
    - config/local-secrets.json
```

**Important**: tracked files (anything in git) are already in the worktree automatically — only use `copyFiles` for gitignored files like `.env` variants and local dev data.

**Security**: path traversal (`../`) is blocked by `isPathWithinRoot()`. Paths must resolve inside the repo root.

## Environment Isolation Pitfalls

### 1. Missing `.env` in worktrees

If the workflow needs `.env` (which is gitignored) and `copyFiles` doesn't list it, workflows will fail at `pnpm nuxi prepare` or database migration steps. **Always add `.env` to `copyFiles` for repos that need runtime env vars.**

### 2. Missing `node_modules` in worktrees

`node_modules` is too large to copy. Workflows must run `pnpm install --frozen-lockfile` as a pre-flight step before any Claude subprocess that depends on it. Add a `preflight` bash node at the top of every workflow:

```yaml
- id: preflight
  bash: |
    set -e
    if [ ! -d node_modules ]; then pnpm install --frozen-lockfile 2>&1 | tail -5; fi
    if [ ! -f .nuxt/eslint.config.mjs ]; then pnpm nuxi prepare 2>&1 | tail -10; fi
  timeout: 600000
```

### 3. MCP server noise in fresh worktrees

Project-local MCP servers (e.g. `drizzle-mcp` needing `node_modules`, `nuxt` MCP needing a dev server on :3000) will fail to connect in fresh worktrees and spam the PR with `MCP server connection failed` comments via Archon's batch mode.

**Fixes**:
- Add pre-flight install (above) so drizzle-mcp resolves
- Move dev-state-dependent MCP servers from committed `.mcp.json` to `~/.claude.json` via `claude mcp add --scope local` — those are path-scoped to the main dev directory, invisible to Archon worktrees
- Slim committed `.mcp.json` to only always-online servers (e.g., external SSE endpoints)

### 4. Duplicate codebase registration

When the webhook auto-registers a codebase at `~/.archon/workspaces/...` alongside the pre-existing CLI-registered codebase at the main dev dir, the Archon dashboard can show confusing duplicate entries. Same `name` + git URL, different `default_cwd`. Deduplicate:

```bash
sqlite3 ~/.archon/archon.db "
  SELECT id, default_cwd FROM remote_agent_codebases
  WHERE name = '<owner>/<repo>'
"
# pick the duplicate to delete (usually the .archon/workspaces one)
sqlite3 ~/.archon/archon.db "
  DELETE FROM remote_agent_codebases WHERE id = '<duplicate_id>'
"
```

Foreign keys are OFF in Archon's SQLite (`PRAGMA foreign_keys = 0`), so check for dependent rows first:

```bash
sqlite3 ~/.archon/archon.db "
  SELECT COUNT(*) FROM remote_agent_conversations WHERE codebase_id = '<id>';
  SELECT COUNT(*) FROM remote_agent_workflow_runs WHERE codebase_id = '<id>';
  SELECT COUNT(*) FROM remote_agent_isolation_environments WHERE codebase_id = '<id>';
"
```

If all zero, the duplicate is safe to delete.

## Diagnostic Queries

### List all active environments for a repo

```sql
SELECT id, workflow_type, workflow_id, status, working_path, created_at
FROM remote_agent_isolation_environments
WHERE codebase_id = (SELECT id FROM remote_agent_codebases WHERE name='<owner>/<repo>')
  AND status = 'active'
ORDER BY created_at DESC;
```

### Find orphaned environments (DB row but filesystem gone)

```bash
sqlite3 ~/.archon/archon.db "
  SELECT id, working_path FROM remote_agent_isolation_environments WHERE status='active'
" | while IFS='|' read id path; do
  if [ ! -d "$path" ]; then
    echo "ORPHAN: $id → $path"
  fi
done
```

### List worktrees git knows about

```bash
git -C <repo-path> worktree list --porcelain
```

## Source of Truth

| Concern | File |
|---|---|
| Branded types | `packages/git/src/types.ts` |
| `execFileAsync` wrapper | `packages/git/src/exec.ts` |
| Low-level worktree ops | `packages/git/src/worktree.ts` |
| Branch ops | `packages/git/src/branch.ts` |
| Repo ops (sync, clone) | `packages/git/src/repo.ts` |
| Isolation request types | `packages/isolation/src/types.ts` |
| `IIsolationStore` interface | `packages/isolation/src/store.ts` |
| Factory / singleton | `packages/isolation/src/factory.ts` |
| 7-step resolver | `packages/isolation/src/resolver.ts` |
| `WorktreeProvider` | `packages/isolation/src/providers/worktree.ts` |
| File copy utilities | `packages/isolation/src/worktree-copy.ts` |
| Error classification | `packages/isolation/src/errors.ts` |
| Cleanup service | `packages/core/src/services/cleanup-service.ts` |
| Port allocation | `packages/core/src/utils/port-allocation.ts` |
| Official docs | `.claude/docs/isolation-and-worktree-guide.md` |
