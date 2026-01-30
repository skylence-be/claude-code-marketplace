# Worktree Maintenance & Cleanup

## Listing Worktrees

```bash
# Basic list
git worktree list

# Output example:
# /path/to/project           abc1234 [main]
# /path/to/project.dev       def5678 [dev]
# /path/to/project.feature   ghi9012 [feature/ticket-123]

# Verbose output (shows lock status)
git worktree list --verbose

# Porcelain format (for scripting)
git worktree list --porcelain
```

---

## Removing Worktrees

### Standard Removal

```bash
# Remove worktree (keeps branch)
git worktree remove ../project.feature

# Remove worktree and delete branch
git worktree remove ../project.feature
git branch -d feature/ticket-123

# Or force delete unmerged branch
git branch -D feature/ticket-123
```

### Force Removal

```bash
# Force remove (ignores uncommitted changes)
git worktree remove --force ../project.feature
```

### Manual Removal

If worktree was deleted manually (e.g., `rm -rf`):

```bash
# Clean up stale references
git worktree prune

# Verify
git worktree list
```

---

## Pruning Stale Worktrees

```bash
# Remove references to deleted worktrees
git worktree prune

# Dry run (show what would be pruned)
git worktree prune --dry-run

# Verbose output
git worktree prune --verbose
```

---

## Locking Worktrees

Prevent accidental removal of important worktrees:

```bash
# Lock a worktree
git worktree lock ../project.production

# Lock with reason
git worktree lock ../project.production --reason "Production environment"

# Unlock
git worktree unlock ../project.production
```

---

## Moving Worktrees

```bash
# Move worktree to new location
git worktree move ../project.feature ../project.feature-renamed

# Note: Must update IDE project paths after moving
```

---

## Repairing Worktrees

```bash
# Repair worktree references after moving .git directory
git worktree repair

# Repair specific worktree
git worktree repair ../project.feature
```

---

## Complete Cleanup Script

```bash
#!/bin/bash
# cleanup-worktrees.sh

echo "Current worktrees:"
git worktree list
echo ""

# Prune stale references
echo "Pruning stale worktrees..."
git worktree prune --verbose
echo ""

# Find worktrees that might be removable
echo "Worktrees with merged branches:"
for wt in $(git worktree list --porcelain | grep "^worktree " | cut -d' ' -f2); do
    branch=$(git -C "$wt" branch --show-current 2>/dev/null)
    if [ -n "$branch" ] && [ "$branch" != "main" ] && [ "$branch" != "dev" ]; then
        # Check if branch is merged into main
        if git branch --merged main | grep -q "$branch"; then
            echo "  $wt ($branch) - merged into main"
        fi
    fi
done
echo ""

echo "To remove a worktree:"
echo "  git worktree remove <path>"
echo "  git branch -d <branch>  # if branch should be deleted"
```

---

## Database Cleanup

When removing a worktree, clean up its database:

```bash
#!/bin/bash
# cleanup-worktree-full.sh

WORKTREE_PATH=$1

if [ -z "$WORKTREE_PATH" ]; then
    echo "Usage: ./cleanup-worktree-full.sh <worktree-path>"
    exit 1
fi

# Get database name from worktree's .env
if [ -f "$WORKTREE_PATH/.env" ]; then
    DB_NAME=$(grep DB_DATABASE "$WORKTREE_PATH/.env" | cut -d '=' -f2)
    echo "Found database: $DB_NAME"

    read -p "Drop database $DB_NAME? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mysql -u root -p -e "DROP DATABASE IF EXISTS $DB_NAME;"
        echo "Database dropped."
    fi
fi

# Get branch name
BRANCH=$(git -C "$WORKTREE_PATH" branch --show-current 2>/dev/null)

# Remove worktree
echo "Removing worktree at $WORKTREE_PATH..."
git worktree remove "$WORKTREE_PATH"

# Optionally delete branch
if [ -n "$BRANCH" ] && [ "$BRANCH" != "main" ] && [ "$BRANCH" != "dev" ]; then
    read -p "Delete branch $BRANCH? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -d "$BRANCH" 2>/dev/null || git branch -D "$BRANCH"
        echo "Branch deleted."
    fi
fi

echo "Cleanup complete."
```

---

## Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Prune stale refs | Weekly | `git worktree prune` |
| List & review | Weekly | `git worktree list` |
| Remove merged | After PR merge | `git worktree remove` |
| Clean databases | After removal | `DROP DATABASE` |
| Check disk space | Monthly | `du -sh worktrees/` |

---

## Troubleshooting

### "Branch is already checked out"

```bash
# Find where branch is checked out
git worktree list | grep branch-name

# Remove the other worktree or use different branch
```

### "Worktree is locked"

```bash
# Check lock reason
git worktree list --verbose

# Unlock if safe
git worktree unlock ../project.feature

# Force remove (caution!)
git worktree remove --force ../project.feature
```

### "Directory not empty"

```bash
# Worktree has uncommitted changes
cd ../project.feature
git status

# Either commit/stash changes or force remove
git stash
# or
git worktree remove --force ../project.feature
```

### "Worktree path does not exist"

```bash
# Directory was manually deleted
git worktree prune
```
