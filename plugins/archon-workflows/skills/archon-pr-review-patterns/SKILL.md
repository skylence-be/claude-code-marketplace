---
name: archon-pr-review-patterns
description: Master Archon PR review patterns — the three review output flavors (top-level plain, top-level anchor-linked, true inline review comments), how to override archon-post-review-to-pr for clickable file:line links, how to build a pr-review-inline custom workflow that parses diff hunks and posts via gh api pulls/{n}/reviews, and the review→fix→re-review loop closure via pr-fix-review-feedback. Use when setting up or customizing Archon PR review behavior, or closing the human-review-feedback loop.
category: engineering
tags: [archon, pr-review, github, inline-comments, code-review, workflow]
related_skills: [archon-dag-workflow-authoring, archon-github-adapter-patterns]
---

# Archon PR Review Patterns

End-to-end patterns for Archon-driven PR review, including the custom inline-comment workflow that the public docs don't cover and the review-fix-review loop for closing the feedback cycle.

## When to Use This Skill

- Setting up a PR review flow for a new repo
- Overriding the bundled `archon-smart-pr-review` to produce better output
- Building a true inline review experience (comments attached to diff lines)
- Closing the review→fix→re-review loop automatically
- Cleaning up MCP noise + bot-marker noise from PR timelines
- Debugging why a review workflow posts nothing (or too much)

## The Three Review Output Flavors

| Flavor | Mechanism | Effort | Output Style |
|---|---|---|---|
| **Top-level plain** | Default `archon-smart-pr-review` | None | Single PR comment, prose + backtick file:line refs |
| **Top-level anchor-linked** | Override `archon-post-review-to-pr` | Low (per-repo command file) | Single PR comment, every `{file}:{line}` is a clickable blob URL pinned to head SHA |
| **True inline review comments** | Custom `pr-review-inline` workflow | High (diff parsing + JSON review payload) | Formal GitHub review with comments attached to individual diff lines |

Start with anchor-linked — it's the highest return per line of code. Build inline only if the team actively cares about per-line thread resolution.

## Flavor A — Default Top-Level (Bundled)

The bundled `archon-smart-pr-review` does:

1. Classify PR complexity (trivial/small/medium/large) with a haiku model
2. Route to relevant review agents (code-review, error-handling, test-coverage, comment-quality, docs-impact) in parallel
3. Synthesize findings into `$ARTIFACTS_DIR/review/synthesis.md`
4. Post as a single PR comment via `archon-post-review-to-pr`
5. Auto-fix CRITICAL/HIGH findings in a separate commit

The final comment contains `Location: \`{file}:{line}\`` references in plain backticks — readable but not clickable.

## Flavor B — Anchor-Linked Override

Create `.archon/commands/archon-post-review-to-pr.md` in the target repo. Same name as the bundled command = your file wins.

Key additions the override must do:

```bash
# Fetch PR head SHA to build stable blob URLs
PR_NUMBER=$(cat $ARTIFACTS_DIR/.pr-number)
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
HEAD_SHA=$(gh pr view "$PR_NUMBER" --json headRefOid --jq .headRefOid)
```

Then instruct the AI to format every Location field as:

```markdown
**Location**: [`{file}:{line}`](https://github.com/{REPO}/blob/{HEAD_SHA}/{file}#L{line})
```

**Why head SHA, not branch name**: branches get deleted after merge; SHA-pinned blob URLs survive forever.

Post with `gh pr comment "$PR_NUMBER" --body-file "$ARTIFACTS_DIR/review/comment-body.md"`. Use `--body-file` (not `--body`) to avoid shell-quoting gotchas with backticks and dollar signs.

## Flavor C — True Inline Review Comments

GitHub has two APIs for PR comments:

- `POST /repos/{owner}/{repo}/issues/{n}/comments` — top-level (what `gh pr comment` uses)
- `POST /repos/{owner}/{repo}/pulls/{n}/reviews` — formal review with optional inline comments[]

Archon's bundled adapter only uses the first. Building a workflow that uses the second requires four steps.

### Step 1: Fetch Diff and Build Valid-Lines Allowlist

GitHub's review-comment API doesn't accept "line 200 of file X" — it accepts a `line` that must be **changed or added on the RIGHT side of the diff**. Any finding pointing at an untouched line gets rejected with 422.

Parse the PR's unified diff and build an allowlist:

```bash
gh api --paginate "repos/$REPO/pulls/$PR_NUM/files" > $ARTIFACTS_DIR/pr-files.json

jq -r '.[] | select(.patch) | "FILE=\(.filename)\n\(.patch)"' \
  $ARTIFACTS_DIR/pr-files.json \
  | awk '
      $0 ~ /^FILE=/ { file=substr($0,6); right=0; next }
      $0 ~ /^@@/ {
        s=$0; sub(/.*\+/,"",s)
        split(s,a,","); split(a[1],b," ")
        right=b[1]+0
        next
      }
      right==0 { next }
      $0 ~ /^\+\+\+/ { next }
      $0 ~ /^---/ { next }
      $0 ~ /^\+/ { print file ":" right; right++; next }
      $0 ~ /^ /  { print file ":" right; right++; next }
    ' > $ARTIFACTS_DIR/valid-lines.txt
```

Each output line is `path:linenumber` — the `line` field you can legally use in a review comment.

### Step 2: AI Review Producing Structured JSON

Constrain the AI to only flag lines from `valid-lines.txt`. Output JSON:

```json
{
  "body": "Top-level review summary in markdown.",
  "findings": [
    {"path": "server/utils/x.ts", "line": 42, "severity": "blocker", "body": "..."},
    {"path": "...", "line": 55, "severity": "suggestion", "body": "..."}
  ]
}
```

Write to `$ARTIFACTS_DIR/review.json`.

### Step 3: Filter and Build Review Payload

```bash
jq -R . $ARTIFACTS_DIR/valid-lines.txt | jq -s . > $ARTIFACTS_DIR/valid-lines.json

jq --slurpfile valid $ARTIFACTS_DIR/valid-lines.json '
  ($valid[0] // []) as $v
  | {
      body: (.body // ""),
      event: "COMMENT",
      comments: [
        (.findings // [])[]
        | . as $f
        | ( ($f.path // "") + ":" + (($f.line // 0) | tostring) ) as $pl
        | select($v | index($pl) != null)
        | {
            path: $f.path,
            line: ($f.line | tonumber),
            side: "RIGHT",
            body: ("**" + (($f.severity // "comment") | ascii_upcase) + "**: " + ($f.body // ""))
          }
      ]
    }
' $ARTIFACTS_DIR/review.json > $ARTIFACTS_DIR/review-payload.json
```

Always use `event: "COMMENT"` — never `APPROVE` or `REQUEST_CHANGES`. A hallucinating AI with merge-blocking power is a disaster.

**GitHub requires non-empty `body` or non-empty `comments`**. Empty both = 422. Fallback:

```bash
INLINE=$(jq '.comments | length' $ARTIFACTS_DIR/review-payload.json)
BODY_LEN=$(jq -r '.body | length' $ARTIFACTS_DIR/review-payload.json)
if [ "$INLINE" = "0" ] && [ "$BODY_LEN" -lt 5 ]; then
  jq '.body = "No issues found. LGTM!"' $ARTIFACTS_DIR/review-payload.json > tmp \
    && mv tmp $ARTIFACTS_DIR/review-payload.json
fi
```

### Step 4: Post the Review

```bash
gh api --method POST "repos/$REPO/pulls/$PR_NUM/reviews" \
  --input $ARTIFACTS_DIR/review-payload.json
```

Findings outside the diff that were dropped should already have been folded into the AI's `body` field (instruct the AI to do this in the prompt). That way nothing is lost — unanchorable findings appear at the top, anchored ones appear as inline threads.

## Review → Fix → Re-Review Loop

`archon-smart-pr-review` has a built-in **auto-fix** phase that addresses CRITICAL/HIGH findings immediately — it's a machine-driven review loop.

What it DOESN'T cover: a **human-driven loop** where a reviewer leaves comments, you want Archon to address them, and then re-review. For that, build a `pr-fix-review-feedback` workflow:

1. Fetch all inline review comments (`gh api repos/.../pulls/<n>/comments`)
2. Fetch top-level PR comments (`gh api repos/.../issues/<n>/comments`)
3. Filter to Archon-authored or human-authored based on allowlist rules
4. Skip resolved threads
5. Read each finding, apply the fix to the PR branch
6. `pnpm lint:fix && pnpm typecheck`
7. Commit on the PR branch
8. Push
9. Post `@archon re-review — feedback addressed in <new-sha>` to trigger the next review

The re-review comment routes through the normal Archon webhook flow → `archon-smart-pr-review` runs again → new findings (ideally fewer) get posted.

## Pre-flight `pnpm install` Pattern

Every review workflow's first bash node MUST ensure `node_modules` and `.nuxt/` exist, because Claude subprocesses spawned in fresh worktrees will otherwise fail their MCP server connections and spam the PR with errors:

```yaml
- id: preflight
  bash: |
    set -e
    if [ ! -d node_modules ]; then
      pnpm install --frozen-lockfile 2>&1 | tail -5
    fi
    if [ ! -f .nuxt/eslint.config.mjs ]; then
      pnpm nuxi prepare 2>&1 | tail -10
    fi
  timeout: 600000
```

Bump the timeout to 600-1200 seconds depending on install+prepare speed on a cold worktree.

## MCP Noise Mitigation

Symptom: 8+ `MCP server connection failed` comments per PR review run, because each DAG node spawns a fresh Claude subprocess and each one tries to connect to project-local MCP servers (e.g. `drizzle-mcp` needs `node_modules`, `nuxt` MCP needs the dev server running on :3000).

**Fix 1 — pre-flight install** (above): addresses drizzle but not nuxt-dev-server-dependent servers.

**Fix 2 — move dev-state MCP servers to user-local config**:

```bash
claude mcp add drizzle --scope local \
  node node_modules/drizzle-mcp/dist/cli.js ./drizzle-mcp.config.ts
claude mcp add nuxt --scope local --transport sse http://localhost:3000/__mcp/sse
```

These land in `~/.claude.json` scoped to the current project's absolute path. Archon worktrees live at a **different** path (`~/.archon/workspaces/...`) so the subprocess Claude running there doesn't see them. Your main dev still does.

**Fix 3 — slim `.mcp.json`** to only servers that work in any worktree (e.g. `nuxt-docs` external SSE). Commit the slim version.

Combining all three brings MCP noise from 8+/run to 0-1/run.

## Post-Run Cleanup

Even with noise mitigation, you'll want a cleanup pass. See `archon-github-adapter-patterns` for the `BOT_RESPONSE_MARKER` filter pattern. Typical run: delete all marker-tagged comments, keep the two substantive `# Comprehensive PR Review` and `# Auto-Fix Report` comments (they lack the marker because they're posted via direct `gh pr comment` inside the DAG).
