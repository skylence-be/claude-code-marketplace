# Self-Reflection Scoring

The core algorithm that differentiates this reviewer from single-pass alternatives. By generating findings first and re-scoring them in a second pass, false positives drop by 40-60% (based on PR-Agent's research).

## Why Two Passes

Single-pass LLM reviews have a fundamental problem: the model generates findings while simultaneously reading code, which means it flags patterns before fully understanding the codebase context. Common failure modes:

- Flagging an intentional pattern as a bug (e.g., a deliberate `any` type for a dynamic plugin system)
- Rating every finding as "high severity" because there's no calibration step
- Missing that similar code exists elsewhere, suggesting the pattern is intentional
- Over-reporting style issues alongside real bugs, making the review noisy

The two-pass approach separates **detection** from **evaluation**, allowing the second pass to apply contextual calibration.

## Phase 2: Finding Generation (First Pass)

In the first pass, be deliberately over-inclusive. Generate a finding for anything that could be an issue. Don't self-censor — that's what the second pass is for.

For each finding, capture:

```
- file: path/to/file.ext
  line: 42
  category: security | correctness | performance | error-handling | edge-case | maintainability | style
  severity: critical | high | medium | low
  description: What the issue is and why it matters
  fix: Concrete code showing the corrected version
```

### What to check (universal rules)

1. **Correctness**: Logic errors, wrong operators, missing returns, unreachable code, type coercion bugs
2. **Security**: Injection (SQL, XSS, command), auth bypass, hardcoded secrets, CSRF, SSRF, path traversal
3. **Error Handling**: Swallowed exceptions, missing null checks, uncaught async errors, missing fallbacks
4. **Performance**: N+1 queries, O(n^2) loops, unbounded queries, memory leaks, unnecessary re-renders
5. **Edge Cases**: Null/empty/zero, unicode, timezone, concurrency, large inputs
6. **Debug Artifacts**: console.log, dd(), print(), commented-out code, TODO without tickets
7. **Maintainability**: Duplicated logic, deeply nested conditions, unclear naming
8. **Style**: Inconsistent formatting, convention violations (lowest priority)

### Technology-specific rules

After universal checks, apply rules from loaded technology context files. These catch framework-specific anti-patterns that generic review misses (e.g., `env()` outside config files in Laravel, missing `takeUntilDestroyed()` in Angular).

## Phase 3: Self-Reflection Scoring (Second Pass)

Now re-read each finding with fresh eyes. For each one, ask:

1. **Is this actually a problem?** Could there be a valid reason for this code?
2. **How confident am I?** Am I certain, or am I speculating?
3. **What's the evidence?** Can I point to the specific line and explain the bug?
4. **Does the codebase do this elsewhere?** If so, it's likely intentional.
5. **Is there a comment explaining it?** The developer may have documented the reason.

### Scoring Rubric

| Score | Criteria | Example |
|-------|----------|---------|
| **10** | Provably wrong. Will cause a bug or vulnerability in production. | SQL injection via string concatenation with user input |
| **9** | Almost certainly wrong. Clear violation of safety rules. | Missing auth middleware on admin endpoint |
| **8** | Very likely wrong. Strong evidence of a defect. | Null dereference on a value that can be null per the type |
| **7** | Likely wrong. Evidence points to a real issue. | Empty catch block swallowing database errors |
| **6** | Probably wrong, but context-dependent. | Missing pagination on a query that could return large results |
| **5** | Possibly wrong. Depends on usage patterns. | Using `any` type in TypeScript (might be intentional) |
| **4** | Somewhat likely. Worth mentioning in thorough review. | Missing null-safe operator on a chain |
| **3** | Uncertain. Might be intentional. | A `TODO` comment without a ticket reference |
| **2** | Likely intentional. Stylistic preference. | Using `array_push` instead of `$arr[] =` |
| **1** | Almost certainly intentional. | Naming convention different from rest of file |

### Score Adjustments

Apply these after initial scoring:

| Condition | Adjustment | Rationale |
|-----------|------------|-----------|
| Matches a known anti-pattern from technology context | **+2** | Documented framework pitfall, higher certainty |
| Involves untrusted input or external data | **+1** | Security boundary, err on side of caution |
| Code has an explanatory comment nearby | **-1** | Developer was aware of the tradeoff |
| Similar pattern exists elsewhere in the codebase | **-2** | Likely an intentional codebase convention |
| Finding is in test/mock/fixture code | **-1** | Lower standards appropriate for test helpers |
| Finding is in generated/vendored code | **-3** | Don't review generated code |

Cap final score at 1 (minimum) and 10 (maximum) after adjustments.

## Phase 4: Threshold Filtering

After scoring, apply the mode-specific threshold:

| Mode | Security Findings | Other Findings |
|------|-------------------|----------------|
| Quick scan | >= 7 | >= 7 |
| Thorough | >= 4 | >= 4 |
| Security-focused | >= 3 | >= 7 |
| PR review | >= 5 | >= 5 |

**Important rules:**
- Never filter out a finding scored 9 or 10, regardless of mode
- In security mode, security-category findings use a lower threshold (>= 3) than other categories (>= 7)
- Report the count of filtered findings for transparency ("12 findings filtered below threshold")
- Mention the highest-confidence filtered finding so the user knows what they're missing

## Handling Disagreement Between Passes

Sometimes the first pass flags something as critical, but the second pass finds evidence it's intentional. This is the system working as designed. Trust the second pass — it has more context.

However, if the finding involves:
- **Security**: Keep it even at lower confidence. Better to over-report security.
- **Data loss**: Keep it. The cost of a false negative is too high.
- **Production impact**: Keep it if the code runs in a hot path.

## Example: Before and After Scoring

### Before (First Pass — 8 findings)
1. SQL injection in raw query — will be scored high
2. Missing null check on optional param — moderate
3. Console.log left in production code — moderate
4. Using `==` instead of `===` in JS — depends on context
5. Missing return type on PHP function — style
6. Todo comment without ticket — low priority
7. Large file (500+ lines) — maintainability
8. Variable named `$x` — unclear naming

### After (Second Pass — 4 findings survive at threshold >= 5)
1. SQL injection → **10/10** — provably vulnerable ✓ KEEP
2. Missing null check → **7/10** — type allows null, no guard ✓ KEEP
3. Console.log → **6/10** — in a utility file, not test code ✓ KEEP
4. `==` vs `===` → **3/10** — codebase uses loose comparison throughout ✗ FILTERED
5. Missing return type → **2/10** — style, codebase doesn't use them ✗ FILTERED
6. Todo without ticket → **4/10** — might be intentional placeholder ✗ FILTERED
7. Large file → **2/10** — it's a migration file, expected ✗ FILTERED
8. Variable `$x` → **5/10** — in a math utility, conventional ✓ KEEP

Result: 4 findings reported, 4 filtered. The review is focused and actionable.
