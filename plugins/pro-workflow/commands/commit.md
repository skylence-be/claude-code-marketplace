---
description: Smart commit with quality gates, code scan, and conventional commit message
model: claude-sonnet-4-5
---

# /commit — Smart Commit with Quality Gates

Create a well-crafted commit after running quality checks.

$ARGUMENTS

## Process

### 1. Pre-Commit Checks

```bash
git status
git diff --stat
```

- Any unstaged changes to include?
- Any files that shouldn't be committed (.env, credentials, large binaries)?

### 2. Quality Gates

Run your project's quality commands:

```bash
# Run whatever lint/typecheck/test commands your project uses
# Examples:
#   npm run lint && npm run typecheck && npm test -- --changed
#   composer test && ./vendor/bin/pint --test
#   python -m pytest --co -q && python -m mypy .
#   flutter test && dart analyze
```

- All checks passing? If not, fix before committing.
- Skip only if user explicitly says `--no-verify`.

### 3. Code Scan

Scan staged changes for problems:

- `console.log` / `debugger` / `alert()` statements (JS/TS)
- `dd()` / `dump()` / `var_dump()` / `ray()` statements (PHP)
- `print()` / `breakpoint()` / `pdb` statements (Python)
- `print()` / `debugPrint()` statements (Dart/Flutter)
- TODO/FIXME/HACK comments without ticket references
- Hardcoded secrets, API keys, or credentials
- Leftover test-only code in production files

Flag any issues before proceeding.

### 4. Commit Message

Draft a conventional commit message based on the staged diff:

```
<type>(<scope>): <short summary>

<body - what changed and why>
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`, `style`

**Rules:**
- Summary under 72 characters
- Body explains *why*, not *what*
- Reference issue numbers when applicable
- No generic messages ("fix bug", "update code", "changes")

### 5. Stage and Commit

```bash
git add <specific files>
git commit -m "<message>"
```

- Stage specific files, not `git add -A`
- Show the commit hash and summary after

### 6. Learning Check

After committing, ask:
- Any learnings from this change to capture?
- Any patterns worth remembering for next time?

## Options

- **default**: Full quality gates + code scan + commit
- **--no-verify**: Skip quality gates (use sparingly)
- **--amend**: Amend the previous commit
- **--push**: Push to remote after commit

## Example Flow

```
> /commit

Pre-commit checks:
  Lint: PASS
  Types: PASS
  Tests: 12/12 PASS

Code scan:
  No debug statements found
  No hardcoded secrets found

Staged changes:
  src/auth/login.ts (+45 -12)
  src/auth/session.ts (+8 -3)

Suggested commit:
  feat(auth): add rate limiting to login endpoint

  Limit login attempts to 5 per IP per 15 minutes using
  Redis-backed sliding window. Returns 429 with Retry-After
  header when exceeded.

  Closes #142

Commit? (y/n)
```

## Related Commands

- `/pro-workflow:wrap-up` — Full end-of-session checklist
- `/pro-workflow:learn-rule` — Capture a learning after committing

---

**Trigger:** Use when user says "commit", "save changes", "commit this", or is ready to commit after making changes.
