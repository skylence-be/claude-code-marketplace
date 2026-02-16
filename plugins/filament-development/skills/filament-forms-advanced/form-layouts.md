# Form Layouts

Filament 5 form layout components for organizing complex forms.

## Grid Layout

```php
use Filament\Forms;

Forms\Components\Grid::make(3)
    ->schema([
        Forms\Components\TextInput::make('first_name')
            ->required(),

        Forms\Components\TextInput::make('middle_name'),

        Forms\Components\TextInput::make('last_name')
            ->required(),
    ]);

// Responsive grid
Forms\Components\Grid::make([
    'default' => 1,
    'sm' => 2,
    'lg' => 3,
])
    ->schema([
        // Fields adapt to screen size
    ]);
```

## Section Component

```php
Forms\Components\Section::make('Personal Information')
    ->description('Enter your personal details')
    ->schema([
        Forms\Components\TextInput::make('name')->required(),
        Forms\Components\TextInput::make('email')->email()->required(),
        Forms\Components\DatePicker::make('birthdate'),
    ])
    ->columns(2)
    ->collapsible()
    ->collapsed(false)
    ->icon('heroicon-o-user');

// Aside section (sidebar style)
Forms\Components\Section::make('Status')
    ->schema([
        Forms\Components\Toggle::make('is_active'),
    ])
    ->aside();
```

## Tabs Layout

```php
Forms\Components\Tabs::make('Product')
    ->tabs([
        Forms\Components\Tabs\Tab::make('Basic Info')
            ->icon('heroicon-o-information-circle')
            ->schema([
                Forms\Components\TextInput::make('name')->required(),
                Forms\Components\Textarea::make('description'),
            ]),

        Forms\Components\Tabs\Tab::make('Pricing')
            ->icon('heroicon-o-currency-dollar')
            ->badge('New')
            ->schema([
                Forms\Components\TextInput::make('price')->numeric()->prefix('$'),
                Forms\Components\TextInput::make('cost')->numeric()->prefix('$'),
            ]),

        Forms\Components\Tabs\Tab::make('Inventory')
            ->icon('heroicon-o-cube')
            ->schema([
                Forms\Components\TextInput::make('stock')->numeric(),
                Forms\Components\TextInput::make('sku'),
            ]),

        Forms\Components\Tabs\Tab::make('SEO')
            ->icon('heroicon-o-magnifying-glass')
            ->schema([
                Forms\Components\TextInput::make('meta_title'),
                Forms\Components\Textarea::make('meta_description'),
            ]),
    ])
    ->persistTabInQueryString()
    ->columnSpanFull();
```

## Split Layout

```php
Forms\Components\Split::make([
    Forms\Components\Section::make('Main Content')
        ->schema([
            Forms\Components\TextInput::make('title')->required(),
            Forms\Components\RichEditor::make('content'),
        ])
        ->grow(true), // Takes remaining space

    Forms\Components\Section::make('Sidebar')
        ->schema([
            Forms\Components\Select::make('status')
                ->options(['draft' => 'Draft', 'published' => 'Published']),
            Forms\Components\DatePicker::make('publish_date'),
            Forms\Components\Toggle::make('featured'),
        ])
        ->grow(false), // Fixed width
])
    ->from('md') // Apply split from md breakpoint
    ->columnSpanFull();
```

## Fieldset Component

```php
Forms\Components\Fieldset::make('Address')
    ->schema([
        Forms\Components\TextInput::make('street')
            ->required()
            ->columnSpanFull(),

        Forms\Components\TextInput::make('city')
            ->required(),

        Forms\Components\Select::make('state')
            ->options([...])
            ->required(),

        Forms\Components\TextInput::make('zip')
            ->required(),
    ])
    ->columns(3);
```

## Card Component

```php
Forms\Components\Card::make()
    ->schema([
        Forms\Components\TextInput::make('name'),
        Forms\Components\TextInput::make('email'),
    ])
    ->columns(2);
```

## Column Spanning

```php
Forms\Components\Section::make()
    ->schema([
        Forms\Components\TextInput::make('title')
            ->columnSpan(2), // Span 2 columns

        Forms\Components\TextInput::make('slug')
            ->columnSpan(1),

        Forms\Components\RichEditor::make('content')
            ->columnSpanFull(), // Span all columns

        Forms\Components\TextInput::make('summary')
            ->columnStart(2), // Start at column 2
    ])
    ->columns(3);
```

## Nested Layouts

```php
Forms\Components\Section::make('Order Details')
    ->schema([
        Forms\Components\Grid::make(2)
            ->schema([
                Forms\Components\TextInput::make('order_number'),
                Forms\Components\DatePicker::make('order_date'),
            ]),

        Forms\Components\Fieldset::make('Customer')
            ->schema([
                Forms\Components\TextInput::make('customer_name'),
                Forms\Components\TextInput::make('customer_email'),
            ])
            ->columns(2),

        Forms\Components\Fieldset::make('Shipping')
            ->schema([
                Forms\Components\TextInput::make('address')->columnSpanFull(),
                Forms\Components\TextInput::make('city'),
                Forms\Components\TextInput::make('state'),
            ])
            ->columns(2),
    ]);
```

## Responsive Design

```php
Forms\Components\Section::make()
    ->schema([
        Forms\Components\TextInput::make('field1')
            ->columnSpan([
                'default' => 'full',
                'sm' => 1,
                'md' => 1,
            ]),

        Forms\Components\TextInput::make('field2')
            ->columnSpan([
                'default' => 'full',
                'sm' => 1,
                'md' => 1,
            ]),
    ])
    ->columns([
        'default' => 1,
        'sm' => 2,
        'md' => 3,
        'lg' => 4,
    ]);
```
