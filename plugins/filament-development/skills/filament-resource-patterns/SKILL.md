---
name: filament-resource-patterns
description: Master Filament 5 resource patterns including form schemas, table columns, filters, actions, relation managers, and multi-tenant resources. Use when building admin panels, CRUD interfaces, or data management systems.
category: filament
tags: [filament, resources, crud, admin-panel, forms, tables]
related_skills: [filament-forms-advanced, filament-tables-optimization, filament-multi-tenancy]
---

# Filament Resource Patterns

Comprehensive patterns for Filament 5 resources, forms, tables, and actions.

## Pattern Files

Load specific patterns based on your needs:

| Pattern | File | Use Case |
|---------|------|----------|
| Resource Structure | [resource-structure.md](resource-structure.md) | Complete resource class, navigation, pages |
| Form Schemas | [form-schemas.md](form-schemas.md) | Advanced form components, validation |
| Table Columns | [table-columns.md](table-columns.md) | Column types, computed state, layouts |
| Actions & Bulk | [actions-bulk.md](actions-bulk.md) | Row actions, bulk operations, forms |
| Relation Managers | [relation-managers.md](relation-managers.md) | HasMany, BelongsToMany, pivot data |

## Quick Reference

### Basic Resource
```php
class ProductResource extends Resource
{
    protected static ?string $model = Product::class;
    protected static ?string $navigationIcon = 'heroicon-o-shopping-bag';
    protected static ?string $navigationGroup = 'Shop';
    protected static ?string $recordTitleAttribute = 'name';

    public static function form(Form $form): Form { ... }
    public static function table(Table $table): Table { ... }
}
```

### Form with Sections
```php
Forms\Components\Section::make('Product Information')
    ->schema([
        Forms\Components\TextInput::make('name')->required(),
        Forms\Components\Select::make('category_id')
            ->relationship('category', 'name')
            ->searchable()
            ->preload(),
    ])
    ->columns(2),
```

### Table Columns
```php
Tables\Columns\TextColumn::make('name')
    ->searchable()
    ->sortable()
    ->badge()
    ->color(fn ($state) => match($state) {...}),

Tables\Columns\TextColumn::make('price')
    ->money('usd')
    ->summarize(Sum::make()->money('usd')),
```

### Actions
```php
Tables\Actions\Action::make('approve')
    ->icon('heroicon-o-check')
    ->requiresConfirmation()
    ->form([...])
    ->action(fn (Model $record, array $data) => ...),
```

### Bulk Actions
```php
Tables\Actions\BulkAction::make('activate')
    ->icon('heroicon-o-check-circle')
    ->action(fn (Collection $records) => $records->each->update(['is_active' => true]))
    ->deselectRecordsAfterCompletion(),
```

### Navigation Badge
```php
public static function getNavigationBadge(): ?string
{
    return static::getModel()::where('status', 'pending')->count();
}
```

## Best Practices

1. Always eager load relationships used in tables
2. Use sections and tabs to organize complex forms
3. Implement global search for better UX
4. Add navigation badges for important counts
5. Use computed properties in table columns
6. Implement authorization with policies
7. Configure proper validation rules
8. Use relation managers for related models
9. Customize search with multiple attributes
10. Test all CRUD operations thoroughly
