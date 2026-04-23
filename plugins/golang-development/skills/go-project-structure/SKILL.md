---
name: go-project-structure
description: Standard Go project layout covering cmd/, internal/, pkg/ conventions, go.mod hygiene, workspace files, and versioning. Use when starting a new Go project, refactoring a flat layout that has grown too large, setting up a monorepo with multiple modules, or publishing a Go library.
---

# Go Project Structure

## When to Use This Skill

- Scaffolding a new Go application or library
- Refactoring a flat `main.go + *.go` layout that has grown unwieldy
- Setting up a monorepo with multiple Go modules using workspaces
- Publishing a Go library with a stable public API (`pkg/`)
- Deciding when to use `internal/` vs `pkg/` vs top-level packages

## Pattern Files

| Pattern | Use Case |
|---------|----------|
| [layout.md](layout.md) | Directory conventions: cmd/, internal/, pkg/, api/, scripts/ |
| [modules.md](modules.md) | go.mod, go.sum, versioning, workspaces, GOPATH/proxy |

## Core Concepts

| Concept | Rule |
|---------|------|
| **`cmd/`** | One subdir per binary; each `main.go` is thin — just wires up `internal/` |
| **`internal/`** | All application code that is not intentionally exported; compiler-enforced |
| **`pkg/`** | Code explicitly intended for external import; don't use reflexively |
| **`api/`** | OpenAPI / Protobuf / gRPC specs; not Go source |
| **No `src/`** | That's a Java habit. Go modules make it unnecessary |
| **Small projects** | Start flat; apply the full layout only when complexity demands it |

## Quick Reference

```
myproject/
├── cmd/
│   └── myapp/
│       └── main.go       # thin: parse flags, wire deps, call internal/
├── internal/
│   ├── config/           # reads env/file config
│   ├── server/           # HTTP server setup
│   ├── handler/          # request handlers
│   └── store/            # DB access layer
├── pkg/
│   └── client/           # public SDK others can import
├── api/
│   └── openapi.yaml
├── scripts/
│   └── seed.go
├── .golangci.yml
├── Makefile
├── go.mod
└── go.sum
```

## Best Practices

1. **`cmd/` is entry points only** — no business logic; delegate to `internal/` immediately
2. **Default to `internal/`** — prevents accidental external dependency before API is stable
3. **No `util` packages** — name by responsibility: `strutil`, `timeutil`, `httputil`
4. **Commit both `go.mod` and `go.sum`** — ensures reproducible builds for everyone
5. **Run `go mod tidy` before every commit** — removes unused dependencies automatically
6. **Major version in module path** — `module github.com/org/repo/v2` for breaking changes
7. **`go.work` for local multi-module dev** — don't commit `go.work` in a library repo

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| Business logic in `main.go` | Move to `internal/`; `main` wires, `internal` works |
| `pkg/` as a catch-all | Only use `pkg/` for code intentionally exported to external consumers |
| `src/` directory | Remove it; Go modules don't need it |
| Floating version tags in `go.mod` | Use exact versions (`v1.2.3`); `go mod tidy` helps |
| `replace` directive in a published module | Only use `replace` locally; strip before publishing |

## Next Steps

- See [layout.md](layout.md) for detailed directory structure with examples for CLI, service, and library projects
- See [modules.md](modules.md) for `go.mod`, versioning strategy, and workspace configuration
