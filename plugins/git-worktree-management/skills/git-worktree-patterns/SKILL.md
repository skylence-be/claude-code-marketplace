---
name: git-worktree-patterns
description: Comprehensive git worktree patterns for parallel development, environment isolation, and workflow optimization. Use when setting up worktrees, managing multiple branches, configuring isolated environments, or optimizing development workflows.
---

# Git Worktree Patterns

## When to Use This Skill

- Setting up a new worktree structure for a project
- Managing parallel development across multiple features
- Creating isolated environments for code review
- Running long processes (tests, builds) without blocking development
- Configuring database isolation for worktrees
- Cleaning up stale worktrees and branches

## Pattern Files

| Pattern | Use Case |
|---------|----------|
| [directory-structures.md](directory-structures.md) | Choosing between nested and sibling worktree organization |
| [creation-workflows.md](creation-workflows.md) | Creating worktrees for features, hotfixes, and reviews |
| [environment-isolation.md](environment-isolation.md) | Configuring .env, databases, and dependencies per worktree |
| [database-duplication.md](database-duplication.md) | Duplicating MySQL/PostgreSQL databases for isolation |
| [maintenance-cleanup.md](maintenance-cleanup.md) | Removing, pruning, and managing worktrees |
| [best-practices.md](best-practices.md) | Team workflows, naming conventions, and common pitfalls |

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Main Worktree** | The original clone with the full `.git` directory |
| **Linked Worktree** | Additional working directories sharing the same `.git` objects |
| **Worktree Lock** | Prevents a branch from being checked out in multiple worktrees |
| **Detached HEAD** | Worktree not associated with any branch (for testing) |

## Quick Reference

### Create Worktree for Existing Branch
```bash
git worktree add ../project.feature feature-branch
```

### Create Worktree with New Branch
```bash
git worktree add -b feature/new-feature ../project.feature main
```

### List All Worktrees
```bash
git worktree list
```

### Remove Worktree
```bash
git worktree remove ../project.feature
```

### Prune Stale References
```bash
git worktree prune
```

## Best Practices

1. **Use descriptive directory names** that indicate the purpose (e.g., `project.dev`, `project.hotfix-123`)
2. **Fetch before creating worktrees** to ensure remote branches are available
3. **Keep worktrees organized** in a dedicated folder or as siblings with consistent naming
4. **Configure separate databases** for each worktree to avoid data conflicts
5. **Rebase often** (`git pull --rebase`) to minimize merge conflicts
6. **Clean up promptly** when done with a feature or review
7. **Add `worktrees/` to `.gitignore`** if using nested structure

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Branch already checked out | Use `git worktree list` to find existing worktree |
| Stale worktree references | Run `git worktree prune` |
| Missing dependencies | Run `composer install` and `npm install` in new worktree |
| Database conflicts | Duplicate database and update `.env` |
| Worktree locked | Use `git worktree unlock <path>` or remove manually |

## Next Steps

- Review [directory-structures.md](directory-structures.md) for organization patterns
- See [environment-isolation.md](environment-isolation.md) for Laravel-specific setup
- Check [database-duplication.md](database-duplication.md) for database cloning commands
