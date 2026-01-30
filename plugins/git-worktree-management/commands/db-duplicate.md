---
description: Duplicate database for worktree isolation
model: haiku
---

# Duplicate Database for Worktree

Create a copy of a database for use with an isolated git worktree.

## Specification

$ARGUMENTS

## MySQL / MariaDB

### Quick Copy

```bash
# Create and copy in one command
mysqldump -u root -p source_database | mysql -u root -p -e "CREATE DATABASE target_database;" -D target_database
```

### Step by Step

```bash
# 1. Create new database
mysql -u root -p -e "CREATE DATABASE project_feature;"

# 2. Copy data
mysqldump -u root -p project_main | mysql -u root -p project_feature
```

### With Options

```bash
# Structure only (no data)
mysqldump -u root -p --no-data project_main | mysql -u root -p project_feature

# Exclude large tables
mysqldump -u root -p project_main \
    --ignore-table=project_main.logs \
    --ignore-table=project_main.sessions \
    | mysql -u root -p project_feature

# Compressed (for large databases)
mysqldump -u root -p project_main | gzip > backup.sql.gz
gunzip < backup.sql.gz | mysql -u root -p project_feature
```

## PostgreSQL

### Quick Copy

```bash
# Create as copy of existing
createdb -U postgres -T source_database target_database
```

### Using pg_dump

```bash
createdb -U postgres target_database
pg_dump -U postgres source_database | psql -U postgres target_database
```

## SQLite

```bash
# Just copy the file
cp database/database.sqlite database/database_feature.sqlite
```

## After Duplication

Update the worktree's `.env`:

```env
DB_DATABASE=project_feature
```

Duplicate the database for worktree isolation.
