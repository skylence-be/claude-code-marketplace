---
name: archon-bundled-commands
description: Reference for all 36 bundled Archon command files (.archon/commands/defaults/archon-*.md). Each command is an AI prompt template invoked by workflow nodes. Override any with a same-named .md in .archon/commands/ to customize behavior per-repo. Covers the review pipeline (code-review-agent, error-handling-agent, test-coverage-agent, comment-quality-agent, docs-impact-agent, synthesize-review, post-review-to-pr, auto-fix-review), the fix pipeline (implement, implement-tasks, implement-review-fixes, investigate-issue, fix-issue), plan management (create-plan, plan-setup, confirm-plan), PR operations (create-pr, finalize-pr, sync-pr-with-main, resolve-merge-conflicts, pr-review-scope), validation (validate, validate-pr-*), and utilities (simplify-changes, self-fix-all, web-research, workflow-summary, issue-completion-report, assist, ralph-generate, ralph-prd). Use when picking commands for workflow nodes, understanding what each does, or overriding specific prompts.
category: engineering
tags: [archon, commands, bundled, defaults, prompts, reference]
related_skills: [archon-dag-workflow-authoring, archon-bundled-workflows, archon-pr-review-patterns]
---

# Bundled Archon Commands

Reference for the 36 bundled command files shipping with Archon v0.3.5 at `/Users/jv/Archon/.archon/commands/defaults/archon-*.md`. Commands are AI prompt templates loaded by workflow `command:` nodes.

## Overrides 101

A same-named file in your repo's `.archon/commands/` **wins** over the bundled default at load time. Override order:

1. `<repo>/.archon/commands/<name>.md` (repo custom) — highest priority
2. `<repo>/.archon/commands/defaults/<name>.md` (repo-level override of defaults)
3. `/Users/jv/Archon/.archon/commands/defaults/<name>.md` (bundled) — fallback

**First match wins**. To override a bundled command, drop a file with the same name into your repo's `.archon/commands/`. No registration needed.

Validate with: `archon validate commands <name>`

## Catalog by Purpose

### Planning and Investigation (5 commands)

| Command | Purpose |
|---|---|
| `archon-investigate-issue` | Root-cause analysis for a GitHub issue; produces `investigation.md` with scope boundaries |
| `archon-create-plan` | Create an implementation plan from an idea or PRD; produces `plan-context.md` |
| `archon-plan-setup` | Setup phase for plan-based workflows; creates artifacts directory structure |
| `archon-confirm-plan` | Interactive plan confirmation gate (shown to user for approval) |
| `archon-web-research` | Web research helper for gathering external context |

### Implementation (4 commands)

| Command | Purpose |
|---|---|
| `archon-implement` | Execute an implementation plan on the current branch |
| `archon-implement-issue` | Implement the fix for an investigated issue |
| `archon-implement-tasks` | Loop-based task execution from a checklist |
| `archon-implement-review-fixes` | Apply fixes from a code review's findings |

### Fix / Apply (3 commands)

| Command | Purpose |
|---|---|
| `archon-fix-issue` | Fix a specific bug using investigation results |
| `archon-auto-fix-review` | Automatically fix CRITICAL/HIGH findings after a review |
| `archon-self-fix-all` | Aggressive self-fix across all review findings (used in `archon-architect`) |

### Review Pipeline (8 commands)

| Command | Purpose |
|---|---|
| `archon-pr-review-scope` | Gather PR context, verify reviewability, prepare artifacts dir for parallel agents |
| `archon-sync-pr-with-main` | Rebase PR branch onto latest main if needed |
| `archon-code-review-agent` | Code quality review — produces `code-review-findings.md` with severity tiers |
| `archon-error-handling-agent` | Error handling / edge case review |
| `archon-test-coverage-agent` | Test coverage analysis |
| `archon-comment-quality-agent` | Code comment / JSDoc / docstring quality |
| `archon-docs-impact-agent` | Docs impact review (CLAUDE.md, READMEs, API docs) |
| `archon-synthesize-review` | Collate findings from parallel agents into a single synthesis |
| `archon-post-review-to-pr` | Post the final review as a PR comment via `gh pr comment` |

### PR Operations (5 commands)

| Command | Purpose |
|---|---|
| `archon-create-pr` | Create a new draft PR using the repo's PR template |
| `archon-finalize-pr` | Mark a draft PR as ready for review |
| `archon-sync-pr-with-main` | (listed also in Review pipeline) |
| `archon-resolve-merge-conflicts` | Auto-resolve simple conflicts, present options for complex ones |
| `archon-simplify-changes` | Post-implementation pass to simplify overly complex code |

### Validation (6 commands)

| Command | Purpose |
|---|---|
| `archon-validate` | Generic validation runner (lint + typecheck + tests) |
| `archon-validate-pr-code-review-main` | Code review on main branch (for PR comparison) |
| `archon-validate-pr-code-review-feature` | Code review on PR feature branch |
| `archon-validate-pr-e2e-main` | E2E test on main branch to reproduce the bug |
| `archon-validate-pr-e2e-feature` | E2E test on PR branch to verify the fix |
| `archon-validate-pr-report` | Final validation report combining code review + E2E results |

### Ralph / Autonomous Loops (2 commands)

| Command | Purpose |
|---|---|
| `archon-ralph-prd` | Generate a PRD (problem, context, stories) from an idea |
| `archon-ralph-generate` | Generate PRD + stories from a raw idea non-interactively |

### Reporting and Summary (3 commands)

| Command | Purpose |
|---|---|
| `archon-workflow-summary` | Summarize a workflow run for the user |
| `archon-issue-completion-report` | Report fix completion back to the original GitHub issue |
| `archon-assist` | Fallback general-purpose AI assistant |

## Command File Format

All bundled commands follow this structure:

```markdown
---
description: One-line description of what this command does
argument-hint: <arg-format> or (no arguments)
---

# Command Title

## Your Mission
<one paragraph describing the goal>

## Phase 1: LOAD
<instructions to read inputs from $ARTIFACTS_DIR>

## Phase 2: EXECUTE / ANALYZE / GENERATE
<main work>

## Phase 3: REPORT
<output expectations>

### PHASE_N_CHECKPOINT
- [ ] required artifact exists
- [ ] required validation passed
```

Phase-based structure is strongly recommended for complex commands. Each phase has a checkpoint list to keep the AI on track.

## Most-Overridden Commands in Practice

Based on real-world use of repo-level overrides:

### 1. `archon-post-review-to-pr`

Override to customize the PR comment format. Example: rewrite every `{file}:{line}` into a clickable GitHub anchor link pinned to the PR head SHA for stable navigation.

Key override points:
- Load `PR_NUMBER`, `REPO`, `HEAD_SHA` via `gh`
- Rewrite Location field as `[`{file}:{line}`](https://github.com/{REPO}/blob/{HEAD_SHA}/{file}#L{line})`
- Post via `gh pr comment "$PR_NUMBER" --body-file "$ARTIFACTS_DIR/review/comment-body.md"`
- Verify via `gh pr view "$PR_NUMBER" --comments --json comments --jq '.comments | length'`

### 2. `archon-code-review-agent`

Override to add project-specific review rules from CLAUDE.md. Example additions:
- CLAUDE.md compliance section
- Framework-specific patterns (Nuxt SSR guards, Zod v3 API)
- Domain-specific correctness (Tastytrade SDK, dxFeed subscriptions)

### 3. `archon-synthesize-review`

Override to change the final synthesis format — group findings differently, emit structured JSON instead of markdown, or change the auto-fix severity threshold.

### 4. `archon-implement-review-fixes`

Override to enforce per-project fix constraints — e.g., "never auto-fix anything in `lib/auth/`".

### 5. `archon-create-plan`

Override to force-include project-specific context (e.g., always read `docs/architecture.md` first, always check `lib/db/schema/` for types).

## Override Pattern — Thin Wrapper

When you only want to ADD instructions to a bundled command (not replace it), the cleanest pattern is still to copy the full file and modify — command files don't support inheritance. But you can write a **minimal wrapper** that links back to the default behavior in prose:

```markdown
---
description: Post code review findings as a PR comment with clickable anchor links
argument-hint: (none - reads from artifacts)
---

# Post Review to PR — Anchor-Linked Override

Follows the default `archon-post-review-to-pr` behavior EXCEPT for Phase 2
(comment formatting), where every `{file}:{line}` reference becomes a
clickable GitHub blob URL pinned to the PR head SHA.

## Phase 1: LOAD — Get Context

(Reference the bundled command for how to load `PR_NUMBER` and `findings.md`;
no changes here.)

## Phase 2: FORMAT — Build PR Comment with Anchor Links

<new instructions>

## Phase 3: POST — Comment on PR

(Same as bundled: `gh pr comment <n> --body-file <file>`.)
```

This approach is fragile because the AI may not actually "reference" the bundled command without seeing it. Safer: copy the full bundled file and clearly mark the sections you changed at the top.

## Source of Truth

| Concern | Location |
|---|---|
| Bundled command files | `/Users/jv/Archon/.archon/commands/defaults/archon-*.md` |
| Workflow node loader | `/Users/jv/Archon/packages/workflows/src/loader.ts` |
| Command discovery order | Repo custom → repo defaults → bundled defaults |
| Per-repo override location | `<repo>/.archon/commands/<name>.md` |
