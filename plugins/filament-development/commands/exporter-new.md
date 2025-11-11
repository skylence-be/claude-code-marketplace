---
description: Create Filament 4 data exporter
model: claude-sonnet-4-5
---

Create a Filament 4 exporter.

## Exporter Specification

$ARGUMENTS

## Filament Exporter Patterns

### 1. **Basic Exporter**

```php
<?php

namespace App\Filament\Exports;

use App\Models\User;
use Filament\Actions\Exports\ExportColumn;
use Filament\Actions\Exports\Exporter;
use Filament\Actions\Exports\Models\Export;

class UserExporter extends Exporter
{
    protected static ?string $model = User::class;

    public static function getColumns(): array
    {
        return [
            ExportColumn::make('id')
                ->label('ID'),

            ExportColumn::make('name'),

            ExportColumn::make('email'),

            ExportColumn::make('created_at')
                ->label('Joined Date'),

            ExportColumn::make('email_verified_at')
                ->label('Email Verified'),
        ];
    }

    public static function getCompletedNotificationBody(Export $export): string
    {
        $body = 'Your user export has completed and ' . number_format($export->successful_rows) . ' ' . str('row')->plural($export->successful_rows) . ' exported.';

        if ($failedRowsCount = $export->getFailedRowsCount()) {
            $body .= ' ' . number_format($failedRowsCount) . ' ' . str('row')->plural($failedRowsCount) . ' failed to export.';
        }

        return $body;
    }
}
```

### 2. **Exporter with Custom Formatting**

```php
<?php

namespace App\Filament\Exports;

use App\Models\Order;
use Filament\Actions\Exports\ExportColumn;
use Filament\Actions\Exports\Exporter;

class OrderExporter extends Exporter
{
    protected static ?string $model = Order::class;

    public static function getColumns(): array
    {
        return [
            ExportColumn::make('id'),

            ExportColumn::make('customer.name')
                ->label('Customer'),

            ExportColumn::make('total')
                ->formatStateUsing(fn ($state) => '$' . number_format($state, 2)),

            ExportColumn::make('status')
                ->formatStateUsing(fn ($state) => ucfirst($state)),

            ExportColumn::make('items_count')
                ->label('Items')
                ->counts('items'),

            ExportColumn::make('created_at')
                ->label('Order Date')
                ->formatStateUsing(fn ($state) => $state->format('Y-m-d H:i')),
        ];
    }
}
```

Generate complete Filament 4 exporter.
