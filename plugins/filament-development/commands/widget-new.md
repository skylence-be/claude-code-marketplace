---
description: Create Filament 4 dashboard widget
model: claude-sonnet-4-5
---

Create a Filament 4 widget.

## Widget Specification

$ARGUMENTS

## Filament Widget Patterns

### 1. **Stats Widget**

```php
<?php

namespace App\Filament\Widgets;

use App\Models\Order;
use App\Models\User;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class StatsOverview extends BaseWidget
{
    protected function getStats(): array
    {
        return [
            Stat::make('Total Users', User::count())
                ->description('Total registered users')
                ->descriptionIcon('heroicon-o-user-group')
                ->color('success')
                ->chart([7, 2, 10, 3, 15, 4, 17]),

            Stat::make('Total Revenue', '$' . number_format(Order::sum('total'), 2))
                ->description('All time revenue')
                ->descriptionIcon('heroicon-o-currency-dollar')
                ->color('primary'),

            Stat::make('Active Orders', Order::where('status', 'processing')->count())
                ->description('Orders being processed')
                ->descriptionIcon('heroicon-o-shopping-cart')
                ->color('warning'),
        ];
    }

    protected static ?int $sort = 0;

    public function getColumns(): int
    {
        return 3;
    }
}
```

### 2. **Chart Widget**

```php
<?php

namespace App\Filament\Widgets;

use App\Models\Order;
use Filament\Widgets\ChartWidget;
use Flowframe\Trend\Trend;
use Flowframe\Trend\TrendValue;

class SalesChart extends ChartWidget
{
    protected static ?string $heading = 'Sales Overview';

    protected static ?int $sort = 1;

    public ?string $filter = '7';

    protected function getData(): array
    {
        $activeFilter = $this->filter;

        $data = Trend::model(Order::class)
            ->between(
                start: now()->subDays($activeFilter),
                end: now(),
            )
            ->perDay()
            ->count();

        return [
            'datasets' => [
                [
                    'label' => 'Orders',
                    'data' => $data->map(fn (TrendValue $value) => $value->aggregate),
                    'backgroundColor' => 'rgba(59, 130, 246, 0.1)',
                    'borderColor' => 'rgb(59, 130, 246)',
                ],
            ],
            'labels' => $data->map(fn (TrendValue $value) => $value->date),
        ];
    }

    protected function getType(): string
    {
        return 'line';
    }

    protected function getFilters(): ?array
    {
        return [
            '7' => 'Last 7 days',
            '30' => 'Last 30 days',
            '90' => 'Last 3 months',
        ];
    }
}
```

### 3. **Table Widget**

```php
<?php

namespace App\Filament\Widgets;

use App\Models\Order;
use Filament\Tables;
use Filament\Tables\Table;
use Filament\Widgets\TableWidget as BaseWidget;

class RecentOrders extends BaseWidget
{
    protected static ?int $sort = 2;

    protected int|string|array $columnSpan = 'full';

    public function table(Table $table): Table
    {
        return $table
            ->query(
                Order::query()
                    ->latest()
                    ->limit(5)
            )
            ->columns([
                Tables\Columns\TextColumn::make('id')
                    ->label('Order #'),

                Tables\Columns\TextColumn::make('user.name')
                    ->label('Customer'),

                Tables\Columns\TextColumn::make('total')
                    ->money('usd'),

                Tables\Columns\BadgeColumn::make('status')
                    ->colors([
                        'warning' => 'pending',
                        'primary' => 'processing',
                        'success' => 'completed',
                    ]),

                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime(),
            ]);
    }
}
```

Generate complete Filament 4 widget.
