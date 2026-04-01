---
name: pennant-feature-flags
description: Laravel Pennant feature flag patterns including flag definition, user-scoped activation, Blade directives, class-based features, and gradual rollout strategies. Use when implementing feature flags, A/B testing, or gradual feature rollouts.
category: laravel
tags: [pennant, feature-flags, toggles, rollout, ab-testing]
related_skills: [laravel-blueprint, laravel-testing-patterns]
---

# Pennant Feature Flags

Laravel Pennant is the official feature flag package for Laravel. It provides a simple API for defining, checking, and activating feature flags scoped to users, teams, or any entity.

## When to Use This Skill

- Implementing feature flags for gradual rollouts
- Adding A/B testing capability
- Gating features for specific users or teams
- Using `@feature` Blade directive
- Managing feature flag lifecycle (define → activate → remove)

## Defining Features

### Closure-Based (Simple)

```php
use Laravel\Pennant\Feature;

// In a service provider's boot() method
Feature::define('new-dashboard', function (User $user) {
    return $user->isAdmin();
});

// Percentage-based rollout
Feature::define('new-checkout', function (User $user) {
    return match (true) {
        $user->isInternal() => true,
        default => lottery(25), // 25% of users
    };
});
```

### Class-Based (Complex Features)

```php
// app/Features/NewDashboard.php
namespace App\Features;

use Laravel\Pennant\Feature;

class NewDashboard
{
    public function resolve(User $user): bool
    {
        return $user->isAdmin();
    }
}
```

## Checking Features

```php
// Current user context
if (Feature::active('new-dashboard')) {
    // Feature is active for authenticated user
}

// Explicit scope
if (Feature::for($user)->active('new-dashboard')) {
    // Feature is active for this specific user
}

// Class-based feature
if (Feature::active(NewDashboard::class)) {
    // ...
}

// Rich values (not just boolean)
$variant = Feature::value('checkout-button-color');
```

## Blade Directive

```blade
@feature('new-dashboard')
    <x-new-dashboard />
@else
    <x-old-dashboard />
@endfeature
```

## Activating / Deactivating

```php
// Activate globally
Feature::activate('new-dashboard');

// Activate for specific user
Feature::for($user)->activate('new-dashboard');

// Deactivate
Feature::deactivate('new-dashboard');
Feature::for($user)->deactivate('new-dashboard');

// Forget stored value (re-evaluates next check)
Feature::forget('new-dashboard');

// Purge all stored values
Feature::purge('new-dashboard');
```

## Testing

```php
use Laravel\Pennant\Feature;

it('shows new dashboard for admins', function () {
    $admin = User::factory()->admin()->create();

    Feature::for($admin)->activate('new-dashboard');

    $this->actingAs($admin)
        ->get('/dashboard')
        ->assertSee('New Dashboard');
});

it('hides new dashboard for regular users', function () {
    $user = User::factory()->create();

    Feature::for($user)->deactivate('new-dashboard');

    $this->actingAs($user)
        ->get('/dashboard')
        ->assertDontSee('New Dashboard');
});
```

## Common Pitfalls

- Forgetting to scope features for specific users/entities
- Not following existing naming conventions for feature flags
- Leaving stale feature flags in code after full rollout (clean up with `Feature::purge()`)
- Using feature flags for permanent configuration (use config values instead)
