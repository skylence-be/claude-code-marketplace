# Advanced Filters

Filament 4 advanced table filtering with performance optimization.

## Multi-Select Filter

```php
Tables\Filters\SelectFilter::make('status')
    ->options([
        'pending' => 'Pending',
        'processing' => 'Processing',
        'completed' => 'Completed',
        'cancelled' => 'Cancelled',
    ])
    ->multiple()
    ->default(['pending', 'processing']),
```

## Relationship Filter

```php
Tables\Filters\SelectFilter::make('customer')
    ->relationship('customer', 'name')
    ->multiple()
    ->searchable()
    ->preload()
    ->optionsLimit(50), // Performance: limit options
```

## Date Range Filter

```php
Tables\Filters\Filter::make('date_range')
    ->form([
        Forms\Components\DatePicker::make('created_from')
            ->label('From')
            ->native(false),
        Forms\Components\DatePicker::make('created_until')
            ->label('To')
            ->native(false),
    ])
    ->query(function (Builder $query, array $data): Builder {
        return $query
            ->when(
                $data['created_from'],
                fn (Builder $q, $date) => $q->where('created_at', '>=', $date)
            )
            ->when(
                $data['created_until'],
                fn (Builder $q, $date) => $q->where('created_at', '<=', $date)
            );
    })
    ->indicateUsing(function (array $data): array {
        $indicators = [];

        if ($data['created_from'] ?? null) {
            $indicators[] = 'From ' . Carbon::parse($data['created_from'])->toFormattedDateString();
        }

        if ($data['created_until'] ?? null) {
            $indicators[] = 'Until ' . Carbon::parse($data['created_until'])->toFormattedDateString();
        }

        return $indicators;
    }),
```

## Numeric Range Filter

```php
Tables\Filters\Filter::make('price_range')
    ->form([
        Forms\Components\Grid::make(2)
            ->schema([
                Forms\Components\TextInput::make('price_from')
                    ->numeric()
                    ->prefix('$')
                    ->placeholder('Min'),
                Forms\Components\TextInput::make('price_to')
                    ->numeric()
                    ->prefix('$')
                    ->placeholder('Max'),
            ]),
    ])
    ->query(function (Builder $query, array $data): Builder {
        return $query
            ->when(
                $data['price_from'],
                fn (Builder $q, $amount) => $q->where('price', '>=', $amount)
            )
            ->when(
                $data['price_to'],
                fn (Builder $q, $amount) => $q->where('price', '<=', $amount)
            );
    })
    ->indicateUsing(function (array $data): ?string {
        if (!$data['price_from'] && !$data['price_to']) {
            return null;
        }

        if ($data['price_from'] && $data['price_to']) {
            return '$' . number_format($data['price_from']) . ' - $' . number_format($data['price_to']);
        }

        return $data['price_from']
            ? 'Min: $' . number_format($data['price_from'])
            : 'Max: $' . number_format($data['price_to']);
    }),
```

## Ternary Filter

```php
Tables\Filters\TernaryFilter::make('is_active')
    ->label('Active Status')
    ->placeholder('All records')
    ->trueLabel('Active only')
    ->falseLabel('Inactive only')
    ->queries(
        true: fn (Builder $query) => $query->where('is_active', true),
        false: fn (Builder $query) => $query->where('is_active', false),
        blank: fn (Builder $query) => $query,
    )
    ->native(false),
```

## Toggle Filter

```php
Tables\Filters\Filter::make('low_stock')
    ->query(fn (Builder $query) => $query->where('stock', '<', 10))
    ->toggle()
    ->label('Low Stock Items'),

Tables\Filters\Filter::make('featured')
    ->query(fn (Builder $query) => $query->where('is_featured', true))
    ->toggle(),
```

## Relationship Count Filter

```php
Tables\Filters\Filter::make('items_count')
    ->form([
        Forms\Components\Select::make('operator')
            ->options([
                '=' => 'Equal to',
                '>' => 'More than',
                '<' => 'Less than',
                '>=' => 'At least',
                '<=' => 'At most',
            ])
            ->default('>='),
        Forms\Components\TextInput::make('count')
            ->numeric()
            ->default(5),
    ])
    ->query(function (Builder $query, array $data): Builder {
        if (!isset($data['operator']) || !isset($data['count'])) {
            return $query;
        }
        return $query->has('items', $data['operator'], $data['count']);
    }),
```

## Complex Custom Filter

```php
Tables\Filters\Filter::make('high_value_customers')
    ->toggle()
    ->label('High Value Customers')
    ->query(fn (Builder $query): Builder =>
        $query->whereHas('customer', function (Builder $q) {
            $q->whereHas('orders', function (Builder $q) {
                $q->selectRaw('SUM(total) as customer_total')
                    ->groupBy('customer_id')
                    ->havingRaw('SUM(total) > 10000');
            });
        })
    ),
```

## Query Builder Filter

```php
Tables\Filters\QueryBuilder::make()
    ->constraints([
        Constraints\TextConstraint::make('name'),
        Constraints\NumberConstraint::make('price'),
        Constraints\DateConstraint::make('created_at'),
        Constraints\SelectConstraint::make('status')
            ->options([
                'pending' => 'Pending',
                'completed' => 'Completed',
            ]),
        Constraints\BooleanConstraint::make('is_active'),
        Constraints\RelationshipConstraint::make('customer')
            ->selectable()
            ->multiple()
            ->searchable(),
    ])
    ->constraintPickerColumns(2),
```

## Filter Layout Options

```php
return $table
    ->filters([...])
    // Layout options
    ->filtersLayout(Tables\Enums\FiltersLayout::AboveContent)
    ->filtersLayout(Tables\Enums\FiltersLayout::AboveContentCollapsible)
    ->filtersLayout(Tables\Enums\FiltersLayout::BelowContent)
    ->filtersLayout(Tables\Enums\FiltersLayout::Dropdown)

    // Persistence
    ->persistFiltersInSession()

    // Custom trigger action
    ->filtersTriggerAction(
        fn (Tables\Actions\Action $action) => $action
            ->button()
            ->label('Filters')
    );
```
