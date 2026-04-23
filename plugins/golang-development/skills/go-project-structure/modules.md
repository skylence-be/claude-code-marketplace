# Go Modules

## go.mod Structure

```
module github.com/myorg/myapp

go 1.22

require (
    golang.org/x/sync v0.6.0
    github.com/some/dep v1.2.3
)

require (
    // indirect dependencies — managed by go mod tidy
    github.com/transitive/dep v0.1.0 // indirect
)
```

- `module` declares the module path — matches the repository URL
- `go` declares the minimum Go version required
- Always commit both `go.mod` and `go.sum`
- Run `go mod tidy` before committing to keep the file clean

## Adding Dependencies

```bash
# Add a dependency at the latest version
go get github.com/some/package

# Add a specific version
go get github.com/some/package@v1.2.3

# Upgrade to latest patch
go get github.com/some/package@patch

# Upgrade to latest minor
go get github.com/some/package@latest

# Remove unused dependencies
go mod tidy
```

## Versioning Your Own Module

Semantic versioning:
- `v0.x.y` — unstable; API may change
- `v1.x.y` — stable; no breaking changes within v1
- `v2.x.y` — breaking changes require a new module path

For v2+, change the module path in `go.mod` and in all import paths:

```
module github.com/myorg/myapp/v2
```

This lets v1 and v2 coexist in the same dependency graph.

## Module Proxy and GOPROXY

By default, Go fetches modules through the module proxy (`https://proxy.golang.org`). This ensures:
- Reproducible builds even if the original repository disappears
- Integrity verification via `go.sum`

For private modules, set `GOPRIVATE`:

```bash
# Don't use proxy for github.com/myorg modules
GOPRIVATE=github.com/myorg go get github.com/myorg/internal

# Or set permanently in your shell profile
export GOPRIVATE=github.com/myorg
```

## Vendoring

`go mod vendor` copies all dependencies into a `vendor/` directory:

```bash
go mod vendor
go build -mod=vendor ./...
```

Use vendoring when:
- Building in air-gapped environments without internet access
- Corporate policy requires vendoring
- You want to ensure reproducible builds without relying on the proxy

Don't vendor in open-source library projects (let consumers manage their own deps).

## Go Workspaces (Multi-Module Development)

Workspaces (`go.work`) let you develop multiple modules locally without `replace` directives:

```bash
# Initialize a workspace
go work init

# Add modules to the workspace
go work use ./myapp
go work use ./mylib

# go.work:
go 1.22
use (
    ./myapp
    ./mylib
)
```

Go commands in a workspace context prefer local modules over the proxy.

**Do NOT commit `go.work` in library repositories** — it breaks consumers who import your module.

## `replace` Directives

Use `replace` in `go.mod` to point a dependency at a local path or fork:

```
replace github.com/some/dep => ../local-fork
```

Rules:
- Use only for local development or debugging
- Remove before publishing (published modules with `replace` break consumers)
- Prefer workspaces (`go.work`) for local multi-module dev instead

## Checking for Vulnerabilities

```bash
# Install govulncheck
go install golang.org/x/vuln/cmd/govulncheck@latest

# Check for known vulnerabilities in your module
govulncheck ./...
```

Run `govulncheck` in CI. It checks against the Go vulnerability database and only reports vulnerabilities reachable in your code.

## `go mod tidy` — Always Before Committing

```bash
go mod tidy
```

This:
- Adds missing dependencies
- Removes unused dependencies
- Updates `go.sum` to match

Make it a git pre-commit hook or CI gate to keep `go.mod` clean.
