---
name: filament-forms-advanced
description: Master advanced Filament 4 form patterns including complex layouts, conditional fields, repeaters, builders, custom fields, file uploads, wizards, and real-time validation. Use when building sophisticated data entry interfaces.
category: filament
tags: [filament, forms, validation, layouts, custom-fields]
related_skills: [filament-resource-patterns, livewire-forms-validation, laravel-api-design]
---

# Filament Forms Advanced

Advanced Filament 4 form patterns for complex data entry interfaces.

## Pattern Files

Load specific patterns based on your needs:

| Pattern | File | Use Case |
|---------|------|----------|
| Form Layouts | `form-layouts.md` | Grid, Section, Tabs, Split, responsive designs |
| Conditional Fields | `conditional-fields.md` | visible(), hidden(), reactive(), live() |
| Repeaters & Builders | `repeaters-builders.md` | Dynamic content, relationships, calculations |
| File Uploads | `file-uploads.md` | Images, documents, S3, validation |
| Wizard Forms | `wizard-forms.md` | Multi-step workflows, step validation |

## Quick Reference

### Layout Components
```php
Forms\Components\Grid::make(2)->schema([...]);
Forms\Components\Section::make('Title')->schema([...])->collapsible();
Forms\Components\Tabs::make('Label')->tabs([...])->persistTabInQueryString();
Forms\Components\Split::make([...])->from('md');
```

### Conditional Visibility
```php
Forms\Components\TextInput::make('field')
    ->visible(fn (Get $get): bool => $get('type') === 'value')
    ->required(fn (Get $get): bool => $get('type') === 'value');
```

### Reactive Fields
```php
Forms\Components\Select::make('category')
    ->reactive()
    ->afterStateUpdated(fn (Set $set) => $set('subcategory', null));
```

### Live Updates
```php
Forms\Components\TextInput::make('title')
    ->live(onBlur: true)
    ->afterStateUpdated(fn ($state, Set $set) => $set('slug', Str::slug($state)));
```

### Repeater
```php
Forms\Components\Repeater::make('items')
    ->relationship()
    ->schema([...])
    ->reorderable()
    ->collapsible()
    ->cloneable();
```

### File Upload
```php
Forms\Components\FileUpload::make('image')
    ->image()
    ->imageEditor()
    ->directory('uploads')
    ->maxSize(2048);
```

### Wizard
```php
Forms\Components\Wizard::make([
    Wizard\Step::make('Step 1')->schema([...])->icon('heroicon-o-user'),
    Wizard\Step::make('Step 2')->schema([...]),
])->persistStepInQueryString();
```

## Best Practices

1. Use `live()` with debounce for real-time validation
2. Always add `dehydrated()` to disabled fields that should save
3. Clear dependent fields in `afterStateUpdated`
4. Use sections and tabs to organize complex forms
5. Validate file uploads with size and type restrictions
6. Use computed totals in repeaters for calculations
7. Provide meaningful default values
8. Test form validation thoroughly
