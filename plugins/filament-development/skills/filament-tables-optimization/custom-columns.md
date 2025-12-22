# Custom Columns

Filament 4 custom table columns with state, computed values, and interactions.

## Computed State Column

```php
Tables\Columns\TextColumn::make('stock_status')
    ->label('Stock')
    ->badge()
    ->color(fn (Model $record): string => match (true) {
        $record->stock === 0 => 'danger',
        $record->stock < $record->low_stock_threshold => 'warning',
        default => 'success',
    })
    ->formatStateUsing(fn (Model $record): string => match (true) {
        $record->stock === 0 => 'Out of Stock',
        $record->stock < $record->low_stock_threshold => "Low ({$record->stock})",
        default => "In Stock ({$record->stock})",
    })
    ->sortable(query: fn (Builder $query, string $direction): Builder =>
        $query->orderBy('stock', $direction)
    ),
```

## Calculated Column

```php
Tables\Columns\TextColumn::make('profit_margin')
    ->label('Margin')
    ->state(function (Model $record): float {
        if ($record->cost === 0) return 0;
        return (($record->price - $record->cost) / $record->price) * 100;
    })
    ->formatStateUsing(fn (float $state): string =>
        number_format($state, 1) . '%'
    )
    ->color(fn (float $state): string => match (true) {
        $state < 20 => 'danger',
        $state < 40 => 'warning',
        default => 'success',
    })
    ->sortable(query: fn (Builder $query, string $direction): Builder =>
        $query
            ->selectRaw('((price - cost) / price * 100) as profit_margin')
            ->orderBy('profit_margin', $direction)
    ),
```

## Toggle Column with Callback

```php
Tables\Columns\ToggleColumn::make('is_active')
    ->label('Active')
    ->onColor('success')
    ->offColor('danger')
    ->afterStateUpdated(function (Model $record, $state) {
        // Log the change
        activity()
            ->performedOn($record)
            ->withProperties(['active' => $state])
            ->log('Product status changed');

        // Clear cache
        cache()->forget("product.{$record->id}");

        // Send notification
        if (!$state) {
            Notification::make()
                ->warning()
                ->title('Product deactivated')
                ->body("Product {$record->name} has been deactivated")
                ->send();
        }
    }),
```

## Icon Column with Multiple States

```php
Tables\Columns\IconColumn::make('availability_status')
    ->icon(fn (Model $record): string => match (true) {
        $record->stock > 0 && $record->is_active => 'heroicon-o-check-circle',
        $record->stock === 0 => 'heroicon-o-x-circle',
        !$record->is_active => 'heroicon-o-pause-circle',
        default => 'heroicon-o-question-mark-circle',
    })
    ->color(fn (Model $record): string => match (true) {
        $record->stock > 0 && $record->is_active => 'success',
        $record->stock === 0 => 'danger',
        !$record->is_active => 'warning',
        default => 'gray',
    })
    ->tooltip(fn (Model $record): string => match (true) {
        $record->stock > 0 && $record->is_active => 'Available for sale',
        $record->stock === 0 => 'Out of stock',
        !$record->is_active => 'Product inactive',
        default => 'Status unknown',
    }),
```

## Cached State Column

```php
Tables\Columns\ViewColumn::make('performance_chart')
    ->view('filament.tables.columns.performance-chart')
    ->state(function (Model $record) {
        // Get sales data with caching
        return cache()->remember(
            "product.{$record->id}.performance",
            now()->addMinutes(15),
            fn () => $record->salesData()->last30Days()->get()
        );
    }),
```

## Image Column with Fallback

```php
Tables\Columns\ImageColumn::make('image')
    ->disk('public')
    ->defaultImageUrl(fn (Model $record) =>
        url('/images/placeholder.png')
    )
    ->circular()
    ->size(60)
    ->checkFileExistence(false), // Performance optimization
```

## Relationship Columns

```php
// Count relationship
Tables\Columns\TextColumn::make('orders_count')
    ->counts('orders')
    ->label('Orders')
    ->badge()
    ->color('info'),

// Sum relationship
Tables\Columns\TextColumn::make('orders_sum_total')
    ->sum('orders', 'total')
    ->label('Total Sales')
    ->money('usd'),

// Average relationship
Tables\Columns\TextColumn::make('reviews_avg_rating')
    ->avg('reviews', 'rating')
    ->label('Avg Rating'),
```

## Summarizers

```php
Tables\Columns\TextColumn::make('total')
    ->money('usd')
    ->summarize([
        Tables\Columns\Summarizers\Sum::make()
            ->money('usd')
            ->label('Total'),

        Tables\Columns\Summarizers\Average::make()
            ->money('usd')
            ->label('Average'),

        Tables\Columns\Summarizers\Count::make()
            ->label('Count'),

        Tables\Columns\Summarizers\Range::make()
            ->label('Range'),
    ]),
```

## Custom View Column

```php
Tables\Columns\ViewColumn::make('progress')
    ->view('filament.tables.columns.progress-bar'),
```

```blade
{{-- resources/views/filament/tables/columns/progress-bar.blade.php --}}
@php
    $percentage = $getState();
@endphp

<div class="w-full">
    <div class="flex justify-between mb-1">
        <span class="text-sm text-gray-600">Progress</span>
        <span class="text-sm text-gray-600">{{ $percentage }}%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div class="h-2.5 rounded-full @if($percentage >= 100) bg-green-600 @elseif($percentage >= 50) bg-blue-600 @else bg-yellow-600 @endif"
             style="width: {{ min($percentage, 100) }}%">
        </div>
    </div>
</div>
```
