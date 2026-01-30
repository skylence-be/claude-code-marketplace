# Database Duplication for Worktrees

## Overview

When creating a new worktree, you often want a copy of the database to:
- Test with real data
- Avoid affecting the main development database
- Have independent data for feature development

## MySQL / MariaDB

### Quick Copy (Single Command)

```bash
# Create database and copy in one pipeline
mysqldump -u root -p source_database | mysql -u root -p -e "CREATE DATABASE target_database;" -D target_database
```

### Step by Step

```bash
# 1. Create the new database
mysql -u root -p -e "CREATE DATABASE project_feature;"

# 2. Copy structure and data
mysqldump -u root -p project_main | mysql -u root -p project_feature
```

### With Specific Options

```bash
# Structure only (no data)
mysqldump -u root -p --no-data project_main | mysql -u root -p project_feature

# Data only (structure already exists)
mysqldump -u root -p --no-create-info project_main | mysql -u root -p project_feature

# Exclude certain tables
mysqldump -u root -p project_main \
    --ignore-table=project_main.logs \
    --ignore-table=project_main.sessions \
    | mysql -u root -p project_feature

# Compressed for large databases
mysqldump -u root -p project_main | gzip > backup.sql.gz
gunzip < backup.sql.gz | mysql -u root -p project_feature
```

### Using Environment Variables

```bash
# Read from .env
source ../project/.env
NEW_DB="project_feature"

mysql -u "$DB_USERNAME" -p"$DB_PASSWORD" -e "CREATE DATABASE $NEW_DB;"
mysqldump -u "$DB_USERNAME" -p"$DB_PASSWORD" "$DB_DATABASE" | \
    mysql -u "$DB_USERNAME" -p"$DB_PASSWORD" "$NEW_DB"
```

---

## PostgreSQL

### Quick Copy

```bash
# Create database as copy (requires no active connections)
createdb -T source_database target_database

# Or with explicit connection
createdb -U postgres -T project_main project_feature
```

### Using pg_dump

```bash
# 1. Create database
createdb -U postgres project_feature

# 2. Copy data
pg_dump -U postgres project_main | psql -U postgres project_feature
```

### With Options

```bash
# Structure only
pg_dump -U postgres --schema-only project_main | psql -U postgres project_feature

# Specific tables only
pg_dump -U postgres -t users -t orders project_main | psql -U postgres project_feature

# Exclude large tables
pg_dump -U postgres --exclude-table=logs project_main | psql -U postgres project_feature

# Compressed
pg_dump -U postgres -Fc project_main > backup.dump
pg_restore -U postgres -d project_feature backup.dump
```

---

## SQLite

SQLite databases are single files, making duplication simple:

```bash
# Just copy the file
cp database/database.sqlite database/database_feature.sqlite

# Update .env
# DB_DATABASE=/path/to/database_feature.sqlite
```

---

## Laravel Artisan Approach

Instead of duplicating, start fresh with migrations and seeders:

```bash
cd new-worktree

# Update .env with new database name first
# Then:
php artisan migrate:fresh --seed
```

### When to Use Each Approach

| Approach | Use Case |
|----------|----------|
| Database copy | Need exact production-like data |
| Fresh migration | Feature doesn't depend on existing data |
| Partial copy | Need some tables, fresh others |

---

## Automated Script

Create a reusable script for database duplication:

```bash
#!/bin/bash
# duplicate-db.sh

SOURCE_DB=$1
TARGET_DB=$2

if [ -z "$SOURCE_DB" ] || [ -z "$TARGET_DB" ]; then
    echo "Usage: ./duplicate-db.sh source_database target_database"
    exit 1
fi

echo "Creating database $TARGET_DB..."
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS $TARGET_DB;"

echo "Copying data from $SOURCE_DB..."
mysqldump -u root -p "$SOURCE_DB" | mysql -u root -p "$TARGET_DB"

echo "Done! Database $TARGET_DB created."
echo "Update your .env: DB_DATABASE=$TARGET_DB"
```

Usage:

```bash
chmod +x duplicate-db.sh
./duplicate-db.sh project_main project_feature
```

---

## Complete Worktree + Database Setup

```bash
#!/bin/bash
# new-worktree-with-db.sh

BRANCH=$1
WORKTREE_NAME=$2
MAIN_WORKTREE="../project"

if [ -z "$BRANCH" ] || [ -z "$WORKTREE_NAME" ]; then
    echo "Usage: ./new-worktree-with-db.sh <branch> <worktree-name>"
    exit 1
fi

# Create worktree
git worktree add "../$WORKTREE_NAME" "$BRANCH"

# Copy environment
cp "$MAIN_WORKTREE/.env" "../$WORKTREE_NAME/.env"

# Get source database from .env
SOURCE_DB=$(grep DB_DATABASE "$MAIN_WORKTREE/.env" | cut -d '=' -f2)
TARGET_DB="${SOURCE_DB}_${WORKTREE_NAME//[^a-zA-Z0-9]/_}"

# Update .env with new database
sed -i "s/DB_DATABASE=.*/DB_DATABASE=$TARGET_DB/" "../$WORKTREE_NAME/.env"

# Create and duplicate database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS $TARGET_DB;"
mysqldump -u root -p "$SOURCE_DB" | mysql -u root -p "$TARGET_DB"

# Install dependencies
cd "../$WORKTREE_NAME"
composer install
npm install

echo ""
echo "Worktree ready at ../$WORKTREE_NAME"
echo "Database: $TARGET_DB"
echo ""
echo "Start server: php artisan serve --port=800X"
```

---

## Cleanup

When removing a worktree, optionally drop its database:

```bash
# Remove worktree
git worktree remove ../project.feature

# Drop database
mysql -u root -p -e "DROP DATABASE project_feature;"

# Or for PostgreSQL
dropdb -U postgres project_feature
```
