# Directory Structure Patterns

## Overview

Choosing the right directory structure for worktrees affects organization, discoverability, and workflow efficiency. There are two main patterns: **nested** and **sibling**.

## Nested Structure (Recommended for Teams)

Keep worktrees inside the repository in a dedicated folder:

```
project/
├── .git/
├── app/
├── config/
├── ...
└── worktrees/
    ├── feature/
    │   ├── ticket-123/
    │   └── ticket-456/
    ├── bugfix/
    │   └── hotfix-789/
    └── review/
        └── PR-101/
```

### Setup Commands

```bash
# Add worktrees/ to .gitignore first
echo "worktrees/" >> .gitignore

# Create feature worktree
git worktree add ./worktrees/feature/ticket-123 feature/ticket-123

# Create bugfix worktree
git worktree add ./worktrees/bugfix/hotfix-789 -b hotfix/789 main

# Create review worktree
git worktree add ./worktrees/review/PR-101 origin/feature/pr-branch
```

### Advantages

- Everything contained in one folder
- Easy to find all worktrees
- Clear categorization by purpose
- Works well with IDE project roots

### Disadvantages

- Deeper directory nesting
- Must add to `.gitignore`

---

## Sibling Structure (Simple Projects)

Keep worktrees as siblings in a parent directory:

```
Code/Work/
├── project/
│   └── project/           ← main worktree
├── project.dev/           ← dev branch
├── project.feature1/      ← feature branch
├── project.hotfix/        ← hotfix branch
└── project.production/    ← production branch
```

### Setup Commands

```bash
# From main worktree
cd project/project

# Create sibling worktrees
git worktree add ../project.dev dev
git worktree add ../project.feature1 -b feature/new-feature dev
git worktree add ../project.hotfix -b hotfix/urgent main
git worktree add ../project.production main
```

### Advantages

- Flat structure, easy to navigate
- Each worktree is a top-level directory
- No need to modify `.gitignore`
- Clear naming shows branch purpose

### Disadvantages

- Worktrees scattered in parent directory
- Less organized for many worktrees

---

## Hybrid Structure

Combine both patterns for flexibility:

```
Code/Work/project/
├── project/               ← main worktree (development)
├── project.production/    ← production worktree (sibling)
└── project/worktrees/     ← feature worktrees (nested)
    ├── feature/
    └── review/
```

### When to Use

- Main and production as siblings for quick access
- Features and reviews nested for organization
- Good balance for medium-sized teams

---

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Main | `project` | `btb.app.core` |
| Development | `project.dev` | `btb.app.core.dev` |
| Feature | `project.feature-name` | `btb.app.core.peppol` |
| Hotfix | `project.hotfix-id` | `btb.app.core.hotfix-123` |
| Review | `project.review-pr` | `btb.app.core.review-456` |
| Production | `project.production` | `btb.app.core.production` |

---

## Recommendations

| Scenario | Recommended Structure |
|----------|----------------------|
| Solo developer | Sibling structure |
| Small team (2-5) | Sibling or nested |
| Large team (5+) | Nested with categories |
| Monorepo | Nested with strict organization |
| Multiple environments | Sibling for main environments |
