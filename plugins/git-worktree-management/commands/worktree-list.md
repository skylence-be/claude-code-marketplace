---
description: List all git worktrees with status information
model: haiku
---

# List Git Worktrees

Display all git worktrees with their status, branches, and additional information.

## Specification

$ARGUMENTS

## Commands

### Basic List

```bash
git worktree list
```

Output:
```
/path/to/project           abc1234 [main]
/path/to/project.dev       def5678 [dev]
/path/to/project.feature   ghi9012 [feature/ticket-123]
```

### Verbose List (with lock status)

```bash
git worktree list --verbose
```

### Porcelain Format (for scripting)

```bash
git worktree list --porcelain
```

### With Additional Status

```bash
# List worktrees with git status for each
for wt in $(git worktree list --porcelain | grep "^worktree " | cut -d' ' -f2); do
    echo "=== $wt ==="
    git -C "$wt" status --short
    echo ""
done
```

### With Database Info

```bash
# List worktrees with their databases
for wt in $(git worktree list --porcelain | grep "^worktree " | cut -d' ' -f2); do
    branch=$(git -C "$wt" branch --show-current 2>/dev/null || echo "detached")
    db=$(grep DB_DATABASE "$wt/.env" 2>/dev/null | cut -d'=' -f2 || echo "N/A")
    echo "$wt | $branch | DB: $db"
done
```

Display worktree information in the requested format.
