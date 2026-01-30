# Git Worktree Best Practices

## Naming Conventions

### Directory Names

Use consistent, descriptive names:

| Pattern | Example | Use Case |
|---------|---------|----------|
| `project.purpose` | `btb.app.core.dev` | General purpose |
| `project.ticket-id` | `btb.app.core.GDW-123` | Ticket tracking |
| `project.feature-name` | `btb.app.core.peppol` | Feature description |
| `worktrees/type/name` | `worktrees/feature/auth` | Categorized nested |

### Branch Names

Match worktree purpose to branch naming:

```
feature/GDW-123-description  →  project.GDW-123
hotfix/urgent-fix            →  project.hotfix-urgent
bugfix/login-issue           →  project.bugfix-login
```

---

## Workflow Best Practices

### 1. Always Fetch First

```bash
# Before creating any worktree
git fetch origin

# This ensures:
# - Remote branches are available
# - You're working with latest refs
```

### 2. Rebase Often

```bash
# In each worktree, stay updated
git pull --rebase origin dev

# Or fetch + rebase
git fetch origin
git rebase origin/dev
```

### 3. One Branch Per Worktree

Git enforces this, but understand why:
- Prevents conflicting checkouts
- Each worktree has clear purpose
- Easy to track what's where

### 4. Clean Up Promptly

```bash
# After merging a PR
git worktree remove ../project.feature
git branch -d feature/completed

# Don't let worktrees accumulate
```

### 5. Document Your Worktrees

Keep a simple record:

```markdown
# Active Worktrees

| Path | Branch | Purpose | Database |
|------|--------|---------|----------|
| project | dev | Main development | project_dev |
| project.auth | feature/auth | Auth system | project_auth |
| project.api | feature/api | API endpoints | project_api |
```

---

## Team Collaboration

### Shared Conventions

Agree on team standards:

```bash
# Standard structure for team
project/
├── main/          # Production-ready code
├── dev/           # Integration branch
├── worktrees/
│   ├── feature/   # Active features
│   └── review/    # Code reviews
```

### PR Review Workflow

```bash
# Reviewer creates review worktree
git fetch origin
git worktree add ./worktrees/review/PR-123 origin/feature/branch-to-review

# Review, test, comment
# Then cleanup
git worktree remove ./worktrees/review/PR-123
```

### Avoiding Conflicts

- Communicate which branches you're working on
- Don't work on same feature branch from different worktrees
- Use worktree list to check team usage (in shared environments)

---

## Performance Considerations

### Disk Space

Worktrees share `.git` objects but duplicate working files:

```bash
# Check worktree sizes
du -sh ../project*

# Shared objects (only stored once)
du -sh .git/objects
```

### Dependencies

Each worktree needs its own:
- `vendor/` (~50-200MB for Laravel)
- `node_modules/` (~200-500MB)

Consider:
```bash
# Symlink node_modules to save space (if same dependencies)
ln -s ../project/node_modules node_modules

# Or use pnpm for shared packages
pnpm install
```

### IDE Resources

Multiple worktrees = multiple IDE instances = more RAM

Tips:
- Close unused worktree projects
- Use lightweight editors for quick reviews
- Consider VS Code workspaces for related worktrees

---

## Security Practices

### Environment Files

```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use different secrets per environment
# Don't copy production secrets to feature worktrees
```

### Database Access

```bash
# Use separate databases with limited permissions
# Feature worktrees shouldn't access production data

# Create restricted database user for worktrees
GRANT ALL ON project_feature.* TO 'dev_user'@'localhost';
```

### Sensitive Branches

```bash
# Lock production worktree
git worktree lock ../project.production --reason "Production - do not remove"

# Consider read-only access for certain worktrees
```

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Forgetting to fetch | Script it: `git fetch && git worktree add` |
| Stale worktrees | Weekly cleanup review |
| Wrong database | Check `.env` before running migrations |
| Uncommitted changes | Always check `git status` before removing |
| Too many worktrees | Limit to 3-4 active at once |
| Merge conflicts | Rebase frequently |

---

## Automation Ideas

### Git Aliases

```bash
# ~/.gitconfig
[alias]
    wta = worktree add
    wtl = worktree list
    wtr = worktree remove
    wtp = worktree prune
```

### Shell Functions

```bash
# ~/.bashrc or ~/.zshrc

# Quick worktree creation
newwt() {
    git fetch origin
    git worktree add -b "$1" "../$(basename $(pwd)).$1" origin/dev
    cd "../$(basename $(pwd)).$1"
    cp ../$(basename $(pwd))/.env .env
    composer install
}

# Quick cleanup
rmwt() {
    local path=$1
    git worktree remove "$path"
    git worktree prune
}
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
# Warn if committing to wrong branch
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" || "$BRANCH" == "production" ]]; then
    echo "Warning: You're committing directly to $BRANCH"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]] || exit 1
fi
```

---

## Quick Reference Card

```bash
# Create
git worktree add <path> <branch>           # Existing branch
git worktree add -b <branch> <path> <base> # New branch

# Manage
git worktree list                          # Show all
git worktree move <old> <new>              # Relocate
git worktree lock <path>                   # Protect
git worktree unlock <path>                 # Unprotect

# Cleanup
git worktree remove <path>                 # Remove
git worktree prune                         # Clean stale
git worktree repair                        # Fix refs

# After creating worktree
cp ../<main>/.env .env                     # Copy env
composer install                            # PHP deps
npm install                                # JS deps
php artisan migrate                        # Database
```
