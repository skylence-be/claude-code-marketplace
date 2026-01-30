---
description: Remove worktree and cleanup associated resources (database, branch)
model: haiku
---

# Cleanup Git Worktree

Remove a git worktree and optionally cleanup associated database and branch.

## Specification

$ARGUMENTS

## Cleanup Steps

1. **Check worktree status** - uncommitted changes, branch info
2. **Remove worktree** using `git worktree remove`
3. **Optionally drop database** if worktree had isolated database
4. **Optionally delete branch** if merged or no longer needed
5. **Prune stale references** with `git worktree prune`

## Examples

### Basic Cleanup

```bash
# Remove worktree only
git worktree remove ../project.feature

# Prune stale references
git worktree prune
```

### Full Cleanup (Worktree + Database + Branch)

```bash
# Get database name from worktree .env before removing
DB_NAME=$(grep DB_DATABASE ../project.feature/.env | cut -d '=' -f2)

# Remove worktree
git worktree remove ../project.feature

# Drop database
mysql -u root -p -e "DROP DATABASE IF EXISTS $DB_NAME;"

# Delete branch (if merged)
git branch -d feature/completed-feature

# Or force delete (if unmerged but sure)
git branch -D feature/abandoned-feature

# Cleanup
git worktree prune
```

### Force Cleanup (Uncommitted Changes)

```bash
# Force remove (loses uncommitted changes!)
git worktree remove --force ../project.feature

git worktree prune
```

### List Before Cleanup

```bash
# See all worktrees
git worktree list

# Check specific worktree status
git -C ../project.feature status
```

Cleanup worktree and associated resources safely.
