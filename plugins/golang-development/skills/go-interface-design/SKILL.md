---
name: go-interface-design
description: Idiomatic Go interface design patterns covering small single-method interfaces, consumer-defined interfaces, accept-interfaces-return-concretes, compile-time verification, and avoiding interface pollution. Use when designing package APIs, choosing between concrete types and interfaces, reviewing for fat interfaces, or enabling testability through dependency injection.
---

# Go Interface Design

## When to Use This Skill

- Designing a new package API and deciding where interfaces belong
- Enabling testability by injecting interfaces instead of concrete types
- Reviewing code for fat interfaces that are hard to mock or implement
- Deciding whether to return an interface or a concrete type from a constructor
- Publishing a library and considering what to export as interfaces vs concretes

## Pattern Files

| Pattern | Use Case |
|---------|----------|
| [patterns.md](patterns.md) | Consumer-defined interfaces, compile-time checks, composition, injection |

## Core Concepts

| Concept | Rule |
|---------|------|
| **Small interfaces** | Single-method interfaces are the most composable and testable |
| **Consumer defines** | The package that *uses* a type defines the interface it needs |
| **Accept interfaces** | Function parameters should be interfaces — flexible for callers |
| **Return concretes** | Function return values should be concrete types — gives callers full access |
| **No preemptive interfaces** | Don't create interfaces before you have two implementations |
| **Pointer to interface** | Almost always wrong. Interfaces already hold a pointer to data |
| **Compile-time check** | `var _ io.Reader = (*MyType)(nil)` catches breakage at compile time |

## Quick Reference

```go
// Small, focused interface — defined at the consumer side
type Storer interface {
    Get(key string) ([]byte, error)
    Set(key string, val []byte) error
}

// Accept interface, return concrete
func NewService(s Storer) *Service {
    return &Service{store: s}
}

// Compile-time interface verification
var _ http.Handler = (*MyHandler)(nil)

// Composition of small interfaces (stdlib pattern)
type ReadWriter interface {
    io.Reader
    io.Writer
}
```

## Best Practices

1. **One method = one interface** — the `io.Reader` / `io.Writer` model; compose from small pieces
2. **Define interfaces in the consumer package** — not in the package that implements them
3. **Return concrete types from constructors** — `*Service`, not `ServiceInterface`
4. **Accept the smallest interface parameter you need** — `io.Reader` not `io.ReadWriteCloser` if you only read
5. **Add `var _ Interface = (*Type)(nil)`** near the type definition to get compile-time verification
6. **Don't mock types you don't own** — use the real implementation or a test double from the owner's package
7. **Prefer `any` over `interface{}`** — they are identical but `any` is more readable (Go 1.18+)

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| Fat interface with 10+ methods | Split into small focused interfaces; compose at call sites |
| Interface defined in the provider package | Move to the consumer package; provider exports a concrete type |
| `func New() MyInterface` | `func New() *MyType` — return concrete, let consumer define interface |
| `*MyInterface` parameter | Use `MyInterface` directly; interfaces already contain an internal pointer |
| Interface for future flexibility | Create it when you have two implementations, not before |

## Next Steps

- See [patterns.md](patterns.md) for complete examples of consumer-defined interfaces, dependency injection, and testable designs
