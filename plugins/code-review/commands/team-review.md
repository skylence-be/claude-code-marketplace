---
description: Spawn a parallel review team with specialized reviewers (security, performance, correctness) for thorough multi-perspective code review
---

# /team-review — Parallel Code Review Team

Spawn an agent team where multiple reviewers analyze the same changeset simultaneously, each through a different lens. Produces a consolidated review with findings from all perspectives.

> **Requires:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in environment or settings.

$ARGUMENTS

## Usage

- No arguments: review staged/unstaged changes with 3 default reviewers
- `--pr <number>`: review a specific PR
- `--commit <sha>`: review a specific commit
- `--files <paths>`: review specific files
- `--reviewers <roles>`: customize reviewer roles (default: security, performance, correctness)
- `--threshold <N>`: confidence threshold for all reviewers (default: 5)

## Default Team (3 Reviewers)

### 1. Security Reviewer
**Focus:** Vulnerabilities, auth bypass, injection, secrets, CSRF, XSS, SSRF
**Confidence threshold for security findings:** >= 3 (aggressive — better to over-report)
**Loads:** Technology-specific security rules from `plugins/code-review/contexts/`

### 2. Performance Reviewer
**Focus:** N+1 queries, O(n^2) algorithms, missing indexes, memory leaks, unbounded queries, unnecessary re-renders
**Confidence threshold:** >= 5
**Loads:** Technology-specific performance rules from `plugins/code-review/contexts/`

### 3. Correctness Reviewer
**Focus:** Logic errors, edge cases, error handling, type bugs, race conditions, missing returns, debug artifacts
**Confidence threshold:** >= 5
**Loads:** Technology-specific correctness rules from `plugins/code-review/contexts/`

## Process

### 1. Determine Scope (Lead)

Before spawning teammates, the lead gathers context:

```bash
# Get changeset info
git status
git diff --cached --stat || git diff --stat

# For PR
gh pr view <number> --json title,body,files,additions,deletions
gh pr diff <number>

# For commit
git show <sha> --stat

# Detect tech stack
cat composer.json 2>/dev/null | head -50
cat package.json 2>/dev/null | head -50
cat pubspec.yaml 2>/dev/null | head -30
```

### 2. Spawn Team

Create the team with specialized roles. Each teammate gets:
- The changeset (diff or file list)
- Their specific review focus area
- Technology-specific rules for detected stack
- The self-reflection scoring instructions

**Spawn prompt template for each reviewer:**

```
You are a [ROLE] reviewer. Review the following changeset through the lens of [FOCUS].

## Changeset
[diff or file list from step 1]

## Detected Stack
[detected technologies]

## Your Review Focus
[role-specific focus areas]

## Technology Rules
[loaded from plugins/code-review/contexts/ for detected stack]

## Review Pipeline
For each file in the changeset:
1. Read the full file (not just the diff)
2. Generate findings for your focus area
3. Score each finding 1-10 confidence
4. Filter below threshold [THRESHOLD]
5. Format as:

### [Severity] Findings
- **[file:line]** (confidence: N/10)
  [Description]
  ```[lang]
  // Current
  [code]
  // Fix
  [code]
  ```

## Boundaries
- Focus ONLY on [FOCUS] — other reviewers handle other areas
- Provide fix suggestions for every finding
- Score honestly — a review full of 10/10 findings loses credibility
- Read full files, not just diffs
```

### 3. Monitor & Collect (Lead)

While teammates work:
- Check progress periodically
- Don't interfere unless a teammate is stuck
- Wait for all teammates to complete

### 4. Synthesize (Lead)

Once all teammates finish, the lead:

1. **Collect** all findings from all reviewers
2. **Deduplicate** — if two reviewers flagged the same issue, keep the one with higher confidence
3. **Sort** by severity (critical > high > medium > low), then confidence
4. **Merge** into a single consolidated report

### 5. Produce Consolidated Report

```
## Team Review: [scope description]
Reviewers: Security, Performance, Correctness
Stack: [detected technologies]
Files reviewed: [N]
Total findings: [N] (Security: [N], Performance: [N], Correctness: [N])

### Critical (Must Fix)
- **[file:line]** [category] (confidence: N/10) — found by: [reviewer]
  [Description + fix]

### High (Should Fix)
[same format]

### Medium (Consider Fixing)
[same format]

### Low (Suggestions)
[same format]

### Security Checklist
- [x/space] No hardcoded secrets
- [x/space] No SQL injection vectors
- [x/space] No XSS vulnerabilities
- [x/space] Auth checks present where needed
- [x/space] Input validation on external data
- [x/space] CSRF protection on state-changing routes

### Reviewer Summary
| Reviewer | Findings | Filtered | Top Finding |
|----------|----------|----------|-------------|
| Security | [N] | [N] | [brief] |
| Performance | [N] | [N] | [brief] |
| Correctness | [N] | [N] | [brief] |

### Verdict
[APPROVED / APPROVED WITH CONDITIONS / CHANGES REQUESTED]
[Summary with conditions if any]
```

## Custom Reviewer Roles

Override the default 3 reviewers with `--reviewers`:

```bash
# Just security and correctness
/code-review:team-review --pr 42 --reviewers security,correctness

# Add a test coverage reviewer
/code-review:team-review --pr 42 --reviewers security,performance,correctness,testing

# Full review with all available roles
/code-review:team-review --pr 42 --reviewers security,performance,correctness,testing,maintainability
```

### Available Roles

| Role | Focus |
|------|-------|
| `security` | Vulnerabilities, auth, injection, secrets, CSRF, XSS |
| `performance` | N+1, algorithms, indexes, memory, unbounded queries |
| `correctness` | Logic errors, edge cases, error handling, types, race conditions |
| `testing` | Test coverage gaps, missing assertions, untested paths |
| `maintainability` | Code structure, duplication, naming, complexity |

## Examples

```bash
# Review PR with default team (3 reviewers)
/code-review:team-review --pr 42

# Review staged changes
/code-review:team-review

# Security-heavy review (2 security + 1 correctness)
/code-review:team-review --pr 42 --reviewers security,security,correctness

# Review specific files with low threshold
/code-review:team-review --files src/auth/ --threshold 3

# Review last commit
/code-review:team-review --commit HEAD
```

## Fallback (No Teams Available)

If agent teams are not enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` not set), fall back to sequential review:

1. Run security review pass
2. Run performance review pass
3. Run correctness review pass
4. Merge findings

This is slower but produces the same multi-perspective output. Suggest enabling teams for parallel execution.
