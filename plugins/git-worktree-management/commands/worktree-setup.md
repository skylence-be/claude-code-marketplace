---
description: Setup environment for existing worktree (env, database, dependencies)
model: haiku
---

# Setup Worktree Environment

Configure an existing git worktree with proper environment, database, and dependencies for Laravel development.

## Specification

$ARGUMENTS

## Setup Steps

1. **Copy `.env`** from main worktree or create from `.env.example`
2. **Configure isolation**:
   - Unique `DB_DATABASE` name
   - Different `APP_PORT` if running multiple servers
   - Separate Redis/cache prefixes if needed
3. **Install dependencies**:
   - `composer install`
   - `npm install`
4. **Database setup**:
   - Create new database
   - Run migrations (fresh or duplicate from main)
5. **Generate app key** if needed

## Examples

### Basic Setup (Fresh Database)

```bash
cd ../project.feature

# Copy environment
cp ../project/.env .env

# Edit .env
# DB_DATABASE=project_feature
# APP_PORT=8001

# Install dependencies
composer install
npm install

# Create database and migrate
mysql -u root -p -e "CREATE DATABASE project_feature;"
php artisan migrate --seed
```

### Setup with Database Copy

```bash
cd ../project.feature

# Copy environment
cp ../project/.env .env

# Update database name in .env
# DB_DATABASE=project_feature

# Install dependencies
composer install
npm install

# Duplicate database
mysql -u root -p -e "CREATE DATABASE project_feature;"
mysqldump -u root -p project_main | mysql -u root -p project_feature
```

### Minimal Setup (Shared Database)

```bash
cd ../project.feature

# Symlink environment (same database)
ln -s ../project/.env .env

# Install dependencies
composer install
npm install
```

Configure the worktree for isolated Laravel development.
