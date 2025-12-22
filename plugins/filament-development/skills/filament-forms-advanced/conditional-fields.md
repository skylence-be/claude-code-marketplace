# Conditional Fields

Filament 4 conditional field visibility, requirements, and dynamic state.

## Basic Visibility

```php
use Filament\Forms;
use Filament\Forms\Get;
use Filament\Forms\Set;

// Show field based on another field's value
Forms\Components\Select::make('account_type')
    ->options([
        'personal' => 'Personal',
        'business' => 'Business',
    ])
    ->required()
    ->reactive(), // Required for conditional updates

Forms\Components\TextInput::make('company_name')
    ->visible(fn (Get $get): bool => $get('account_type') === 'business')
    ->required(fn (Get $get): bool => $get('account_type') === 'business'),

Forms\Components\TextInput::make('tax_id')
    ->visible(fn (Get $get): bool => $get('account_type') === 'business'),
```

## Hidden vs Visible

```php
// hidden() - Hide when condition is true
Forms\Components\TextInput::make('personal_field')
    ->hidden(fn (Get $get): bool => $get('type') === 'business');

// visible() - Show when condition is true
Forms\Components\TextInput::make('business_field')
    ->visible(fn (Get $get): bool => $get('type') === 'business');
```

## Conditional Requirements

```php
Forms\Components\Toggle::make('has_discount')
    ->reactive(),

Forms\Components\TextInput::make('discount_code')
    ->visible(fn (Get $get): bool => $get('has_discount'))
    ->required(fn (Get $get): bool => $get('has_discount')),

Forms\Components\TextInput::make('discount_percentage')
    ->visible(fn (Get $get): bool => $get('has_discount'))
    ->required(fn (Get $get): bool => $get('has_discount'))
    ->numeric()
    ->minValue(1)
    ->maxValue(100),
```

## Conditional Disabled State

```php
Forms\Components\Select::make('subscription_plan')
    ->options([
        'free' => 'Free',
        'pro' => 'Pro',
        'enterprise' => 'Enterprise',
    ])
    ->reactive(),

Forms\Components\TextInput::make('api_limit')
    ->disabled(fn (Get $get): bool => $get('subscription_plan') === 'free')
    ->default(fn (Get $get): int => match($get('subscription_plan')) {
        'free' => 100,
        'pro' => 10000,
        'enterprise' => 0, // Unlimited
        default => 100,
    }),
```

## AfterStateUpdated - Reacting to Changes

```php
Forms\Components\Select::make('category_id')
    ->options(Category::pluck('name', 'id'))
    ->reactive()
    ->afterStateUpdated(function (Set $set, $state) {
        // Clear dependent fields when category changes
        $set('subcategory_id', null);
        $set('product_type_id', null);

        // Set default values based on category
        if ($state) {
            $category = Category::find($state);
            $set('tax_rate', $category->default_tax_rate);
        }
    }),

Forms\Components\Select::make('subcategory_id')
    ->options(function (Get $get) {
        $categoryId = $get('category_id');
        if (!$categoryId) {
            return [];
        }
        return Category::where('parent_id', $categoryId)->pluck('name', 'id');
    })
    ->disabled(fn (Get $get): bool => !$get('category_id'))
    ->reactive()
    ->afterStateUpdated(fn (Set $set) => $set('product_type_id', null)),
```

## Live Updates

```php
// live() - Updates on every change
Forms\Components\TextInput::make('title')
    ->live()
    ->afterStateUpdated(function ($state, Set $set) {
        $set('slug', \Str::slug($state));
    }),

// live(onBlur: true) - Updates when field loses focus
Forms\Components\TextInput::make('email')
    ->email()
    ->live(onBlur: true)
    ->afterStateUpdated(function ($state, Set $set) {
        // Check if email exists
        $exists = User::where('email', $state)->exists();
        $set('email_exists', $exists);
    }),

// live(debounce: 500) - Updates after pause in typing
Forms\Components\TextInput::make('search')
    ->live(debounce: 500)
    ->afterStateUpdated(function ($state, Set $set) {
        $results = Product::search($state)->get();
        $set('search_results', $results->pluck('name', 'id')->toArray());
    }),
```

## Multiple Conditions

```php
Forms\Components\Select::make('order_type')
    ->options(['delivery' => 'Delivery', 'pickup' => 'Pickup', 'dine_in' => 'Dine In'])
    ->reactive(),

Forms\Components\Toggle::make('express_delivery')
    ->reactive()
    ->visible(fn (Get $get): bool => $get('order_type') === 'delivery'),

// Show only for express delivery orders
Forms\Components\TextInput::make('express_fee')
    ->visible(fn (Get $get): bool =>
        $get('order_type') === 'delivery' && $get('express_delivery')
    )
    ->disabled()
    ->dehydrated()
    ->default(9.99),
```

## Conditional Validation

```php
Forms\Components\TextInput::make('password')
    ->password()
    ->required(fn (string $context): bool => $context === 'create')
    ->minLength(8)
    ->confirmed(),

Forms\Components\TextInput::make('password_confirmation')
    ->password()
    ->required(fn (string $context): bool => $context === 'create')
    ->visible(fn (string $context): bool => $context === 'create'),
```

## Accessing Parent/Nested State

```php
// In a Repeater, access parent state
Forms\Components\Repeater::make('items')
    ->schema([
        Forms\Components\TextInput::make('name'),

        Forms\Components\TextInput::make('discount')
            // Access parent form state with '../'
            ->visible(fn (Get $get): bool => $get('../../has_discounts')),

        Forms\Components\Select::make('tax_rate')
            // Access sibling repeater item
            ->options(fn (Get $get) => $get('../category_id')
                ? TaxRate::where('category_id', $get('../category_id'))->pluck('name', 'id')
                : []
            ),
    ]),
```

## Complex Conditional Logic

```php
class OrderResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form->schema([
            Forms\Components\Radio::make('order_type')
                ->options([
                    'delivery' => 'Delivery',
                    'pickup' => 'Pickup',
                    'dine_in' => 'Dine In',
                ])
                ->reactive()
                ->afterStateUpdated(function (Set $set, $state) {
                    // Reset all conditional fields
                    if ($state !== 'delivery') {
                        $set('delivery_address', null);
                        $set('delivery_fee', 0);
                    }
                    if ($state !== 'pickup') {
                        $set('pickup_location', null);
                    }
                    if ($state !== 'dine_in') {
                        $set('table_number', null);
                    }
                }),

            // Delivery Section
            Forms\Components\Section::make('Delivery Information')
                ->visible(fn (Get $get): bool => $get('order_type') === 'delivery')
                ->schema([
                    Forms\Components\TextInput::make('delivery_address')
                        ->required()
                        ->live(onBlur: true)
                        ->afterStateUpdated(function ($state, Set $set) {
                            $fee = self::calculateDeliveryFee($state);
                            $set('delivery_fee', $fee);
                        }),

                    Forms\Components\TextInput::make('delivery_fee')
                        ->disabled()
                        ->dehydrated()
                        ->prefix('$'),
                ]),

            // Pickup Section
            Forms\Components\Section::make('Pickup Information')
                ->visible(fn (Get $get): bool => $get('order_type') === 'pickup')
                ->schema([
                    Forms\Components\Select::make('pickup_location')
                        ->options(Location::pluck('name', 'id'))
                        ->required(),
                ]),

            // Dine-In Section
            Forms\Components\Section::make('Table Information')
                ->visible(fn (Get $get): bool => $get('order_type') === 'dine_in')
                ->schema([
                    Forms\Components\TextInput::make('table_number')
                        ->required()
                        ->numeric(),
                ]),
        ]);
    }
}
```
