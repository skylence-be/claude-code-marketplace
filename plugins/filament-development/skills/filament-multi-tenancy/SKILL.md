---
name: filament-multi-tenancy
description: Master Filament 4 multi-tenancy patterns including panel configuration, tenant models, tenant-aware queries, global scopes, tenant switching, billing, team management, and security isolation. Use when building SaaS applications or multi-tenant systems.
category: filament
tags: [filament, multi-tenancy, saas, teams, security, isolation]
related_skills: [filament-resource-patterns, laravel-security-patterns, eloquent-patterns]
---

# Filament Multi-Tenancy

Multi-tenant SaaS application patterns for Filament 4.

## Pattern Files

Load specific patterns based on your needs:

| Pattern | File | Use Case |
|---------|------|----------|
| Panel Configuration | `panel-configuration.md` | Panel setup, tenant routes, middleware |
| Tenant Models | `tenant-models.md` | Team/User models, relationships |
| Tenant Resources | `tenant-resources.md` | Tenant-aware resources, global scopes |
| Team Management | `team-management.md` | Registration, profile, members, invitations |
| Billing & Storage | `tenant-billing.md` | Subscriptions, storage isolation |

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
