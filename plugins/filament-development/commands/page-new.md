---
description: Create custom Filament 5 page
model: claude-sonnet-4-5
---

Create a custom Filament 5 page.

## Page Specification

$ARGUMENTS

## Filament Page Patterns

### 1. **Basic Custom Page**

```php
<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;

class Settings extends Page
{
    protected static ?string $navigationIcon = 'heroicon-o-cog-6-tooth';

    protected static string $view = 'filament.pages.settings';

    protected static ?string $navigationGroup = 'Administration';

    protected static ?int $navigationSort = 99;

    public function mount(): void
    {
        static::authorizeAccess();
    }

    public static function canAccess(): bool
    {
        return auth()->user()->isAdmin();
    }
}
```

### 2. **Page with Form**

```php
<?php

namespace App\Filament\Pages;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Pages\Page;
use Filament\Notifications\Notification;

class ManageSettings extends Page implements Forms\Contracts\HasForms
{
    use Forms\Concerns\InteractsWithForms;

    protected static ?string $navigationIcon = 'heroicon-o-cog-6-tooth';

    protected static string $view = 'filament.pages.manage-settings';

    public ?array $data = [];

    public function mount(): void
    {
        $this->form->fill([
            'site_name' => config('app.name'),
            'site_email' => config('mail.from.address'),
            'maintenance_mode' => app()->isDownForMaintenance(),
        ]);
    }

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('General Settings')
                    ->schema([
                        Forms\Components\TextInput::make('site_name')
                            ->required()
                            ->maxLength(255),

                        Forms\Components\TextInput::make('site_email')
                            ->email()
                            ->required(),

                        Forms\Components\Toggle::make('maintenance_mode')
                            ->label('Maintenance Mode'),
                    ]),

                Forms\Components\Section::make('Email Settings')
                    ->schema([
                        Forms\Components\TextInput::make('smtp_host')
                            ->label('SMTP Host'),

                        Forms\Components\TextInput::make('smtp_port')
                            ->label('SMTP Port')
                            ->numeric(),
                    ]),
            ])
            ->statePath('data');
    }

    public function save(): void
    {
        $data = $this->form->getState();

        // Save settings to database or config
        // Settings::set('site_name', $data['site_name']);

        Notification::make()
            ->title('Settings saved successfully')
            ->success()
            ->send();
    }
}
```

### 3. **Dashboard Page with Widgets**

```php
<?php

namespace App\Filament\Pages;

use Filament\Pages\Dashboard as BaseDashboard;

class Dashboard extends BaseDashboard
{
    protected static ?string $navigationIcon = 'heroicon-o-home';

    public function getWidgets(): array
    {
        return [
            \App\Filament\Widgets\StatsOverview::class,
            \App\Filament\Widgets\RecentOrders::class,
            \App\Filament\Widgets\SalesChart::class,
        ];
    }

    public function getColumns(): int|string|array
    {
        return 2;
    }
}
```

Generate complete Filament 5 custom page.
