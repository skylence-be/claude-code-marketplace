# Git Diff Analysis

How to gather the right code for review depending on the scope: staged changes, unstaged changes, specific commits, PR diffs, or arbitrary file sets.

## Scope Resolution

### Priority Order (when no arguments given)

1. **Staged changes** (`git diff --cached`) — most common pre-commit review
2. **Unstaged changes** (`git diff`) — working directory review
3. **Last commit** (`git diff HEAD~1`) — review what was just committed

If all three are empty, there's nothing to review.

### Explicit Scopes

| Flag | Diff Command | Use Case |
|------|-------------|----------|
| (none) | `git diff --cached` → `git diff` → `git diff HEAD~1` | Pre-commit review |
| `--pr [N]` | `gh pr diff [N]` | Pull request review |
| `--commit <sha>` | `git diff <sha>~1..<sha>` | Review a specific commit |
| `--files <paths>` | `git diff -- <paths>` or direct file read | Review specific files |

## Reading Diffs Correctly

### Always Read the Full File

The diff shows what changed, but **the review needs the full file context**. A function that looks correct in isolation might be wrong when you see the surrounding code.

For each file in the changeset:
1. Read the diff to understand what changed
2. Read the full file to understand the context
3. Check imports and dependencies the changed code relies on

### Diff Stat First

Before reading full diffs, get the stat view to understand scope:

```bash
git diff --cached --stat    # Files changed + line counts
git diff --cached --numstat # Machine-readable: additions, deletions, file
```

This tells you:
- How many files changed (scope of review)
- Which files have the most changes (prioritize these)
- Total line count (determines auto-mode selection)

### Understanding Hunk Headers

```diff
@@ -15,7 +15,9 @@ function processOrder($order)
```

This means: starting at line 15 in the old file (7 lines of context), starting at line 15 in the new file (9 lines of context). The function name after `@@` tells you which function was modified.

## Handling Large Diffs

When the changeset is very large (> 500 lines changed, > 20 files):

### Prioritization Strategy

1. **Security-sensitive files first**: Auth, middleware, API routes, payment processing
2. **New files second**: Entirely new code needs more scrutiny than modifications
3. **Core logic third**: Business logic, models, services
4. **Config/migration/test last**: Lower risk, review if time permits

### File Type Priority

| Priority | File Types |
|----------|-----------|
| Critical | Auth controllers, middleware, API routes, payment handlers |
| High | Models, services, repositories, form requests |
| Medium | Views/templates, components, migrations |
| Low | Config files, test files, documentation, lock files |

### When to Skip Files

- Auto-generated files (migrations with only `up`/`down` boilerplate)
- Lock files (`composer.lock`, `package-lock.json`) — note they changed, don't review contents
- IDE/editor config (`.vscode/`, `.idea/`)
- Build artifacts (`.next/`, `dist/`, `build/`)

## File Rename Detection

Git diffs can show renamed files as a deletion + addition. Check for renames:

```bash
git diff --cached --diff-filter=R --name-only  # Renamed files
git diff --cached -M                           # Show renames with similarity %
```

When a file is renamed:
- Don't flag the "deleted" code as removed functionality
- Focus review on what actually changed in content, not the rename itself
- Check if all import paths were updated to reflect the new name

## PR-Specific Diff Handling

### Getting PR Context

```bash
# PR metadata
gh pr view <number> --json title,body,baseRefName,headRefName,files,additions,deletions

# Full diff against base
gh pr diff <number>

# Commits in the PR
gh pr view <number> --json commits
```

### Reviewing Against Base Branch

The PR diff shows changes relative to the base branch. Important considerations:
- Changes that exist in the base branch are not part of this review
- If the PR has merge commits, focus on the authored commits, not merge resolution
- Check if the base branch is up to date — stale base branches can mask conflicts

### Multi-Commit PRs

For PRs with many commits, understand the narrative:
1. Read commit messages to understand the sequence of changes
2. Review the final state (cumulative diff), not each commit individually
3. Exception: if commits show a fix-on-fix pattern, check that the final version is actually correct

## Branch Context

### Checking What's New

```bash
# What's different from main
git diff main...HEAD --stat

# Commits since branching from main
git log main..HEAD --oneline

# Files only in this branch
git diff main...HEAD --name-only
```

### Checking for Conflicts

```bash
# Check if branch can merge cleanly
git merge-tree $(git merge-base main HEAD) main HEAD

# Search for conflict markers in code (should never be committed)
grep -r "<<<<<<< " --include="*.php" --include="*.ts" --include="*.vue" .
```

Always scan for accidental merge conflict markers in the changeset — they're a critical finding (confidence: 10/10).
