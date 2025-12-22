# Wizard Forms

Filament 4 multi-step wizard forms for complex workflows.

## Basic Wizard

```php
use Filament\Forms;
use Filament\Forms\Components\Wizard;

Forms\Components\Wizard::make([
    Wizard\Step::make('Personal Info')
        ->schema([
            Forms\Components\TextInput::make('first_name')
                ->required(),
            Forms\Components\TextInput::make('last_name')
                ->required(),
            Forms\Components\DatePicker::make('birthdate')
                ->required(),
        ])
        ->columns(2),

    Wizard\Step::make('Contact')
        ->schema([
            Forms\Components\TextInput::make('email')
                ->email()
                ->required(),
            Forms\Components\TextInput::make('phone')
                ->tel(),
        ]),

    Wizard\Step::make('Review')
        ->schema([
            Forms\Components\Placeholder::make('review')
                ->content('Please review your information before submitting.'),
        ]),
])
    ->columnSpanFull();
```

## Wizard in Create Page

```php
<?php

namespace App\Filament\Resources\UserResource\Pages;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Forms\Components\Wizard;
use Filament\Resources\Pages\CreateRecord;

class CreateUser extends CreateRecord
{
    use CreateRecord\Concerns\HasWizard;

    protected static string $resource = UserResource::class;

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Wizard::make([
                    Wizard\Step::make('Account')
                        ->icon('heroicon-o-user')
                        ->description('Basic account information')
                        ->schema([
                            Forms\Components\TextInput::make('name')
                                ->required()
                                ->maxLength(255),

                            Forms\Components\TextInput::make('email')
                                ->email()
                                ->required()
                                ->unique(),

                            Forms\Components\TextInput::make('password')
                                ->password()
                                ->required()
                                ->minLength(8)
                                ->confirmed()
                                ->revealable(),

                            Forms\Components\TextInput::make('password_confirmation')
                                ->password()
                                ->required()
                                ->revealable(),
                        ])
                        ->columns(2),

                    Wizard\Step::make('Profile')
                        ->icon('heroicon-o-identification')
                        ->description('Personal details')
                        ->schema([
                            Forms\Components\FileUpload::make('avatar')
                                ->image()
                                ->avatar()
                                ->directory('avatars'),

                            Forms\Components\Select::make('department')
                                ->options([
                                    'sales' => 'Sales',
                                    'marketing' => 'Marketing',
                                    'engineering' => 'Engineering',
                                ])
                                ->required(),

                            Forms\Components\TextInput::make('job_title')
                                ->required(),

                            Forms\Components\DatePicker::make('hire_date')
                                ->required()
                                ->default(now()),
                        ])
                        ->columns(2),

                    Wizard\Step::make('Permissions')
                        ->icon('heroicon-o-key')
                        ->description('Access and roles')
                        ->schema([
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
                        ]),
                ])
                    ->columnSpanFull()
                    ->persistStepInQueryString()
                    ->submitAction(view('filament.wizard-submit')),
            ]);
    }

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('index');
    }
}
```

## Step Validation

```php
Wizard\Step::make('Account')
    ->schema([
        Forms\Components\TextInput::make('email')
            ->email()
            ->required()
            ->unique(),

        Forms\Components\TextInput::make('password')
            ->password()
            ->required()
            ->minLength(8),
    ])
    // Validate before moving to next step
    ->afterValidation(function () {
        // Custom validation passed
        \Notification::make()
            ->success()
            ->title('Step validated')
            ->send();
    })
    ->beforeValidation(function () {
        // Run before validation
    });
```

## Conditional Steps

```php
Forms\Components\Select::make('account_type')
    ->options([
        'personal' => 'Personal',
        'business' => 'Business',
    ])
    ->reactive()
    ->required(),

Wizard::make([
    Wizard\Step::make('Basic Info')
        ->schema([...]),

    Wizard\Step::make('Personal Details')
        ->schema([
            Forms\Components\TextInput::make('ssn')
                ->label('SSN')
                ->required(),
        ])
        ->visible(fn (Get $get) => $get('account_type') === 'personal'),

    Wizard\Step::make('Business Details')
        ->schema([
            Forms\Components\TextInput::make('ein')
                ->label('EIN')
                ->required(),
            Forms\Components\TextInput::make('company_name')
                ->required(),
        ])
        ->visible(fn (Get $get) => $get('account_type') === 'business'),

    Wizard\Step::make('Review')
        ->schema([...]),
]);
```

## Step Icons and Badges

```php
Wizard\Step::make('Account')
    ->icon('heroicon-o-user')
    ->completedIcon('heroicon-o-check-circle')
    ->description('Create your account')
    ->badge('Required')
    ->schema([...]);
```

## Wizard Options

```php
Wizard::make([...])
    // Persist step in URL
    ->persistStepInQueryString()
    ->persistStepInQueryString('wizard-step') // Custom key

    // Navigation
    ->skippable() // Allow skipping steps
    ->startOnStep(2) // Start on specific step

    // Actions
    ->nextAction(
        fn (Forms\Components\Actions\Action $action) => $action
            ->label('Continue')
            ->icon('heroicon-o-arrow-right')
    )
    ->previousAction(
        fn (Forms\Components\Actions\Action $action) => $action
            ->label('Back')
            ->icon('heroicon-o-arrow-left')
    )
    ->submitAction(
        fn (Forms\Components\Actions\Action $action) => $action
            ->label('Create Account')
            ->icon('heroicon-o-check')
    )

    // Callbacks
    ->afterValidation(function () {
        // After step validation
    });
```

## Step Lifecycle Hooks

```php
Wizard\Step::make('Payment')
    ->schema([...])

    // Before moving to next step
    ->beforeValidation(function (Get $get, Set $set) {
        // Prepare data
    })

    // After validation passes
    ->afterValidation(function (Get $get, Set $set) {
        // Process validated data
        $set('payment_verified', true);
    });
```

## Custom Submit Button View

```blade
{{-- resources/views/filament/wizard-submit.blade.php --}}
<x-filament::button
    type="submit"
    size="lg"
    color="success"
    icon="heroicon-o-check"
    wire:loading.attr="disabled"
>
    <span wire:loading.remove>Create Account</span>
    <span wire:loading>Processing...</span>
</x-filament::button>
```

## Complete Onboarding Example

```php
class CreateCompany extends CreateRecord
{
    use CreateRecord\Concerns\HasWizard;

    protected static string $resource = CompanyResource::class;

    public function form(Form $form): Form
    {
        return $form->schema([
            Wizard::make([
                Wizard\Step::make('Company Info')
                    ->icon('heroicon-o-building-office')
                    ->description('Basic company information')
                    ->schema([
                        Forms\Components\TextInput::make('name')
                            ->required()
                            ->maxLength(255)
                            ->live(onBlur: true)
                            ->afterStateUpdated(fn ($state, Set $set) =>
                                $set('slug', \Str::slug($state))
                            ),

                        Forms\Components\TextInput::make('slug')
                            ->required()
                            ->unique()
                            ->disabled()
                            ->dehydrated(),

                        Forms\Components\Select::make('industry')
                            ->options([
                                'tech' => 'Technology',
                                'finance' => 'Finance',
                                'healthcare' => 'Healthcare',
                                'retail' => 'Retail',
                            ])
                            ->required(),

                        Forms\Components\TextInput::make('website')
                            ->url()
                            ->prefixIcon('heroicon-o-globe-alt'),

                        Forms\Components\FileUpload::make('logo')
                            ->image()
                            ->imageEditor()
                            ->directory('company-logos')
                            ->columnSpanFull(),
                    ])
                    ->columns(2),

                Wizard\Step::make('Address')
                    ->icon('heroicon-o-map-pin')
                    ->description('Company location')
                    ->schema([
                        Forms\Components\TextInput::make('street')
                            ->required()
                            ->columnSpanFull(),

                        Forms\Components\TextInput::make('city')
                            ->required(),

                        Forms\Components\Select::make('state')
                            ->options([...])
                            ->searchable()
                            ->required(),

                        Forms\Components\TextInput::make('zip')
                            ->required(),

                        Forms\Components\Select::make('country')
                            ->options([...])
                            ->searchable()
                            ->default('US')
                            ->required(),
                    ])
                    ->columns(2),

                Wizard\Step::make('Billing')
                    ->icon('heroicon-o-credit-card')
                    ->description('Payment information')
                    ->schema([
                        Forms\Components\Select::make('plan')
                            ->options([
                                'starter' => 'Starter - $29/mo',
                                'pro' => 'Pro - $99/mo',
                                'enterprise' => 'Enterprise - $299/mo',
                            ])
                            ->required()
                            ->reactive(),

                        Forms\Components\Toggle::make('annual_billing')
                            ->label('Annual Billing (Save 20%)')
                            ->default(false),

                        Forms\Components\Placeholder::make('price')
                            ->content(function (Get $get) {
                                $plan = $get('plan');
                                $annual = $get('annual_billing');

                                $prices = [
                                    'starter' => 29,
                                    'pro' => 99,
                                    'enterprise' => 299,
                                ];

                                $price = $prices[$plan] ?? 0;
                                if ($annual) {
                                    $price = $price * 12 * 0.8;
                                    return '$' . number_format($price) . '/year';
                                }
                                return '$' . $price . '/month';
                            }),
                    ]),

                Wizard\Step::make('Review')
                    ->icon('heroicon-o-clipboard-document-check')
                    ->description('Confirm your details')
                    ->schema([
                        Forms\Components\Placeholder::make('review_notice')
                            ->content('Please review your company details before creating.')
                            ->columnSpanFull(),
                    ]),
            ])
                ->columnSpanFull()
                ->persistStepInQueryString()
                ->submitAction(view('filament.wizard-submit')),
        ]);
    }
}
```
