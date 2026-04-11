---
name: archon-bundled-workflows
description: Reference for all 20 bundled Archon workflows — what each one does, when to use it, triggers, how to invoke, and how to override with a same-named file in .archon/workflows/. Covers archon-fix-github-issue, archon-smart-pr-review, archon-comprehensive-pr-review, archon-plan-to-pr, archon-idea-to-pr, archon-feature-development, archon-piv-loop, archon-refactor-safely, archon-architect, archon-create-issue, archon-resolve-conflicts, archon-issue-review-full, archon-validate-pr, archon-adversarial-dev, archon-interactive-prd, archon-ralph-dag, archon-remotion-generate, archon-workflow-builder, archon-test-loop-dag, archon-assist. Use when picking a workflow, wiring up automation, or deciding what to override.
category: engineering
tags: [archon, workflows, bundled, defaults, reference]
related_skills: [archon-dag-workflow-authoring, archon-bundled-commands, archon-cli-reference]
---

# Bundled Archon Workflows

Reference for the 20 workflows that ship with Archon v0.3.5 as default definitions at `/Users/jv/Archon/.archon/workflows/defaults/*.yaml`. Override any of them by creating a same-named file at `.archon/workflows/<name>.yaml` in your repo — the repo version wins at load time.

## Overrides 101

To customize a bundled workflow for one repo:

1. Copy the YAML: `cp /Users/jv/Archon/.archon/workflows/defaults/archon-smart-pr-review.yaml .archon/workflows/`
2. Edit: tweak nodes, change prompts, add/remove steps
3. Validate: `archon validate workflows archon-smart-pr-review`

Same strategy for command files (`.archon/commands/<name>.md` overrides `.archon/commands/defaults/<name>.md`).

To disable bundled workflows entirely in one repo, add to `.archon/config.yaml`:

```yaml
defaults:
  loadDefaultWorkflows: false
```

## Full Catalog

### 1. `archon-fix-github-issue`

**Purpose**: End-to-end fix for a GitHub issue — from bug classification through PR creation and smart review.

**Shape**: DAG (`nodes:` mode) with classify → investigate OR plan (based on type) → implement → create-pr → smart-review → self-fix → report.

**Triggers**: "fix this issue", "implement issue #123", "resolve this bug", "fix it", "fix issue", "resolve issue", "fix #123"

**NOT for**: Comprehensive multi-agent reviews (use `archon-issue-review-full`), questions about issues, CI failures, PR reviews, general exploration.

**Invoke**:
```bash
archon workflow run archon-fix-github-issue --branch fix/issue-42 "Fix #42"
```

---

### 2. `archon-smart-pr-review`

**Purpose**: Complexity-adaptive PR review. Classifies the PR first (trivial / small / medium / large) and routes to only the relevant review agents. Auto-fixes CRITICAL and HIGH findings.

**Shape**: DAG. Nodes: scope → sync → classify (haiku, structured output) → parallel review agents (code-review, error-handling, test-coverage, comment-quality, docs-impact) filtered by classifier → synthesize → auto-fix → post-review-to-pr.

**Triggers**: "smart review", "review this PR", "review PR #123", "efficient review", "smart PR review", "quick review"

**NOT for**: When you explicitly want ALL review agents (use `archon-comprehensive-pr-review` instead).

**Invoke**:
```bash
archon workflow run archon-smart-pr-review --branch review/pr-1 "Review PR #1"
```

Also responds to GitHub webhook mentions like `@archon review this PR`.

---

### 3. `archon-comprehensive-pr-review`

**Purpose**: Full multi-agent PR review that always runs every review agent in parallel regardless of PR complexity.

**Shape**: DAG. Same as smart-pr-review but without the classifier-based routing — all five review agents always run.

**Triggers**: "review this PR", "review PR #123", "comprehensive review", "full PR review", "review and fix", "check this PR", "code review"

**NOT for**: Quick questions about a PR, checking CI status, simple "what changed" queries. For small PRs prefer `archon-smart-pr-review`.

---

### 4. `archon-plan-to-pr`

**Purpose**: Execute an existing implementation plan end-to-end through PR.

**Shape**: 11-step pipeline. Reads plan, setup branch, scope limits, verify research, implement all tasks, validate, create PR, comprehensive review, synthesize + fix, final summary.

**Input**: Path to a plan file (`$ARTIFACTS_DIR/plan.md` or `.agents/plans/*.md`).

**NOT for**: Creating plans from scratch (use `archon-idea-to-pr`), quick fixes, standalone reviews.

---

### 5. `archon-idea-to-pr`

**Purpose**: Feature idea or description → end-to-end development → merged PR.

**Shape**: Like `archon-plan-to-pr` but with an initial planning phase that creates the plan from the idea.

**Input**: Feature description in natural language or a PRD file path.

**NOT for**: Executing existing plans (use `archon-plan-to-pr`), quick fixes, standalone reviews.

---

### 6. `archon-feature-development`

**Purpose**: Implement a feature from an existing plan → create PR. No review phase.

**Shape**: Steps mode. Implement the plan with validation loops → create pull request.

**Input**: Plan file path or GitHub issue containing a plan.

**NOT for**: Creating plans (plans should be created separately), bug fixes, code reviews.

---

### 7. `archon-piv-loop`

**Purpose**: Plan-Implement-Validate loop with human-in-the-loop at each phase.

**Shape**: Interactive. 1) EXPLORE conversation (arbitrary rounds) → 2) PLAN iteration → 3) IMPLEMENT autonomous loop (ralph) → 4) VALIDATE with human feedback.

**Triggers**: "piv", "piv loop", "plan implement validate", "guided development", "structured development", "build a feature", "develop with review"

**NOT for**: Autonomous implementation without planning (use `archon-feature-development`). NOT for PRD creation (use `archon-interactive-prd`). NOT for Ralph story-based implementation (use `archon-ralph-dag`).

**Note**: This is an **interactive** workflow. Requires the transparent relay protocol — not fully autonomous.

---

### 8. `archon-refactor-safely`

**Purpose**: Refactor code with continuous validation and behavior preservation.

**Shape**: DAG. Scans scope (read-only) → analyzes impact (read-only) → plans ordered task list → executes with type-check hooks after every edit → validates full suite → verifies behavior preservation (read-only) → creates PR with before/after comparison.

**Triggers**: "refactor", "refactor safely", "split this file", "extract module", "break up", "decompose", "safe refactor", "split file", "extract into modules"

**Safety features**:
- Analysis and verification nodes are read-only (`denied_tools: [Write, Edit, Bash]`)
- PreToolUse hooks check if each edit is in the plan
- PostToolUse hooks force type-check after every file change
- Behavior verification confirms no logic changes

---

### 9. `archon-architect`

**Purpose**: Architectural sweep, complexity reduction, codebase health improvement.

**Shape**: DAG with per-node hooks. Scans codebase metrics → analyzes with principled lens → plans simplifications → executes with self-review loops → validates → creates PR.

**Triggers**: "architect", "simplify codebase", "reduce complexity", "architectural sweep", "clean up architecture", "codebase health", "fix architecture"

**Noteworthy**: Uses per-node hooks to create organic quality loops (lint after write, self-review) and inject architectural principles before changes.

---

### 10. `archon-create-issue`

**Purpose**: Report a bug as a GitHub issue with automated reproduction.

**Shape**: DAG. Classifies problem area (haiku) → gathers context in parallel (templates, git state, duplicates) → investigates relevant code → reproduces using area-specific tools (agent-browser, CLI, DB queries) → gates on reproduction success → creates issue with evidence OR reports back if cannot reproduce.

**Triggers**: "create issue", "file a bug", "report this bug", "open an issue for", "create github issue", "report issue", "log this bug"

**Reproduction gating**: If the issue cannot be reproduced, the workflow does NOT create an issue. Instead it reports what was tried and suggests next steps.

---

### 11. `archon-resolve-conflicts`

**Purpose**: PR merge conflict resolution.

**Shape**: Fetches latest base branch → analyzes conflicts → auto-resolves simple ones → presents options for complex conflicts → commits and pushes resolution.

**Triggers**: "resolve conflicts", "fix merge conflicts", "rebase this PR", "resolve this", "fix conflicts", "merge conflicts", "rebase and fix"

**NOT for**: PRs without conflicts, general rebasing without conflicts, squashing commits.

---

### 12. `archon-issue-review-full`

**Purpose**: Full comprehensive fix + review pipeline for a GitHub issue. Multi-phase pipeline combining investigation, implementation, comprehensive review, fix, and summary.

**Shape**: 5 stages: investigate → implement → comprehensive-review → fix-review-issues → final-summary

**Triggers**: "full review", "comprehensive fix", "fix with full review", "deep review", "issue review full"

**NOT for**: Simple issue fixes (use `archon-fix-github-issue` instead).

---

### 13. `archon-validate-pr`

**Purpose**: PR validation that tests both main (reproduce bug) and feature branch (verify fix).

**Shape**: Fetches PR info → finds free ports → parallel code review (main vs feature) → E2E test on main (reproduce bug) → E2E test on feature (verify fix) → final verdict report.

**Triggers**: "validate PR", "validate pr #123", "test this PR", "verify PR", "full PR validation", "validate pull request", "test PR end-to-end"

**NOT for**: Quick code-only reviews (use `archon-smart-pr-review`), fixing issues, general exploration.

**Designed for parallel execution**: each instance finds its own free ports to avoid conflicts.

---

### 14. `archon-adversarial-dev`

**Purpose**: Build a complete application from scratch using adversarial (GAN-inspired) development.

**Shape**: Three-role GAN workflow — Planner creates spec with sprints, state-machine loop alternates between Generator (builds code) and Evaluator (attacks it) with hard pass/fail thresholds (each criterion ≥ 7/10). Stops on sprint failure after max retries.

**Triggers**: "adversarial dev", "adversarial development", "build with adversarial", "gan dev", "adversarial build", "build app adversarially", "adversarial coding"

**NOT for**: Bug fixes, PR reviews, refactoring existing code, simple one-off tasks.

---

### 15. `archon-interactive-prd`

**Purpose**: Create a Product Requirements Document through guided conversation.

**Shape**: Interactive. 1) Understand the idea → ask foundation questions → 2) Research market & codebase → ask deep-dive questions → 3) Assess feasibility → ask scope questions → 4) Generate PRD → validate technical claims.

**Triggers**: "create a prd", "new prd", "interactive prd", "plan a feature", "product requirements", "write a prd"

**NOT for**: Autonomous PRD generation without human input.

**Note**: Requires the transparent relay protocol.

---

### 16. `archon-ralph-dag`

**Purpose**: Run a Ralph (stateless-loop) implementation from a PRD or idea.

**Shape**: DAG that detects input type (existing `prd.json`, existing `prd.md` needing stories, or raw idea), generates PRD if needed, runs stateless Ralph loop implementing one story per iteration, creates PR.

**Triggers**: "ralph", "run ralph", "ralph dag", "run ralph dag"

**Accepts**: idea description, path to existing `prd.md`, or directory with `prd.md + prd.json`.

---

### 17. `archon-remotion-generate`

**Purpose**: Generate or modify Remotion video compositions using AI.

**Shape**: AI writes Remotion React code → renders preview stills → renders full video → summarizes output.

**Triggers**: "create a video", "generate video", "remotion", "make an animation", "video about", "animate"

**Requires**: A Remotion project in the working directory (`src/index.ts`, `src/Root.tsx`).

---

### 18. `archon-workflow-builder`

**Purpose**: Create new custom workflows through guided generation.

**Shape**: Scans codebase → extracts intent (JSON) → generates YAML → validates → saves.

**Triggers**: "build me a workflow", "create a workflow", "generate a workflow", "new workflow", "make a workflow for", "workflow builder"

**NOT for**: Editing existing workflows, creating non-workflow files.

**Note**: Archon's built-in workflow authoring. For more control (pre-flight install, naming conventions, suggested branches), use a custom `workflow-author` workflow with the `archon-workflow-author` agent.

---

### 19. `archon-test-loop-dag`

**Purpose**: Demo/testing workflow. Initializes a counter, iterates until 3, reports completion.

**Shape**: DAG with a loop node. Pure demonstration.

**Triggers**: "test-loop-dag", "run test-loop-dag" (explicit only)

**NOT for**: Real work. This is a sanity-check workflow for the loop node type.

---

### 20. `archon-assist`

**Purpose**: Fallback agent for requests that don't match any other workflow.

**Shape**: Full Claude Code agent with all tools available.

**Triggers**: "no other workflow matches" — the orchestrator routes here when the router prompt can't pick a more specific workflow.

**Notes**: Will inform the user when assist mode is used so they know which workflow fired.

## Grouping by Purpose

| Goal | Workflow |
|---|---|
| Fix a bug from an issue | `archon-fix-github-issue` |
| Implement a feature from scratch | `archon-idea-to-pr` |
| Implement a feature from a plan | `archon-plan-to-pr` or `archon-feature-development` |
| Quick PR review | `archon-smart-pr-review` |
| Thorough PR review | `archon-comprehensive-pr-review` or `archon-issue-review-full` |
| PR validation with E2E | `archon-validate-pr` |
| Resolve merge conflicts | `archon-resolve-conflicts` |
| Refactor safely | `archon-refactor-safely` |
| Architecture sweep | `archon-architect` |
| Create a bug issue | `archon-create-issue` |
| Create a PRD interactively | `archon-interactive-prd` |
| Guided PIV development | `archon-piv-loop` |
| Ralph-style autonomous | `archon-ralph-dag` |
| Build from scratch (GAN style) | `archon-adversarial-dev` |
| Generate a video | `archon-remotion-generate` |
| Generate a new workflow | `archon-workflow-builder` |
| Catch-all assistant | `archon-assist` |

## Override Patterns

### Pattern 1: Customize output formatting

Example: rewrite `archon-post-review-to-pr.md` command to produce anchor-linked Location references. Copy the default, add GitHub blob URL generation, commit at `.archon/commands/archon-post-review-to-pr.md`.

### Pattern 2: Replace a workflow with a thin wrapper

Example: shadow `archon-smart-pr-review` to route to an inline-review workflow. Create `.archon/workflows/archon-smart-pr-review.yaml` that only contains one node calling the custom workflow.

### Pattern 3: Disable bundled defaults entirely

`.archon/config.yaml`:
```yaml
defaults:
  loadDefaultWorkflows: false
  loadDefaultCommands: false
```

Use when the bundled workflows don't fit the project's style and you want a minimal dashboard.

### Pattern 4: Selective disable via override

Create an empty `.archon/workflows/archon-remotion-generate.yaml` with invalid content — wait, **don't do this**, it creates noise. Better: leave all defaults loaded and rely on the router's description match to prevent accidental invocation.
