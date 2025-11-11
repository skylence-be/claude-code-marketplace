---
name: filament-forms-advanced
description: Master advanced Filament 4 form patterns including complex layouts, conditional fields, repeaters, builders, custom fields, file uploads, wizards, and real-time validation. Use when building sophisticated data entry interfaces.
category: filament
tags: [filament, forms, validation, layouts, custom-fields]
related_skills: [filament-resource-patterns, livewire-forms-validation, laravel-api-design]
---

# Filament Forms Advanced

Comprehensive guide to implementing advanced form patterns in Filament 4, covering complex layouts, conditional visibility, dynamic repeating fields, custom form components, file upload handling, multi-step wizards, cascading selects, and real-time validation strategies.

## When to Use This Skill

- Building complex multi-section forms with nested layouts
- Implementing conditional field visibility based on other field values
- Creating dynamic repeating field groups with Repeater components
- Building flexible content blocks with Builder components
- Developing custom form fields for specialized data types
- Implementing file upload with image manipulation and validation
- Creating multi-step form wizards for complex workflows
- Building dependent dropdown fields and cascading selects
- Handling JSON field input with KeyValue components
- Implementing real-time validation with custom rules

## Core Concepts

### 1. Form Layouts
- **Grid**: Responsive column-based layouts
- **Section**: Grouped fields with collapsible headings
- **Tabs**: Organize fields into separate tabbed panels
- **Fieldset**: Traditional HTML fieldset grouping
- **Card**: Visually distinct card containers
- **Split**: Side-by-side column layouts

### 2. Conditional Logic
- **hidden()**: Hide fields based on conditions
- **visible()**: Show fields based on conditions
- **disabled()**: Disable fields dynamically
- **required()**: Make fields required conditionally
- **reactive()**: Listen to changes in other fields

### 3. Dynamic Fields
- **Repeater**: Add/remove repeating field groups
- **Builder**: Create flexible content blocks
- **KeyValue**: Manage key-value pair inputs
- **TagsInput**: Dynamic tag management
- **CheckboxList**: Multiple checkbox selections

### 4. File Handling
- **FileUpload**: File and image uploads
- **Image Editor**: Built-in image manipulation
- **Multiple Files**: Handle multiple file uploads
- **Validation**: Size, type, and dimension validation
- **Storage**: Disk configuration and visibility

### 5. Form State
- **Live Updates**: Real-time field updates
- **Dehydration**: Control data saved to model
- **Hydration**: Control data loaded from model
- **Afterstate**: React to field changes
- **Default Values**: Set intelligent defaults

## Quick Start

```php
<?php

use Filament\Forms;
use Filament\Forms\Form;

public static function form(Form $form): Form
{
    return $form
        ->schema([
            Forms\Components\Section::make('Basic Information')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->required()
                        ->live(onBlur: true),

                    Forms\Components\Select::make('type')
                        ->options([
                            'individual' => 'Individual',
                            'company' => 'Company',
                        ])
                        ->required()
                        ->reactive(),

                    Forms\Components\TextInput::make('company_name')
                        ->required()
                        ->visible(fn ($get) => $get('type') === 'company'),
                ])
                ->columns(2),
        ]);
}
```

## Fundamental Patterns

### Pattern 1: Advanced Grid Layouts

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;

class ProfileResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                // Full-width section
                Forms\Components\Section::make('Personal Information')
                    ->schema([
                        Forms\Components\Grid::make(3)
                            ->schema([
                                Forms\Components\TextInput::make('first_name')
                                    ->required()
                                    ->maxLength(255),

                                Forms\Components\TextInput::make('middle_name')
                                    ->maxLength(255),

                                Forms\Components\TextInput::make('last_name')
                                    ->required()
                                    ->maxLength(255),
                            ]),

                        Forms\Components\Grid::make(2)
                            ->schema([
                                Forms\Components\DatePicker::make('date_of_birth')
                                    ->required()
                                    ->native(false)
                                    ->maxDate(now()->subYears(18))
                                    ->displayFormat('M d, Y'),

                                Forms\Components\Select::make('gender')
                                    ->options([
                                        'male' => 'Male',
                                        'female' => 'Female',
                                        'other' => 'Other',
                                        'prefer_not_to_say' => 'Prefer not to say',
                                    ])
                                    ->native(false),
                            ]),

                        Forms\Components\TextInput::make('email')
                            ->email()
                            ->required()
                            ->unique(ignoreRecord: true)
                            ->maxLength(255)
                            ->prefixIcon('heroicon-o-envelope')
                            ->columnSpanFull(),

                        Forms\Components\Grid::make(2)
                            ->schema([
                                Forms\Components\TextInput::make('phone')
                                    ->tel()
                                    ->maxLength(20)
                                    ->prefixIcon('heroicon-o-phone'),

                                Forms\Components\TextInput::make('mobile')
                                    ->tel()
                                    ->maxLength(20)
                                    ->prefixIcon('heroicon-o-device-phone-mobile'),
                            ]),
                    ])
                    ->columns(1),

                // Two-column split layout
                Forms\Components\Split::make([
                    Forms\Components\Section::make('Address')
                        ->schema([
                            Forms\Components\TextInput::make('street_address')
                                ->required()
                                ->maxLength(255),

                            Forms\Components\TextInput::make('apartment')
                                ->label('Apt, Suite, etc.')
                                ->maxLength(50),

                            Forms\Components\Grid::make(2)
                                ->schema([
                                    Forms\Components\TextInput::make('city')
                                        ->required()
                                        ->maxLength(100),

                                    Forms\Components\Select::make('state')
                                        ->options([
                                            'CA' => 'California',
                                            'NY' => 'New York',
                                            'TX' => 'Texas',
                                            // ... more states
                                        ])
                                        ->searchable()
                                        ->required(),
                                ]),

                            Forms\Components\TextInput::make('zip_code')
                                ->required()
                                ->maxLength(10),
                        ])
                        ->grow(true),

                    Forms\Components\Section::make('Emergency Contact')
                        ->schema([
                            Forms\Components\TextInput::make('emergency_name')
                                ->label('Name')
                                ->required()
                                ->maxLength(255),

                            Forms\Components\TextInput::make('emergency_relationship')
                                ->label('Relationship')
                                ->required()
                                ->maxLength(100),

                            Forms\Components\TextInput::make('emergency_phone')
                                ->label('Phone')
                                ->tel()
                                ->required()
                                ->maxLength(20),
                        ])
                        ->grow(false),
                ])
                    ->from('md')
                    ->columnSpanFull(),

                // Fieldset example
                Forms\Components\Fieldset::make('Preferences')
                    ->schema([
                        Forms\Components\Toggle::make('newsletter_subscribed')
                            ->label('Subscribe to newsletter')
                            ->default(true),

                        Forms\Components\Toggle::make('sms_notifications')
                            ->label('Receive SMS notifications'),

                        Forms\Components\Select::make('language')
                            ->options([
                                'en' => 'English',
                                'es' => 'Spanish',
                                'fr' => 'French',
                                'de' => 'German',
                            ])
                            ->default('en')
                            ->native(false),

                        Forms\Components\Select::make('timezone')
                            ->options(\DateTimeZone::listIdentifiers())
                            ->searchable()
                            ->default('America/New_York'),
                    ])
                    ->columns(2),
            ]);
    }
}
```

### Pattern 2: Conditional Field Visibility

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Forms\Get;
use Filament\Forms\Set;

class OrderResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Order Type')
                    ->schema([
                        Forms\Components\Radio::make('order_type')
                            ->options([
                                'delivery' => 'Delivery',
                                'pickup' => 'Pickup',
                                'dine_in' => 'Dine In',
                            ])
                            ->required()
                            ->reactive()
                            ->afterStateUpdated(function (Set $set, $state) {
                                if ($state !== 'delivery') {
                                    $set('delivery_address', null);
                                    $set('delivery_instructions', null);
                                }
                            })
                            ->inline(),
                    ]),

                // Delivery fields (visible only for delivery orders)
                Forms\Components\Section::make('Delivery Information')
                    ->schema([
                        Forms\Components\TextInput::make('delivery_address')
                            ->required()
                            ->maxLength(255)
                            ->live(onBlur: true)
                            ->afterStateUpdated(function (Get $get, Set $set, $state) {
                                // Auto-calculate delivery fee based on address
                                $fee = calculateDeliveryFee($state);
                                $set('delivery_fee', $fee);
                            }),

                        Forms\Components\Textarea::make('delivery_instructions')
                            ->rows(3)
                            ->maxLength(500),

                        Forms\Components\TextInput::make('delivery_fee')
                            ->numeric()
                            ->prefix('$')
                            ->disabled()
                            ->dehydrated()
                            ->default(0),

                        Forms\Components\DateTimePicker::make('delivery_time')
                            ->required()
                            ->native(false)
                            ->minDate(now())
                            ->displayFormat('M d, Y H:i'),
                    ])
                    ->visible(fn (Get $get): bool => $get('order_type') === 'delivery')
                    ->columns(2),

                // Pickup fields
                Forms\Components\Section::make('Pickup Information')
                    ->schema([
                        Forms\Components\Select::make('pickup_location')
                            ->options([
                                'main_street' => 'Main Street Location',
                                'downtown' => 'Downtown Location',
                                'west_end' => 'West End Location',
                            ])
                            ->required()
                            ->native(false),

                        Forms\Components\DateTimePicker::make('pickup_time')
                            ->required()
                            ->native(false)
                            ->minDate(now())
                            ->displayFormat('M d, Y H:i'),
                    ])
                    ->visible(fn (Get $get): bool => $get('order_type') === 'pickup')
                    ->columns(2),

                // Dine-in fields
                Forms\Components\Section::make('Dine-In Information')
                    ->schema([
                        Forms\Components\TextInput::make('table_number')
                            ->required()
                            ->numeric()
                            ->minValue(1),

                        Forms\Components\TextInput::make('number_of_guests')
                            ->required()
                            ->numeric()
                            ->minValue(1)
                            ->default(1),

                        Forms\Components\Toggle::make('has_reservation')
                            ->reactive(),

                        Forms\Components\TextInput::make('reservation_code')
                            ->required(fn (Get $get): bool => $get('has_reservation'))
                            ->visible(fn (Get $get): bool => $get('has_reservation'))
                            ->maxLength(20),
                    ])
                    ->visible(fn (Get $get): bool => $get('order_type') === 'dine_in')
                    ->columns(2),

                // Payment section with conditional fields
                Forms\Components\Section::make('Payment')
                    ->schema([
                        Forms\Components\Select::make('payment_method')
                            ->options([
                                'credit_card' => 'Credit Card',
                                'cash' => 'Cash',
                                'gift_card' => 'Gift Card',
                                'account' => 'Account Billing',
                            ])
                            ->required()
                            ->reactive()
                            ->native(false),

                        Forms\Components\Grid::make(2)
                            ->schema([
                                Forms\Components\TextInput::make('card_number')
                                    ->label('Card Number')
                                    ->required()
                                    ->mask('9999 9999 9999 9999')
                                    ->placeholder('1234 5678 9012 3456'),

                                Forms\Components\TextInput::make('card_name')
                                    ->label('Name on Card')
                                    ->required()
                                    ->maxLength(255),

                                Forms\Components\TextInput::make('card_expiry')
                                    ->label('Expiry Date')
                                    ->required()
                                    ->mask('99/99')
                                    ->placeholder('MM/YY'),

                                Forms\Components\TextInput::make('card_cvv')
                                    ->label('CVV')
                                    ->required()
                                    ->mask('999')
                                    ->password()
                                    ->revealable(),
                            ])
                            ->visible(fn (Get $get): bool =>
                                $get('payment_method') === 'credit_card'
                            ),

                        Forms\Components\TextInput::make('gift_card_number')
                            ->required()
                            ->mask('9999-9999-9999-9999')
                            ->visible(fn (Get $get): bool =>
                                $get('payment_method') === 'gift_card'
                            ),

                        Forms\Components\Select::make('billing_account_id')
                            ->label('Account')
                            ->relationship('billingAccount', 'name')
                            ->required()
                            ->searchable()
                            ->preload()
                            ->visible(fn (Get $get): bool =>
                                $get('payment_method') === 'account'
                            ),
                    ])
                    ->columns(1),
            ]);
    }
}
```

### Pattern 3: Repeater Fields for Dynamic Content

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Forms\Get;
use Filament\Forms\Set;

class InvoiceResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Invoice Details')
                    ->schema([
                        Forms\Components\Grid::make(3)
                            ->schema([
                                Forms\Components\TextInput::make('invoice_number')
                                    ->required()
                                    ->unique(ignoreRecord: true)
                                    ->default(fn () => 'INV-' . str_pad(Invoice::max('id') + 1, 6, '0', STR_PAD_LEFT))
                                    ->disabled()
                                    ->dehydrated(),

                                Forms\Components\DatePicker::make('invoice_date')
                                    ->required()
                                    ->default(now())
                                    ->native(false),

                                Forms\Components\DatePicker::make('due_date')
                                    ->required()
                                    ->native(false)
                                    ->default(now()->addDays(30))
                                    ->after('invoice_date'),
                            ]),

                        Forms\Components\Select::make('customer_id')
                            ->relationship('customer', 'name')
                            ->required()
                            ->searchable()
                            ->preload()
                            ->createOptionForm([
                                Forms\Components\TextInput::make('name')
                                    ->required()
                                    ->maxLength(255),
                                Forms\Components\TextInput::make('email')
                                    ->email()
                                    ->required(),
                                Forms\Components\TextInput::make('phone')
                                    ->tel(),
                            ]),
                    ])
                    ->columns(1),

                Forms\Components\Section::make('Line Items')
                    ->schema([
                        Forms\Components\Repeater::make('items')
                            ->relationship()
                            ->schema([
                                Forms\Components\Grid::make(12)
                                    ->schema([
                                        Forms\Components\Select::make('product_id')
                                            ->label('Product')
                                            ->options(Product::pluck('name', 'id'))
                                            ->required()
                                            ->searchable()
                                            ->reactive()
                                            ->afterStateUpdated(function (Get $get, Set $set, $state) {
                                                $product = Product::find($state);
                                                if ($product) {
                                                    $set('description', $product->description);
                                                    $set('unit_price', $product->price);

                                                    // Recalculate totals
                                                    $quantity = $get('quantity') ?? 1;
                                                    $set('quantity', $quantity);
                                                    self::updateLineItemTotal($get, $set);
                                                }
                                            })
                                            ->columnSpan(4),

                                        Forms\Components\Textarea::make('description')
                                            ->rows(1)
                                            ->columnSpan(4),

                                        Forms\Components\TextInput::make('quantity')
                                            ->numeric()
                                            ->required()
                                            ->default(1)
                                            ->minValue(1)
                                            ->reactive()
                                            ->afterStateUpdated(fn (Get $get, Set $set) =>
                                                self::updateLineItemTotal($get, $set)
                                            )
                                            ->columnSpan(1),

                                        Forms\Components\TextInput::make('unit_price')
                                            ->numeric()
                                            ->required()
                                            ->prefix('$')
                                            ->reactive()
                                            ->afterStateUpdated(fn (Get $get, Set $set) =>
                                                self::updateLineItemTotal($get, $set)
                                            )
                                            ->columnSpan(1),

                                        Forms\Components\TextInput::make('tax_rate')
                                            ->numeric()
                                            ->suffix('%')
                                            ->default(0)
                                            ->minValue(0)
                                            ->maxValue(100)
                                            ->reactive()
                                            ->afterStateUpdated(fn (Get $get, Set $set) =>
                                                self::updateLineItemTotal($get, $set)
                                            )
                                            ->columnSpan(1),

                                        Forms\Components\TextInput::make('total')
                                            ->numeric()
                                            ->prefix('$')
                                            ->disabled()
                                            ->dehydrated()
                                            ->columnSpan(1),
                                    ]),
                            ])
                            ->defaultItems(1)
                            ->addActionLabel('Add Line Item')
                            ->reorderable()
                            ->collapsible()
                            ->cloneable()
                            ->itemLabel(fn (array $state): ?string =>
                                $state['description'] ?? 'New Item'
                            )
                            ->live()
                            ->afterStateUpdated(function (Get $get, Set $set) {
                                self::updateInvoiceTotals($get, $set);
                            })
                            ->deleteAction(
                                fn (Forms\Components\Actions\Action $action) =>
                                    $action->after(fn (Get $get, Set $set) =>
                                        self::updateInvoiceTotals($get, $set)
                                    )
                            ),
                    ]),

                Forms\Components\Section::make('Totals')
                    ->schema([
                        Forms\Components\Grid::make(4)
                            ->schema([
                                Forms\Components\Placeholder::make('subtotal_label')
                                    ->content('Subtotal:')
                                    ->columnStart(3),

                                Forms\Components\TextInput::make('subtotal')
                                    ->numeric()
                                    ->prefix('$')
                                    ->disabled()
                                    ->dehydrated(),

                                Forms\Components\Placeholder::make('tax_label')
                                    ->content('Tax:'),

                                Forms\Components\TextInput::make('tax_total')
                                    ->numeric()
                                    ->prefix('$')
                                    ->disabled()
                                    ->dehydrated(),

                                Forms\Components\Placeholder::make('discount_label')
                                    ->content('Discount:'),

                                Forms\Components\TextInput::make('discount')
                                    ->numeric()
                                    ->prefix('$')
                                    ->default(0)
                                    ->reactive()
                                    ->afterStateUpdated(fn (Get $get, Set $set) =>
                                        self::updateInvoiceTotals($get, $set)
                                    ),

                                Forms\Components\Placeholder::make('total_label')
                                    ->content('Total:')
                                    ->extraAttributes(['class' => 'font-bold text-lg']),

                                Forms\Components\TextInput::make('total')
                                    ->numeric()
                                    ->prefix('$')
                                    ->disabled()
                                    ->dehydrated()
                                    ->extraInputAttributes(['class' => 'font-bold text-lg']),
                            ]),
                    ]),

                Forms\Components\Section::make('Notes')
                    ->schema([
                        Forms\Components\Textarea::make('notes')
                            ->rows(3)
                            ->maxLength(1000),

                        Forms\Components\Textarea::make('terms')
                            ->label('Terms & Conditions')
                            ->rows(3)
                            ->default('Payment due within 30 days. Late payments may incur additional fees.')
                            ->maxLength(1000),
                    ])
                    ->columns(1)
                    ->collapsible(),
            ]);
    }

    protected static function updateLineItemTotal(Get $get, Set $set): void
    {
        $quantity = (float) ($get('quantity') ?? 0);
        $unitPrice = (float) ($get('unit_price') ?? 0);
        $taxRate = (float) ($get('tax_rate') ?? 0);

        $subtotal = $quantity * $unitPrice;
        $tax = $subtotal * ($taxRate / 100);
        $total = $subtotal + $tax;

        $set('total', number_format($total, 2, '.', ''));
    }

    protected static function updateInvoiceTotals(Get $get, Set $set): void
    {
        $items = $get('items') ?? [];

        $subtotal = 0;
        $taxTotal = 0;

        foreach ($items as $item) {
            $quantity = (float) ($item['quantity'] ?? 0);
            $unitPrice = (float) ($item['unit_price'] ?? 0);
            $taxRate = (float) ($item['tax_rate'] ?? 0);

            $itemSubtotal = $quantity * $unitPrice;
            $itemTax = $itemSubtotal * ($taxRate / 100);

            $subtotal += $itemSubtotal;
            $taxTotal += $itemTax;
        }

        $discount = (float) ($get('discount') ?? 0);
        $total = $subtotal + $taxTotal - $discount;

        $set('subtotal', number_format($subtotal, 2, '.', ''));
        $set('tax_total', number_format($taxTotal, 2, '.', ''));
        $set('total', number_format($total, 2, '.', ''));
    }
}
```

### Pattern 4: Builder Component for Flexible Content

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;

class PageResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Page Information')
                    ->schema([
                        Forms\Components\TextInput::make('title')
                            ->required()
                            ->maxLength(255)
                            ->live(onBlur: true)
                            ->afterStateUpdated(fn ($state, callable $set) =>
                                $set('slug', \Str::slug($state))
                            ),

                        Forms\Components\TextInput::make('slug')
                            ->required()
                            ->unique(ignoreRecord: true)
                            ->maxLength(255),

                        Forms\Components\Select::make('status')
                            ->options([
                                'draft' => 'Draft',
                                'published' => 'Published',
                                'archived' => 'Archived',
                            ])
                            ->default('draft')
                            ->required()
                            ->native(false),
                    ])
                    ->columns(2),

                Forms\Components\Builder::make('content')
                    ->blocks([
                        Forms\Components\Builder\Block::make('heading')
                            ->schema([
                                Forms\Components\Select::make('level')
                                    ->options([
                                        'h1' => 'Heading 1',
                                        'h2' => 'Heading 2',
                                        'h3' => 'Heading 3',
                                        'h4' => 'Heading 4',
                                    ])
                                    ->required()
                                    ->default('h2'),

                                Forms\Components\TextInput::make('content')
                                    ->required()
                                    ->maxLength(255),
                            ])
                            ->columns(2)
                            ->icon('heroicon-o-hashtag'),

                        Forms\Components\Builder\Block::make('paragraph')
                            ->schema([
                                Forms\Components\RichEditor::make('content')
                                    ->required()
                                    ->toolbarButtons([
                                        'bold',
                                        'italic',
                                        'underline',
                                        'strike',
                                        'link',
                                        'bulletList',
                                        'orderedList',
                                        'blockquote',
                                    ])
                                    ->columnSpanFull(),
                            ])
                            ->icon('heroicon-o-document-text'),

                        Forms\Components\Builder\Block::make('image')
                            ->schema([
                                Forms\Components\FileUpload::make('url')
                                    ->label('Image')
                                    ->image()
                                    ->imageEditor()
                                    ->required()
                                    ->directory('pages/images')
                                    ->columnSpanFull(),

                                Forms\Components\TextInput::make('alt')
                                    ->label('Alt Text')
                                    ->required()
                                    ->maxLength(255),

                                Forms\Components\TextInput::make('caption')
                                    ->maxLength(255),
                            ])
                            ->columns(2)
                            ->icon('heroicon-o-photo'),

                        Forms\Components\Builder\Block::make('gallery')
                            ->schema([
                                Forms\Components\FileUpload::make('images')
                                    ->multiple()
                                    ->image()
                                    ->reorderable()
                                    ->maxFiles(10)
                                    ->directory('pages/galleries')
                                    ->columnSpanFull(),

                                Forms\Components\Select::make('layout')
                                    ->options([
                                        'grid' => 'Grid',
                                        'masonry' => 'Masonry',
                                        'carousel' => 'Carousel',
                                    ])
                                    ->default('grid')
                                    ->required(),

                                Forms\Components\TextInput::make('columns')
                                    ->numeric()
                                    ->default(3)
                                    ->minValue(1)
                                    ->maxValue(6),
                            ])
                            ->columns(2)
                            ->icon('heroicon-o-photo'),

                        Forms\Components\Builder\Block::make('video')
                            ->schema([
                                Forms\Components\Select::make('source')
                                    ->options([
                                        'youtube' => 'YouTube',
                                        'vimeo' => 'Vimeo',
                                        'upload' => 'Upload',
                                    ])
                                    ->required()
                                    ->reactive()
                                    ->default('youtube'),

                                Forms\Components\TextInput::make('url')
                                    ->label('Video URL')
                                    ->required()
                                    ->url()
                                    ->visible(fn ($get) => in_array($get('source'), ['youtube', 'vimeo'])),

                                Forms\Components\FileUpload::make('file')
                                    ->label('Video File')
                                    ->required()
                                    ->acceptedFileTypes(['video/*'])
                                    ->maxSize(102400) // 100MB
                                    ->directory('pages/videos')
                                    ->visible(fn ($get) => $get('source') === 'upload'),

                                Forms\Components\TextInput::make('title')
                                    ->maxLength(255),
                            ])
                            ->columns(2)
                            ->icon('heroicon-o-video-camera'),

                        Forms\Components\Builder\Block::make('quote')
                            ->schema([
                                Forms\Components\Textarea::make('content')
                                    ->required()
                                    ->rows(3)
                                    ->columnSpanFull(),

                                Forms\Components\TextInput::make('author')
                                    ->maxLength(255),

                                Forms\Components\TextInput::make('author_title')
                                    ->maxLength(255),
                            ])
                            ->columns(2)
                            ->icon('heroicon-o-chat-bubble-left-right'),

                        Forms\Components\Builder\Block::make('code')
                            ->schema([
                                Forms\Components\Select::make('language')
                                    ->options([
                                        'php' => 'PHP',
                                        'javascript' => 'JavaScript',
                                        'python' => 'Python',
                                        'html' => 'HTML',
                                        'css' => 'CSS',
                                        'sql' => 'SQL',
                                    ])
                                    ->required()
                                    ->searchable(),

                                Forms\Components\Textarea::make('code')
                                    ->required()
                                    ->rows(10)
                                    ->columnSpanFull(),
                            ])
                            ->icon('heroicon-o-code-bracket'),

                        Forms\Components\Builder\Block::make('cta')
                            ->label('Call to Action')
                            ->schema([
                                Forms\Components\TextInput::make('heading')
                                    ->required()
                                    ->maxLength(255),

                                Forms\Components\Textarea::make('text')
                                    ->rows(3)
                                    ->columnSpanFull(),

                                Forms\Components\TextInput::make('button_text')
                                    ->required()
                                    ->default('Learn More'),

                                Forms\Components\TextInput::make('button_url')
                                    ->url()
                                    ->required(),

                                Forms\Components\Select::make('style')
                                    ->options([
                                        'primary' => 'Primary',
                                        'secondary' => 'Secondary',
                                        'success' => 'Success',
                                        'danger' => 'Danger',
                                    ])
                                    ->default('primary'),
                            ])
                            ->columns(2)
                            ->icon('heroicon-o-megaphone'),
                    ])
                    ->collapsible()
                    ->cloneable()
                    ->reorderable()
                    ->blockNumbers(false)
                    ->addActionLabel('Add Content Block')
                    ->columnSpanFull(),
            ]);
    }
}
```

### Pattern 5: File Upload with Advanced Features

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;

class MediaResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('File Upload')
                    ->schema([
                        Forms\Components\FileUpload::make('image')
                            ->label('Main Image')
                            ->image()
                            ->imageEditor()
                            ->imageEditorAspectRatios([
                                null,
                                '16:9',
                                '4:3',
                                '1:1',
                            ])
                            ->imageEditorMode(2)
                            ->imageEditorViewportWidth('1920')
                            ->imageEditorViewportHeight('1080')
                            ->directory('media/images')
                            ->visibility('public')
                            ->disk('public')
                            ->maxSize(5120) // 5MB
                            ->minSize(100) // 100KB
                            ->acceptedFileTypes(['image/jpeg', 'image/png', 'image/webp'])
                            ->imagePreviewHeight('250')
                            ->loadingIndicatorPosition('center')
                            ->panelAspectRatio('2:1')
                            ->panelLayout('integrated')
                            ->removeUploadedFileButtonPosition('right')
                            ->uploadButtonPosition('left')
                            ->uploadProgressIndicatorPosition('left')
                            ->downloadable()
                            ->openable()
                            ->previewable()
                            ->deletable()
                            ->columnSpanFull()
                            ->helperText('Upload a high-quality image. Max size: 5MB.'),

                        Forms\Components\FileUpload::make('gallery')
                            ->label('Image Gallery')
                            ->multiple()
                            ->image()
                            ->reorderable()
                            ->appendFiles()
                            ->maxFiles(10)
                            ->minFiles(1)
                            ->directory('media/galleries')
                            ->visibility('public')
                            ->disk('public')
                            ->maxSize(5120)
                            ->acceptedFileTypes(['image/*'])
                            ->imagePreviewHeight('150')
                            ->panelLayout('grid')
                            ->downloadable()
                            ->openable()
                            ->columnSpanFull(),

                        Forms\Components\FileUpload::make('documents')
                            ->label('Documents')
                            ->multiple()
                            ->directory('media/documents')
                            ->visibility('private')
                            ->disk('private')
                            ->maxSize(10240) // 10MB
                            ->acceptedFileTypes([
                                'application/pdf',
                                'application/msword',
                                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                'application/vnd.ms-excel',
                                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            ])
                            ->previewable(false)
                            ->downloadable()
                            ->openable()
                            ->columnSpanFull(),

                        Forms\Components\FileUpload::make('avatar')
                            ->label('Avatar')
                            ->image()
                            ->avatar()
                            ->imageEditor()
                            ->circleCropper()
                            ->directory('avatars')
                            ->maxSize(2048)
                            ->columnSpan(1),
                    ])
                    ->columns(1),

                Forms\Components\Section::make('File Information')
                    ->schema([
                        Forms\Components\TextInput::make('title')
                            ->required()
                            ->maxLength(255),

                        Forms\Components\Textarea::make('description')
                            ->rows(3)
                            ->maxLength(500),

                        Forms\Components\TagsInput::make('tags')
                            ->separator(','),

                        Forms\Components\Select::make('category')
                            ->options([
                                'photos' => 'Photos',
                                'videos' => 'Videos',
                                'documents' => 'Documents',
                                'other' => 'Other',
                            ])
                            ->required(),
                    ])
                    ->columns(2),
            ]);
    }
}
```

### Pattern 6: Multi-Step Wizard Form

```php
<?php

namespace App\Filament\Resources\UserResource\Pages;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Pages\CreateRecord;
use Filament\Forms\Components\Wizard;

class CreateUser extends CreateRecord
{
    use CreateRecord\Concerns\HasWizard;

    protected static string $resource = UserResource::class;

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Wizard::make([
                    Wizard\Step::make('Personal Information')
                        ->schema([
                            Forms\Components\TextInput::make('first_name')
                                ->required()
                                ->maxLength(255),

                            Forms\Components\TextInput::make('last_name')
                                ->required()
                                ->maxLength(255),

                            Forms\Components\DatePicker::make('date_of_birth')
                                ->required()
                                ->native(false)
                                ->maxDate(now()->subYears(18)),

                            Forms\Components\Select::make('gender')
                                ->options([
                                    'male' => 'Male',
                                    'female' => 'Female',
                                    'other' => 'Other',
                                ])
                                ->required(),
                        ])
                        ->columns(2)
                        ->icon('heroicon-o-user')
                        ->description('Enter the user\'s personal details'),

                    Wizard\Step::make('Contact Information')
                        ->schema([
                            Forms\Components\TextInput::make('email')
                                ->email()
                                ->required()
                                ->unique()
                                ->maxLength(255),

                            Forms\Components\TextInput::make('phone')
                                ->tel()
                                ->required()
                                ->maxLength(20),

                            Forms\Components\TextInput::make('mobile')
                                ->tel()
                                ->maxLength(20),

                            Forms\Components\TextInput::make('address')
                                ->required()
                                ->maxLength(255)
                                ->columnSpanFull(),

                            Forms\Components\TextInput::make('city')
                                ->required()
                                ->maxLength(100),

                            Forms\Components\Select::make('state')
                                ->options([
                                    'CA' => 'California',
                                    'NY' => 'New York',
                                    'TX' => 'Texas',
                                ])
                                ->required()
                                ->searchable(),

                            Forms\Components\TextInput::make('zip_code')
                                ->required()
                                ->maxLength(10),
                        ])
                        ->columns(3)
                        ->icon('heroicon-o-envelope')
                        ->description('Enter contact and address information'),

                    Wizard\Step::make('Account Settings')
                        ->schema([
                            Forms\Components\TextInput::make('username')
                                ->required()
                                ->unique()
                                ->maxLength(50)
                                ->alphaNum(),

                            Forms\Components\TextInput::make('password')
                                ->password()
                                ->required()
                                ->minLength(8)
                                ->confirmed()
                                ->revealable(),

                            Forms\Components\TextInput::make('password_confirmation')
                                ->password()
                                ->required()
                                ->minLength(8)
                                ->revealable(),

                            Forms\Components\Select::make('roles')
                                ->multiple()
                                ->relationship('roles', 'name')
                                ->preload()
                                ->required(),

                            Forms\Components\Toggle::make('is_active')
                                ->label('Active Account')
                                ->default(true),

                            Forms\Components\Toggle::make('email_verified')
                                ->label('Email Verified')
                                ->default(false),
                        ])
                        ->columns(2)
                        ->icon('heroicon-o-key')
                        ->description('Configure account settings and permissions'),

                    Wizard\Step::make('Additional Information')
                        ->schema([
                            Forms\Components\FileUpload::make('avatar')
                                ->image()
                                ->avatar()
                                ->imageEditor()
                                ->circleCropper()
                                ->directory('avatars')
                                ->maxSize(2048),

                            Forms\Components\Select::make('department')
                                ->options([
                                    'sales' => 'Sales',
                                    'marketing' => 'Marketing',
                                    'engineering' => 'Engineering',
                                    'support' => 'Support',
                                ])
                                ->required(),

                            Forms\Components\TextInput::make('job_title')
                                ->required()
                                ->maxLength(255),

                            Forms\Components\Select::make('manager_id')
                                ->label('Manager')
                                ->relationship('manager', 'name')
                                ->searchable()
                                ->preload(),

                            Forms\Components\DatePicker::make('hire_date')
                                ->required()
                                ->native(false)
                                ->default(now()),

                            Forms\Components\Textarea::make('notes')
                                ->rows(4)
                                ->columnSpanFull(),
                        ])
                        ->columns(2)
                        ->icon('heroicon-o-information-circle')
                        ->description('Add additional user information'),
                ])
                    ->columnSpanFull()
                    ->persistStepInQueryString()
                    ->submitAction(view('filament.pages.actions.wizard-submit-button')),
            ]);
    }

    protected function getCreatedNotificationTitle(): ?string
    {
        return 'User created successfully';
    }

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('index');
    }
}
```

### Pattern 7: Cascading Dependent Select Fields

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Forms\Get;
use Filament\Forms\Set;
use Illuminate\Support\Collection;

class ProductResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Product Categorization')
                    ->schema([
                        Forms\Components\Select::make('category_id')
                            ->label('Category')
                            ->options(Category::whereNull('parent_id')->pluck('name', 'id'))
                            ->required()
                            ->searchable()
                            ->reactive()
                            ->afterStateUpdated(function (Set $set) {
                                $set('subcategory_id', null);
                                $set('type_id', null);
                            }),

                        Forms\Components\Select::make('subcategory_id')
                            ->label('Subcategory')
                            ->options(function (Get $get): Collection {
                                $categoryId = $get('category_id');

                                if (! $categoryId) {
                                    return collect();
                                }

                                return Category::where('parent_id', $categoryId)
                                    ->pluck('name', 'id');
                            })
                            ->required()
                            ->searchable()
                            ->reactive()
                            ->afterStateUpdated(fn (Set $set) => $set('type_id', null))
                            ->disabled(fn (Get $get): bool => ! $get('category_id')),

                        Forms\Components\Select::make('type_id')
                            ->label('Product Type')
                            ->options(function (Get $get): Collection {
                                $subcategoryId = $get('subcategory_id');

                                if (! $subcategoryId) {
                                    return collect();
                                }

                                return ProductType::where('category_id', $subcategoryId)
                                    ->pluck('name', 'id');
                            })
                            ->required()
                            ->searchable()
                            ->disabled(fn (Get $get): bool => ! $get('subcategory_id')),
                    ])
                    ->columns(3),

                Forms\Components\Section::make('Location')
                    ->schema([
                        Forms\Components\Select::make('country_id')
                            ->label('Country')
                            ->options(Country::pluck('name', 'id'))
                            ->required()
                            ->searchable()
                            ->reactive()
                            ->afterStateUpdated(function (Set $set) {
                                $set('state_id', null);
                                $set('city_id', null);
                            }),

                        Forms\Components\Select::make('state_id')
                            ->label('State/Province')
                            ->options(function (Get $get): Collection {
                                $countryId = $get('country_id');

                                if (! $countryId) {
                                    return collect();
                                }

                                return State::where('country_id', $countryId)
                                    ->pluck('name', 'id');
                            })
                            ->required()
                            ->searchable()
                            ->reactive()
                            ->afterStateUpdated(fn (Set $set) => $set('city_id', null))
                            ->disabled(fn (Get $get): bool => ! $get('country_id')),

                        Forms\Components\Select::make('city_id')
                            ->label('City')
                            ->options(function (Get $get): Collection {
                                $stateId = $get('state_id');

                                if (! $stateId) {
                                    return collect();
                                }

                                return City::where('state_id', $stateId)
                                    ->pluck('name', 'id');
                            })
                            ->required()
                            ->searchable()
                            ->disabled(fn (Get $get): bool => ! $get('state_id'))
                            ->createOptionForm([
                                Forms\Components\TextInput::make('name')
                                    ->required(),
                                Forms\Components\Hidden::make('state_id')
                                    ->default(fn (Get $get) => $get('../../state_id')),
                            ])
                            ->createOptionUsing(function (array $data, Get $get) {
                                $data['state_id'] = $get('state_id');
                                return City::create($data)->id;
                            }),
                    ])
                    ->columns(3),
            ]);
    }
}
```

## Advanced Patterns

### Pattern 8: Custom Form Field Component

```php
<?php

namespace App\Forms\Components;

use Filament\Forms\Components\Field;

class ColorPicker extends Field
{
    protected string $view = 'forms.components.color-picker';

    protected array $swatches = [];

    protected bool $copyable = true;

    public function swatches(array $swatches): static
    {
        $this->swatches = $swatches;

        return $this;
    }

    public function getSwatches(): array
    {
        return $this->evaluate($this->swatches);
    }

    public function copyable(bool $condition = true): static
    {
        $this->copyable = $condition;

        return $this;
    }

    public function isCopyable(): bool
    {
        return $this->evaluate($this->copyable);
    }
}
```

```blade
{{-- resources/views/forms/components/color-picker.blade.php --}}
<x-dynamic-component
    :component="$getFieldWrapperView()"
    :field="$field"
>
    <div
        x-data="{
            state: $wire.$entangle('{{ $getStatePath() }}'),
            copyColor() {
                navigator.clipboard.writeText(this.state);
                $tooltip('Color copied to clipboard');
            }
        }"
        class="space-y-2"
    >
        <div class="flex items-center gap-2">
            <input
                type="color"
                x-model="state"
                {{ $attributes->merge(['class' => 'h-10 w-20 rounded border-gray-300 dark:border-gray-700']) }}
                {{ $isDisabled() ? 'disabled' : '' }}
            >

            <input
                type="text"
                x-model="state"
                placeholder="#000000"
                {{ $attributes->merge(['class' => 'flex-1 rounded border-gray-300 dark:border-gray-700']) }}
                {{ $isDisabled() ? 'disabled' : '' }}
            >

            @if($isCopyable())
                <button
                    type="button"
                    x-on:click="copyColor()"
                    class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded"
                >
                    Copy
                </button>
            @endif
        </div>

        @if(count($getSwatches()) > 0)
            <div class="flex flex-wrap gap-2">
                @foreach($getSwatches() as $swatch)
                    <button
                        type="button"
                        x-on:click="state = '{{ $swatch }}'"
                        class="w-8 h-8 rounded border-2 border-gray-300 hover:border-gray-500"
                        style="background-color: {{ $swatch }}"
                        title="{{ $swatch }}"
                    ></button>
                @endforeach
            </div>
        @endif
    </div>
</x-dynamic-component>
```

```php
<?php

// Usage in resource
use App\Forms\Components\ColorPicker;

Forms\Components\Section::make('Branding')
    ->schema([
        ColorPicker::make('primary_color')
            ->label('Primary Color')
            ->required()
            ->swatches([
                '#ef4444',
                '#f59e0b',
                '#10b981',
                '#3b82f6',
                '#6366f1',
                '#8b5cf6',
            ])
            ->copyable(),

        ColorPicker::make('secondary_color')
            ->label('Secondary Color')
            ->swatches([
                '#64748b',
                '#71717a',
                '#737373',
            ]),
    ]);
```

### Pattern 9: JSON Field Handling with KeyValue

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;

class SettingsResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Configuration')
                    ->schema([
                        Forms\Components\KeyValue::make('settings')
                            ->keyLabel('Setting Name')
                            ->valueLabel('Value')
                            ->reorderable()
                            ->addActionLabel('Add Setting')
                            ->deleteActionLabel('Remove')
                            ->keyPlaceholder('e.g., max_upload_size')
                            ->valuePlaceholder('e.g., 10MB')
                            ->default([
                                'site_name' => 'My Application',
                                'items_per_page' => '20',
                                'enable_cache' => 'true',
                            ])
                            ->columnSpanFull(),

                        Forms\Components\KeyValue::make('meta_tags')
                            ->keyLabel('Meta Tag')
                            ->valueLabel('Content')
                            ->reorderable()
                            ->addable()
                            ->deletable()
                            ->editableKeys()
                            ->editableValues()
                            ->columnSpanFull(),

                        Forms\Components\KeyValue::make('email_settings')
                            ->schema([
                                Forms\Components\TextInput::make('value')
                                    ->required(),
                                Forms\Components\Toggle::make('enabled')
                                    ->default(true),
                            ])
                            ->addActionLabel('Add Email Setting')
                            ->columnSpanFull(),
                    ]),

                Forms\Components\Section::make('Feature Flags')
                    ->schema([
                        Forms\Components\Repeater::make('feature_flags')
                            ->schema([
                                Forms\Components\TextInput::make('name')
                                    ->required()
                                    ->maxLength(255),

                                Forms\Components\Toggle::make('enabled')
                                    ->default(false),

                                Forms\Components\Textarea::make('description')
                                    ->rows(2),

                                Forms\Components\KeyValue::make('parameters')
                                    ->columnSpanFull(),
                            ])
                            ->columns(2)
                            ->collapsible()
                            ->itemLabel(fn (array $state): ?string =>
                                $state['name'] ?? 'New Feature'
                            )
                            ->columnSpanFull(),
                    ]),
            ]);
    }
}
```

### Pattern 10: Real-Time Validation

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Forms\Get;
use Filament\Forms\Set;
use Illuminate\Validation\Rules\Password;

class RegistrationResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Account Information')
                    ->schema([
                        Forms\Components\TextInput::make('username')
                            ->required()
                            ->minLength(3)
                            ->maxLength(50)
                            ->unique(ignoreRecord: true)
                            ->alphaNum()
                            ->live(onBlur: true)
                            ->afterStateUpdated(function (Get $get, Set $set, $state) {
                                // Check username availability in real-time
                                $available = ! User::where('username', $state)->exists();

                                if (! $available) {
                                    $set('username_available', false);
                                } else {
                                    $set('username_available', true);
                                }
                            })
                            ->suffix(fn (Get $get) => $get('username_available') === true
                                ? '✓ Available'
                                : ($get('username_available') === false ? '✗ Taken' : '')
                            )
                            ->helperText('Choose a unique username (3-50 characters, letters and numbers only)'),

                        Forms\Components\Hidden::make('username_available'),

                        Forms\Components\TextInput::make('email')
                            ->email()
                            ->required()
                            ->unique(ignoreRecord: true)
                            ->live(onBlur: true)
                            ->afterStateUpdated(function ($state, callable $set) {
                                // Validate email format in real-time
                                if ($state && filter_var($state, FILTER_VALIDATE_EMAIL)) {
                                    // Check if email domain is disposable
                                    $domain = substr(strrchr($state, '@'), 1);
                                    $disposable = in_array($domain, ['tempmail.com', '10minutemail.com']);

                                    if ($disposable) {
                                        $set('email_warning', 'Disposable email addresses are not allowed');
                                    } else {
                                        $set('email_warning', null);
                                    }
                                }
                            })
                            ->helperText(fn (Get $get) => $get('email_warning')),

                        Forms\Components\Hidden::make('email_warning'),

                        Forms\Components\TextInput::make('password')
                            ->password()
                            ->required()
                            ->revealable()
                            ->rule(Password::min(8)
                                ->mixedCase()
                                ->letters()
                                ->numbers()
                                ->symbols()
                            )
                            ->live(onBlur: true)
                            ->afterStateUpdated(function ($state, callable $set) {
                                // Calculate password strength
                                $strength = 0;

                                if (strlen($state) >= 8) $strength++;
                                if (strlen($state) >= 12) $strength++;
                                if (preg_match('/[a-z]/', $state)) $strength++;
                                if (preg_match('/[A-Z]/', $state)) $strength++;
                                if (preg_match('/[0-9]/', $state)) $strength++;
                                if (preg_match('/[^a-zA-Z0-9]/', $state)) $strength++;

                                $set('password_strength', $strength);
                            })
                            ->helperText(function (Get $get) {
                                $strength = $get('password_strength') ?? 0;

                                return match (true) {
                                    $strength < 3 => '🔴 Weak password',
                                    $strength < 5 => '🟡 Medium password',
                                    default => '🟢 Strong password',
                                };
                            }),

                        Forms\Components\Hidden::make('password_strength'),

                        Forms\Components\TextInput::make('password_confirmation')
                            ->password()
                            ->required()
                            ->same('password')
                            ->revealable()
                            ->live(onBlur: true)
                            ->helperText('Re-enter your password to confirm'),
                    ])
                    ->columns(2),

                Forms\Components\Section::make('Profile')
                    ->schema([
                        Forms\Components\TextInput::make('phone')
                            ->tel()
                            ->live(onBlur: true)
                            ->afterStateUpdated(function ($state, callable $set) {
                                // Format phone number
                                $cleaned = preg_replace('/[^0-9]/', '', $state);
                                if (strlen($cleaned) === 10) {
                                    $formatted = sprintf('(%s) %s-%s',
                                        substr($cleaned, 0, 3),
                                        substr($cleaned, 3, 3),
                                        substr($cleaned, 6)
                                    );
                                    $set('phone', $formatted);
                                }
                            }),
                    ]),
            ]);
    }
}
```

## Testing Strategies

```php
<?php

namespace Tests\Feature\Filament\Forms;

use App\Filament\Resources\ProductResource;
use App\Models\Product;
use App\Models\User;
use Livewire\Livewire;
use Tests\TestCase;

class ProductFormTest extends TestCase
{
    public function test_form_renders_all_fields(): void
    {
        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\CreateProduct::class)
            ->assertFormExists()
            ->assertFormFieldExists('name')
            ->assertFormFieldExists('slug')
            ->assertFormFieldExists('price')
            ->assertFormFieldExists('description');
    }

    public function test_form_validates_required_fields(): void
    {
        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\CreateProduct::class)
            ->fillForm([
                'name' => null,
                'price' => null,
            ])
            ->call('create')
            ->assertHasFormErrors(['name', 'price']);
    }

    public function test_slug_auto_generates_from_name(): void
    {
        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\CreateProduct::class)
            ->fillForm(['name' => 'Test Product'])
            ->assertFormSet(['slug' => 'test-product']);
    }

    public function test_conditional_field_visibility(): void
    {
        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\CreateProduct::class)
            ->assertFormFieldIsVisible('standard_field')
            ->fillForm(['type' => 'digital'])
            ->assertFormFieldIsVisible('download_link')
            ->assertFormFieldIsHidden('shipping_weight');
    }

    public function test_repeater_can_add_items(): void
    {
        $this->actingAs(User::factory()->create());

        Livewire::test(InvoiceResource\Pages\CreateInvoice::class)
            ->assertFormFieldExists('items')
            ->fillForm([
                'items' => [
                    ['description' => 'Item 1', 'quantity' => 2, 'price' => 10],
                    ['description' => 'Item 2', 'quantity' => 1, 'price' => 20],
                ],
            ])
            ->call('create')
            ->assertHasNoFormErrors();

        expect(Invoice::first()->items)->toHaveCount(2);
    }
}
```

## Common Pitfalls

### Pitfall 1: Not Using reactive() for Dependent Fields

```php
// WRONG: Changes won't trigger updates
Forms\Components\Select::make('type')
    ->options([...]),

// CORRECT: Use reactive to trigger updates
Forms\Components\Select::make('type')
    ->options([...])
    ->reactive(),
```

### Pitfall 2: Forgetting dehydrated() on Disabled Fields

```php
// WRONG: Value won't save
Forms\Components\TextInput::make('calculated_field')
    ->disabled(),

// CORRECT: Use dehydrated to save
Forms\Components\TextInput::make('calculated_field')
    ->disabled()
    ->dehydrated(),
```

### Pitfall 3: Not Clearing Dependent Fields

```php
// WRONG: Old values remain
Forms\Components\Select::make('category')
    ->reactive(),

// CORRECT: Clear dependent fields
Forms\Components\Select::make('category')
    ->reactive()
    ->afterStateUpdated(fn (Set $set) => $set('subcategory', null)),
```

## Best Practices

1. **Use live() with debounce** for real-time validation without excessive server requests
2. **Implement afterStateUpdated** for dependent field logic
3. **Use sections and tabs** to organize complex forms logically
4. **Add helper text** to guide users on field requirements
5. **Validate file uploads** with appropriate size and type restrictions
6. **Use computed totals** in repeaters for dynamic calculations
7. **Implement conditional visibility** to simplify user experience
8. **Provide meaningful default values** for better UX
9. **Use KeyValue for flexible JSON storage** when structure varies
10. **Test form validation** thoroughly with edge cases

## Resources

- **Filament Forms Documentation**: https://filamentphp.com/docs/forms/overview
- **Form Fields**: https://filamentphp.com/docs/forms/fields
- **Form Layouts**: https://filamentphp.com/docs/forms/layout
- **Form Validation**: https://filamentphp.com/docs/forms/validation
- **Custom Fields**: https://filamentphp.com/docs/forms/custom-fields
