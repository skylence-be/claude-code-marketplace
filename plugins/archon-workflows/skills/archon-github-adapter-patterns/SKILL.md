---
name: archon-github-adapter-patterns
description: Master Archon's GitHub adapter — webhook event subscriptions, @archon mention detection, SSO-authorized PAT requirements, GITHUB_ALLOWED_USERS and GITHUB_BOT_MENTION config, BOT_RESPONSE_MARKER comment hygiene, stream vs batch mode, and the duplicate codebase registration bug. Use when installing the archon-webhook on a new repo, debugging webhooks that return 200 but never dispatch workflows, cleaning up noise comments from the adapter, or resolving SSO-related token failures in SSO-enforcing GitHub orgs.
category: engineering
tags: [archon, github, webhook, oauth, sso, bot, pr-review]
related_skills: [archon-dag-workflow-authoring, archon-pr-review-patterns]
---

# Archon GitHub Adapter Patterns

Hands-on guide to wiring, debugging, and hardening Archon's GitHub adapter. Covers webhook event selection, PAT requirements for SSO-enforcing orgs, common silent-failure modes, and how to clean up the noise that the current adapter's stream behavior leaves on PRs.

## When to Use This Skill

- Installing the Archon webhook on a new GitHub repo
- Debugging `@archon` mentions that reach Archon (200 OK) but don't dispatch a workflow
- Resolving 404 errors when Archon's octokit calls a private org repo
- Cleaning up `<!-- archon-bot-response -->` noise after a workflow run
- Configuring `GITHUB_ALLOWED_USERS` and `GITHUB_BOT_MENTION`
- Understanding why `pull_request.opened` doesn't trigger anything (only comments do)
- Deduplicating codebase entries when a repo got auto-registered twice

## The Webhook Event Set

**Install with exactly these events:**

```
issue_comment
pull_request
pull_request_review
pull_request_review_comment
```

**NOT needed** (and noisy if added):
- `push` — passes HMAC then silently no-ops in Archon v0.3.5
- `issues` — Archon reacts to issue *comments*, not `issues.opened`
- Everything else

**Critical distinction**: Archon's adapter reacts to `@archon` **mentions in comments only**. Mentions in PR bodies or issue descriptions are *explicitly ignored* (see `adapter.ts:364` — "We intentionally do NOT handle issues.opened or pull_request.opened"). Subscribing to `pull_request` is still useful for close/merge cleanup and for the orchestrator's isolation hints, but it won't auto-dispatch a review.

Subscribe via `gh api -X POST repos/<owner>/<repo>/hooks --input -` with the right JSON, or use the `archon-webhook` skill that automates the install. Upgrading an existing hook's event list is a `PATCH` on the hook ID.

## Required Config Env Vars (in `~/.archon/.env`)

```bash
WEBHOOK_SECRET=<hex>              # must match GitHub webhook secret
GITHUB_TOKEN=ghp_...              # adapter API calls read this FIRST
GH_TOKEN=ghp_...                  # clone handler reads this — no fallback
GITHUB_BOT_MENTION=archon         # the handle the adapter listens for
GITHUB_ALLOWED_USERS=user1,user2  # comma-separated allowlist
```

**Both `GITHUB_TOKEN` and `GH_TOKEN` must be set to the same value.** `adapter.ts:493` uses `GITHUB_TOKEN ?? GH_TOKEN` for octokit calls; `clone.ts:300` uses `GH_TOKEN` only with no fallback. Setting only one breaks either API calls OR cloning.

## PAT Types and SSO Orgs

**Classic PAT + SSO click-through is the right choice** for orgs that enforce SAML SSO (like private company orgs).

- **Classic PAT**: Generate with scopes `repo`, `read:org`, `workflow`. On the token detail page, scroll to **SSO** section and click **"Configure SSO" → "Authorize"** for the target org. Without this step, octokit returns 404 on every org repo even though the token is "valid".
- **Fine-grained PAT**: Requires per-org admin approval. Slower and trickier. Not recommended unless the org admins are on standby.

**Symptom of SSO-not-authorized**: octokit `repos.get` returns 404, the adapter's error message is swallowed (goes to the server's `/dev/null` stdout), the webhook shows `conversation created` but zero messages and zero workflow runs in `~/.archon/archon.db`.

**Verify before installing**:
```bash
curl -sS -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/<owner>/<repo> \
  -o /dev/null -w "HTTP %{http_code}\n"
```
Expect `HTTP 200`. Anything else = SSO step was missed or scopes wrong.

## Adapter Behavior Cheatsheet

From reading `/Users/jv/Archon/packages/adapters/src/forge/github/adapter.ts`:

| Event | Action |
|---|---|
| `push` | HMAC verify → no-op |
| `pull_request.opened/reopened/synchronize/edited` | **Ignored for routing** (not a mention trigger). Used for isolation hints. |
| `pull_request.closed/merged` | Cleanup worktree for the PR's isolation env |
| `issue_comment.created` (including PR comments) | HMAC + allowlist + mention-detect → if `@<BOT_MENTION>` → route to orchestrator |
| `pull_request_review` / `pull_request_review_comment` | Same mention logic as issue_comment |

**Mention matching** is case-insensitive and prefix-based. The comment body must contain the literal `@<GITHUB_BOT_MENTION>` token (e.g. `@archon`).

## Stream vs Batch Mode

GitHub adapter is hardcoded to **`batch`** mode (`adapter.ts:225`). This means each workflow node gets its own clean-ish output comment instead of every Claude chunk streaming live. But batch mode still posts multiple comments per workflow run:

- `🚀 Starting workflow: <name>` once per workflow
- Per-DAG-node assistant outputs
- `MCP server connection failed: ...` errors from Claude subprocess startup
- Final synthesized review/report

All Archon-authored comments contain a hidden marker: `<!-- archon-bot-response -->`

## Bot Response Marker Cleanup Pattern

After a workflow run, filter and delete noise:

```bash
gh api 'repos/<owner>/<repo>/issues/<n>/comments' \
  --jq '.[] | select(.body | contains("<!-- archon-bot-response -->")) | .id' \
  | while IFS= read -r id; do
      gh api -X DELETE "repos/<owner>/<repo>/issues/comments/$id" && echo "deleted $id"
    done
```

Preserves substantive comments (the Comprehensive PR Review + Auto-Fix Report, which are posted via `gh pr comment` in a DAG node and therefore lack the marker — fortunate side effect).

## Common Silent Failure: "200 OK but no workflow dispatch"

When `@archon` comment is posted, webhook returns 200, but `archon workflow status` shows nothing and no reply comment lands — walk through this checklist:

1. **Token scope / SSO**: test directly with `curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/repos/<owner>/<repo>`. If 404 → SSO not authorized. Fix: classic PAT + SSO click-through.
2. **Allowlist**: commenter's GitHub login must be in `GITHUB_ALLOWED_USERS`. Missing = silent reject.
3. **Bot mention format**: comment must contain literal `@<GITHUB_BOT_MENTION>`. A bare "archon" without the `@` doesn't match.
4. **Check the DB**: `sqlite3 ~/.archon/archon.db "SELECT * FROM remote_agent_conversations WHERE platform_type='github' ORDER BY created_at DESC LIMIT 5"`. If a conversation exists with zero messages, orchestrator started but clone or metadata fetch failed.
5. **Logs lost to /dev/null**: Archon server's launchd plist redirects stdout to `/dev/null` by default. Temporarily change `StandardOutPath` to `~/Library/Logs/archon/server.out.log` to see the silent errors during a debug session.

## Duplicate Codebase Registration Bug

After a webhook-originated workflow run, Archon sometimes registers a second `remote_agent_codebases` row pointing at `/Users/jv/.archon/workspaces/<owner>/<repo>` alongside the original row pointing at the user's main dev dir. Both have the same `name` and git URL but different `default_cwd`.

**Check**:
```bash
sqlite3 ~/.archon/archon.db \
  "SELECT id, name, default_cwd FROM remote_agent_codebases WHERE name='<owner>/<repo>'"
```

**Fix** (after confirming the duplicate has zero dependent rows):
```bash
sqlite3 ~/.archon/archon.db "DELETE FROM remote_agent_codebases WHERE id = '<duplicate_id>'"
```

**Verify no orphans** first: `remote_agent_conversations`, `remote_agent_workflow_runs`, and `remote_agent_isolation_environments` shouldn't reference the `id` you're about to delete. Foreign keys are off in Archon's SQLite (`PRAGMA foreign_keys = 0`), so the DB won't stop you.

## `archon-webhook` Skill Installation Pattern

The canonical webhook install script reads `WEBHOOK_URL` and `WEBHOOK_SECRET` from `~/.archon/.env`, checks for an existing hook by URL match, and either creates (POST) or upgrades (PATCH) the events list to the canonical set above. Running it twice is safe. Upgrading an existing hook preserves the hook ID and delivery history.
