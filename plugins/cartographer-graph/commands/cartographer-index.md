---
description: Index a repository with cartographer to build or refresh its code graph
---

# Cartographer Index

Register and index a repository with `cartographer`, building the LadybugDB graph that downstream tools (CLI queries, MCP server) operate on.

## Specification

$ARGUMENTS

## Process

1. **Confirm the cartographer binary is installed**: `command -v cartographer` (install with `cargo install cartographer-cli` or via the repo's release page if not)
2. **Choose the target path** from the specification (defaults to current directory)
3. **Run the index**: `cartographer index <path>`
4. **Confirm success**: `cartographer status` reports the repo with a recent timestamp and `fresh` staleness
5. **Optional**: install git hooks so the graph stays fresh automatically (`cartographer hooks install`)

## Examples

### Current directory

```bash
cartographer index .
```

### Specific path

```bash
cartographer index ~/code/my-app
```

### Multiple repos in parallel

```bash
cartographer index --paths ~/code/repo-a ~/code/repo-b --jobs 2
```

### Skip embeddings (faster, no semantic search)

```bash
cartographer index . --no-embeddings
```

### Index all subdirectories as separate repos

```bash
cartographer index --dir ~/code/workspace --jobs 2
```

## Performance Notes

- The first run downloads the ONNX embedding model (Snowflake Arctic Embed XS, 384 dim). Subsequent runs reuse the cached model.
- On a laptop, keep `--jobs 1` (the default for one repo). Indexing is CPU-bound and memory-hungry; concurrent indexing plus an active `cargo nextest` can starve the kernel.
- `--no-embeddings` skips the HNSW stage; useful for iterating on the parser or for repos where you only need FTS/Cypher queries.

## Verifying the Index

```bash
cartographer status                          # all repos
cartographer status --repo my-app            # one repo
cartographer query my-app "MATCH (f:Function) RETURN count(f)"   # sanity check
```

If `staleness != fresh` reports for a repo, re-run `cartographer index <path>`.

## Auto-Refresh on Commit

```bash
cartographer hooks install
```

Installs `post-commit`, `post-merge`, and `post-checkout` hooks that incrementally update the graph. With these enabled the graph stays fresh without manual reindexing.
