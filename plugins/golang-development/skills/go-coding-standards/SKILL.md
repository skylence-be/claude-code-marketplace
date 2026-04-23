---
name: go-coding-standards
description: Idiomatic Go coding standards covering gofmt formatting, naming conventions, the line-of-sight pattern, and initialisms. Use when writing new Go code, reviewing for style, enforcing team standards, or onboarding to a Go codebase.
---

# Go Coding Standards

## When to Use This Skill

- Writing new Go packages and ensuring idiomatic style from the start
- Reviewing code for naming violations or formatting issues
- Onboarding to a codebase with unfamiliar conventions
- Setting up a style guide for a Go team
- Understanding why gofmt decisions cannot be debated

## Pattern Files

| Pattern | Use Case |
|---------|----------|
| [formatting.md](formatting.md) | gofmt, goimports, tab indentation, brace placement |
| [naming-conventions.md](naming-conventions.md) | MixedCaps, receivers, initialisms, package names, getters |

## Core Concepts

| Concept | Rule |
|---------|------|
| **gofmt** | Non-negotiable. All code must be gofmt-formatted. No discussion. |
| **MixedCaps** | Exported identifiers use `UpperCamelCase`; unexported use `lowerCamelCase`. Never underscores. |
| **Initialisms** | Consistent case within an identifier: `userID` not `userId`, `parseURL` not `parseUrl` |
| **Package names** | Lowercase, single word, no underscores. Base on directory name. Never `util`, `helper`, `common` |
| **Receiver names** | 1–2 letter abbreviation of the type. Consistent across all methods. `func (c *Client)` |
| **Line of sight** | Handle errors early, return early. Happy path stays leftmost. No `else` after `return`. |
| **No Get prefix** | Use `Owner()` not `GetOwner()`. Setters use `SetOwner()`. |

## Quick Reference

```go
// Package: lowercase, single word
package config

// Exported type: UpperCamelCase
type HTTPClient struct {
    baseURL string   // unexported field: lowerCamelCase
    timeout int
}

// Receiver: 1-2 letters, abbreviate the type
func (c *HTTPClient) Do(req *http.Request) (*http.Response, error) { ... }

// Getter: no Get prefix
func (c *HTTPClient) Timeout() int { return c.timeout }

// Setter: Set prefix
func (c *HTTPClient) SetTimeout(d int) { c.timeout = d }

// Initialism: keep consistent case
type UserID string            // not UserId
func parseURL(s string) {}   // not parseUrl

// Line of sight
if err != nil {
    return err
}
doWork()     // happy path stays leftmost — no else branch needed
```

## Best Practices

1. **Run gofmt on save** — configure your editor or CI to enforce it; never debate spacing
2. **Use goimports** instead of gofmt — it also manages import grouping automatically
3. **Name variables by role, not type** — `user` not `userString`, `count` not `intCount`
4. **Short names for short scopes** — `i`, `n`, `v` are fine in for loops; use longer names in wider scope
5. **Avoid redundant package qualification** — `http.Client` not `http.HTTPClient`, `widget.New()` not `widget.NewWidget()`
6. **Comment exported symbols** — every exported type, function, method needs a doc comment starting with its name
7. **One concept per file** — group by responsibility, not one file per type

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `func GetUser()` | `func User()` — drop the Get prefix |
| `userId`, `parseUrl` | `userID`, `parseURL` — keep initialism case consistent |
| `package util` | Name for what it does: `package strutil`, `package timeutil` |
| Copying a `sync.Mutex` | Always use a pointer receiver or embed as pointer |
| `else` after `return` | Remove the `else`; code falls through naturally |

## Next Steps

- Review [formatting.md](formatting.md) for gofmt and import organization rules
- Review [naming-conventions.md](naming-conventions.md) for comprehensive naming guidance
