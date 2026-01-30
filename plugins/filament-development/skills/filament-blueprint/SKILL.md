---
name: filament-blueprint
description: Master Filament Blueprint - the AI planning format for generating accurate, production-ready Filament code. Use when planning complex Filament implementations, creating detailed specifications, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
category: filament
tags: [filament, blueprint, ai, planning, architecture, specification]
related_skills: [filament-resource-patterns, filament-forms-advanced, filament-tables-optimization]
---

# Filament Blueprint

Filament Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Filament projects. It bridges the gap between high-level requirements and production-ready code.

## When to Use This Skill

- Planning complex Filament admin panel implementations
- Creating detailed specifications before writing code
- Generating comprehensive resource architectures
- Documenting user flows and interactions
- Ensuring all details are captured (namespaces, methods, components)
- Avoiding vague plans that lead to vague code

## Blueprint Plan Structure

A complete Blueprint includes these sections:

### 1. Overview & Key Decisions

```markdown
# Invoice Management System

A single-tenant admin panel for managing invoices.

## Key Decisions
- Manual invoice sending (no automated emails)
- Partial payments supported
- Monetary values stored as cents (integers)
- Status-driven action visibility
```

### 2. User Flows

Document step-by-step interactions:

```markdown
## User Flows

### Creating an Invoice
1. User navigates to Invoices > Create
2. Selects customer (searchable dropdown)
3. Adds line items via repeater:
   - Product selection (preloads price)
   - Quantity input (live updates subtotal)
   - Subtotal calculated: quantity × unit_price
4. Tax rate entry (optional, default 0%)
5. System calculates: subtotal + (subtotal × tax_rate / 100)
6. Saves as Draft status
```

### 3. Artisan Commands

Sequential commands for scaffolding:

```markdown
## Commands

php artisan make:model Invoice -mf --no-interaction
php artisan make:model Customer -mf --no-interaction
php artisan make:filament-resource CustomerResource --generate --no-interaction
php artisan make:filament-relation-manager CustomerResource invoices --no-interaction
```

### 4. Models Specification

Include exact attributes, relationships, and methods:

```markdown
## Models

### Invoice
**Table**: invoices

| Column | Type | Constraints |
|--------|------|-------------|
| id | uuid | primary |
| customer_id | foreignId | required, constrained |
| number | string | required, unique |
| status | string | default: draft |
| subtotal | integer | default: 0 (cents) |
| tax_rate | decimal(5,2) | default: 0 |
| total | integer | default: 0 (cents) |

**Relationships**:
- belongsTo: Customer
- hasMany: InvoiceItem, Payment

**Accessors**:
- balance_due: total - amount_paid

**Traits**: SoftDeletes, HasUuids
```

### 5. Enums

Define status enums with Filament contracts:

```markdown
## Enums

### InvoiceStatus
Implements: HasLabel, HasColor, HasIcon

| Case | Label | Color | Icon |
|------|-------|-------|------|
| Draft | Draft | gray | pencil |
| Sent | Sent | info | paper-airplane |
| Paid | Paid | success | check-circle |
| Overdue | Overdue | danger | exclamation-circle |
```

### 6. Resource Specifications

Complete resource with form, table, and actions:

```markdown
## Resources

### InvoiceResource
**Namespace**: App\Filament\Resources
**Navigation**: Group: Sales, Icon: document-text, Sort: 2

#### Form Schema
- Section "Invoice Details":
  - Select customer_id: relationship, searchable, preload, required
  - TextInput number: required, disabled on edit, default: auto-generated
  - Select status: enum options, default: draft

- Section "Line Items":
  - Repeater items: relationship
    - Select product_id: relationship, searchable, afterStateUpdated: fill unit_price
    - TextInput quantity: numeric, default: 1, live
    - TextInput unit_price: numeric, prefix: $, divideBy: 100
    - Placeholder subtotal: calculated, money format

- Section "Totals":
  - TextInput tax_rate: numeric, suffix: %, default: 0
  - Placeholder subtotal: sum of line items
  - Placeholder total: subtotal + tax

#### Table Columns
| Column | Type | Searchable | Sortable |
|--------|------|------------|----------|
| number | Text | yes | yes |
| customer.name | Text | yes | yes |
| status | Badge (enum) | no | yes |
| total | Text (money) | no | yes |
| created_at | Date | no | yes |

#### Actions
| Action | Icon | Color | Visible When | Confirmation |
|--------|------|-------|--------------|--------------|
| Send | paper-airplane | info | status = draft | yes |
| Record Payment | currency-dollar | success | status in [sent, overdue] | modal form |
| Mark Paid | check | success | balance_due = 0 | yes |
```

### 7. Relation Managers

```markdown
## Relation Managers

### PaymentsRelationManager
**For**: InvoiceResource
**Relationship**: payments
**Create**: disabled (use Record Payment action)
**Edit**: enabled
**Delete**: enabled with confirmation
```

### 8. Authorization

```markdown
## Authorization

### InvoicePolicy
- viewAny: all authenticated users
- view: owner or admin
- create: all authenticated users
- update: owner, status = draft
- delete: owner, status = draft
```

### 9. Testing Strategy

```markdown
## Testing

### InvoiceResourceTest

**Validation Tests** (dataset pattern):
- number required
- customer_id required
- items required (min 1)

**Component Tests**:
- unit_price column displays as money
- status column displays correct badge colors

**Action Tests**:
- Send action only visible when draft
- Record Payment validates amount <= balance_due
- Mark Paid only visible when balance = 0
```

### 10. Verification Checklist

```markdown
## Verification

### Manual Testing
1. [ ] Access panel at /admin
2. [ ] Create customer with all fields
3. [ ] Create invoice with 3+ line items
4. [ ] Verify calculations update live
5. [ ] Send invoice (status changes)
6. [ ] Record partial payment
7. [ ] Record remaining payment
8. [ ] Verify Mark Paid action appears

### Automated
php artisan test --filter=InvoiceResourceTest
```

## Vague Plan vs Blueprint: Critical Differences

A vague plan answers "what to build" but leaves "how" to interpretation. A Blueprint provides **implementation-ready specifications** with exact code patterns.

### ❌ VAGUE PLAN (Before Blueprint)

```markdown
## InvoiceResource
- Customer dropdown (searchable)
- Line items repeater
- Total calculation
- Send action
- Record Payment action
```

**Problems:**
- No field configurations or validation rules
- No `afterStateUpdated` callbacks for live updates
- No visibility conditions for actions
- No modal form specifications
- No documentation references

### ✅ BLUEPRINT (Implementation-Ready)

```markdown
## InvoiceResource
**Namespace**: App\Filament\Resources\InvoiceResource
**Docs**: https://filamentphp.com/docs/5.x/panels/resources

### Form Schema

#### Section: Invoice Details
| Field | Component | Configuration |
|-------|-----------|---------------|
| customer_id | Select | `->relationship('customer', 'name')->searchable()->preload()->required()` |
| number | TextInput | `->required()->disabled(fn ($context) => $context === 'edit')->default(fn () => 'INV-' . str_pad(Invoice::count() + 1, 5, '0', STR_PAD_LEFT))` |
| status | Select | `->options(InvoiceStatus::class)->default(InvoiceStatus::Draft)->required()` |

#### Section: Line Items
```php
Repeater::make('items')
    ->relationship()
    ->schema([
        Select::make('product_id')
            ->relationship('product', 'name')
            ->searchable()
            ->preload()
            ->required()
            ->afterStateUpdated(fn (Set $set, ?string $state) =>
                $set('unit_price', Product::find($state)?->price ?? 0)
            )
            ->live(),

        TextInput::make('quantity')
            ->numeric()
            ->default(1)
            ->required()
            ->live()
            ->afterStateUpdated(fn (Set $set, Get $get) =>
                $set('subtotal', $get('quantity') * $get('unit_price'))
            ),

        TextInput::make('unit_price')
            ->numeric()
            ->prefix('$')
            ->disabled()
            ->dehydrated()
            ->formatStateUsing(fn (?int $state) => $state / 100)
            ->mutateStateForValidationUsing(fn (?float $state) => $state * 100),

        Placeholder::make('subtotal')
            ->content(fn (Get $get): string =>
                '$' . number_format(($get('quantity') ?? 0) * ($get('unit_price') ?? 0) / 100, 2)
            ),
    ])
    ->columns(4)
    ->defaultItems(1)
    ->addActionLabel('Add line item')
    ->reorderable()
    ->collapsible()
```

### Actions

#### Mark as Sent
```php
Action::make('markAsSent')
    ->icon('heroicon-o-paper-airplane')
    ->color('info')
    ->visible(fn (Invoice $record): bool =>
        $record->status === InvoiceStatus::Draft
    )
    ->requiresConfirmation()
    ->modalHeading('Send Invoice')
    ->modalDescription('This will mark the invoice as sent and notify the customer.')
    ->action(function (Invoice $record): void {
        $record->update([
            'status' => InvoiceStatus::Sent,
            'sent_at' => now(),
        ]);

        Notification::make()
            ->title('Invoice sent')
            ->success()
            ->send();
    })
```

#### Record Payment
```php
Action::make('recordPayment')
    ->icon('heroicon-o-currency-dollar')
    ->color('success')
    ->visible(fn (Invoice $record): bool =>
        in_array($record->status, [InvoiceStatus::Sent, InvoiceStatus::Overdue])
    )
    ->form([
        TextInput::make('amount')
            ->numeric()
            ->prefix('$')
            ->required()
            ->default(fn (Invoice $record): float => $record->balance_due / 100)
            ->rules([
                fn (Invoice $record): Closure => function (string $attribute, $value, Closure $fail) use ($record) {
                    if ($value * 100 > $record->balance_due) {
                        $fail('Amount cannot exceed balance due.');
                    }
                },
            ]),
        Select::make('method')
            ->options(PaymentMethod::class)
            ->required()
            ->default(PaymentMethod::BankTransfer),
        Textarea::make('notes')
            ->rows(2),
    ])
    ->action(function (Invoice $record, array $data): void {
        $record->payments()->create([
            'amount' => $data['amount'] * 100,
            'method' => $data['method'],
            'notes' => $data['notes'],
            'paid_at' => now(),
        ]);

        $record->increment('amount_paid', $data['amount'] * 100);

        if ($record->balance_due === 0) {
            $record->update(['status' => InvoiceStatus::Paid]);
        }

        Notification::make()
            ->title('Payment recorded')
            ->success()
            ->send();
    })
```
```

## Best Practices

1. **Be explicit** - Include namespaces, method signatures, exact syntax
2. **Include documentation links** - Reference official Filament docs for each component
3. **Show complete code** - Not just names, but full configurations
4. **Document calculations** - Show formulas: `total = subtotal + (subtotal × tax_rate / 100)`
5. **Specify money handling** - Store as cents (integers), display with `divideBy: 100`
6. **Map action visibility** - Exact conditions with enum comparisons
7. **Include validation closures** - For complex rules like "amount <= balance_due"
8. **Show afterStateUpdated** - For live field updates and calculations
9. **Include modal forms** - For actions that need additional input
10. **Define relationships** - Document both directions with cardinality
11. **Test with datasets** - Parameterized tests for validation rules
12. **File inventory** - Categorized list of all generated files

## Anti-Patterns to Avoid

| ❌ Vague | ✅ Blueprint |
|----------|-------------|
| "searchable dropdown" | `->searchable()->preload()->required()` |
| "calculate total" | `afterStateUpdated` callback with formula |
| "Send button" | Full Action with visibility, confirmation, notification |
| "validates amount" | Closure rule with exact comparison |
| "updates status" | `$record->update(['status' => InvoiceStatus::Sent])` |
| "shows loading" | `wire:loading` with proper targets |

## Common Patterns

### Monetary Values
- Store in cents (integers) in database
- Display with `->divideBy(100)` in forms/tables
- Use `->prefix('$')` or `->money('USD')`

### Status-Driven Actions
```php
->visible(fn (Invoice $record): bool => $record->status === InvoiceStatus::Draft)
```

### Live Calculations
```php
TextInput::make('quantity')
    ->live()
    ->afterStateUpdated(fn (Set $set, Get $get) =>
        $set('subtotal', $get('quantity') * $get('unit_price'))
    )
```

### Auto-Generated Numbers
```php
->default(fn () => 'INV-' . str_pad(Invoice::count() + 1, 5, '0', STR_PAD_LEFT))
```

### Repeater with Live Calculations
```php
Repeater::make('items')
    ->relationship()
    ->schema([...])
    ->live()
    ->afterStateUpdated(function (Get $get, Set $set) {
        $items = $get('items') ?? [];
        $subtotal = collect($items)->sum(fn ($item) =>
            ($item['quantity'] ?? 0) * ($item['unit_price'] ?? 0)
        );
        $set('subtotal', $subtotal);
        $set('total', $subtotal + ($subtotal * ($get('tax_rate') ?? 0) / 100));
    })
```

### Modal Form Action with Validation
```php
Action::make('recordPayment')
    ->form([
        TextInput::make('amount')
            ->required()
            ->numeric()
            ->prefix('$')
            ->default(fn (Invoice $record) => $record->balance_due / 100)
            ->rules([
                fn (Invoice $record): Closure => function ($attr, $val, $fail) use ($record) {
                    if ($val * 100 > $record->balance_due) {
                        $fail('Amount exceeds balance due.');
                    }
                },
            ]),
    ])
    ->action(fn (Invoice $record, array $data) => ...)
```

## File Inventory Template

Every Blueprint should end with a categorized file list:

```markdown
## Files

### Enums (2)
- app/Enums/InvoiceStatus.php
- app/Enums/PaymentMethod.php

### Models (5)
- app/Models/Customer.php
- app/Models/Product.php
- app/Models/Invoice.php
- app/Models/InvoiceItem.php
- app/Models/Payment.php

### Resources (3)
- app/Filament/Resources/CustomerResource.php
  - app/Filament/Resources/CustomerResource/Pages/ListCustomers.php
  - app/Filament/Resources/CustomerResource/Pages/CreateCustomer.php
  - app/Filament/Resources/CustomerResource/Pages/EditCustomer.php
- app/Filament/Resources/ProductResource.php
- app/Filament/Resources/InvoiceResource.php

### Relation Managers (2)
- app/Filament/Resources/CustomerResource/RelationManagers/InvoicesRelationManager.php
- app/Filament/Resources/InvoiceResource/RelationManagers/PaymentsRelationManager.php

### Migrations (5)
- database/migrations/xxxx_create_customers_table.php
- database/migrations/xxxx_create_products_table.php
- database/migrations/xxxx_create_invoices_table.php
- database/migrations/xxxx_create_invoice_items_table.php
- database/migrations/xxxx_create_payments_table.php

### Factories (5)
- database/factories/CustomerFactory.php
- database/factories/ProductFactory.php
- database/factories/InvoiceFactory.php
- database/factories/InvoiceItemFactory.php
- database/factories/PaymentFactory.php

### Tests (3)
- tests/Feature/Filament/CustomerResourceTest.php
- tests/Feature/Filament/ProductResourceTest.php
- tests/Feature/Filament/InvoiceResourceTest.php
```

## Testing Patterns

### Dataset Pattern for Validation
```php
it('validates required fields', function (string $field) {
    livewire(CreateInvoice::class)
        ->fillForm([$field => null])
        ->call('create')
        ->assertHasFormErrors([$field => 'required']);
})->with(['customer_id', 'number', 'items']);
```

### Component Configuration Tests
```php
it('displays unit_price as money', function () {
    $product = Product::factory()->create(['price' => 1999]);

    livewire(ListProducts::class)
        ->assertTableColumnFormattedStateSet('price', '$19.99', $product);
});
```

### Action Visibility Tests
```php
it('shows Send action only for draft invoices', function () {
    $draft = Invoice::factory()->draft()->create();
    $sent = Invoice::factory()->sent()->create();

    livewire(ListInvoices::class)
        ->assertTableActionVisible('markAsSent', $draft)
        ->assertTableActionHidden('markAsSent', $sent);
});
```

### Action Behavior Tests
```php
it('validates payment amount does not exceed balance', function () {
    $invoice = Invoice::factory()->create(['total' => 10000, 'amount_paid' => 5000]);

    livewire(EditInvoice::class, ['record' => $invoice])
        ->callAction('recordPayment', ['amount' => 100]) // $100 > $50 balance
        ->assertHasActionErrors(['amount']);
});
```
