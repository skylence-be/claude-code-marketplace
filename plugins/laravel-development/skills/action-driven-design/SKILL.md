---
name: action-driven-design
description: Master action-driven architecture with typed DTOs, constructor-promoted dependencies, and form request bridges. Use when creating actions, DTOs, form requests, or refactoring services into actions.
---

# Action-Driven Design (The Default Architecture)

Plain PHP action classes. No `lorisleiva/laravel-actions` package. The constraint is the convention, not the framework — and the convention is enforced by Pest architecture tests. No runtime framework needed.

## Quick Reference

| Rule | Summary |
|------|---------|
| One public method | `execute` — not `handle`, not `__invoke`, not `run` |
| Input is typed DTO | Spatie laravel-data DTO — never `array $data`, never primitive parameter list |
| Return is typed | Model, value object, or `void` for pure side effects — never `mixed`, never `array` |
| Side effects in PHPDoc | Document events, jobs, mail fired in class-level PHPDoc |
| `final` by default | Override only with comment explaining why |
| No HTTP knowledge | Action never sees `Request` — form request maps to DTO first |
| Constructor-promoted deps | `private readonly` — no setter injection, no `app()` calls |
| No static methods | Actions are container-resolved instances |
| Namespace | `App\Actions\{Domain}\{Verb}{Noun}Action` |
| Testing | Unit test (action in isolation) + Feature test (through entry point) |

## What an Action Is

A class with one public method (`execute`), one typed DTO input, one typed return. Side effects are explicit and documented. The class is final unless there's a documented reason to extend it.

## Canonical Shape

```php
<?php

namespace App\Actions\Invoices;

use App\Data\Invoices\CreateInvoiceData;
use App\Events\Invoices\InvoiceCreated;
use App\Models\Invoice;

/**
 * Create an invoice and fire the InvoiceCreated event.
 *
 * Side effects:
 * - persists Invoice
 * - dispatches InvoiceCreated event
 */
final class CreateInvoiceAction
{
    public function execute(CreateInvoiceData $data): Invoice
    {
        $invoice = Invoice::create($data->toArray());

        InvoiceCreated::dispatch($invoice);

        return $invoice;
    }
}
```

## Rules

1. **One public method.** Anything else is design smell. If you need helpers, make them private. If you need too many private helpers, you have multiple actions hiding in a trench coat — split them.
2. **The method is `execute`.** Not `handle`. Not `__invoke`. Not `run`. Pick one name, use it everywhere — makes grep cheap | call sites scannable.
3. **Input is typed DTO.** Spatie laravel-data DTO — `final class CreateInvoiceData extends \Spatie\LaravelData\Data` with readonly constructor-promoted properties. Never `array $data`. Never primitive parameter list (no `execute(int $userId, string $email, array $items)` — that's three arguments asking to become DTO).
4. **Return is typed and meaningful.** Return model you created | value object you computed. Return `void` if action's whole point is side effect (e.g. `SendWelcomeEmailAction::execute(): void`). Never return `mixed`. Never return `array`.
5. **Side effects documented in PHPDoc.** Anyone reading class without opening it should know what events | jobs | mail it fires. Verifier checks this.
6. **`final` by default.** Override only with comment explaining why subclassing is wanted.
7. **No constructor dependencies that aren't real collaborators.** If you find yourself injecting `Request`, you're doing it wrong — action should not know about HTTP. Form request maps to DTO, controller calls action with DTO. Action sees nothing of HTTP.
8. **Constructor-promoted, readonly dependencies.** When action does have collaborators, declare them with constructor property promotion: `public function __construct(private readonly StockChecker $stock) {}`. No setter injection. No `app()` calls inside `execute`.
9. **No static methods.** Actions are instances. Container resolves them. Mockable in tests when (rarely) needed | keeps constraint that one action = one instance with one job.

## Calling an Action

From controller:

```php
public function store(StoreInvoiceRequest $request, CreateInvoiceAction $action): RedirectResponse
{
    $action->execute($request->toData());

    return redirect()->route('invoices.index');
}
```

From job:

```php
public function handle(CreateInvoiceAction $action): void
{
    $action->execute($this->data);
}
```

From console command:

```php
public function handle(CreateInvoiceAction $action): int
{
    $data = CreateInvoiceData::from([...]);
    $action->execute($data);

    return self::SUCCESS;
}
```

From event listener:

```php
public function handle(SomethingHappened $event, CreateInvoiceAction $action): void
{
    $action->execute(CreateInvoiceData::fromEvent($event));
}
```

Pattern is identical in all four. Action is injected. `execute()` is called. Nothing else happens in entry point.

## The Form Request to DTO Bridge

Form requests are where HTTP becomes domain data. Request validates; single method maps to DTO. Controller never sees `$request->validated()` directly — it calls `$request->toData()` and hands result to action.

```php
// app/Http/Requests/Invoices/StoreInvoiceRequest.php
namespace App\Http\Requests\Invoices;

use App\Data\Invoices\CreateInvoiceData;
use Illuminate\Foundation\Http\FormRequest;

final class StoreInvoiceRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'customer_id' => ['required', 'integer', 'exists:users,id'],
            'amount_cents' => ['required', 'integer', 'min:1'],
        ];
    }

    public function toData(): CreateInvoiceData
    {
        return CreateInvoiceData::from($this->validated());
    }
}
```

Action's signature stays free of HTTP — it sees only DTO, which is same shape whether call comes from HTTP, job, or artisan command. This is the seam that lets same action serve every entry point in the "Calling an action" examples.

## Testing an Action

Two tests per action: unit test | feature test. Unit test exercises action in isolation. Feature test exercises it through its real entry point (HTTP, queue, console).

```php
// tests/Unit/Actions/Invoices/CreateInvoiceActionTest.php
use App\Actions\Invoices\CreateInvoiceAction;
use App\Data\Invoices\CreateInvoiceData;
use App\Events\Invoices\InvoiceCreated;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Event;

uses(RefreshDatabase::class);

it('persists an invoice and fires InvoiceCreated', function (): void {
    Event::fake();

    $data = CreateInvoiceData::from([
        'customer_id' => 1,
        'amount_cents' => 9900,
    ]);

    $invoice = app(CreateInvoiceAction::class)->execute($data);

    expect($invoice->amount_cents)->toBe(9900);
    Event::assertDispatched(InvoiceCreated::class);
});
```

```php
// tests/Feature/Invoices/CreateInvoiceTest.php
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(RefreshDatabase::class);

it('creates an invoice via POST /invoices', function (): void {
    $this->actingAs(User::factory()->create())
        ->post('/invoices', ['customer_id' => 1, 'amount_cents' => 9900])
        ->assertRedirect(route('invoices.index'));

    $this->assertDatabaseHas('invoices', ['amount_cents' => 9900]);
});
```

## When NOT to Use an Action

- **Work is genuinely query.** If method takes no inputs and returns derived data with no side effects, it's query, not action. Put it on query class | scope, not in `Actions/`.
- **Work is chain of >3 transformations.** Use pipeline of actions instead — see pipeline-patterns skill.
- **Work needs entire bounded context's vocabulary.** Promote to DDD — see ddd-bounded-contexts skill.
