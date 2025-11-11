---
name: filament-tables-optimization
description: Master Filament 4 table optimization including query performance, custom columns, bulk actions, filters, exports, imports, summarizers, and pagination strategies. Use when building high-performance data tables and list views.
category: filament
tags: [filament, tables, performance, optimization, export, import]
related_skills: [filament-resource-patterns, laravel-caching-strategies, eloquent-patterns]
---

# Filament Tables Optimization

Comprehensive guide to optimizing Filament 4 tables for performance, covering efficient query strategies, eager loading, custom table columns with state management, performant bulk actions, advanced filtering, export/import with queues, data summarizers, and pagination optimization techniques.

## When to Use This Skill

- Building high-performance tables with thousands of records
- Implementing complex data export functionality with queues
- Creating bulk import features with validation
- Optimizing table queries to prevent N+1 problems
- Building custom table columns with computed data
- Implementing advanced filtering with query optimization
- Creating data summarizers for aggregated information
- Designing efficient pagination strategies
- Building searchable tables with multiple columns
- Implementing real-time table updates with polling

## Core Concepts

### 1. Query Optimization
- **Eager Loading**: Prevent N+1 queries with proper relationships
- **Select Specific Columns**: Load only required data
- **Query Scopes**: Reusable query logic
- **Indexing**: Database index optimization
- **Caching**: Cache expensive queries

### 2. Table Performance
- **Pagination**: Efficient data chunking
- **Lazy Loading**: Load data on demand
- **Debouncing**: Reduce search query frequency
- **Column Selection**: Hide unnecessary columns
- **Virtual Scrolling**: Handle large datasets

### 3. Bulk Operations
- **Chunk Processing**: Handle large record sets
- **Queue Jobs**: Background processing
- **Progress Tracking**: User feedback
- **Transaction Safety**: Data integrity
- **Memory Management**: Prevent timeouts

### 4. Import/Export
- **Queue Processing**: Background jobs
- **Validation**: Data integrity checks
- **Format Support**: CSV, Excel, JSON
- **Error Handling**: Failed row tracking
- **Progress Indicators**: User experience

### 5. Advanced Features
- **Summarizers**: Aggregate calculations
- **Custom Actions**: Specialized operations
- **Global Search**: Cross-table searching
- **State Persistence**: Remember filters
- **Real-time Updates**: Polling strategies

## Quick Start

```php
<?php

use Filament\Tables;
use Filament\Tables\Table;

public static function table(Table $table): Table
{
    return $table
        ->columns([
            Tables\Columns\TextColumn::make('name')->searchable()->sortable(),
            Tables\Columns\TextColumn::make('email')->searchable(),
        ])
        ->filters([
            Tables\Filters\SelectFilter::make('status'),
        ])
        ->actions([
            Tables\Actions\EditAction::make(),
        ])
        ->bulkActions([
            Tables\Actions\BulkActionGroup::make([
                Tables\Actions\DeleteBulkAction::make(),
            ]),
        ])
        ->defaultSort('created_at', 'desc');
}
```

## Fundamental Patterns

### Pattern 1: Query Optimization with Eager Loading

```php
<?php

namespace App\Filament\Resources;

use Filament\Tables;
use Filament\Tables\Table;
use Filament\Resources\Resource;
use Illuminate\Database\Eloquent\Builder;
use App\Models\Order;

class OrderResource extends Resource
{
    protected static ?string $model = Order::class;

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
                'payment_status',
                'total',
                'created_at',
                'updated_at',
            ])
            // Add computed columns
            ->selectRaw('DATEDIFF(NOW(), created_at) as days_since_created');
    }

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
                    ->sortable(query: function (Builder $query, string $direction): Builder {
                        return $query
                            ->join('customers', 'orders.customer_id', '=', 'customers.id')
                            ->orderBy('customers.name', $direction);
                    }),

                // Use withCount result
                Tables\Columns\TextColumn::make('items_count')
                    ->label('Items')
                    ->badge()
                    ->alignCenter(),

                // Use withSum result
                Tables\Columns\TextColumn::make('items_sum_subtotal')
                    ->label('Subtotal')
                    ->money('usd')
                    ->sortable(),

                Tables\Columns\TextColumn::make('total')
                    ->money('usd')
                    ->sortable()
                    ->summarize([
                        Tables\Columns\Summarizers\Sum::make()
                            ->money('usd')
                            ->label('Total Revenue'),
                    ]),

                Tables\Columns\BadgeColumn::make('status')
                    ->colors([
                        'secondary' => 'pending',
                        'warning' => 'processing',
                        'success' => 'completed',
                        'danger' => 'cancelled',
                    ]),

                // Use computed column
                Tables\Columns\TextColumn::make('days_since_created')
                    ->label('Age')
                    ->suffix(' days')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'pending' => 'Pending',
                        'processing' => 'Processing',
                        'completed' => 'Completed',
                        'cancelled' => 'Cancelled',
                    ])
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
                        Forms\Components\DatePicker::make('created_from')
                            ->native(false),
                        Forms\Components\DatePicker::make('created_until')
                            ->native(false),
                    ])
                    ->query(function (Builder $query, array $data): Builder {
                        return $query
                            ->when(
                                $data['created_from'],
                                fn (Builder $query, $date): Builder =>
                                    $query->whereDate('created_at', '>=', $date)
                            )
                            ->when(
                                $data['created_until'],
                                fn (Builder $query, $date): Builder =>
                                    $query->whereDate('created_at', '<=', $date)
                            );
                    }),
            ])
            // Use database indexing for search
            ->persistSearchInSession()
            ->persistFiltersInSession()
            ->persistSortInSession()
            // Use cursor pagination for better performance
            ->paginationPageOptions([10, 25, 50, 100])
            ->defaultPaginationPageOption(25)
            // Enable query caching
            ->poll('30s')
            ->deferLoading();
    }
}
```

### Pattern 2: Custom Table Columns with State

```php
<?php

namespace App\Filament\Resources;

use Filament\Tables;
use Filament\Tables\Table;
use Filament\Tables\Columns\Column;
use App\Models\Product;

class ProductResource extends Resource
{
    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                // Custom column with state calculations
                Tables\Columns\TextColumn::make('stock_status')
                    ->label('Stock')
                    ->badge()
                    ->color(fn (Product $record): string => match (true) {
                        $record->stock === 0 => 'danger',
                        $record->stock < $record->low_stock_threshold => 'warning',
                        default => 'success',
                    })
                    ->formatStateUsing(fn (Product $record): string => match (true) {
                        $record->stock === 0 => 'Out of Stock',
                        $record->stock < $record->low_stock_threshold => "Low ({$record->stock})",
                        default => "In Stock ({$record->stock})",
                    })
                    ->sortable(query: function (Builder $query, string $direction): Builder {
                        return $query->orderBy('stock', $direction);
                    }),

                // Custom column with calculations
                Tables\Columns\TextColumn::make('profit_margin')
                    ->label('Margin')
                    ->state(function (Product $record): float {
                        if ($record->cost === 0) {
                            return 0;
                        }

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
                    ->sortable(query: function (Builder $query, string $direction): Builder {
                        return $query
                            ->selectRaw('((price - cost) / price * 100) as profit_margin')
                            ->orderBy('profit_margin', $direction);
                    }),

                // Toggle column with action
                Tables\Columns\ToggleColumn::make('is_active')
                    ->label('Active')
                    ->afterStateUpdated(function (Product $record, $state) {
                        // Log the change
                        activity()
                            ->performedOn($record)
                            ->withProperties(['active' => $state])
                            ->log('Product status changed');

                        // Clear cache
                        cache()->forget("product.{$record->id}");

                        // Send notification if deactivated
                        if (!$state) {
                            \Notification::make()
                                ->warning()
                                ->title('Product deactivated')
                                ->body("Product {$record->name} has been deactivated")
                                ->send();
                        }
                    }),

                // Custom view column with state
                Tables\Columns\ViewColumn::make('performance_chart')
                    ->view('filament.tables.columns.performance-chart')
                    ->state(function (Product $record) {
                        // Get sales data for last 30 days
                        return cache()->remember(
                            "product.{$record->id}.performance",
                            now()->addMinutes(15),
                            fn () => $record->salesData()->last30Days()->get()
                        );
                    }),

                // Icon column with multiple states
                Tables\Columns\IconColumn::make('availability_status')
                    ->icon(fn (Product $record): string => match (true) {
                        $record->stock > 0 && $record->is_active => 'heroicon-o-check-circle',
                        $record->stock === 0 => 'heroicon-o-x-circle',
                        !$record->is_active => 'heroicon-o-pause-circle',
                        default => 'heroicon-o-question-mark-circle',
                    })
                    ->color(fn (Product $record): string => match (true) {
                        $record->stock > 0 && $record->is_active => 'success',
                        $record->stock === 0 => 'danger',
                        !$record->is_active => 'warning',
                        default => 'gray',
                    })
                    ->tooltip(fn (Product $record): string => match (true) {
                        $record->stock > 0 && $record->is_active => 'Available for sale',
                        $record->stock === 0 => 'Out of stock',
                        !$record->is_active => 'Product inactive',
                        default => 'Status unknown',
                    }),

                // Image column with fallback
                Tables\Columns\ImageColumn::make('image')
                    ->disk('public')
                    ->defaultImageUrl(url('/images/placeholder.png'))
                    ->circular()
                    ->size(60)
                    ->checkFileExistence(false), // Performance optimization

                // Layout stack for mobile
                Tables\Columns\Layout\Stack::make([
                    Tables\Columns\ImageColumn::make('image')
                        ->size(40),
                    Tables\Columns\TextColumn::make('name')
                        ->weight('bold')
                        ->searchable(),
                    Tables\Columns\Layout\Split::make([
                        Tables\Columns\TextColumn::make('price')
                            ->money('usd')
                            ->color('success'),
                        Tables\Columns\TextColumn::make('stock')
                            ->badge(),
                    ]),
                ])
                    ->space(2)
                    ->collapsible()
                    ->hiddenFrom('md'),
            ])
            ->contentGrid([
                'md' => 2,
                'xl' => 3,
            ])
            ->extremePaginationLinks();
    }
}
```

### Pattern 3: Optimized Bulk Actions

```php
<?php

namespace App\Filament\Resources;

use Filament\Tables;
use Filament\Tables\Table;
use Filament\Notifications\Notification;
use App\Jobs\ProcessBulkProductUpdate;
use App\Jobs\ExportProducts;
use Illuminate\Database\Eloquent\Collection;

class ProductResource extends Resource
{
    public static function table(Table $table): Table
    {
        return $table
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    // Standard delete with chunk processing
                    Tables\Actions\DeleteBulkAction::make()
                        ->action(function (Collection $records) {
                            // Process in chunks to avoid memory issues
                            $records->chunk(100)->each(function ($chunk) {
                                $chunk->each->delete();
                            });

                            Notification::make()
                                ->success()
                                ->title('Products deleted')
                                ->body("{$records->count()} products have been deleted")
                                ->send();
                        }),

                    // Bulk update with queue
                    Tables\Actions\BulkAction::make('update_prices')
                        ->label('Update Prices')
                        ->icon('heroicon-o-currency-dollar')
                        ->form([
                            Forms\Components\Select::make('action')
                                ->options([
                                    'increase' => 'Increase',
                                    'decrease' => 'Decrease',
                                    'set' => 'Set to',
                                ])
                                ->required()
                                ->reactive(),

                            Forms\Components\TextInput::make('value')
                                ->numeric()
                                ->required()
                                ->suffix(fn ($get) =>
                                    $get('action') === 'set' ? 'USD' : '%'
                                ),
                        ])
                        ->action(function (Collection $records, array $data) {
                            // Dispatch to queue for large operations
                            if ($records->count() > 100) {
                                ProcessBulkProductUpdate::dispatch(
                                    $records->pluck('id')->toArray(),
                                    $data
                                );

                                Notification::make()
                                    ->success()
                                    ->title('Price update queued')
                                    ->body('Updates will be processed in the background')
                                    ->send();
                            } else {
                                // Process immediately for small batches
                                self::processPriceUpdates($records, $data);

                                Notification::make()
                                    ->success()
                                    ->title('Prices updated')
                                    ->body("{$records->count()} products updated")
                                    ->send();
                            }
                        })
                        ->deselectRecordsAfterCompletion(),

                    // Bulk export with queue
                    Tables\Actions\BulkAction::make('export')
                        ->label('Export Selected')
                        ->icon('heroicon-o-arrow-down-tray')
                        ->form([
                            Forms\Components\Select::make('format')
                                ->options([
                                    'csv' => 'CSV',
                                    'xlsx' => 'Excel',
                                    'json' => 'JSON',
                                ])
                                ->default('csv')
                                ->required(),

                            Forms\Components\CheckboxList::make('columns')
                                ->options([
                                    'name' => 'Name',
                                    'sku' => 'SKU',
                                    'price' => 'Price',
                                    'cost' => 'Cost',
                                    'stock' => 'Stock',
                                    'category' => 'Category',
                                ])
                                ->default(['name', 'sku', 'price', 'stock'])
                                ->required()
                                ->columns(2),
                        ])
                        ->action(function (Collection $records, array $data) {
                            $filename = 'products-' . now()->format('Y-m-d-His') . '.' . $data['format'];

                            ExportProducts::dispatch(
                                $records->pluck('id')->toArray(),
                                $data['columns'],
                                $data['format'],
                                auth()->id(),
                                $filename
                            );

                            Notification::make()
                                ->success()
                                ->title('Export started')
                                ->body('You will be notified when the export is ready')
                                ->send();
                        })
                        ->requiresConfirmation(),

                    // Bulk categorize
                    Tables\Actions\BulkAction::make('categorize')
                        ->label('Change Category')
                        ->icon('heroicon-o-tag')
                        ->form([
                            Forms\Components\Select::make('category_id')
                                ->label('Category')
                                ->relationship('category', 'name')
                                ->required()
                                ->searchable()
                                ->preload(),
                        ])
                        ->action(function (Collection $records, array $data) {
                            $records->each->update(['category_id' => $data['category_id']]);

                            // Clear cache
                            cache()->tags(['products', 'categories'])->flush();

                            Notification::make()
                                ->success()
                                ->title('Category updated')
                                ->send();
                        })
                        ->deselectRecordsAfterCompletion(),

                    // Bulk activate/deactivate
                    Tables\Actions\BulkAction::make('toggle_status')
                        ->label('Activate/Deactivate')
                        ->icon('heroicon-o-arrows-right-left')
                        ->form([
                            Forms\Components\Radio::make('status')
                                ->options([
                                    'activate' => 'Activate all selected',
                                    'deactivate' => 'Deactivate all selected',
                                ])
                                ->required(),
                        ])
                        ->action(function (Collection $records, array $data) {
                            $isActive = $data['status'] === 'activate';

                            \DB::transaction(function () use ($records, $isActive) {
                                $records->each->update(['is_active' => $isActive]);

                                // Log bulk action
                                activity()
                                    ->withProperties([
                                        'count' => $records->count(),
                                        'active' => $isActive,
                                    ])
                                    ->log('Bulk status update');
                            });

                            Notification::make()
                                ->success()
                                ->title('Status updated')
                                ->body("{$records->count()} products " .
                                    ($isActive ? 'activated' : 'deactivated'))
                                ->send();
                        })
                        ->deselectRecordsAfterCompletion()
                        ->color(fn (array $data) =>
                            ($data['status'] ?? '') === 'activate' ? 'success' : 'danger'
                        ),
                ]),
            ])
            ->selectCurrentPageOnly()
            ->deselectAllRecordsWhenFiltered(false);
    }

    protected static function processPriceUpdates(Collection $records, array $data): void
    {
        \DB::transaction(function () use ($records, $data) {
            foreach ($records as $record) {
                $newPrice = match ($data['action']) {
                    'increase' => $record->price * (1 + $data['value'] / 100),
                    'decrease' => $record->price * (1 - $data['value'] / 100),
                    'set' => $data['value'],
                };

                $record->update(['price' => round($newPrice, 2)]);
            }
        });
    }
}
```

### Pattern 4: Advanced Filtering with Performance

```php
<?php

namespace App\Filament\Resources;

use Filament\Tables;
use Filament\Tables\Table;
use Filament\Tables\Filters\QueryBuilder;
use Filament\Tables\Filters\QueryBuilder\Constraints;
use Illuminate\Database\Eloquent\Builder;

class OrderResource extends Resource
{
    public static function table(Table $table): Table
    {
        return $table
            ->filters([
                // Multi-select filter with search
                Tables\Filters\SelectFilter::make('customer')
                    ->relationship('customer', 'name')
                    ->multiple()
                    ->searchable()
                    ->preload()
                    ->optionsLimit(50), // Performance: limit options

                // Status filter with badges
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'pending' => 'Pending',
                        'processing' => 'Processing',
                        'completed' => 'Completed',
                        'cancelled' => 'Cancelled',
                    ])
                    ->multiple()
                    ->default(['pending', 'processing']),

                // Efficient date range filter
                Tables\Filters\Filter::make('date_range')
                    ->form([
                        Forms\Components\DatePicker::make('created_from')
                            ->label('From')
                            ->native(false)
                            ->placeholder('Select start date'),
                        Forms\Components\DatePicker::make('created_until')
                            ->label('To')
                            ->native(false)
                            ->placeholder('Select end date'),
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

                // Numeric range filter
                Tables\Filters\Filter::make('total')
                    ->form([
                        Forms\Components\Grid::make(2)
                            ->schema([
                                Forms\Components\TextInput::make('total_from')
                                    ->numeric()
                                    ->prefix('$')
                                    ->placeholder('Min'),
                                Forms\Components\TextInput::make('total_to')
                                    ->numeric()
                                    ->prefix('$')
                                    ->placeholder('Max'),
                            ]),
                    ])
                    ->query(function (Builder $query, array $data): Builder {
                        return $query
                            ->when(
                                $data['total_from'],
                                fn (Builder $q, $amount) => $q->where('total', '>=', $amount)
                            )
                            ->when(
                                $data['total_to'],
                                fn (Builder $q, $amount) => $q->where('total', '<=', $amount)
                            );
                    })
                    ->indicateUsing(function (array $data): ?string {
                        if (!$data['total_from'] && !$data['total_to']) {
                            return null;
                        }

                        if ($data['total_from'] && $data['total_to']) {
                            return '$' . number_format($data['total_from']) . ' - $' . number_format($data['total_to']);
                        }

                        if ($data['total_from']) {
                            return 'Min: $' . number_format($data['total_from']);
                        }

                        return 'Max: $' . number_format($data['total_to']);
                    }),

                // Ternary filter for boolean fields
                Tables\Filters\TernaryFilter::make('is_gift')
                    ->label('Gift Orders')
                    ->placeholder('All orders')
                    ->trueLabel('Gift orders only')
                    ->falseLabel('Regular orders only')
                    ->queries(
                        true: fn (Builder $query) => $query->where('is_gift', true),
                        false: fn (Builder $query) => $query->where('is_gift', false),
                        blank: fn (Builder $query) => $query,
                    )
                    ->native(false),

                // Custom filter with complex logic
                Tables\Filters\Filter::make('high_value_customers')
                    ->toggle()
                    ->query(fn (Builder $query): Builder =>
                        $query->whereHas('customer', function (Builder $q) {
                            $q->whereHas('orders', function (Builder $q) {
                                $q->selectRaw('SUM(total) as customer_total')
                                    ->groupBy('customer_id')
                                    ->havingRaw('SUM(total) > 10000');
                            });
                        })
                    ),

                // Relationship filter with counts
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

                // Query builder for advanced filtering
                Tables\Filters\QueryBuilder::make()
                    ->constraints([
                        Constraints\TextConstraint::make('number'),
                        Constraints\NumberConstraint::make('total'),
                        Constraints\DateConstraint::make('created_at'),
                        Constraints\SelectConstraint::make('status')
                            ->options([
                                'pending' => 'Pending',
                                'processing' => 'Processing',
                                'completed' => 'Completed',
                                'cancelled' => 'Cancelled',
                            ]),
                        Constraints\BooleanConstraint::make('is_gift'),
                        Constraints\RelationshipConstraint::make('customer')
                            ->selectable()
                            ->multiple()
                            ->searchable()
                            ->preload(),
                    ])
                    ->constraintPickerColumns(2),
            ])
            ->filtersLayout(Tables\Enums\FiltersLayout::AboveContentCollapsible)
            ->persistFiltersInSession()
            ->filtersTriggerAction(
                fn (Tables\Actions\Action $action) => $action
                    ->button()
                    ->label('Filters')
            );
    }
}
```

### Pattern 5: Export with Queue and Progress

```php
<?php

namespace App\Filament\Resources\ProductResource\Pages;

use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
use Filament\Forms;
use App\Jobs\ExportProducts;

class ListProducts extends ListRecords
{
    protected static string $resource = ProductResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),

            Actions\Action::make('export')
                ->label('Export')
                ->icon('heroicon-o-arrow-down-tray')
                ->form([
                    Forms\Components\Select::make('format')
                        ->label('File Format')
                        ->options([
                            'csv' => 'CSV',
                            'xlsx' => 'Excel (XLSX)',
                            'json' => 'JSON',
                            'pdf' => 'PDF',
                        ])
                        ->default('xlsx')
                        ->required()
                        ->native(false),

                    Forms\Components\CheckboxList::make('columns')
                        ->label('Columns to Export')
                        ->options([
                            'id' => 'ID',
                            'name' => 'Name',
                            'sku' => 'SKU',
                            'category' => 'Category',
                            'price' => 'Price',
                            'cost' => 'Cost',
                            'stock' => 'Stock',
                            'is_active' => 'Status',
                            'created_at' => 'Created Date',
                        ])
                        ->default(['name', 'sku', 'category', 'price', 'stock'])
                        ->required()
                        ->columns(3)
                        ->searchable(),

                    Forms\Components\Toggle::make('include_images')
                        ->label('Include Product Images')
                        ->helperText('Only available for Excel format')
                        ->visible(fn ($get) => $get('format') === 'xlsx'),

                    Forms\Components\Toggle::make('apply_filters')
                        ->label('Apply Current Filters')
                        ->helperText('Export only filtered results')
                        ->default(false),

                    Forms\Components\Radio::make('scope')
                        ->label('Export Scope')
                        ->options([
                            'all' => 'All Products',
                            'filtered' => 'Filtered Products',
                            'visible' => 'Visible on Current Page',
                        ])
                        ->default('filtered')
                        ->required(),
                ])
                ->action(function (array $data, $livewire) {
                    $query = static::getResource()::getEloquentQuery();

                    // Apply filters if requested
                    if ($data['apply_filters']) {
                        $tableFilters = $livewire->tableFilters;
                        // Apply each filter to query
                        foreach ($tableFilters as $filter => $value) {
                            if ($value) {
                                // Apply filter logic
                            }
                        }
                    }

                    $productIds = $query->pluck('id')->toArray();

                    // Dispatch export job
                    $filename = 'products-export-' . now()->format('Y-m-d-His') . '.' . $data['format'];

                    ExportProducts::dispatch(
                        productIds: $productIds,
                        columns: $data['columns'],
                        format: $data['format'],
                        userId: auth()->id(),
                        filename: $filename,
                        includeImages: $data['include_images'] ?? false
                    );

                    Notification::make()
                        ->success()
                        ->title('Export started')
                        ->body('You will receive a notification when your export is ready to download.')
                        ->persistent()
                        ->send();
                })
                ->modalWidth('2xl')
                ->slideOver(),
        ];
    }
}
```

```php
<?php

namespace App\Jobs;

use App\Models\User;
use App\Models\Product;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Storage;
use Filament\Notifications\Notification;
use Filament\Notifications\Actions\Action;

class ExportProducts implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        public array $productIds,
        public array $columns,
        public string $format,
        public int $userId,
        public string $filename,
        public bool $includeImages = false
    ) {}

    public function handle(): void
    {
        $products = Product::whereIn('id', $this->productIds)
            ->with(['category'])
            ->get();

        $data = [];
        $totalProducts = $products->count();
        $processed = 0;

        foreach ($products as $product) {
            $row = [];

            foreach ($this->columns as $column) {
                $row[$column] = match($column) {
                    'category' => $product->category?->name,
                    'is_active' => $product->is_active ? 'Active' : 'Inactive',
                    default => $product->$column,
                };
            }

            $data[] = $row;
            $processed++;

            // Update progress every 100 items
            if ($processed % 100 === 0) {
                $this->updateProgress($processed, $totalProducts);
            }
        }

        // Generate file based on format
        $path = $this->generateFile($data, $this->format);

        // Send notification with download link
        $user = User::find($this->userId);

        Notification::make()
            ->success()
            ->title('Export completed')
            ->body("{$totalProducts} products exported successfully.")
            ->actions([
                Action::make('download')
                    ->button()
                    ->url(Storage::url($path))
                    ->openUrlInNewTab(),
            ])
            ->persistent()
            ->sendToDatabase($user);
    }

    protected function generateFile(array $data, string $format): string
    {
        $path = "exports/{$this->filename}";

        switch ($format) {
            case 'csv':
                return $this->generateCsv($data, $path);
            case 'xlsx':
                return $this->generateExcel($data, $path);
            case 'json':
                return $this->generateJson($data, $path);
            case 'pdf':
                return $this->generatePdf($data, $path);
        }
    }

    protected function generateCsv(array $data, string $path): string
    {
        $csv = \League\Csv\Writer::createFromPath(storage_path("app/{$path}"), 'w+');

        // Add header
        if (count($data) > 0) {
            $csv->insertOne(array_keys($data[0]));
        }

        // Add data
        $csv->insertAll($data);

        return $path;
    }

    protected function generateExcel(array $data, string $path): string
    {
        // Use Laravel Excel or similar package
        \Excel::store(new ProductsExport($data, $this->includeImages), $path);

        return $path;
    }

    protected function generateJson(array $data, string $path): string
    {
        Storage::put($path, json_encode($data, JSON_PRETTY_PRINT));

        return $path;
    }

    protected function updateProgress(int $processed, int $total): void
    {
        cache()->put(
            "export.{$this->userId}.progress",
            [
                'processed' => $processed,
                'total' => $total,
                'percentage' => round(($processed / $total) * 100),
            ],
            now()->addHour()
        );
    }
}
```

### Pattern 6: Import with Validation and Progress

```php
<?php

namespace App\Filament\Resources\ProductResource\Pages;

use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
use Filament\Forms;
use Filament\Notifications\Notification;
use App\Jobs\ImportProducts;

class ListProducts extends ListRecords
{
    protected function getHeaderActions(): array
    {
        return [
            Actions\Action::make('import')
                ->label('Import')
                ->icon('heroicon-o-arrow-up-tray')
                ->form([
                    Forms\Components\FileUpload::make('file')
                        ->label('Import File')
                        ->required()
                        ->acceptedFileTypes([
                            'text/csv',
                            'application/vnd.ms-excel',
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        ])
                        ->maxSize(10240) // 10MB
                        ->directory('imports')
                        ->storeFiles(false) // Handle manually
                        ->helperText('Upload a CSV or Excel file with product data'),

                    Forms\Components\Toggle::make('update_existing')
                        ->label('Update Existing Products')
                        ->helperText('Update products if SKU already exists')
                        ->default(true),

                    Forms\Components\Toggle::make('validate_only')
                        ->label('Validate Only')
                        ->helperText('Check for errors without importing')
                        ->default(false),

                    Forms\Components\Select::make('duplicate_handling')
                        ->label('Duplicate Handling')
                        ->options([
                            'skip' => 'Skip duplicates',
                            'update' => 'Update duplicates',
                            'error' => 'Report as error',
                        ])
                        ->default('update')
                        ->required(),
                ])
                ->action(function (array $data) {
                    $file = $data['file'];

                    // Store file
                    $path = Storage::disk('local')->putFile('imports', $file);

                    // Dispatch import job
                    ImportProducts::dispatch(
                        filePath: $path,
                        userId: auth()->id(),
                        updateExisting: $data['update_existing'],
                        validateOnly: $data['validate_only'],
                        duplicateHandling: $data['duplicate_handling']
                    );

                    Notification::make()
                        ->success()
                        ->title('Import started')
                        ->body('You will be notified when the import is complete.')
                        ->send();
                })
                ->modalWidth('lg'),
        ];
    }
}
```

```php
<?php

namespace App\Jobs;

use App\Models\Product;
use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
use Filament\Notifications\Notification;

class ImportProducts implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $timeout = 3600; // 1 hour

    public function __construct(
        public string $filePath,
        public int $userId,
        public bool $updateExisting = true,
        public bool $validateOnly = false,
        public string $duplicateHandling = 'update'
    ) {}

    public function handle(): void
    {
        $rows = $this->readCsv(Storage::disk('local')->path($this->filePath));

        $totalRows = count($rows);
        $processed = 0;
        $created = 0;
        $updated = 0;
        $skipped = 0;
        $errors = [];

        foreach ($rows as $index => $row) {
            $result = $this->processRow($row, $index + 2); // +2 for header and 1-based index

            if ($result['status'] === 'error') {
                $errors[] = $result['message'];
                $skipped++;
            } elseif ($result['status'] === 'created') {
                $created++;
            } elseif ($result['status'] === 'updated') {
                $updated++;
            } else {
                $skipped++;
            }

            $processed++;

            // Update progress
            if ($processed % 50 === 0) {
                $this->updateProgress($processed, $totalRows, $created, $updated, $skipped);
            }
        }

        // Send completion notification
        $this->sendCompletionNotification($created, $updated, $skipped, $errors);

        // Clean up
        Storage::disk('local')->delete($this->filePath);
    }

    protected function processRow(array $row, int $lineNumber): array
    {
        // Validate row
        $validator = Validator::make($row, [
            'sku' => 'required|string|max:50',
            'name' => 'required|string|max:255',
            'price' => 'required|numeric|min:0',
            'stock' => 'required|integer|min:0',
            'category_id' => 'required|exists:categories,id',
        ]);

        if ($validator->fails()) {
            return [
                'status' => 'error',
                'message' => "Line {$lineNumber}: " . implode(', ', $validator->errors()->all()),
            ];
        }

        if ($this->validateOnly) {
            return ['status' => 'validated'];
        }

        // Check for duplicate
        $existing = Product::where('sku', $row['sku'])->first();

        if ($existing) {
            if ($this->duplicateHandling === 'skip') {
                return ['status' => 'skipped'];
            }

            if ($this->duplicateHandling === 'error') {
                return [
                    'status' => 'error',
                    'message' => "Line {$lineNumber}: SKU {$row['sku']} already exists",
                ];
            }

            // Update
            $existing->update($row);
            return ['status' => 'updated'];
        }

        // Create
        Product::create($row);
        return ['status' => 'created'];
    }

    protected function readCsv(string $path): array
    {
        $csv = \League\Csv\Reader::createFromPath($path, 'r');
        $csv->setHeaderOffset(0);

        return iterator_to_array($csv->getRecords());
    }

    protected function updateProgress(int $processed, int $total, int $created, int $updated, int $skipped): void
    {
        cache()->put(
            "import.{$this->userId}.progress",
            [
                'processed' => $processed,
                'total' => $total,
                'created' => $created,
                'updated' => $updated,
                'skipped' => $skipped,
                'percentage' => round(($processed / $total) * 100),
            ],
            now()->addHour()
        );
    }

    protected function sendCompletionNotification(int $created, int $updated, int $skipped, array $errors): void
    {
        $user = User::find($this->userId);

        $notification = Notification::make()
            ->title('Import completed')
            ->body("Created: {$created}, Updated: {$updated}, Skipped: {$skipped}");

        if (count($errors) > 0) {
            $notification
                ->warning()
                ->body($notification->getBody() . "\n\n" . count($errors) . " errors occurred.");
        } else {
            $notification->success();
        }

        $notification->sendToDatabase($user);
    }
}
```

## Advanced Patterns

### Pattern 7: Table Summarizers

```php
<?php

use Filament\Tables;
use Filament\Tables\Table;

public static function table(Table $table): Table
{
    return $table
        ->columns([
            Tables\Columns\TextColumn::make('product.name')
                ->searchable()
                ->sortable(),

            Tables\Columns\TextColumn::make('quantity')
                ->numeric()
                ->summarize([
                    Tables\Columns\Summarizers\Sum::make()
                        ->label('Total Quantity'),

                    Tables\Columns\Summarizers\Average::make()
                        ->label('Avg Qty')
                        ->numeric(decimalPlaces: 1),

                    Tables\Columns\Summarizers\Range::make()
                        ->label('Range'),
                ]),

            Tables\Columns\TextColumn::make('unit_price')
                ->money('usd')
                ->summarize([
                    Tables\Columns\Summarizers\Average::make()
                        ->money('usd')
                        ->label('Avg Price'),
                ]),

            Tables\Columns\TextColumn::make('subtotal')
                ->money('usd')
                ->summarize([
                    Tables\Columns\Summarizers\Sum::make()
                        ->money('usd')
                        ->label('Total'),

                    Tables\Columns\Summarizers\Average::make()
                        ->money('usd')
                        ->label('Average'),

                    Tables\Columns\Summarizers\Count::make()
                        ->label('Items'),
                ]),

            Tables\Columns\TextColumn::make('tax')
                ->money('usd')
                ->summarize([
                    Tables\Columns\Summarizers\Sum::make()
                        ->money('usd')
                        ->using(fn ($query) =>
                            $query->sum('tax')
                        ),
                ]),
        ])
        ->defaultGroup('product.category.name')
        ->groups([
            'product.category.name' => Tables\Grouping\Group::make('Category')
                ->collapsible(),
            'created_at' => Tables\Grouping\Group::make('Date')
                ->date()
                ->collapsible(),
        ]);
}
```

### Pattern 8: Searchable with Multiple Columns

```php
<?php

public static function table(Table $table): Table
{
    return $table
        ->columns([
            Tables\Columns\TextColumn::make('name')
                ->searchable(['name', 'sku', 'description'])
                ->sortable()
                ->weight('bold'),

            Tables\Columns\TextColumn::make('customer.name')
                ->searchable(query: function (Builder $query, string $search): Builder {
                    return $query->whereHas('customer', function (Builder $q) use ($search) {
                        $q->where('name', 'like', "%{$search}%")
                          ->orWhere('email', 'like', "%{$search}%")
                          ->orWhere('phone', 'like', "%{$search}%");
                    });
                })
                ->sortable(),
        ])
        ->persistSearchInSession()
        ->searchDebounce('500ms')
        ->searchOnBlur();
}
```

## Testing Strategies

```php
<?php

namespace Tests\Feature\Filament;

use App\Filament\Resources\ProductResource;
use App\Models\Product;
use App\Models\User;
use Livewire\Livewire;
use Tests\TestCase;

class ProductTableTest extends TestCase
{
    public function test_table_loads_efficiently(): void
    {
        Product::factory()->count(100)->create();

        $this->actingAs(User::factory()->create());

        \DB::enableQueryLog();

        Livewire::test(ProductResource\Pages\ListProducts::class)
            ->assertSuccessful();

        // Should use eager loading, not exceed 5 queries
        expect(count(\DB::getQueryLog()))->toBeLessThan(5);
    }

    public function test_bulk_action_processes_records(): void
    {
        $products = Product::factory()->count(10)->create(['is_active' => false]);

        Livewire::test(ProductResource\Pages\ListProducts::class)
            ->callTableBulkAction('activate', $products);

        expect(Product::where('is_active', true)->count())->toBe(10);
    }
}
```

## Common Pitfalls

### Pitfall 1: N+1 Queries in Tables

```php
// WRONG: Causes N+1
Tables\Columns\TextColumn::make('author.name'),

// CORRECT: Eager load
public static function getEloquentQuery(): Builder
{
    return parent::getEloquentQuery()->with('author');
}
```

### Pitfall 2: Not Chunking Large Exports

```php
// WRONG: Memory issues
$products->each->export();

// CORRECT: Use chunks
$products->chunk(100)->each(fn ($chunk) => process($chunk));
```

## Best Practices

1. **Always eager load** relationships used in table columns
2. **Use select()** to load only required columns
3. **Implement caching** for expensive calculations
4. **Process bulk actions** in chunks for large datasets
5. **Queue long-running operations** like exports
6. **Add progress indicators** for background jobs
7. **Persist filters** for better UX
8. **Use database indexes** for searchable columns
9. **Implement proper validation** in imports
10. **Monitor query performance** with logging

## Resources

- **Filament Tables**: https://filamentphp.com/docs/tables/overview
- **Laravel Query Optimization**: https://laravel.com/docs/eloquent
- **Queue Jobs**: https://laravel.com/docs/queues
- **Laravel Excel**: https://laravel-excel.com
