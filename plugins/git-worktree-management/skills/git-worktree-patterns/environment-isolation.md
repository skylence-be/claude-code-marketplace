# Environment Isolation for Worktrees

## Overview

Each worktree is a separate working directory with its own files. This means:

| Shared (single copy) | Separate (per worktree) |
|---------------------|------------------------|
| `.git` objects & history | All working files |
| Branches & tags | `.env` |
| Stash | `node_modules` |
| Git config | `vendor` |
| Hooks | `storage/` cache |
| | IDE settings |

## Laravel Environment Setup

### Step 1: Copy Environment File

```bash
cd new-worktree

# Option A: Copy from main worktree
cp ../project/.env .env

# Option B: Copy from example
cp .env.example .env
php artisan key:generate
```

### Step 2: Configure Isolation

Edit `.env` to avoid conflicts with other worktrees:

```env
# Unique app name for identification
APP_NAME="ProjectName (Feature)"

# Different port if running multiple servers
APP_PORT=8001

# Separate database (critical!)
DB_DATABASE=project_feature

# Separate Redis database (0-15 available)
REDIS_DB=1
REDIS_CACHE_DB=2

# Separate session/cache
SESSION_DRIVER=file
CACHE_DRIVER=file

# Or use Redis with different prefix
CACHE_PREFIX=project_feature_cache
SESSION_PREFIX=project_feature_session
```

### Step 3: Install Dependencies

```bash
composer install
npm install
```

### Step 4: Database Setup

```bash
# Option A: Fresh database with migrations
php artisan migrate --seed

# Option B: Duplicate existing database (see database-duplication.md)
```

---

## Symlink Strategy (Shared Configuration)

If you want worktrees to share the same environment:

```bash
cd new-worktree

# Symlink .env (shared database, same config)
ln -s ../project/.env .env

# Symlink storage (shared uploaded files)
ln -s ../project/storage storage

# Symlink node_modules (save disk space)
ln -s ../project/node_modules node_modules
```

### Warning

Shared configuration means:
- Same database (changes affect all worktrees)
- Same cache (potential conflicts)
- Cannot run multiple servers simultaneously

---

## Port Management

When running multiple worktrees simultaneously:

| Worktree | APP_PORT | Vite Port | MySQL |
|----------|----------|-----------|-------|
| main | 8000 | 5173 | 3306 |
| dev | 8001 | 5174 | 3306 |
| feature1 | 8002 | 5175 | 3306 |
| feature2 | 8003 | 5176 | 3306 |

### Vite Configuration

Update `vite.config.js` for different ports:

```javascript
export default defineConfig({
    server: {
        port: parseInt(process.env.VITE_PORT) || 5173,
    },
    // ...
});
```

Then in `.env`:

```env
VITE_PORT=5174
```

---

## Docker/Sail Considerations

For Laravel Sail, each worktree needs different container names and ports:

```env
# .env for feature worktree
APP_SERVICE=project-feature
APP_PORT=8001
FORWARD_DB_PORT=3307
FORWARD_REDIS_PORT=6380
FORWARD_MAILPIT_PORT=1026
FORWARD_MAILPIT_DASHBOARD_PORT=8026
```

Or use separate `docker-compose.override.yml` per worktree.

---

## IDE Configuration

Each worktree can have its own IDE settings:

```
new-worktree/
├── .idea/           ← PHPStorm settings (separate)
├── .vscode/         ← VS Code settings (separate)
└── ...
```

### PHPStorm

Open each worktree as a separate project for independent:
- Run configurations
- Database connections
- PHP interpreter settings

### VS Code

Open each worktree in a separate window:

```bash
code ../project.feature
```

---

## Quick Setup Script

Create a script for new worktree setup:

```bash
#!/bin/bash
# setup-worktree.sh

WORKTREE_PATH=$1
MAIN_PATH="../project"
DB_SUFFIX=$(basename $WORKTREE_PATH | sed 's/[^a-zA-Z0-9]/_/g')

# Copy environment
cp "$MAIN_PATH/.env" "$WORKTREE_PATH/.env"

# Update database name
sed -i "s/DB_DATABASE=.*/DB_DATABASE=project_$DB_SUFFIX/" "$WORKTREE_PATH/.env"

# Install dependencies
cd "$WORKTREE_PATH"
composer install
npm install

# Create database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS project_$DB_SUFFIX;"

# Run migrations
php artisan migrate --seed

echo "Worktree ready at $WORKTREE_PATH"
```

Usage:

```bash
git worktree add ../project.feature feature-branch
./setup-worktree.sh ../project.feature
```
