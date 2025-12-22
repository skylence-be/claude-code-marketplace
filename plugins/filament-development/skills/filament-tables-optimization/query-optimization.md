# Query Optimization

Filament 4 table query optimization with eager loading and efficient queries.

## Eager Loading

```php
<?php

namespace App\Filament\Resources;

use Filament\Resources\Resource;
use Illuminate\Database\Eloquent\Builder;

class OrderResource extends Resource
{
    /**
     * Optimize query with eager loading and column selection.
     */
    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            // Eager load relationships to prevent N+1
            ->with([
                'customer:id,name,email',
                'items.product:id,name,sku',
                'shippingAddress:id,order_id,city,state',
            ])
            // Add counts without loading full relationships
            ->withCount([
                'items',
                'items as total_quantity' => fn (Builder $query) =>
                    $query->select(\DB::raw('sum(quantity)')),
            ])
            // Add aggregates
            ->withSum('items', 'subtotal')
            // Select only needed columns from main table
            ->select([
                'id',
                'number',
                'customer_id',
                'status',
                'total',
                'created_at',
            ])
            // Add computed columns
            ->selectRaw('DATEDIFF(NOW(), created_at) as days_since_created');
    }
}
```

## Table with Optimized Columns

```php
public static function table(Table $table): Table
{
    return $table
        ->columns([
            Tables\Columns\TextColumn::make('number')
                ->searchable()
                ->sortable()
                ->copyable(),

            // Access eager-loaded relationship
            Tables\Columns\TextColumn::make('customer.name')
                ->searchable(['customers.name', 'customers.email'])
                ->sortable(query: fn (Builder $query, string $direction): Builder =>
                    $query
                        ->join('customers', 'orders.customer_id', '=', 'customers.id')
                        ->orderBy('customers.name', $direction)
                ),

            // Use withCount result
            Tables\Columns\TextColumn::make('items_count')
                ->label('Items')
                ->badge(),

            // Use withSum result
            Tables\Columns\TextColumn::make('items_sum_subtotal')
                ->label('Subtotal')
                ->money('usd'),

            // Use computed column
            Tables\Columns\TextColumn::make('days_since_created')
                ->label('Age')
                ->suffix(' days'),
        ])
        // Use database indexing for search
        ->persistSearchInSession()
        ->persistFiltersInSession()
        // Cursor pagination for better performance
        ->paginationPageOptions([10, 25, 50, 100])
        ->defaultPaginationPageOption(25)
        // Enable polling if needed
        ->poll('30s')
        // Defer loading for faster initial render
        ->deferLoading();
}
```

## Efficient Filter Queries

```php
->filters([
    Tables\Filters\SelectFilter::make('status')
        ->options([...])
        ->multiple()
        // Optimize filter query
        ->query(function (Builder $query, array $data): Builder {
            if (empty($data['values'])) {
                return $query;
            }
            return $query->whereIn('status', $data['values']);
        }),

    // Efficient date range filter
    Tables\Filters\Filter::make('created_at')
        ->form([
            Forms\Components\DatePicker::make('created_from'),
            Forms\Components\DatePicker::make('created_until'),
        ])
        ->query(function (Builder $query, array $data): Builder {
            return $query
                ->when(
                    $data['created_from'],
                    fn (Builder $q, $date) => $q->whereDate('created_at', '>=', $date)
                )
                ->when(
                    $data['created_until'],
                    fn (Builder $q, $date) => $q->whereDate('created_at', '<=', $date)
                );
        }),
])
```

## Search Optimization

```php
Tables\Columns\TextColumn::make('name')
    // Search multiple columns
    ->searchable(['name', 'sku', 'description']),

Tables\Columns\TextColumn::make('customer.name')
    // Custom search query for relationship
    ->searchable(query: function (Builder $query, string $search): Builder {
        return $query->whereHas('customer', function (Builder $q) use ($search) {
            $q->where('name', 'like', "%{$search}%")
              ->orWhere('email', 'like', "%{$search}%");
        });
    }),
```

## Table Performance Options

```php
return $table
    // Persist state in session
    ->persistSearchInSession()
    ->persistFiltersInSession()
    ->persistSortInSession()

    // Search optimization
    ->searchDebounce('500ms')
    ->searchOnBlur()

    // Pagination
    ->paginationPageOptions([10, 25, 50, 100])
    ->defaultPaginationPageOption(25)
    ->extremePaginationLinks()

    // Loading optimization
    ->deferLoading()

    // Filter deselection
    ->deselectAllRecordsWhenFiltered(false);
```

## Database Indexes

```php
// Migration for optimized queries
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->string('number')->index();
    $table->foreignId('customer_id')->constrained()->index();
    $table->string('status')->index();
    $table->decimal('total', 10, 2);
    $table->timestamps();

    // Composite index for common filters
    $table->index(['status', 'created_at']);
    $table->index(['customer_id', 'status']);
});
```
