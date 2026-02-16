# Panel Configuration

Filament 5 multi-tenancy panel setup and configuration.

## Basic Panel Tenancy

```php
<?php

namespace App\Providers\Filament;

use App\Filament\Pages\Tenancy\EditTeam;
use App\Filament\Pages\Tenancy\RegisterTeam;
use App\Models\Team;
use Filament\Panel;
use Filament\PanelProvider;

class AdminPanelProvider extends PanelProvider
{
    public function panel(Panel $panel): Panel
    {
        return $panel
            ->default()
            ->id('admin')
            ->path('app')
            ->login()
            ->registration()
            ->passwordReset()
            ->emailVerification()

            // Enable multi-tenancy
            ->tenant(Team::class)
            ->tenantRegistration(RegisterTeam::class)
            ->tenantProfile(EditTeam::class)

            // Customize tenant menu
            ->tenantMenuItems([
                'register' => MenuItem::make()->label('Create Team'),
                'profile' => MenuItem::make()->label('Team Settings'),
            ])

            // Show menu only if multiple teams
            ->tenantMenu(fn () => auth()->user()->teams()->count() > 1)

            // Billing provider
            ->tenantBillingProvider(new StripeProvider())

            // Ownership relationship name
            ->tenantOwnershipRelationshipName('team')

            // URL structure: /app/team-slug/...
            ->tenantRoutePrefix('/{tenant}')

            ->discoverResources(in: app_path('Filament/Resources'), for: 'App\\Filament\\Resources')
            ->discoverPages(in: app_path('Filament/Pages'), for: 'App\\Filament\\Pages')
            ->pages([
                Pages\Dashboard::class,
            ]);
    }
}
```

## URL Structure Options

```php
// Path-based (default): /app/{tenant}/resources
->tenantRoutePrefix('/{tenant}')

// Custom prefix: /app/workspace/{tenant}
->tenantRoutePrefix('/workspace/{tenant}')

// Subdomain tenancy (requires additional setup)
->tenantDomain('{tenant}.example.com')
```

## Tenant Menu Configuration

```php
->tenantMenuItems([
    'register' => MenuItem::make()
        ->label('Create New Team')
        ->icon('heroicon-o-plus'),

    'profile' => MenuItem::make()
        ->label('Team Settings')
        ->icon('heroicon-o-cog'),

    MenuItem::make()
        ->label('Billing')
        ->icon('heroicon-o-credit-card')
        ->url(fn () => route('billing')),
])

// Conditionally show tenant menu
->tenantMenu(function () {
    return auth()->user()->teams()->count() > 1;
})
```

## Middleware Configuration

```php
->middleware([
    EncryptCookies::class,
    AddQueuedCookiesToResponse::class,
    StartSession::class,
    AuthenticateSession::class,
    ShareErrorsFromSession::class,
    VerifyCsrfToken::class,
    SubstituteBindings::class,
    DisableBladeIconComponents::class,
    DispatchServingFilamentEvent::class,
])
->authMiddleware([
    Authenticate::class,
])
->tenantMiddleware([
    // Custom tenant middleware
    EnsureTenantIsActive::class,
    VerifyTenantSubscription::class,
])
```

## Custom Tenant Middleware

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Filament\Facades\Filament;

class EnsureTenantIsActive
{
    public function handle($request, Closure $next)
    {
        $tenant = Filament::getTenant();

        if ($tenant && !$tenant->is_active) {
            return redirect()->route('tenant.suspended');
        }

        return $next($request);
    }
}
```

## Branding Per Tenant

```php
// In PanelProvider
->brandName(fn () => Filament::getTenant()?->name ?? config('app.name'))
->brandLogo(fn () => Filament::getTenant()?->logo_url)
->favicon(fn () => Filament::getTenant()?->favicon_url)
->colors([
    'primary' => fn () => Color::hex(
        Filament::getTenant()?->branding['primary_color'] ?? '#3b82f6'
    ),
])
```
