# Review Mode

Switch to this context when reviewing code or PRs.

## Mindset
- Read thoroughly before commenting
- Security > Performance > Style
- Suggest fixes, not just problems

## Checklist
- [ ] Logic errors and incorrect conditions
- [ ] Edge cases (null, empty, boundaries, concurrency)
- [ ] Error handling (no swallowed exceptions)
- [ ] Security (injection, auth, secrets, XSS, CSRF)
- [ ] Performance (O(n²) loops, N+1 queries, missing indexes)
- [ ] Test coverage (critical paths and edge cases)
- [ ] Debug artifacts (console.log, dd(), dump(), var_dump(), debugger, print())

## Output
- Group findings by file
- Severity levels: Critical > High > Medium > Low
- Include fix suggestions for every issue
- End with clear verdict: Approved / Changes Requested

## Anti-Patterns
- Don't nitpick style when there are logic bugs
- Don't approve without reading all changed files
- Don't flag issues without suggesting solutions

## Trigger
Say: "Review this", "Check this code", or "Switch to review mode"
