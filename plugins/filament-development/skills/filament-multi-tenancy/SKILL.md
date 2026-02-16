---
name: filament-multi-tenancy
description: Master Filament 5 multi-tenancy patterns including panel configuration, tenant models, tenant-aware queries, global scopes, tenant switching, billing, team management, and security isolation. Use when building SaaS applications or multi-tenant systems.
category: filament
tags: [filament, multi-tenancy, saas, teams, security, isolation]
related_skills: [filament-resource-patterns, laravel-security-patterns, eloquent-patterns]
---

# Filament Multi-Tenancy

Multi-tenant SaaS application patterns for Filament 5.

## Pattern Files

Load specific patterns based on your needs:

| Pattern | File | Use Case |
|---------|------|----------|
| Panel Configuration | [panel-configuration.md](panel-configuration.md) | Panel setup, tenant routes, middleware |
| Tenant Models | [tenant-models.md](tenant-models.md) | Team/User models, relationships |
| Tenant Resources | [tenant-resources.md](tenant-resources.md) | Tenant-aware resources, global scopes |
| Team Management | [team-management.md](team-management.md) | Registration, profile, members, invitations |
| Billing & Storage | [tenant-billing.md](tenant-billing.md) | Subscriptions, storage isolation |

## Quick Reference

### Enable Tenancy in Panel
```php
->tenant(Team::class)
->tenantRegistration(RegisterTeam::class)
->tenantProfile(EditTeam::class)
->tenantOwnershipRelationshipName('team')
```

### User Model (HasTenants)
```php
class User implements FilamentUser, HasTenants
{
    public function getTenants(Panel $panel): Collection
    {
        return $this->teams;
    }

    public function canAccessTenant(Model $tenant): bool
    {
        return $this->teams->contains($tenant);
    }
}
```

### Tenant-Scoped Resource Query
```php
public static function getEloquentQuery(): Builder
{
    return parent::getEloquentQuery()
        ->whereBelongsTo(Filament::getTenant());
}
```

### Auto-Set Tenant on Create
```php
Forms\Components\Hidden::make('team_id')
    ->default(fn () => Filament::getTenant()->id),
```

### Tenant-Scoped Relationship
```php
Forms\Components\Select::make('category_id')
    ->relationship(
        'category',
        'name',
        fn (Builder $query) => $query->whereBelongsTo(Filament::getTenant())
    ),
```

### Navigation Badge Per Tenant
```php
public static function getNavigationBadge(): ?string
{
    return static::getModel()::whereBelongsTo(Filament::getTenant())
        ->where('status', 'pending')
        ->count();
}
```

## Security Gotchas (CRITICAL)

### 1. Use `scopedUnique` NOT `unique` for Tenant Isolation
```php
// WRONG - checks uniqueness across ALL tenants
Forms\Components\TextInput::make('slug')
    ->unique();

// CORRECT - checks uniqueness within current tenant only
Forms\Components\TextInput::make('slug')
    ->unique(modifyRuleUsing: fn ($rule) =>
        $rule->where('team_id', Filament::getTenant()->id)
    );
// Note: ignoreRecord: true is the default in Filament 5, no need to specify
```

### 2. `canAccessTenant()` is the ONLY Defense Against URL Manipulation
```php
// This is the ONLY thing preventing /team/999/posts URL manipulation
public function canAccessTenant(Model $tenant): bool
{
    return $this->teams->contains($tenant);
}
// If this returns true for wrong tenants, ALL data is exposed
```

### 3. Soft-Deleted Records Can Bypass Tenant Scoping
```php
// WRONG - soft-deleted records from other tenants may leak
public static function getEloquentQuery(): Builder
{
    return parent::getEloquentQuery()
        ->withoutGlobalScopes([SoftDeletingScope::class]);
}

// CORRECT - always maintain tenant scope when removing soft delete scope
public static function getEloquentQuery(): Builder
{
    return parent::getEloquentQuery()
        ->withoutGlobalScopes([SoftDeletingScope::class])
        ->whereBelongsTo(Filament::getTenant());
}
```

### 4. Relationship Options Must Be Tenant-Scoped
```php
// WRONG - shows categories from ALL tenants
Forms\Components\Select::make('category_id')
    ->relationship('category', 'name');

// CORRECT - scope to current tenant
Forms\Components\Select::make('category_id')
    ->relationship(
        'category',
        'name',
        fn (Builder $query) => $query->whereBelongsTo(Filament::getTenant())
    );
```

## Best Practices

1. Always scope queries to current tenant using `getEloquentQuery()`
2. Use global scopes for automatic tenant isolation
3. Auto-set tenant_id on model creation
4. Filter relationship options by tenant
5. Verify tenant ownership before updates/deletes
6. Implement proper authorization per tenant
7. Use tenant middleware for subscription checks
8. Isolate file storage per tenant
9. Clear caches when switching tenants
10. Test cross-tenant access prevention
11. Use `scopedUnique` validation, never bare `unique` in multi-tenant context
12. Always maintain tenant scope even when disabling other global scopes
