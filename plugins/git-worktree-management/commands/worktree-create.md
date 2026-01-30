---
description: Create a new git worktree with environment setup
model: haiku
---

# Create Git Worktree

Create a new git worktree with proper environment configuration for Laravel development.

## Specification

$ARGUMENTS

## Process

1. **Fetch latest changes** from remote
2. **Create worktree** with appropriate directory structure
3. **Copy environment** file from main worktree
4. **Configure database** isolation in `.env`
5. **Install dependencies** (composer, npm)
6. **Optionally duplicate database** if requested

## Examples

### Feature Branch Worktree

```bash
# Fetch and create
git fetch origin
git worktree add -b feature/new-feature ../project.feature origin/dev

# Setup environment
cd ../project.feature
cp ../project/.env .env

# Update .env
# DB_DATABASE=project_feature
# APP_PORT=8001

# Install dependencies
composer install
npm install
```

### Existing Branch Worktree

```bash
git fetch origin
git worktree add ../project.dev dev

cd ../project.dev
cp ../project/.env .env
composer install
npm install
```

### Review Worktree

```bash
git fetch origin
git worktree add ../project.review origin/feature/branch-to-review

cd ../project.review
cp ../project/.env .env
composer install
npm install
php artisan test
```

Create the worktree following Laravel best practices for environment isolation.
