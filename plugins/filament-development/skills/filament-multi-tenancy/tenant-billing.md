# Tenant Billing & Storage

Filament 4 subscription management and tenant storage isolation.

## Billing Page

```php
<?php

namespace App\Filament\Pages;

use Filament\Facades\Filament;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Pages\Page;

class TeamBilling extends Page
{
    protected static ?string $navigationIcon = 'heroicon-o-credit-card';
    protected static string $view = 'filament.pages.team-billing';
    protected static ?string $navigationGroup = 'Team Management';

    public ?array $data = [];

    public function mount(): void
    {
        $this->form->fill([
            'plan' => Filament::getTenant()->plan,
        ]);
    }

    public static function canAccess(): bool
    {
        $team = Filament::getTenant();
        return $team && ($team->owner_id === auth()->id());
    }

    protected function getFormSchema(): array
    {
        $team = Filament::getTenant();

        return [
            Forms\Components\Section::make('Current Plan')
                ->schema([
                    Forms\Components\Placeholder::make('current_plan')
                        ->label('Plan')
                        ->content(ucfirst($team->plan)),

                    Forms\Components\Placeholder::make('status')
                        ->content(function () use ($team) {
                            if ($team->onTrial()) {
                                return 'Trial (ends ' . $team->trial_ends_at->format('M d, Y') . ')';
                            }
                            if ($team->hasActiveSubscription()) {
                                return 'Active (renews ' . $team->subscription_ends_at->format('M d, Y') . ')';
                            }
                            return 'Inactive';
                        }),

                    Forms\Components\Placeholder::make('members')
                        ->label('Team Members')
                        ->content($team->members()->count() . ' / ' . ($team->getMemberLimit() ?? '∞')),
                ])
                ->columns(3),

            Forms\Components\Section::make('Change Plan')
                ->schema([
                    Forms\Components\Radio::make('plan')
                        ->options([
                            'free' => 'Free - Up to 3 members',
                            'pro' => 'Pro - $29/month - Up to 25 members',
                            'enterprise' => 'Enterprise - $99/month - Unlimited',
                        ])
                        ->descriptions([
                            'free' => '100MB storage, basic features',
                            'pro' => '10GB storage, advanced features',
                            'enterprise' => '100GB storage, all features',
                        ])
                        ->required()
                        ->reactive(),

                    Forms\Components\Actions::make([
                        Forms\Components\Actions\Action::make('update_plan')
                            ->label(fn ($get) =>
                                $get('plan') === 'free' ? 'Downgrade to Free' : 'Subscribe'
                            )
                            ->color(fn ($get) =>
                                $get('plan') === 'free' ? 'danger' : 'primary'
                            )
                            ->requiresConfirmation()
                            ->disabled(fn ($get) => $get('plan') === $team->plan)
                            ->action(function (array $data) use ($team) {
                                if ($data['plan'] === 'free') {
                                    $team->update(['plan' => 'free']);
                                    Notification::make()
                                        ->success()
                                        ->title('Downgraded to Free')
                                        ->send();
                                } else {
                                    // Redirect to Stripe/payment
                                    $checkout = $team->newSubscription('default', $data['plan'])
                                        ->checkout([
                                            'success_url' => route('filament.admin.pages.team-billing'),
                                            'cancel_url' => route('filament.admin.pages.team-billing'),
                                        ]);
                                    return redirect($checkout->url);
                                }
                            }),
                    ]),
                ])
                ->collapsible(),
        ];
    }
}
```

## Storage Isolation Service

```php
<?php

namespace App\Services;

use Filament\Facades\Filament;
use Illuminate\Support\Facades\Storage;

class TenantStorage
{
    public static function disk(): \Illuminate\Contracts\Filesystem\Filesystem
    {
        $tenant = Filament::getTenant();

        if (!$tenant) {
            throw new \Exception('No active tenant');
        }

        // Use tenant-specific path within default disk
        return Storage::disk('public');
    }

    public static function path(string $path = ''): string
    {
        $tenant = Filament::getTenant();
        return "tenants/{$tenant->id}/{$path}";
    }

    public static function put(string $path, $contents, array $options = []): string
    {
        return static::disk()->put(static::path($path), $contents, $options);
    }

    public static function get(string $path): string
    {
        return static::disk()->get(static::path($path));
    }

    public static function delete(string $path): bool
    {
        return static::disk()->delete(static::path($path));
    }

    public static function getUsage(): int
    {
        $disk = static::disk();
        $files = $disk->allFiles(static::path());

        $totalSize = 0;
        foreach ($files as $file) {
            $totalSize += $disk->size($file);
        }

        return $totalSize;
    }

    public static function hasExceededLimit(): bool
    {
        $tenant = Filament::getTenant();
        return static::getUsage() >= $tenant->getStorageLimit();
    }

    public static function getUsagePercentage(): float
    {
        $tenant = Filament::getTenant();
        $limit = $tenant->getStorageLimit();

        if ($limit === 0) {
            return 0;
        }

        return (static::getUsage() / $limit) * 100;
    }

    public static function formatSize(int $bytes): string
    {
        $units = ['B', 'KB', 'MB', 'GB', 'TB'];
        $unitIndex = 0;

        while ($bytes >= 1024 && $unitIndex < count($units) - 1) {
            $bytes /= 1024;
            $unitIndex++;
        }

        return round($bytes, 2) . ' ' . $units[$unitIndex];
    }
}
```

## Storage Limit in Team Model

```php
// In Team model
public function getStorageLimit(): int
{
    return match($this->plan) {
        'free' => 1024 * 1024 * 100,        // 100MB
        'pro' => 1024 * 1024 * 1024 * 10,   // 10GB
        'enterprise' => 1024 * 1024 * 1024 * 100, // 100GB
        default => 0,
    };
}
```

## FileUpload with Tenant Storage

```php
// In resource form
Forms\Components\FileUpload::make('document')
    ->disk('public')
    ->directory(fn () => TenantStorage::path('documents'))
    ->visibility('private')
    ->maxSize(fn () => Filament::getTenant()->getMaxUploadSize())
    ->beforeStateUpdated(function () {
        if (TenantStorage::hasExceededLimit()) {
            Notification::make()
                ->danger()
                ->title('Storage limit exceeded')
                ->body('Please upgrade your plan to upload more files.')
                ->send();

            throw new \Exception('Storage limit exceeded');
        }
    }),
```

## Storage Usage Widget

```php
<?php

namespace App\Filament\Widgets;

use App\Services\TenantStorage;
use Filament\Facades\Filament;
use Filament\Widgets\StatsOverviewWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class StorageUsageWidget extends StatsOverviewWidget
{
    protected function getStats(): array
    {
        $team = Filament::getTenant();
        $usage = TenantStorage::getUsage();
        $limit = $team->getStorageLimit();
        $percentage = TenantStorage::getUsagePercentage();

        return [
            Stat::make('Storage Used', TenantStorage::formatSize($usage))
                ->description(TenantStorage::formatSize($limit) . ' total')
                ->descriptionIcon('heroicon-o-server')
                ->color(match (true) {
                    $percentage >= 90 => 'danger',
                    $percentage >= 70 => 'warning',
                    default => 'success',
                })
                ->chart([$percentage, 100 - $percentage]),

            Stat::make('Team Members', $team->members()->count())
                ->description(($team->getMemberLimit() ?? '∞') . ' max')
                ->descriptionIcon('heroicon-o-users'),

            Stat::make('Plan', ucfirst($team->plan))
                ->description($team->hasActiveSubscription() ? 'Active' : 'Trial')
                ->descriptionIcon('heroicon-o-credit-card'),
        ];
    }
}
```
