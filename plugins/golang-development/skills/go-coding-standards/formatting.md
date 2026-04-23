# Go Formatting

## gofmt

`gofmt` is the non-negotiable Go formatter. All Go source must be `gofmt`-formatted — no exceptions, no debates.

- Uses tabs for indentation (not spaces)
- Opening braces on the same line as the declaration (mandatory syntax rule, not style)
- No configurable options — the tool makes all decisions

```bash
# Format a file in place
gofmt -w file.go

# Format the entire module
gofmt -w .

# Check without modifying (for CI)
gofmt -l .
```

## goimports

`goimports` extends `gofmt` by also managing import grouping and adding/removing imports automatically. **Prefer goimports over gofmt** in your editor and CI.

Import grouping convention (goimports enforces this):

```go
import (
    // 1. Standard library
    "context"
    "fmt"
    "net/http"

    // 2. Third-party (blank line separates from stdlib)
    "golang.org/x/sync/errgroup"
    "github.com/some/pkg"

    // 3. Internal / local (blank line separates from third-party)
    "github.com/myorg/myapp/internal/config"
)
```

## gofumpt

`gofumpt` is a stricter superset of `gofmt`. It adds additional rules:

- Enforces blank lines around certain constructs
- Stricter empty line rules inside functions
- Used by teams that want more uniformity than base `gofmt`

Enable in `.golangci.yml`:
```yaml
linters:
  enable:
    - gofumpt
```

## Editor Setup

**VS Code** (Go extension):
```json
{
  "go.formatTool": "goimports",
  "editor.formatOnSave": true
}
```

**JetBrains GoLand**: Settings → Go → Code Style → enable "Run goimports on save"

**Neovim** (gopls): goimports is the default formatter via `vim.lsp.buf.format()`

## CI Enforcement

Add to CI pipeline to fail on unformatted code:

```bash
# Check formatting
if [ -n "$(gofmt -l .)" ]; then
  echo "Go files are not formatted. Run: gofmt -w ."
  exit 1
fi
```

Or via golangci-lint:
```yaml
linters:
  enable:
    - goimports  # formats AND manages imports
```

## Line Length

Go has **no hard line length limit**. However:

- Lines over 100 characters should be refactored, not wrapped arbitrarily
- Long function signatures: break parameters into one-per-line
- Long expressions: extract into named intermediate variables
- Long strings: use raw string literals or `+` concatenation at natural break points

```go
// Too long — refactor, don't wrap
result, err := somePackage.DoSomethingWithAVeryLongFunctionName(paramOne, paramTwo, paramThree)

// Better: extract intermediate variables or break the call
result, err := somePackage.DoSomethingWithAVeryLongFunctionName(
    paramOne,
    paramTwo,
    paramThree,
)
```
