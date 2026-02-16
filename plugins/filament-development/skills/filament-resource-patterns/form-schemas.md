# Form Schemas

Filament 5 advanced form component patterns.

## Tabbed Form

```php
public static function form(Form $form): Form
{
    return $form
        ->schema([
            Forms\Components\Tabs::make('Article')
                ->tabs([
                    Forms\Components\Tabs\Tab::make('Content')
                        ->schema([
                            Forms\Components\TextInput::make('title')
                                ->required()
                                ->maxLength(255)
                                ->live(onBlur: true)
                                ->afterStateUpdated(fn ($state, Set $set) =>
                                    $set('slug', \Str::slug($state))
                                ),

                            Forms\Components\TextInput::make('slug')
                                ->required()
                                ->unique(),

                            Forms\Components\Select::make('author_id')
                                ->relationship('author', 'name')
                                ->searchable()
                                ->preload(),

                            Forms\Components\RichEditor::make('content')
                                ->required()
                                ->columnSpanFull()
                                ->fileAttachmentsDisk('public')
                                ->fileAttachmentsDirectory('articles'),
                        ]),

                    Forms\Components\Tabs\Tab::make('Metadata')
                        ->schema([
                            Forms\Components\Select::make('categories')
                                ->multiple()
                                ->relationship('categories', 'name')
                                ->preload()
                                ->searchable()
                                ->createOptionForm([
                                    Forms\Components\TextInput::make('name')
                                        ->required(),
                                    Forms\Components\TextInput::make('slug')
                                        ->required(),
                                ]),

                            Forms\Components\TagsInput::make('tags')
                                ->separator(','),

                            Forms\Components\DateTimePicker::make('published_at')
                                ->native(false),

                            Forms\Components\Toggle::make('is_featured'),
                        ]),

                    Forms\Components\Tabs\Tab::make('SEO')
                        ->schema([
                            Forms\Components\TextInput::make('meta_title')
                                ->maxLength(60),

                            Forms\Components\Textarea::make('meta_description')
                                ->maxLength(160)
                                ->rows(3),

                            Forms\Components\Select::make('robots')
                                ->options([
                                    'index,follow' => 'Index, Follow',
                                    'noindex,follow' => 'No Index, Follow',
                                ])
                                ->default('index,follow'),
                        ]),
                ])
                ->columnSpanFull(),
        ]);
}
```

## Select with Relationship

```php
// Basic relationship
Forms\Components\Select::make('category_id')
    ->relationship('category', 'name')
    ->required()
    ->searchable()
    ->preload(),

// With create option
Forms\Components\Select::make('category_id')
    ->relationship('category', 'name')
    ->createOptionForm([
        Forms\Components\TextInput::make('name')
            ->required()
            ->maxLength(255),
        Forms\Components\TextInput::make('slug')
            ->required(),
    ])
    ->createOptionAction(fn ($action) =>
        $action->modalWidth('md')
    ),

// Multi-select
Forms\Components\Select::make('tags')
    ->multiple()
    ->relationship('tags', 'name')
    ->preload()
    ->searchable(),

// With query modification
Forms\Components\Select::make('parent_id')
    ->relationship(
        'parent',
        'name',
        fn (Builder $query, ?Model $record) =>
            $query->when($record, fn ($q) =>
                $q->where('id', '!=', $record->id)
            )
    )
    ->searchable(),
```

## Live Fields with Calculations

```php
Forms\Components\Section::make('Pricing')
    ->schema([
        Forms\Components\TextInput::make('quantity')
            ->numeric()
            ->default(1)
            ->live()
            ->afterStateUpdated(fn (Get $get, Set $set) =>
                $set('total', $get('quantity') * $get('unit_price'))
            ),

        Forms\Components\TextInput::make('unit_price')
            ->numeric()
            ->prefix('$')
            ->live()
            ->afterStateUpdated(fn (Get $get, Set $set) =>
                $set('total', $get('quantity') * $get('unit_price'))
            ),

        Forms\Components\TextInput::make('discount_percent')
            ->numeric()
            ->suffix('%')
            ->default(0)
            ->live()
            ->afterStateUpdated(function (Get $get, Set $set) {
                $subtotal = $get('quantity') * $get('unit_price');
                $discount = $subtotal * ($get('discount_percent') / 100);
                $set('total', $subtotal - $discount);
            }),

        Forms\Components\TextInput::make('total')
            ->numeric()
            ->prefix('$')
            ->disabled()
            ->dehydrated(),
    ])
    ->columns(4),
```

## Conditional Fields

```php
Forms\Components\Select::make('type')
    ->options([
        'physical' => 'Physical Product',
        'digital' => 'Digital Product',
        'service' => 'Service',
    ])
    ->required()
    ->live(),

// Physical product fields
Forms\Components\Section::make('Shipping')
    ->schema([
        Forms\Components\TextInput::make('weight')
            ->numeric()
            ->suffix('kg'),
        Forms\Components\TextInput::make('dimensions'),
        Forms\Components\Toggle::make('requires_shipping')
            ->default(true),
    ])
    ->visible(fn (Get $get) => $get('type') === 'physical'),

// Digital product fields
Forms\Components\Section::make('Digital Delivery')
    ->schema([
        Forms\Components\FileUpload::make('download_file')
            ->required(),
        Forms\Components\TextInput::make('download_limit')
            ->numeric(),
    ])
    ->visible(fn (Get $get) => $get('type') === 'digital'),

// Service fields
Forms\Components\Section::make('Service Details')
    ->schema([
        Forms\Components\TextInput::make('duration')
            ->numeric()
            ->suffix('hours'),
        Forms\Components\Toggle::make('booking_required'),
    ])
    ->visible(fn (Get $get) => $get('type') === 'service'),
```

## File Uploads

```php
Forms\Components\Section::make('Media')
    ->schema([
        Forms\Components\FileUpload::make('featured_image')
            ->image()
            ->imageEditor()
            ->imageEditorAspectRatios(['16:9', '4:3', '1:1'])
            ->directory('products/featured')
            ->maxSize(2048)
            ->downloadable()
            ->openable(),

        Forms\Components\FileUpload::make('gallery')
            ->multiple()
            ->image()
            ->reorderable()
            ->maxFiles(10)
            ->directory('products/gallery')
            ->panelLayout('grid'),

        Forms\Components\FileUpload::make('documents')
            ->multiple()
            ->acceptedFileTypes(['application/pdf'])
            ->directory('products/documents')
            ->downloadable(),
    ]),
```

## Custom Validation

```php
Forms\Components\TextInput::make('email')
    ->email()
    ->required()
    ->unique()
    ->rules(['email:rfc,dns']),

Forms\Components\TextInput::make('password')
    ->password()
    ->required(fn (string $context) => $context === 'create')
    ->minLength(8)
    ->confirmed()
    ->revealable()
    ->dehydrateStateUsing(fn ($state) =>
        filled($state) ? Hash::make($state) : null
    )
    ->dehydrated(fn ($state) => filled($state)),

Forms\Components\TextInput::make('sku')
    ->required()
    ->unique()
    ->rules([
        fn (): \Closure => function (string $attribute, $value, \Closure $fail) {
            if (!preg_match('/^[A-Z]{2}-\d{4}$/', $value)) {
                $fail('SKU must match format: XX-0000');
            }
        },
    ]),
```
