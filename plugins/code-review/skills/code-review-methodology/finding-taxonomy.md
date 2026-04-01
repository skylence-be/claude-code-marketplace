# Finding Taxonomy

Categories, severity levels, and output formatting for review findings.

## Categories

Every finding belongs to exactly one category. Categories are ordered by review priority.

### 1. Security

Issues that could lead to unauthorized access, data exposure, or system compromise.

**Examples:**
- SQL injection via string concatenation in queries
- XSS from unescaped user input rendered in HTML
- Hardcoded API key or password in source code
- Missing authentication on a protected endpoint
- CSRF vulnerability on state-changing route
- Path traversal in file upload/download
- SSRF via unvalidated URL parameter
- Insecure deserialization of user input

**Default severity:** Critical or High

### 2. Correctness

Code that produces wrong results or doesn't behave as intended.

**Examples:**
- Off-by-one error in loop boundary
- Wrong comparison operator (`>` instead of `>=`)
- Missing return statement in a branch
- Variable shadowing hiding an outer variable
- Type coercion bug (`==` vs `===` causing unexpected match)
- Race condition in concurrent code
- Inverted boolean condition

**Default severity:** High or Medium

### 3. Performance

Code that will be slow, use excessive resources, or degrade at scale.

**Examples:**
- N+1 query pattern (lazy loading in a loop)
- O(n^2) algorithm on potentially unbounded input
- Unbounded query without pagination or LIMIT
- Missing database index on a frequently queried column
- Memory leak (event listener never removed, growing array)
- Unnecessary re-render on every state change
- Synchronous I/O blocking an async context

**Default severity:** Medium or High (High if in a hot path)

### 4. Error Handling

Missing or incorrect error handling that could cause silent failures or crashes.

**Examples:**
- Empty catch block swallowing an exception
- Catch-all without logging or re-throwing
- Missing try-catch around external service call
- Unchecked null/undefined dereference
- Missing error boundary in UI component tree
- No fallback when an API call fails
- Promise without `.catch()` or `try/await`

**Default severity:** Medium

### 5. Edge Cases

Valid inputs or conditions that the code doesn't handle.

**Examples:**
- Empty array/collection passed to a function expecting at least one item
- Null value where the type technically allows it
- Zero or negative number in a division or index operation
- Unicode characters in string comparison or truncation
- Timezone-naive date comparison across zones
- Concurrent request modifying the same resource
- Deeply nested data exceeding recursion limits

**Default severity:** Medium or Low

### 6. Maintainability

Code that works but is hard to understand, modify, or extend.

**Examples:**
- Duplicated logic that should be a shared function
- Deeply nested conditionals (4+ levels)
- Function over 100 lines with mixed responsibilities
- Magic numbers without named constants
- Tightly coupled modules with circular dependencies
- Inconsistent error handling patterns across similar code

**Default severity:** Low or Medium

### 7. Style

Convention violations and formatting inconsistencies. Lowest priority — only flag if the project has established conventions.

**Examples:**
- Inconsistent naming (camelCase mixed with snake_case)
- Missing type annotations where the codebase uses them
- Import order doesn't match project convention
- Trailing whitespace or inconsistent indentation

**Default severity:** Low

## Severity Levels

### Critical (Must Fix Before Merge)

**Criteria:** Will cause data loss, security breach, or production outage if merged.

- Active security vulnerability exploitable in production
- Data corruption or loss path
- Authentication/authorization bypass
- Crash on common code path
- Merge conflict markers in code

### High (Should Fix Before Merge)

**Criteria:** Significant defect that will likely cause problems but isn't an immediate crisis.

- Bug that affects core functionality
- Security issue requiring specific conditions to exploit
- N+1 query that will be noticeable at current scale
- Error handling gap that could cause silent data loss
- Missing validation on user input

### Medium (Consider Fixing)

**Criteria:** Real issue that could cause problems but has limited blast radius or is unlikely to trigger.

- Edge case that could be hit in production
- Performance issue at scale but fine at current load
- Error handling gap with graceful degradation
- Missing test coverage for changed code path
- Debug artifact left in code

### Low (Suggestion)

**Criteria:** Not wrong, but could be better. Won't cause problems if ignored.

- Maintainability improvement
- Style inconsistency
- Minor performance optimization
- Code that could be more idiomatic
- Missing documentation on complex logic

## Writing Good Findings

### Description

A good finding description answers three questions in 1-2 sentences:

1. **What** is the issue? (the specific problem)
2. **Where** is it? (file and line)
3. **Why** does it matter? (the consequence)

**Good:** "The `processPayment()` function at `app/Services/PaymentService.php:45` concatenates user input directly into a SQL query, allowing SQL injection that could expose payment data."

**Bad:** "SQL injection possible." (too vague — where? what's the impact?)

**Bad:** "On line 45 of PaymentService.php, the function processPayment takes a parameter $amount which is passed to DB::raw() without using parameter binding, which means that if a malicious user were to craft a special input..." (too verbose — get to the point)

### Fix Suggestions

Every finding MUST include a concrete fix. Not pseudo-code — actual code the developer can copy.

**Good:**
```php
// Current (vulnerable)
DB::select("SELECT * FROM payments WHERE amount = $amount");

// Fix (parameterized)
DB::select("SELECT * FROM payments WHERE amount = ?", [$amount]);
```

**Bad:** "Use parameterized queries instead." (not actionable enough — show the code)

## Report Format

### Standard Report Structure

```
## Code Review: [scope description]
Mode: [quick-scan | thorough | security-focused | pr-review]
Stack: [detected technologies]
Files reviewed: [N]
Findings: [N total] ([N after filtering])
```

### Finding Format

```
### [Severity] (N findings)

- **[file:line]** [category] (confidence: N/10)
  [1-2 sentence description: what, where, why]
  ```[lang]
  // Current code
  [problematic code snippet]

  // Suggested fix
  [fixed code snippet]
  ```
```

### Section Order

1. Critical findings (must fix)
2. High findings (should fix)
3. Medium findings (consider fixing)
4. Low findings (suggestions)
5. Filtered out summary (transparency)
6. Security checklist
7. Test status
8. Verdict (PR mode only)

### Filtered Out Section

Always include for transparency:

```
### Filtered Out (below threshold)
4 findings filtered with confidence < 5
Highest-confidence filtered: Missing return type on `getUser()` (confidence: 4/10)
```

This lets the reviewer and developer know what was intentionally suppressed, and the highest-confidence filtered finding gives a sense of whether the threshold is too aggressive.
