# Go Project Layout

## Standard Directory Structure

```
myproject/
├── cmd/                    # entry points — one subdirectory per binary
│   ├── myapp/
│   │   └── main.go         # thin: parse flags, wire deps, run
│   └── worker/
│       └── main.go
├── internal/               # private application code; enforced by compiler
│   ├── config/             # reads environment / file configuration
│   ├── server/             # HTTP/gRPC server setup
│   ├── handler/            # request handlers (one file per resource)
│   ├── service/            # business logic layer
│   ├── store/              # database access layer
│   └── middleware/         # HTTP middleware
├── pkg/                    # public library code external consumers may import
│   └── client/             # SDK for calling this service
├── api/                    # schema files: OpenAPI, Protobuf, gRPC
│   └── openapi.yaml
├── web/                    # static assets, embedded FS, HTML templates
├── configs/                # config file templates and defaults
├── scripts/                # build, migration, seed scripts
├── build/                  # Docker, CI configs (not Go source)
│   ├── Dockerfile
│   └── .github/workflows/
├── test/                   # additional integration test fixtures and data
│   └── testdata/
├── docs/                   # design documents
├── .golangci.yml
├── Makefile
├── go.mod
└── go.sum
```

## `cmd/` — Entry Points Only

`main.go` in each `cmd/` subdirectory should be fewer than 50 lines. It:
1. Parses flags and environment
2. Reads configuration
3. Wires up dependencies (DB, cache, HTTP client)
4. Calls into `internal/`

```go
// cmd/server/main.go — thin, no business logic
func main() {
    cfg := config.Load()
    db := store.Connect(cfg.DSN)
    svc := service.NewUserService(db)
    srv := server.New(cfg, svc)
    log.Fatal(srv.ListenAndServe(cfg.Addr))
}
```

## `internal/` — Application Code

Everything that isn't intentionally exported goes in `internal/`. The Go compiler enforces this: external packages cannot import from `internal/`.

Organize by responsibility, not by layer:

```
internal/
├── user/           # everything about users: handler, service, store
│   ├── handler.go
│   ├── service.go
│   └── store.go
├── auth/           # authentication: middleware, tokens
├── config/         # configuration loading and defaults
└── server/         # HTTP server wire-up
```

Or by layer (both are valid — pick one and be consistent):

```
internal/
├── handler/        # HTTP handlers for all resources
├── service/        # business logic for all resources
└── store/          # DB access for all resources
```

## `pkg/` — Intentionally Public

Only put code in `pkg/` when you explicitly intend for external consumers to import it. It is not a catch-all for internal utilities.

Good candidates for `pkg/`:
- Client SDK for your service (`pkg/client/`)
- Reusable utilities with stable APIs (`pkg/retry/`, `pkg/telemetry/`)

Don't put in `pkg/`:
- Internal business logic
- Things you might export someday (use `internal/` until you're sure)

## Small Projects — Start Flat

Don't apply the full layout to small or early-stage projects:

```
myproject/
├── main.go
├── handler.go
├── store.go
├── go.mod
└── go.sum
```

Move to the full layout when:
- You have more than one binary (`cmd/`)
- You want to enforce internal privacy (`internal/`)
- You're publishing a library (`pkg/`)

## What NOT to Include

| Don't use | Reason |
|-----------|--------|
| `src/` | Java habit; Go modules don't need it |
| `lib/` | Use `pkg/` for public, `internal/` for private |
| `util/` or `helpers/` | Too vague; names lie about responsibility |
| One-file-per-type rule | Group by responsibility, not type name |

## Makefile Targets

```makefile
.PHONY: build test lint vet tidy

build:
	go build ./cmd/...

test:
	go test -race -count=1 ./...

lint:
	golangci-lint run ./...

vet:
	go vet ./...

tidy:
	go mod tidy
```
