---
description: Systematic framework upgrade with codebase analysis, breaking change detection, and step-by-step migration
---

# /upgrade — Framework Upgrade Assistant

Systematically upgrade Laravel ecosystem packages using a codebase-analysis-first approach. Scans for breaking changes before making modifications.

$ARGUMENTS

## Usage

Specify what to upgrade:
- `--laravel <version>`: Upgrade Laravel (e.g., `--laravel 13`)
- `--livewire <version>`: Upgrade Livewire (e.g., `--livewire 4`)
- `--inertia <version>`: Upgrade Inertia.js (e.g., `--inertia 3`)
- `--pest <version>`: Upgrade Pest (e.g., `--pest 4`)
- `--tailwind <version>`: Upgrade Tailwind CSS (e.g., `--tailwind 4`)

If no version specified, upgrades to the latest stable version.

## Process

### Phase 1: Assessment

Before changing anything, understand the current state:

```bash
# Current versions
cat composer.json | head -50
cat package.json | head -30
php -v
php artisan --version

# Git safety — create upgrade branch
git checkout -b upgrade/[package]-v[version]
git status
```

### Phase 2: Safety Net

Establish a test baseline before upgrading:

```bash
# Run existing tests
php artisan test --compact 2>&1 | tail -5

# Record current test count and status
php artisan test --compact 2>&1 | grep -E "Tests:|Passed:|Failed:"
```

If tests are already failing, note the failures. They should not increase after upgrade.

### Phase 3: Codebase Scan for Breaking Changes

Search the codebase for patterns that will break in the target version. This is the critical step — find issues BEFORE upgrading.

#### For Laravel Upgrades:
- Search for deprecated middleware registration patterns
- Check for removed/renamed config keys
- Scan for deprecated Eloquent methods
- Check route file structure changes
- Verify service provider registration patterns

#### For Livewire Upgrades:
- Search for `wire:model` without modifiers (behavior changed in v4)
- Check for deprecated lifecycle hooks
- Scan for removed component methods
- Check JavaScript hook API changes

#### For Inertia Upgrades:
- Search for `router.on('invalid'` (removed in v3)
- Check for `router.cancel()` usage
- Scan for deprecated `lazy()` prop usage
- Check `resolveComponent` changes

#### For Tailwind Upgrades:
- Search for `@tailwind` directives (replaced by `@import` in v4)
- Scan for deprecated utilities (`bg-opacity-*`, `flex-shrink-*`)
- Check for `tailwind.config.js` (replaced by `@theme` in v4)

```bash
# Example: scan for Tailwind v3 patterns before upgrading to v4
grep -r "@tailwind" --include="*.css" .
grep -r "bg-opacity-\|text-opacity-\|flex-shrink-\|flex-grow-\|overflow-ellipsis" --include="*.blade.php" --include="*.vue" --include="*.tsx" .
```

### Phase 4: Document Breaking Changes

Before making changes, list every breaking change found:

```
## Breaking Changes Found

### High Priority (will cause errors)
1. [file:line] — Pattern: [what needs changing]
   Fix: [exact replacement]

### Medium Priority (deprecated, will warn)
1. [file:line] — Pattern: [what needs changing]
   Fix: [exact replacement]

### Low Priority (recommended changes)
1. [file:line] — Pattern: [what could be improved]
   Fix: [suggested replacement]
```

### Phase 5: Apply Dependency Updates

```bash
# Update composer dependencies
composer require [package]:[version] --with-all-dependencies

# Update npm dependencies (if frontend package)
npm install [package]@[version]

# Clear caches
php artisan config:clear
php artisan cache:clear
php artisan view:clear
```

### Phase 6: Apply Code Changes

Work through the breaking changes list from Phase 4, applying fixes in order:
1. High priority first (errors)
2. Medium priority (deprecations)
3. Low priority (recommendations)

### Phase 7: Verify

```bash
# Run tests again
php artisan test --compact

# Compare with Phase 2 baseline
# Test count should be same or higher
# No new failures should exist

# Check for runtime errors
php artisan serve &
# Manually test critical paths
```

### Phase 8: Report

Output a summary of what was changed:

```
## Upgrade Summary: [package] v[old] → v[new]

### Dependencies Updated
- [package]: v[old] → v[new]

### Code Changes
- [N] files modified
- [N] breaking patterns replaced
- [N] deprecation warnings resolved

### Test Results
- Before: [X] tests, [Y] passed
- After: [X] tests, [Y] passed

### Manual Testing Required
- [ ] [critical path 1]
- [ ] [critical path 2]
```

## Examples

```
# Upgrade Laravel to v13
/laravel-development:upgrade --laravel 13

# Upgrade Livewire to v4
/laravel-development:upgrade --livewire 4

# Upgrade Tailwind to v4
/laravel-development:upgrade --tailwind 4

# Upgrade Inertia to v3
/laravel-development:upgrade --inertia 3
```
