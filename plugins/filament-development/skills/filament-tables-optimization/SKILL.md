---
name: filament-tables-optimization
description: Master Filament 5 table optimization including query performance, custom columns, bulk actions, filters, exports, imports, summarizers, and pagination strategies. Use when building high-performance data tables and list views.
category: filament
tags: [filament, tables, performance, optimization, export, import]
related_skills: [filament-resource-patterns, laravel-caching-strategies, eloquent-patterns]
---

# Filament Tables Optimization

High-performance table patterns for Filament 5.

## Pattern Files

Load specific patterns based on your needs:

| Pattern | File | Use Case |
|---------|------|----------|
| Query Optimization | [query-optimization.md](query-optimization.md) | Eager loading, efficient queries, indexes |
| Custom Columns | [custom-columns.md](custom-columns.md) | Computed state, toggles, summarizers |
| Bulk Operations | [bulk-operations.md](bulk-operations.md) | Bulk actions, queued processing |
| Advanced Filters | [filters-advanced.md](filters-advanced.md) | Date ranges, relationships, query builder |
| Export & Import | [export-import.md](export-import.md) | Queued export/import with progress |

## Quick Reference

### Eager Loading
```php
public static function getEloquentQuery(): Builder
{
    return parent::getEloquentQuery()
        ->with(['customer:id,name', 'items.product:id,name'])
        ->withCount('items')
        ->withSum('items', 'subtotal');
}
```

### Computed Column
```php
Tables\Columns\TextColumn::make('profit_margin')
    ->state(fn (Model $record): float =>
        (($record->price - $record->cost) / $record->price) * 100
    )
    ->formatStateUsing(fn (float $state) => number_format($state, 1) . '%')
    ->color(fn (float $state) => $state < 20 ? 'danger' : 'success'),
```

### Toggle Column
```php
Tables\Columns\ToggleColumn::make('is_active')
    ->afterStateUpdated(function (Model $record, $state) {
        cache()->forget("product.{$record->id}");
    }),
```

### Summarizers
```php
Tables\Columns\TextColumn::make('total')
    ->money('usd')
    ->summarize([
        Sum::make()->money('usd'),
        Average::make()->money('usd'),
    ]),
```

### Bulk Action
```php
Tables\Actions\BulkAction::make('export')
    ->icon('heroicon-o-arrow-down-tray')
    ->action(function (Collection $records) {
        ExportJob::dispatch($records->pluck('id')->toArray());
    }),
```

### Date Range Filter
```php
Tables\Filters\Filter::make('created_at')
    ->form([
        Forms\Components\DatePicker::make('from'),
        Forms\Components\DatePicker::make('until'),
    ])
    ->query(fn (Builder $query, array $data) =>
        $query->when($data['from'], fn ($q, $d) => $q->whereDate('created_at', '>=', $d))
    ),
```

### Table Options
```php
return $table
    ->persistSearchInSession()
    ->persistFiltersInSession()
    ->paginationPageOptions([10, 25, 50, 100])
    ->deferLoading()
    ->poll('30s');
```

## Performance Rules

### Max ~10 Visible Columns
Tables with more than 10 visible columns create poor UX and performance issues. Use `->toggleable(isToggledHiddenByDefault: true)` for less important columns like `created_at`, `updated_at`, `id`.

### Always Defer Loading
Every table should use `->deferLoading()` to load data via AJAX after initial page render. This dramatically improves page load time.

### Searchable for Large Option Lists
Select, CheckboxList, and Radio components with 10+ options MUST have `->searchable()` for usability.

### Use Heroicon Enum for Icons
```php
// Prefer enum over string
use Filament\Support\Icons\Heroicon;

Tables\Actions\BulkAction::make('export')
    ->icon(Heroicon::ArrowDownTray),
```

### Use FontWeight Enum
```php
use Filament\Support\Enums\FontWeight;

Tables\Columns\TextColumn::make('name')
    ->weight(FontWeight::Bold),
```

## Best Practices

1. Always eager load relationships used in columns
2. Use `withCount()` and `withSum()` for aggregates
3. Process bulk actions in chunks for large datasets
4. Queue long-running export/import operations
5. Add database indexes for searchable columns
6. Use `deferLoading()` for faster initial render
7. Persist filters and search in session
8. Limit options in relationship filters
9. Use summarizers for aggregate data display
10. Monitor query performance with debugbar
11. Keep visible columns under 10, use toggleable for extras
12. Use `Heroicon::*` enum instead of string icons
13. Use `FontWeight::*` enum instead of string weights
