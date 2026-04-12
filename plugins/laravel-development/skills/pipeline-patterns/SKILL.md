---
name: pipeline-patterns
description: Master Laravel Pipeline patterns for multi-step payload transformations. Use when implementing 3+ sequential data transformations, checkout flows, or processing pipelines.
---

# Pipeline Patterns — Multi-Step Transformations of Typed Payload

Use when feature reads as "input goes in, gets transformed in N steps, output comes out" and N >= 3. Two-step pipelines are smell — call actions directly.

## Quick Reference

| Rule | Summary |
|------|---------|
| Minimum 3 steps | Two-step "pipelines" are anti-pattern — call actions directly |
| Pipeline class wraps `Pipeline::send()` | Callers call `execute()`, never `send()` |
| Pipes are actions | Same rules: `final`, single public method, no HTTP knowledge, documented side effects |
| Pipe method is `handle` | `handle(Data $data, Closure $next): Data` |
| DTO immutability | Every pipe returns new DTO instance via `$data->with(...)` — never mutate |
| Private pipes nest | `app/Pipelines/{Domain}/Pipes/` unless reused by second caller |
| Reusable pipes promote | Move to `app/Actions/{Domain}/` when second caller appears |
| No conditional pipes | Pipe should always run and no-op when not applicable |
| Container-resolved | Let Laravel resolve pipes — don't pre-instantiate with `new` |
| Two-level testing | Unit test each pipe in isolation + Feature test pipeline as whole |

## What Laravel Pipeline IS

`Illuminate\Pipeline\Pipeline` is built-in class that threads payload through ordered list of "pipes." Each pipe receives payload | `Closure $next`, does its work, returns result of calling `$next($payload)` — identical to middleware pipeline Laravel uses for HTTP requests.

```php
app(Pipeline::class)
    ->send($data)
    ->through([ValidateStock::class, ReserveInventory::class, CreateOrder::class])
    ->thenReturn();
```

Container resolves each pipe class, injects any dependencies pipe needs, calls `handle($payload, Closure $next)` on it.

## Pipes ARE Actions

A pipe is action with different method signature. Same rules (`final`, single public method, no HTTP knowledge, documented side effects) — only difference is method shape:

| | Action | Pipe |
|---|---|---|
| Method | `execute(Data $data): Return` | `handle(Data $data, Closure $next): Data` |
| Returns | model, VO, void | payload (transformed), passed through `$next` |
| Called from | controllers, jobs, commands, listeners | only from inside pipeline |

Same file naming (`{Verb}{Noun}Action`). Same location (`app/Actions/{Domain}/`) when reusable — **if pipe is reused outside pipeline, put it in `Actions/`**. Otherwise nest it under `app/Pipelines/{Domain}/Pipes/`.

## The Pipeline Class Is Itself an Action

Don't expose `Pipeline::send()->through()->thenReturn()` to rest of app. Wrap it. `CheckoutPipeline` is class with `execute(StartCheckoutData $data): CheckoutResult` and orchestration is private implementation detail.

Why: callers shouldn't care whether their checkout is one action, three actions in sequence, or twelve pipes routed through queue batch. They hand DTO in, receive DTO out. Pipeline is free to refactor internally without breaking single call site.

```php
public function execute(StartCheckoutData $data): CheckoutResult
{
    return app(Pipeline::class)
        ->send($data)
        ->through($this->pipes)
        ->thenReturn();
}
```

## DTO Immutability Through Chain

Every pipe returns **new DTO instance**. Never mutates. Spatie laravel-data supports this cleanly via `$data->with(...)` (or manual `new SameData(...)`).

```php
public function handle(StartCheckoutData $data, Closure $next): StartCheckoutData
{
    $reservation = $this->reserver->reserve($data->lineItems);

    return $next($data->with(reservation: $reservation));
}
```

Why: mutation makes pipes order-dependent in subtle ways, breaks test reuse (you can't instantiate pipe and re-run it on same input), silently destroys original payload caller passed in.

## File Location

| Thing | Path |
|---|---|
| Pipeline class (top-level) | `app/Pipelines/{Domain}/{Process}Pipeline.php` |
| Private pipe (only used by one pipeline) | `app/Pipelines/{Domain}/Pipes/{Verb}{Noun}Action.php` |
| Reusable pipe (used by pipeline AND directly) | `app/Actions/{Domain}/{Verb}{Noun}Action.php` (has both `handle` and nothing else — it's pipe) |
| DTO | `app/Data/{Domain}/{Process}Data.php` |
| Pipeline test | `tests/Feature/{Domain}/{Process}PipelineTest.php` |
| Pipe test | `tests/Unit/Pipelines/{Domain}/Pipes/{Verb}{Noun}ActionTest.php` |

**Rule:** if pipe is only referenced from one pipeline, nest it. Promote to `app/Actions/` only once second caller appears. Premature sharing is how `app/Actions/` becomes junk drawer.

## Canonical Example — CheckoutPipeline

Three-step checkout: validate stock -> reserve inventory -> create order.

### The DTO (Entry and Exit of Pipeline)

```php
<?php

namespace App\Data\Checkout;

use App\Models\Order;
use Spatie\LaravelData\Data;

final class StartCheckoutData extends Data
{
    public function __construct(
        public readonly int $userId,
        /** @var array<int, array{product_id: int, quantity: int}> */
        public readonly array $lineItems,
        public readonly ?string $reservationId = null,
        public readonly ?Order $order = null,
    ) {}
}
```

### The Pipeline

```php
<?php

namespace App\Pipelines\Checkout;

use App\Data\Checkout\StartCheckoutData;
use App\Pipelines\Checkout\Pipes\CreateOrderAction;
use App\Pipelines\Checkout\Pipes\ReserveInventoryAction;
use App\Pipelines\Checkout\Pipes\ValidateStockAction;
use Illuminate\Pipeline\Pipeline;

/**
 * Walk a StartCheckoutData through validate -> reserve -> create.
 *
 * Side effects (across the chain):
 * - Reserves inventory in the warehouse service
 * - Persists an Order row
 * - Dispatches OrderPlaced (fired by CreateOrderAction)
 */
final class CheckoutPipeline
{
    /** @var array<int, class-string> */
    private array $pipes = [
        ValidateStockAction::class,
        ReserveInventoryAction::class,
        CreateOrderAction::class,
    ];

    public function execute(StartCheckoutData $data): StartCheckoutData
    {
        return app(Pipeline::class)
            ->send($data)
            ->through($this->pipes)
            ->thenReturn();
    }
}
```

### The Pipes

```php
<?php

namespace App\Pipelines\Checkout\Pipes;

use App\Data\Checkout\StartCheckoutData;
use App\Exceptions\Checkout\OutOfStockException;
use App\Services\Warehouse\StockChecker;
use Closure;

final class ValidateStockAction
{
    public function __construct(private readonly StockChecker $stock) {}

    public function handle(StartCheckoutData $data, Closure $next): StartCheckoutData
    {
        foreach ($data->lineItems as $item) {
            if (! $this->stock->hasAvailable($item['product_id'], $item['quantity'])) {
                throw new OutOfStockException($item['product_id']);
            }
        }

        return $next($data);
    }
}
```

```php
<?php

namespace App\Pipelines\Checkout\Pipes;

use App\Data\Checkout\StartCheckoutData;
use App\Services\Warehouse\InventoryReserver;
use Closure;

final class ReserveInventoryAction
{
    public function __construct(private readonly InventoryReserver $reserver) {}

    public function handle(StartCheckoutData $data, Closure $next): StartCheckoutData
    {
        $reservationId = $this->reserver->reserve($data->lineItems);

        return $next($data->with(reservationId: $reservationId));
    }
}
```

```php
<?php

namespace App\Pipelines\Checkout\Pipes;

use App\Data\Checkout\StartCheckoutData;
use App\Events\Checkout\OrderPlaced;
use App\Models\Order;
use Closure;

final class CreateOrderAction
{
    public function handle(StartCheckoutData $data, Closure $next): StartCheckoutData
    {
        $order = Order::create([
            'user_id' => $data->userId,
            'reservation_id' => $data->reservationId,
            'line_items' => $data->lineItems,
        ]);

        OrderPlaced::dispatch($order);

        return $next($data->with(order: $order));
    }
}
```

### Calling It From Controller

```php
public function store(StoreCheckoutRequest $request, CheckoutPipeline $pipeline): RedirectResponse
{
    $result = $pipeline->execute($request->toData());

    return redirect()->route('orders.show', $result->order);
}
```

Controller has no idea there are three pipes inside. Adding fourth pipe (e.g., `ChargePayment`) is one-line change in `$this->pipes` — no controller change.

## When to Use Pipeline vs Single Action vs DDD

| Signal | Architecture |
|---|---|
| 1 verb, 1 DTO in, 1 thing out | **action** |
| 2 sequential steps | **action** (inline second step as private method, or call two actions from caller) |
| 3+ sequential transformations on same payload | **pipeline** |
| 3+ sequential transformations on same payload AND new aggregate, cross-cutting events, >5 verbs | **ddd**, with pipeline living inside `app/Domains/{Context}/Pipelines/` |

Three-step threshold is not ceiling — it's floor. If you have 2 transformations, indirection costs more than it saves.

## Testing Pattern

**Two levels:**

1. **Unit test each pipe in isolation.** Instantiate pipe, pass DTO, pass `Closure` that captures and returns what pipe handed to it, assert on both returned DTO and whatever side effect happened.
2. **Feature test pipeline as whole.** Call `$pipeline->execute($data)` against real DB (`uses(RefreshDatabase::class)`), assert on final state and events fired.

Example pipe unit test:

```php
it('reserves inventory and attaches the reservation id to the payload', function (): void {
    $reserver = Mockery::mock(InventoryReserver::class);
    $reserver->shouldReceive('reserve')->once()->andReturn('res-123');

    $pipe = new ReserveInventoryAction($reserver);
    $data = StartCheckoutData::from(['userId' => 1, 'lineItems' => [['product_id' => 1, 'quantity' => 2]]]);

    $result = $pipe->handle($data, fn ($payload) => $payload);

    expect($result->reservationId)->toBe('res-123');
});
```

Example pipeline feature test:

```php
uses(RefreshDatabase::class);

it('turns a StartCheckoutData into an Order', function (): void {
    Event::fake();
    $user = User::factory()->create();
    $product = Product::factory()->create(['stock' => 10]);

    $data = StartCheckoutData::from([
        'userId' => $user->id,
        'lineItems' => [['product_id' => $product->id, 'quantity' => 2]],
    ]);

    $result = app(CheckoutPipeline::class)->execute($data);

    expect($result->order)->toBeInstanceOf(Order::class);
    $this->assertDatabaseHas('orders', ['id' => $result->order->id]);
    Event::assertDispatched(OrderPlaced::class);
});
```

## Anti-Patterns

- **Two-step "pipelines."** Call action directly. The `Pipeline::send()->through()` scaffolding exists to hide complexity — if there is no complexity, you're adding friction for free.
- **Pipes that mutate payload.** `$data->reservationId = 'foo'` is forbidden. Return new DTO (`$data->with(...)`). Mutation couples pipes in invisible ways.
- **Pipes resolved per-call with `new` instead of container-resolved.** Laravel's pipeline already resolves pipes through container with proper DI. Don't pre-instantiate pipes in pipeline class constructor unless you're intentionally caching them for lifetime of request.
- **Conditional pipes (`if ($x) $pipes[] = Foo::class`).** If pipe is optional, it should always run and no-op when it shouldn't apply (`return $next($data)` without doing anything). Branching pipelines are fork-in-the-road features masquerading as linear flows — either make two pipelines | handle branch inside single pipe.
- **Exposing `Pipeline::send()` to caller.** Pipeline class wraps it. Controllers | jobs | commands call `execute()`, never `send()`.
- **Putting pipe that's used from three callers under `app/Pipelines/{Domain}/Pipes/`.** Promote it to `app/Actions/{Domain}/` — it's action that happens to have pipe shape.
- **Mixing `execute` and `handle` on same class.** Pick one. If class is both pipe and directly-callable action, give it `handle` and call `$pipe->handle($data, fn ($x) => $x)` from direct path. Less common than you'd think.
- **Pipes that take `Request` | any HTTP context as dependency.** Pipes know about DTOs, not HTTP.
