# Review Modes

Four review modes optimized for different scenarios. Each mode adjusts the confidence threshold, category focus, and output format to match the review context.

## Mode Selection

### Auto-Selection Logic

When no mode is specified, the reviewer auto-selects based on:

1. If `--pr` flag is present → **PR Review** mode
2. If total lines changed < 100 → **Quick Scan** mode
3. If total lines changed >= 100 → **Thorough Review** mode
4. If `--mode security` is specified → **Security-Focused** mode (always manual)

### Override

Users can always override with `--mode <mode>`. The `--threshold <N>` flag overrides the mode's default threshold.

## Quick Scan

**Purpose:** Fast feedback on small changes. Get results in under a minute.

| Setting | Value |
|---------|-------|
| Confidence threshold | >= 7 |
| Categories checked | security, correctness |
| Categories skipped | maintainability, style |
| Default trigger | < 100 lines changed |

### Behavior
- Only report findings the reviewer is highly confident about
- Skip style and maintainability — these are noise for small changes
- Still check all security rules (but threshold filters low-confidence ones)
- No verdict — just findings and security checklist
- Skip debug artifact scan (too noisy for quick feedback)

### When to Use
- Reviewing a quick bug fix
- Checking a small config change
- Fast feedback during development iteration
- Pre-commit sanity check on staged changes

## Thorough Review

**Purpose:** Comprehensive quality gate before merge. Catches everything worth catching.

| Setting | Value |
|---------|-------|
| Confidence threshold | >= 4 |
| Categories checked | ALL (security, correctness, performance, error-handling, edge-case, maintainability, style) |
| Categories skipped | None |
| Default trigger | >= 100 lines changed |

### Behavior
- Report all findings above the threshold, including moderate-confidence ones
- Include maintainability and style suggestions (separated in their own section)
- Run full debug artifact scan (console.log, dd(), commented-out code, TODO without tickets)
- Run existing test suites
- Report coverage gaps for changed code paths
- Include the "Filtered Out" section showing what was below threshold

### When to Use
- Final review before merging a feature branch
- Quality gate in CI/CD pipeline
- Reviewing a large refactoring
- Code audit of a new module or feature

## Security-Focused

**Purpose:** Prioritize security findings. Use for security audits and sensitive code areas.

| Setting | Value |
|---------|-------|
| Security finding threshold | >= 3 |
| Non-security finding threshold | >= 7 |
| Categories checked | ALL, but security gets priority |
| Default trigger | Manual only (`--mode security`) |

### Behavior
- Security findings use a lower threshold (>= 3) — err on the side of over-reporting
- Non-security findings still included but only at high confidence (>= 7)
- Extended security checklist (all OWASP Top 10 categories)
- Scan for hardcoded secrets (API keys, passwords, tokens, private keys)
- Check dependency lock files for known vulnerabilities if changed
- Flag any use of `eval()`, `exec()`, `shell_exec()`, `Function()` constructors
- Check auth middleware coverage on all route changes
- Verify CSRF protection on state-changing endpoints
- Check for path traversal in file operations
- Report security findings first, before other categories

### Additional Security Checks
- **Secrets scanning**: Regex patterns for AWS keys, API tokens, private keys, passwords in strings
- **Dependency audit**: If `composer.lock`, `package-lock.json`, or `yarn.lock` changed, note that dependency audit should be run
- **Auth coverage**: For every new/modified route, verify auth middleware is applied
- **Input validation**: For every new/modified endpoint, verify input is validated before use

### When to Use
- Security audit before release
- Reviewing authentication/authorization code
- Changes to payment processing, user data handling, or API keys
- After a security incident (reviewing related code)
- Compliance review

## PR Review

**Purpose:** Pull request review with a verdict. Designed for the PR review workflow.

| Setting | Value |
|---------|-------|
| Confidence threshold | >= 5 |
| Categories checked | ALL |
| Verdict | APPROVED / APPROVED WITH CONDITIONS / CHANGES REQUESTED |
| Default trigger | When `--pr` flag is used |

### Behavior
- Include diff context (what specific lines changed in each file)
- Produce a clear verdict at the end
- Check for merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Verify PR description matches the actual changes
- Check that new tests exist for new functionality
- Report if tests pass or fail
- If `--comment` flag is present, format output for posting as PR comment

### Verdict Criteria

**APPROVED:**
- No critical or high-severity findings
- All security checks pass
- Tests pass (or no tests to run)

**APPROVED WITH CONDITIONS:**
- No critical findings
- 1-2 high-severity findings that are straightforward to fix
- Or: tests not run but code looks correct
- List specific conditions that must be met

**CHANGES REQUESTED:**
- Any critical finding
- 3+ high-severity findings
- Security vulnerabilities found
- Tests fail
- Missing tests for new functionality with complex logic

### PR Comment Format

When `--comment` is used, the output is formatted for GitHub/GitLab:

```markdown
## Code Review

**Mode:** PR Review | **Stack:** [detected] | **Files:** [N]

[Severity-grouped findings with code suggestions]

### Security Checklist
[checklist]

### Verdict: [APPROVED/CONDITIONS/CHANGES REQUESTED]
[summary]

---
*Reviewed with self-reflection scoring (threshold: 5/10)*
```
