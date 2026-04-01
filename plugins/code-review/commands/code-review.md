---
description: Code review with self-reflection scoring, technology-aware rules, and multi-mode support
---

# /code-review — Self-Reflection Scored Code Review

Review code changes using the two-pass self-reflection scoring pipeline. Generates findings, scores each for confidence 1-10, and filters noise by threshold.

$ARGUMENTS

## Usage

Determine the review scope from arguments:

- No arguments: review staged changes (`git diff --cached`), fall back to unstaged (`git diff`), fall back to last commit (`git diff HEAD~1`)
- `--pr` or `--pr <number>`: review the current PR or a specific PR number
- `--commit <sha>`: review a specific commit
- `--files <paths>`: review specific files or directories
- `--mode <mode>`: set review mode (`quick`, `thorough`, `security`, `pr`)
  - Default: auto-select based on changeset size (< 100 lines = quick, else thorough)
  - When `--pr` is used, default mode is `pr`
- `--threshold <N>`: override confidence threshold (1-10, default: per-mode)
- `--comment`: post review as PR comment (requires `--pr`)

## Process

### 1. Determine Scope

```bash
# Check current state
git status
git log --oneline -5

# For staged changes (default)
git diff --cached --stat
git diff --cached

# For unstaged changes (fallback)
git diff --stat
git diff

# For PR review
gh pr view --json number,title,body,files
gh pr diff

# For specific commit
git show <sha> --stat
git diff <sha>~1..<sha>

# For specific files
git diff -- <paths>
```

Count total lines changed to auto-select mode if not specified.

### 2. Detect Technology Stack

```bash
# Check project config files
cat composer.json 2>/dev/null | head -50
cat package.json 2>/dev/null | head -50
cat pubspec.yaml 2>/dev/null | head -30
cat angular.json 2>/dev/null | head -10
```

Based on detected stack, read matching context files from `plugins/code-review/contexts/`:
- PHP project → load `php.md`
- Laravel detected → load `laravel.md`
- Livewire detected → load `livewire.md`
- Filament detected → load `filament.md`
- Vue/Nuxt detected → load `vue-nuxt.md`
- Angular detected → load `angular.md`
- Magento 2 detected → load `magento2.md`
- WordPress detected → load `wordpress.md`
- Electron detected → load `electron.md`
- Flutter/Dart detected → load `flutter.md`
- NativePHP detected → load `nativephp.md`
- TypeScript files → load `typescript.md`

Multiple contexts can be loaded simultaneously.

### 3. Read All Changed Files in Full

For each changed file, read the entire file (not just the diff hunk). Understanding surrounding context is essential for accurate review.

### 4. First Pass — Generate Findings

Check every changed file against:
- Universal review rules (correctness, security, error handling, performance, edge cases, debug artifacts)
- Loaded technology-specific rules

For each finding, record:
- File path and line number
- Category and severity
- Description of the issue
- Suggested fix with actual code

### 5. Second Pass — Self-Reflection Scoring

Re-evaluate each finding and assign confidence 1-10:

| Score | Meaning |
|-------|---------|
| 9-10 | Certain bug or vulnerability |
| 7-8 | Very likely a real issue |
| 5-6 | Probably an issue, context-dependent |
| 3-4 | Might be intentional, worth flagging |
| 1-2 | Likely intentional or stylistic |

Apply adjustments:
- +2 if matches a known technology-specific anti-pattern from loaded contexts
- +1 if involves untrusted input or external data
- -1 if code has a comment explaining the pattern
- -1 if finding is in test/mock/fixture code
- -2 if similar code exists elsewhere in codebase (likely intentional)
- -3 if finding is in generated or vendored code

### 6. Filter by Threshold

| Mode | Default Threshold | Description |
|------|-------------------|-------------|
| quick | >= 7 | Security + correctness only, skip style |
| thorough | >= 4 | All categories |
| security | >= 3 (security) / >= 7 (other) | Security-focused |
| pr | >= 5 | PR review with verdict |

### 7. Run Tests

```bash
# Detect and run test suite
# PHP/Laravel
composer test 2>/dev/null || php artisan test 2>/dev/null || ./vendor/bin/pest 2>/dev/null || ./vendor/bin/phpunit 2>/dev/null

# JavaScript/TypeScript
npm test 2>/dev/null || npx vitest run 2>/dev/null || npx jest 2>/dev/null

# Flutter/Dart
flutter test 2>/dev/null

# Python
pytest 2>/dev/null
```

### 8. Produce Report

Output the structured review report with:
- Severity-grouped findings with confidence scores
- Code-level fix suggestions for every finding
- Security checklist
- Test status
- Filtered findings count (transparency)
- Verdict (for PR mode)

## Examples

```
# Review staged changes (auto-detect mode)
/code-review:code-review

# Thorough review of all changes
/code-review:code-review --mode thorough

# Review a specific PR
/code-review:code-review --pr 42

# Review PR and post as comment
/code-review:code-review --pr 42 --comment

# Security audit of specific files
/code-review:code-review --mode security --files src/auth/

# Review last commit with lower threshold
/code-review:code-review --commit HEAD --threshold 3

# Quick scan of staged changes
/code-review:code-review --mode quick
```
