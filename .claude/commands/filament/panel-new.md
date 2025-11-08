---
description: Create new Filament 4 panel
model: claude-sonnet-4-5
---

Create a new Filament 4 panel.

## Panel Specification

$ARGUMENTS

## Filament Panel Patterns

### 1. **Admin Panel Configuration**

```php
<?php

use Filament\Panel;

return Panel::make()
    ->id('admin')
    ->path('admin')
    ->login()
    ->colors([
        'primary' => Color::Amber,
    ])
    ->discoverResources(in: app_path('Filament/Resources'), for: 'App\\Filament\\Resources')
    ->discoverPages(in: app_path('Filament/Pages'), for: 'App\\Filament\\Pages')
    ->discoverWidgets(in: app_path('Filament/Widgets'), for: 'App\\Filament\\Widgets')
    ->widgets([
        Widgets\AccountWidget::class,
        Widgets\FilamentInfoWidget::class,
    ])
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
    ->brandName('My Admin')
    ->brandLogo(asset('images/logo.svg'))
    ->darkMode(true)
    ->favicon(asset('favicon.ico'));
```

### 2. **User Panel Configuration**

```php
<?php

use Filament\Panel;

return Panel::make()
    ->id('user')
    ->path('dashboard')
    ->login()
    ->registration()
    ->passwordReset()
    ->emailVerification()
    ->profile()
    ->colors([
        'primary' => Color::Blue,
    ])
    ->discoverResources(in: app_path('Filament/User/Resources'), for: 'App\\Filament\\User\\Resources')
    ->discoverPages(in: app_path('Filament/User/Pages'), for: 'App\\Filament\\User\\Pages')
    ->pages([
        Pages\Dashboard::class,
    ])
    ->brandName('User Portal')
    ->spa();
```

### 3. **Multi-tenant Panel**

```php
<?php

use Filament\Panel;

return Panel::make()
    ->id('app')
    ->path('app')
    ->login()
    ->tenant(Team::class)
    ->tenantRegistration(RegisterTeam::class)
    ->tenantProfile(EditTeamProfile::class)
    ->colors([
        'primary' => Color::Indigo,
    ])
    ->discoverResources(in: app_path('Filament/App/Resources'), for: 'App\\Filament\\App\\Resources')
    ->resources([
        //
    ])
    ->pages([
        Pages\Dashboard::class,
    ])
    ->plugins([
        \Filament\SpatieLaravelMediaLibraryPlugin::make(),
        \Jeffgreco13\FilamentBreezy\BreezyCore::make(),
    ]);
```

Generate complete Filament 4 panel configuration.
