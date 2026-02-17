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

**InvoiceResource**
**Namespace**: `App\Filament\Resources\InvoiceResource`
**Docs**: https://filamentphp.com/docs/5.x/panels/resources

**Form Schema — Section: Invoice Details:**

| Field | Component | Configuration |
|-------|-----------|---------------|
| customer_id | Select | `->relationship('customer', 'name')->searchable()->preload()->required()` |
| number | TextInput | `->required()->disabled(fn ($context) => $context === 'edit')->default(fn () => 'INV-' . str_pad(Invoice::count() + 1, 5, '0', STR_PAD_LEFT))` |
| status | Select | `->options(InvoiceStatus::class)->default(InvoiceStatus::Draft)->required()` |

**Form Schema — Section: Line Items:**

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

**Actions — Mark as Sent:**

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

**Actions — Record Payment:**

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

## Filament 5 Namespace Reference

Every Blueprint component MUST use full namespaces. This is the #1 source of errors.

| Category | Namespace Pattern | Example |
|----------|------------------|---------|
| Form fields | `Filament\Forms\Components\{Component}` | `Filament\Forms\Components\TextInput` |
| Table columns | `Filament\Tables\Columns\{Column}` | `Filament\Tables\Columns\TextColumn` |
| Table filters | `Filament\Tables\Filters\{Filter}` | `Filament\Tables\Filters\SelectFilter` |
| Actions | `Filament\Actions\{Action}` | `Filament\Actions\Action` (NOT `Filament\Notifications\Actions\Action`) |
| Bulk actions | `Filament\Actions\BulkAction` | `Filament\Actions\BulkAction` |
| Icons (enum) | `Filament\Support\Icons\Heroicon` | `Heroicon::Pencil`, `Heroicon::PencilSquare` |
| Font weights (enum) | `Filament\Support\Enums\FontWeight` | `FontWeight::Bold`, `FontWeight::SemiBold` |
| Infolist entries | `Filament\Infolists\Components\{Entry}` | `Filament\Infolists\Components\TextEntry` |
| Layouts | `Filament\Schemas\Components\{Component}` | `Filament\Schemas\Components\Section` |
| Reactive utils | `Filament\Schemas\Components\Utilities\{Class}` | `Filament\Schemas\Components\Utilities\Get` |

**CRITICAL**: The reactive utilities `Get` and `Set` are at `Filament\Schemas\Components\Utilities\Get` and `Filament\Schemas\Components\Utilities\Set`. NOT `Filament\Forms\Get` or `Filament\Forms\Set`.

**CRITICAL**: Use `->live()` NOT `->reactive()`. The `reactive()` method does not exist in Filament 5.

## Form Field Selection by Data Type

| Data Type | Component | When to Use |
|-----------|-----------|-------------|
| String (short) | `TextInput` | Names, titles, codes |
| String (long) | `Textarea` | Descriptions, notes |
| Rich text | `RichEditor` | Formatted content |
| Enum (many options) | `Select` | Searchable, >10 options |
| Enum (few options) | `Radio` or `ToggleButtons` | 2-5 visible options |
| Enum (multi-select) | `CheckboxList` | Select multiple from <10 fixed |
| Boolean (setting) | `Toggle` | On/off preferences |
| Boolean (agreement) | `Checkbox` | Terms, confirmations |
| Date | `DatePicker` | Date only |
| DateTime | `DateTimePicker` | Date and time |
| Foreign key | `Select->relationship()` | Simple belongsTo |
| Foreign key (complex) | `ModalTableSelect` | Need multi-column search |
| belongsToMany | `Select->relationship()->multiple()` | Variable options, compact |
| hasMany (few) | `Repeater` | Inline editing, drag-reorder |
| hasMany (many) | RelationManager | Search, filter, independent lifecycle |
| JSON array | `TagsInput` | Free-form tags |
| Key-value pairs | `KeyValue` | Settings, metadata |
| File | `FileUpload` | Images, documents |
| Number (integer) | `TextInput->integer()` | Whole numbers |
| Number (decimal) | `TextInput->numeric()->step(0.01)` | Prices, measurements |
| Money | `TextInput->numeric()->prefix('$')` | Store as cents |

## Relationship Decision Tree

| Relationship | When to Use Select | When to Use ModalTableSelect | When to Use Repeater | When to Use RelationManager |
|-------------|-------------------|-----------------------------|--------------------|---------------------------|
| belongsTo | Default choice, simple title search | Need multi-column search, many records | N/A | N/A |
| hasMany | N/A | N/A | Few items, inline edit, drag-reorder | Many items, search/filter needed |
| belongsToMany | Variable options, compact UI | Need multi-column display | N/A | Need pivot data editing |

## Column Width Rules (CRITICAL)

Columns multiply through nesting. This is the most common layout mistake.

| Form Columns | Section Columns | Effective Width | Result |
|-------------|-----------------|-----------------|--------|
| 2 | 2 | 25% | TOO NARROW |
| 2 | 1 | 50% | OK |
| 1 | 2 | 50% | OK |
| 2 (with ColumnSpan: full) | 2 | 50% | OK |

**Rule**: If form has 2 columns and section has 2 columns, fields are 25% wide (too narrow for most inputs). Either set section `Columns: 1` or field `ColumnSpan: full`.

## Code Quality Checklist (FilaCheck Rules)

Before finalizing any Blueprint plan or implementation, verify against these rules:

### Performance Rules
| Rule | What to Check | Fix |
|------|--------------|-----|
| **Max ~10 visible columns** | Tables with >10 visible columns | Use `->toggleable(isToggledHiddenByDefault: true)` for less important columns |
| **Always defer loading** | Every `table()` method must use `->deferLoading()` | Loads data via AJAX after page render |
| **Eager load relationships** | Any dot-notation column (`user.name`) needs eager loading | Add `->modifyQueryUsing(fn (Builder $query) => $query->with([...]))` |
| **Searchable for 10+ options** | Select/CheckboxList/Radio with >=10 options | Add `->searchable()` for usability |

### Type Safety Rules
| Rule | Wrong | Correct |
|------|-------|---------|
| **Use Heroicon enum** | `->icon('heroicon-o-pencil')` | `->icon(Heroicon::Pencil)` with `use Filament\Support\Icons\Heroicon` |
| **Use FontWeight enum** | `->weight('bold')` | `->weight(FontWeight::Bold)` with `use Filament\Support\Enums\FontWeight` |
| **Use consolidated Action namespace** | `Filament\Notifications\Actions\Action` | `Filament\Actions\Action` |

### Redundancy Rules
| Rule | What to Check | Fix |
|------|--------------|-----|
| **No redundant ignoreRecord** | `->unique(ignoreRecord: true)` | `->unique()` -- `ignoreRecord: true` is the default in Filament 5 |
| **Custom theme for Tailwind** | Using Tailwind classes in Blade views | Must configure custom Filament theme via `->viteTheme()` and compile CSS |

## Common Planning Mistakes Checklist

| Mistake | Impact | Fix |
|---------|--------|-----|
| Missing namespaces | Implementing agent guesses wrong | Include full namespace for EVERY component |
| Vague specifications | "Add a status field" | Specify Component, Config, Validation, Docs URL |
| Missing scaffold commands | Files not created | Include all `php artisan make:*` commands |
| Nested columns too narrow | Fields cramped at 25% width | Check column multiplication rules |
| Components that don't exist | `Card` (use `Section`), `BadgeColumn` (use `TextColumn->badge()`) | Verify against Filament 5 docs |
| Wrong namespaces | `Filament\Forms\Get` | Use `Filament\Schemas\Components\Utilities\Get` |
| Wrong methods | `->reactive()` | Use `->live()` in Filament 5 |
| String icons/weights | `'heroicon-o-pencil'`, `'bold'` | Use `Heroicon::Pencil`, `FontWeight::Bold` enums |
| Missing tests | No quality assurance | Include authorization, validation, action tests |
| Unclear authorization | Vague permission rules | Specify exact ability + condition in plain English |
| `unique` in multi-tenant | Data leak across tenants | Use `scopedUnique:table,column` |
| Redundant ignoreRecord | Unnecessary code | `ignoreRecord: true` is default in Filament 5 |

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
13. **Plan in order** - Models → Resources → Authorization → Tests
14. **Verify syntax** - Check Filament docs that methods exist before planning

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
