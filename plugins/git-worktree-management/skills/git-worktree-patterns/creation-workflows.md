# Worktree Creation Workflows

## Prerequisites

Always fetch before creating worktrees to ensure remote branches are available:

```bash
git fetch origin
```

## Creating Worktrees

### For Existing Branch

```bash
# Basic syntax
git worktree add <path> <branch>

# Examples
git worktree add ../project.dev dev
git worktree add ./worktrees/feature/ticket-123 feature/ticket-123
git worktree add ../project.review origin/feature/other-dev-branch
```

### For New Branch

```bash
# Basic syntax
git worktree add -b <new-branch> <path> <start-point>

# Examples - create new feature branch from dev
git worktree add -b feature/new-feature ../project.feature dev

# Create hotfix branch from main
git worktree add -b hotfix/urgent-fix ../project.hotfix main

# Create experimental branch (detached HEAD)
git worktree add -d ../project.experiment
```

---

## Workflow: Feature Development

```bash
# 1. Ensure you have latest changes
git fetch origin

# 2. Create worktree with new feature branch
git worktree add -b feature/GDW-123-new-feature ../project.feature-123 origin/dev

# 3. Navigate to worktree
cd ../project.feature-123

# 4. Set up environment (Laravel)
cp ../project/.env .env
# Edit .env - change DB_DATABASE, APP_PORT if needed

# 5. Install dependencies
composer install
npm install

# 6. Start development
php artisan serve --port=8001
```

---

## Workflow: Hotfix

```bash
# 1. Create hotfix worktree from main/production
git worktree add -b hotfix/critical-bug ../project.hotfix origin/main

# 2. Set up environment
cd ../project.hotfix
cp ../project/.env .env
# Edit .env for hotfix environment

# 3. Install dependencies
composer install

# 4. Fix the bug, test, commit
git add .
git commit -m "Fix critical bug"

# 5. Push and create PR
git push -u origin hotfix/critical-bug

# 6. After merge, cleanup
cd ../project
git worktree remove ../project.hotfix
git branch -d hotfix/critical-bug
```

---

## Workflow: Code Review

```bash
# 1. Fetch the PR branch
git fetch origin pull/123/head:review/PR-123
# Or if branch exists
git fetch origin feature/other-dev-branch

# 2. Create review worktree
git worktree add ../project.review-123 review/PR-123

# 3. Set up and test
cd ../project.review-123
cp ../project/.env .env
composer install
npm install
php artisan test

# 4. Review code in your IDE
# Make comments on PR

# 5. Cleanup after review
cd ../project
git worktree remove ../project.review-123
git branch -D review/PR-123
```

---

## Workflow: Long-Running Process

```bash
# Scenario: Run full test suite while continuing development

# 1. Create worktree for testing
git worktree add ../project.testing HEAD

# 2. Run tests in background
cd ../project.testing
php artisan test --parallel &

# 3. Continue working in main worktree
cd ../project
# ... continue development ...

# 4. Check test results when done
# 5. Remove testing worktree
git worktree remove ../project.testing
```

---

## Workflow: Multiple Claude Code Instances

```bash
# For parallel AI-assisted development

# 1. Create worktrees for different features
git worktree add -b feature/auth ../project.auth dev
git worktree add -b feature/api ../project.api dev

# 2. Open separate terminals
# Terminal 1: cd ../project.auth && claude
# Terminal 2: cd ../project.api && claude

# 3. Each Claude instance works independently
# Run /init in each to orient Claude to that worktree

# 4. Cleanup when features complete
git worktree remove ../project.auth
git worktree remove ../project.api
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Existing branch | `git worktree add <path> <branch>` |
| New branch | `git worktree add -b <branch> <path> <base>` |
| Detached HEAD | `git worktree add -d <path>` |
| From remote | `git worktree add <path> origin/<branch>` |
| List worktrees | `git worktree list` |
