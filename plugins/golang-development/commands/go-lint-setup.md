---
description: Set up golangci-lint with a recommended .golangci.yml configuration for a Go project
---

# Go Lint Setup

Configure `golangci-lint` with a production-ready `.golangci.yml` that enables the most valuable linters for correctness, security, and style without excessive noise.

## Specification

$ARGUMENTS

## Process

1. **Check if golangci-lint is installed** (`which golangci-lint`)
2. **Detect Go version** from `go.mod` to pick compatible linters
3. **Write `.golangci.yml`** with recommended linter set and sane defaults
4. **Add lint target to Makefile** if one exists
5. **Add CI step** in `.github/workflows/` if GitHub Actions is configured
6. **Run once** to surface any pre-existing issues: `golangci-lint run ./...`

## Linter selection rationale

| Linter | Catches |
|--------|---------|
| `govet` | Suspicious constructs (built-in correctness) |
| `staticcheck` | 150+ checks — the gold standard |
| `errcheck` | Unchecked errors and type assertions |
| `errorlint` | Wrong error comparison (`==` vs `errors.Is`) |
| `gosimple` | Unnecessary complexity |
| `ineffassign` | Assigned variables never read |
| `unused` | Dead code |
| `revive` | Style (replaces deprecated `golint`) |
| `goimports` | Import grouping and formatting |
| `gosec` | Security anti-patterns |
| `misspell` | Typos in comments and strings |
| `nilerr` | Returning nil after checking for error |
| `bodyclose` | Unclosed HTTP response bodies |
| `tparallel` | Missing `t.Parallel()` in parallel-capable tests |
| `thelper` | Missing `t.Helper()` in test helpers |

## Generated .golangci.yml

```yaml
run:
  timeout: 5m

linters:
  enable:
    - govet
    - staticcheck
    - errcheck
    - errorlint
    - gosimple
    - ineffassign
    - unused
    - revive
    - goimports
    - gosec
    - misspell
    - nilerr
    - bodyclose
    - tparallel
    - thelper

linters-settings:
  errcheck:
    check-type-assertions: true
    check-blank: true
  errorlint:
    errorf: true
    asserts: true
    comparison: true
  revive:
    rules:
      - name: exported
      - name: var-naming
      - name: package-comments

issues:
  exclude-rules:
    - path: "_test\\.go"
      linters:
        - gosec
        - errcheck
```

Generate the `.golangci.yml` tailored to the project's Go version and existing code patterns.
