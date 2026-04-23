---
name: go-error-handling
description: Idiomatic Go error handling patterns including sentinel errors, error wrapping with %w, errors.Is/As, custom error types, and single-point handling. Use when implementing error handling in Go, reviewing code for missed errors, designing package error contracts, or migrating from pre-1.13 error patterns.
---

# Go Error Handling

## When to Use This Skill

- Implementing error handling for a new package or service
- Reviewing Go code for unchecked errors or double-handling
- Designing the error contract for a public package API
- Converting legacy error patterns (`==` comparison) to `errors.Is`/`errors.As`
- Deciding between sentinel errors, wrapped errors, and custom error types

## Pattern Files

| Pattern | Use Case |
|---------|----------|
| [sentinel-errors.md](sentinel-errors.md) | Package-level error variables callers check by identity |
| [error-wrapping.md](error-wrapping.md) | Adding context with `%w`, when to use `%v` instead |
| [custom-error-types.md](custom-error-types.md) | Structured error types for caller-inspectable data |

## Core Concepts

| Concept | Rule |
|---------|------|
| **Error as last return** | `error` is always the last return value |
| **nil for success** | Return `nil` error on success, never in-band signals |
| **Handle once** | Don't log AND return the same error — choose one |
| **`%w` to wrap** | Use `fmt.Errorf("context: %w", err)` to preserve unwrap chain |
| **`errors.Is`** | Always use `errors.Is(err, ErrSentinel)` — never `err == ErrSentinel` |
| **`errors.As`** | Use `errors.As(err, &target)` to extract typed error values |
| **No panic for errors** | `panic` is for programmer invariant violations only |

## Quick Reference

```go
// Sentinel error — package-level var, Err prefix
var ErrNotFound = errors.New("not found")

// Wrap with context using %w
return fmt.Errorf("loading user %d: %w", id, err)

// Check sentinel through wrap chain
if errors.Is(err, ErrNotFound) { ... }

// Extract custom error data
var ve *ValidationError
if errors.As(err, &ve) {
    log.Printf("field %s: %s", ve.Field, ve.Message)
}

// Handle once — log OR return, not both
if err != nil {
    return fmt.Errorf("doing work: %w", err)   // caller logs
}
```

## Best Practices

1. **Every error must be handled** — address it, return it, or `log.Fatal` it; never `_ = err` without a comment
2. **Add context when wrapping** — only add context the underlying error lacks; don't duplicate its message
3. **Return `error` interface, not concrete types** — prevents nil-interface bugs in exported functions
4. **Error strings are lowercase** — no trailing punctuation; they compose into larger messages
5. **`Must` functions only in `init`/program startup** — `regexp.MustCompile`, `template.Must`, never in request handlers
6. **Exported functions must return `error`** — not `*MyError`; callers check with `errors.As`
7. **Document your sentinel errors** — add a doc comment on every `var Err...` so callers know when to expect it

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `if err == ErrNotFound` | `if errors.Is(err, ErrNotFound)` — works through wrap chains |
| Log and return the same error | Choose one. Return the error; let the caller log at the right level |
| `return nil, &MyError{...}` (exported) | Return `error` interface; callers use `errors.As` |
| Ignore errors with `_ = err` | Handle it or add a comment explaining why it's safe to ignore |
| `panic(err)` in a handler | Return the error; `panic` must not escape package boundaries |

## Next Steps

- See [sentinel-errors.md](sentinel-errors.md) for when and how to define `var ErrX` sentinels
- See [error-wrapping.md](error-wrapping.md) for `%w` vs `%v` decision rules
- See [custom-error-types.md](custom-error-types.md) for structured error types with `errors.As`
