---
name: code-review-methodology
description: Master the self-reflection scoring code review pipeline with technology-aware rule loading, multi-mode review, git diff analysis, and structured finding taxonomy. Use when reviewing code, understanding the review pipeline, or customizing review behavior.
category: quality
tags: [code-review, self-reflection, scoring, security, quality, pipeline]
related_skills: [laravel-security-patterns, laravel-testing-patterns, vitest-testing-patterns, typescript-vue-patterns]
---

# Code Review Methodology

A systematic code review approach combining automated finding generation with self-reflection confidence scoring to reduce noise and surface high-impact issues. Inspired by PR-Agent's two-pass scoring and Kodus AI's rule-based filtering.

## When to Use This Skill

- Understanding how the review pipeline works
- Customizing review modes and thresholds
- Working with git diffs for review scope
- Understanding finding categories and severity levels
- Implementing technology-specific review rules
- Tuning the confidence scoring to reduce false positives

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Self-Reflection Scoring | [self-reflection-scoring.md](self-reflection-scoring.md) | The generate-score-filter pipeline |
| Review Modes | [review-modes.md](review-modes.md) | Quick/thorough/security/PR mode configuration |
| Git Diff Analysis | [git-diff-analysis.md](git-diff-analysis.md) | Working with staged changes, commits, PRs |
| Finding Taxonomy | [finding-taxonomy.md](finding-taxonomy.md) | Categories, severity levels, output format |

## Quick Reference

### The Pipeline in 30 Seconds

```
1. GATHER  → git diff, detect stack, load rule contexts
2. DETECT  → identify technology stack from project files
3. GENERATE → first pass: find all potential issues
4. SCORE   → second pass: rate each finding 1-10 confidence
5. FILTER  → remove findings below mode threshold
6. REPORT  → severity-grouped output with fixes + verdict
```

### Mode Thresholds

| Mode | Threshold | When |
|------|-----------|------|
| Quick scan | >= 7 | Small changes (< 100 lines), fast feedback |
| Thorough | >= 4 | Large changes (> 100 lines), quality gate |
| Security | >= 3 (security) / >= 7 (other) | Security audits |
| PR review | >= 5 | Pull request review with verdict |

### Confidence Score Guide

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Certain bug or vulnerability | Always report |
| 7-8 | Very likely a real issue | Report in all modes |
| 5-6 | Probably an issue, context-dependent | Report in thorough/PR |
| 3-4 | Might be intentional, worth flagging | Report in thorough/security |
| 1-2 | Likely intentional or stylistic | Filter out in most modes |

### Score Adjustments

| Condition | Adjustment |
|-----------|------------|
| Matches known technology anti-pattern | +2 |
| Involves untrusted input or external data | +1 |
| Code has explanatory comment | -1 |
| Finding is in test/mock/fixture code | -1 |
| Similar pattern exists elsewhere in codebase | -2 |
| Finding is in generated/vendored code | -3 |

## Best Practices

1. **Always read the full file**, not just the diff — context determines whether code is actually buggy
2. **Score honestly** — a review full of 10/10 findings loses credibility
3. **Security findings get priority** — never filter out security issues aggressively
4. **Provide fixes, not just complaints** — every finding must include a suggested fix with code
5. **Respect existing patterns** — if the codebase uses a pattern consistently, reduce confidence rather than flagging it
6. **Check tests exist** — changed code without tests is always worth flagging
7. **Run existing tests** — a green test suite gives confidence; a red one changes review priority
8. **Load technology rules** — generic review misses framework-specific pitfalls; always detect and load contexts
