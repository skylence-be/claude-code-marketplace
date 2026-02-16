# Repeaters & Builders

Filament 5 Repeater and Builder components for dynamic form content.

## Basic Repeater

```php
use Filament\Forms;
use Filament\Schemas\Components\Utilities\Get;
use Filament\Schemas\Components\Utilities\Set;

Forms\Components\Repeater::make('items')
    ->schema([
        Forms\Components\TextInput::make('name')
            ->required(),

        Forms\Components\TextInput::make('quantity')
            ->numeric()
            ->default(1)
            ->minValue(1),

        Forms\Components\TextInput::make('price')
            ->numeric()
            ->prefix('$'),
    ])
    ->columns(3)
    ->defaultItems(1)
    ->minItems(1)
    ->maxItems(10)
    ->addActionLabel('Add Item')
    ->reorderable()
    ->collapsible()
    ->cloneable();
```

## Repeater with Relationship

```php
Forms\Components\Repeater::make('addresses')
    ->relationship() // Uses model relationship
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

        Forms\Components\Toggle::make('is_primary')
            ->default(false),
    ])
    ->columns(3)
    ->itemLabel(fn (array $state): ?string =>
        $state['street'] ?? 'New Address'
    )
    ->orderColumn('sort_order');
```

## Repeater with Calculations

```php
Forms\Components\Section::make('Invoice Items')
    ->schema([
        Forms\Components\Repeater::make('items')
            ->relationship()
            ->schema([
                Forms\Components\Select::make('product_id')
                    ->options(Product::pluck('name', 'id'))
                    ->required()
                    ->live()
                    ->afterStateUpdated(function (Get $get, Set $set, $state) {
                        $product = Product::find($state);
                        if ($product) {
                            $set('unit_price', $product->price);
                            self::calculateLineTotal($get, $set);
                        }
                    })
                    ->columnSpan(3),

                Forms\Components\TextInput::make('quantity')
                    ->numeric()
                    ->default(1)
                    ->minValue(1)
                    ->live()
                    ->afterStateUpdated(fn (Get $get, Set $set) =>
                        self::calculateLineTotal($get, $set)
                    )
                    ->columnSpan(2),

                Forms\Components\TextInput::make('unit_price')
                    ->numeric()
                    ->prefix('$')
                    ->live()
                    ->afterStateUpdated(fn (Get $get, Set $set) =>
                        self::calculateLineTotal($get, $set)
                    )
                    ->columnSpan(2),

                Forms\Components\TextInput::make('total')
                    ->numeric()
                    ->prefix('$')
                    ->disabled()
                    ->dehydrated()
                    ->columnSpan(2),
            ])
            ->columns(9)
            ->live()
            ->afterStateUpdated(fn (Get $get, Set $set) =>
                self::calculateInvoiceTotal($get, $set)
            )
            ->deleteAction(
                fn (Forms\Components\Actions\Action $action) =>
                    $action->after(fn (Get $get, Set $set) =>
                        self::calculateInvoiceTotal($get, $set)
                    )
            ),

        Forms\Components\Grid::make(4)
            ->schema([
                Forms\Components\Placeholder::make('subtotal_label')
                    ->content('Subtotal:')
                    ->columnStart(3),

                Forms\Components\TextInput::make('subtotal')
                    ->disabled()
                    ->dehydrated()
                    ->prefix('$'),
            ]),
    ]);

// Helper methods
protected static function calculateLineTotal(Get $get, Set $set): void
{
    $quantity = (float) ($get('quantity') ?? 0);
    $unitPrice = (float) ($get('unit_price') ?? 0);
    $set('total', number_format($quantity * $unitPrice, 2, '.', ''));
}

protected static function calculateInvoiceTotal(Get $get, Set $set): void
{
    $items = $get('items') ?? [];
    $subtotal = collect($items)->sum(fn ($item) =>
        (float) ($item['quantity'] ?? 0) * (float) ($item['unit_price'] ?? 0)
    );
    $set('subtotal', number_format($subtotal, 2, '.', ''));
}
```

## Builder Component

```php
Forms\Components\Builder::make('content')
    ->blocks([
        Forms\Components\Builder\Block::make('heading')
            ->schema([
                Forms\Components\Select::make('level')
                    ->options([
                        'h1' => 'Heading 1',
                        'h2' => 'Heading 2',
                        'h3' => 'Heading 3',
                    ])
                    ->default('h2')
                    ->required(),

                Forms\Components\TextInput::make('content')
                    ->required(),
            ])
            ->columns(2)
            ->icon('heroicon-o-hashtag')
            ->label('Heading'),

        Forms\Components\Builder\Block::make('paragraph')
            ->schema([
                Forms\Components\RichEditor::make('content')
                    ->required()
                    ->toolbarButtons([
                        'bold', 'italic', 'link',
                        'bulletList', 'orderedList',
                    ]),
            ])
            ->icon('heroicon-o-document-text')
            ->label('Paragraph'),

        Forms\Components\Builder\Block::make('image')
            ->schema([
                Forms\Components\FileUpload::make('url')
                    ->image()
                    ->imageEditor()
                    ->required()
                    ->columnSpanFull(),

                Forms\Components\TextInput::make('alt')
                    ->required(),

                Forms\Components\TextInput::make('caption'),
            ])
            ->columns(2)
            ->icon('heroicon-o-photo')
            ->label('Image'),

        Forms\Components\Builder\Block::make('quote')
            ->schema([
                Forms\Components\Textarea::make('content')
                    ->required()
                    ->columnSpanFull(),

                Forms\Components\TextInput::make('author'),
                Forms\Components\TextInput::make('source'),
            ])
            ->columns(2)
            ->icon('heroicon-o-chat-bubble-left-right')
            ->label('Quote'),

        Forms\Components\Builder\Block::make('video')
            ->schema([
                Forms\Components\Select::make('source')
                    ->options([
                        'youtube' => 'YouTube',
                        'vimeo' => 'Vimeo',
                    ])
                    ->required()
                    ->live(),

                Forms\Components\TextInput::make('url')
                    ->url()
                    ->required()
                    ->placeholder(fn (Get $get) => match($get('source')) {
                        'youtube' => 'https://youtube.com/watch?v=...',
                        'vimeo' => 'https://vimeo.com/...',
                        default => 'Enter URL',
                    }),
            ])
            ->columns(2)
            ->icon('heroicon-o-video-camera')
            ->label('Video'),

        Forms\Components\Builder\Block::make('call_to_action')
            ->schema([
                Forms\Components\TextInput::make('heading')
                    ->required(),

                Forms\Components\Textarea::make('description'),

                Forms\Components\TextInput::make('button_text')
                    ->default('Learn More'),

                Forms\Components\TextInput::make('button_url')
                    ->url()
                    ->required(),

                Forms\Components\Select::make('style')
                    ->options([
                        'primary' => 'Primary',
                        'secondary' => 'Secondary',
                    ])
                    ->default('primary'),
            ])
            ->columns(2)
            ->icon('heroicon-o-megaphone')
            ->label('Call to Action'),
    ])
    ->blockNumbers(false)
    ->collapsible()
    ->reorderable()
    ->cloneable()
    ->addActionLabel('Add Content Block')
    ->columnSpanFull();
```

## Nested Repeaters

```php
Forms\Components\Repeater::make('sections')
    ->schema([
        Forms\Components\TextInput::make('title')
            ->required()
            ->columnSpanFull(),

        Forms\Components\Repeater::make('items')
            ->schema([
                Forms\Components\TextInput::make('name')
                    ->required(),

                Forms\Components\TextInput::make('value')
                    ->required(),
            ])
            ->columns(2)
            ->defaultItems(1)
            ->columnSpanFull(),
    ])
    ->collapsible()
    ->itemLabel(fn (array $state): ?string =>
        $state['title'] ?? 'New Section'
    );
```

## Repeater Options

```php
Forms\Components\Repeater::make('items')
    ->schema([...])

    // Item management
    ->defaultItems(1)
    ->minItems(1)
    ->maxItems(10)

    // Actions
    ->addActionLabel('Add New Item')
    ->reorderable()
    ->reorderableWithDragAndDrop()
    ->reorderableWithButtons()
    ->collapsible()
    ->collapsed(false) // Start expanded
    ->cloneable()

    // Item labels
    ->itemLabel(fn (array $state): ?string =>
        $state['name'] ?? 'New Item'
    )

    // Simple mode (inline items)
    ->simple(
        Forms\Components\TextInput::make('name')
    )

    // Grid layout
    ->grid(2) // 2 columns of items

    // Customize delete action
    ->deleteAction(
        fn (Forms\Components\Actions\Action $action) => $action
            ->requiresConfirmation()
            ->modalHeading('Delete item?')
    )

    // Live updates
    ->live()
    ->afterStateUpdated(function ($state) {
        // React to changes
    });
```

## Builder Options

```php
Forms\Components\Builder::make('content')
    ->blocks([...])

    // Block management
    ->blockNumbers(false)
    ->reorderable()
    ->reorderableWithDragAndDrop()
    ->collapsible()
    ->collapsed(false)
    ->cloneable()

    // Labels and icons
    ->blockLabels(true)
    ->addActionLabel('Add Block')

    // Restrict blocks
    ->maxItems(20)

    // Block picker columns
    ->blockPickerColumns(3)

    // Block picker width
    ->blockPickerWidth('md');
```
