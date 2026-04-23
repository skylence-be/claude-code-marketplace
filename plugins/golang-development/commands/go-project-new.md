---
description: Scaffold a new idiomatic Go project with standard layout, go.mod, Makefile, and golangci-lint config
---

# New Go Project

Scaffold a new idiomatic Go project following the Standard Go Project Layout with module setup, linting configuration, and a working Makefile.

## Specification

$ARGUMENTS

## Process

1. **Determine module path** from the specification (e.g., `github.com/org/repo`)
2. **Create directory structure** following `cmd/`, `internal/`, `pkg/` conventions
3. **Initialize go.mod** with the correct module path and minimum Go version
4. **Write the thin main.go** in `cmd/<appname>/` that wires up `internal/`
5. **Create `.golangci.yml`** with the recommended linter set
6. **Write Makefile** with `build`, `test`, `lint`, `vet`, and `tidy` targets
7. **Add `.gitignore`** with Go-specific patterns

## Examples

### Simple CLI application

```bash
# Arguments: github.com/acme/mytool
mkdir -p mytool/{cmd/mytool,internal/config,internal/handler}
cd mytool
go mod init github.com/acme/mytool
```

Resulting structure:
```
mytool/
├── cmd/
│   └── mytool/
│       └── main.go          # thin: parse flags, call internal/
├── internal/
│   ├── config/
│   │   └── config.go
│   └── handler/
│       └── handler.go
├── .golangci.yml
├── Makefile
└── go.mod
```

### HTTP service

```bash
# Arguments: github.com/acme/myservice --type=service
mkdir -p myservice/{cmd/server,internal/{config,server,handler,middleware},pkg/client}
cd myservice
go mod init github.com/acme/myservice
go get golang.org/x/sync
```

Resulting structure:
```
myservice/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   ├── server/
│   ├── handler/
│   └── middleware/
├── pkg/
│   └── client/              # public SDK others can import
├── .golangci.yml
├── Makefile
└── go.mod
```

Scaffold the project following Standard Go Project Layout and idiomatic module conventions.
