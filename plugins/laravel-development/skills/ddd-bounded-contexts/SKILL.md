---
name: ddd-bounded-contexts
description: Master Domain-Driven Design bounded contexts in Laravel with proper folder structure, cross-context communication via events, and public/private contracts. Use when the architecture classifier scores ddd >= 3.
---

# DDD Bounded Contexts in Laravel

Reach for this only when decision tree scores `ddd >= 3`. Premature DDD is single most expensive mistake planner can make. Every domain folder is folder you have to maintain, namespace imports must reach into, boundary your team has to police.

## Quick Reference

| Rule | Summary |
|------|---------|
| Threshold | `ddd >= 3` on classifier, OR new aggregate with >5 verbs, OR cross-context domain events |
| Folder root | `app/Domains/{Context}/` |
| Mandatory subfolders | `Actions/`, `Data/`, `Models/` — create on day one |
| Optional subfolders | `Events/`, `Contracts/`, `ValueObjects/`, `Enums/`, `Listeners/`, `Pipelines/`, `Exceptions/` — only when first file needed |
| Anti-pattern subfolders | `Repositories/`, `Services/`, `ServiceProviders/` — never create these |
| Public contract | `Contracts/`, `Data/`, `Events/`, `Enums/` — other contexts may depend on these |
| Private internals | `Actions/`, `Models/`, `Pipelines/`, `Listeners/` — never imported cross-context |
| Cross-context communication | Events first, Contracts second, direct imports never |
| Domain events carry IDs | Not full models — keeps events serializable and decoupled |
| Routes and controllers | Stay in `routes/` and `app/Http/Controllers/` — Laravel convention |
| Value object threshold | Same primitive in >= 3 places with same constraints |
| `ddd-lite` | If target context already exists, add to it — don't create new top-level context |
| Enforcement | Arch test asserts no cross-context imports into private subfolders |

## When DDD Is the Right Call

From decision tree:

- **ddd >= 3** on classifier scoring, OR
- **new aggregate** (not "add a column") AND **>5 verbs** on that aggregate, OR
- Feature emits **domain events** that other contexts subscribe to, OR
- Feature needs **ValueObject** | **Enum** to encode invariants that will be reused in >= 3 places.

Below those thresholds, use single action | pipeline. Above them, bounded context earns its folder.

**Corollary — `ddd-lite`:** if target context already exists under `app/Domains/`, add to it rather than inventing new one. Don't create `app/Domains/Billing` | `app/Domains/Subscriptions` when one context owns both.

## Folder Structure

```
app/Domains/{Context}/
├── Actions/         # the verbs (private, internal use + direct controller calls)
├── Data/            # Spatie laravel-data DTOs (public — other contexts may depend on these)
├── Events/          # domain events (public — other contexts may subscribe)
├── Contracts/       # interfaces this context exposes outward (public)
├── Models/          # Eloquent models (private — never imported cross-context)
├── ValueObjects/    # invariant-protecting value types
├── Enums/           # closed sets (status, type discriminators)
├── Listeners/       # internal listeners reacting to this context's own events
├── Pipelines/       # multi-step processes within this context
└── Exceptions/      # domain-specific exceptions
```

**Mandatory on day one:** `Actions/` | `Data/` | `Models/`. Everything else is created **only when first file of that type is needed**. No empty folders. No `README.md` placeholder. Tree depth stays flat.

## Mandatory / Optional / Anti-Pattern Subfolders

| Subfolder | Status | Why |
|---|---|---|
| `Actions/` | mandatory | The verbs. This is where business logic lives. |
| `Data/` | mandatory | Every action takes DTO. No exceptions. |
| `Models/` | mandatory | The aggregate(s) this context owns. |
| `Events/` | optional | Only when context emits something. |
| `Contracts/` | optional | Only when another context needs to depend on this one without coupling to its models. |
| `ValueObjects/` | optional | Only when same primitive appears in >= 3 places with identical constraints. |
| `Enums/` | optional | Closed sets only. Status fields, type discriminators. Not "list of countries." |
| `Listeners/` | optional | Only for listeners that react to this context's OWN events. Cross-context listeners live in subscribing context. |
| `Pipelines/` | optional | Only when promoting 3-step process from inline action calls. |
| `Exceptions/` | optional | Only when caller would reasonably want to `catch (\App\Domains\X\Exceptions\Foo $e)`. |
| `Repositories/` | anti-pattern | **Eloquent IS the repository.** Wrapping it doubles surface area for zero gain. |
| `Services/` | anti-pattern | **Actions ARE the service layer.** "Service" has no constraints; "Action" has them baked in. |
| `ServiceProviders/` | anti-pattern | Register bindings in `AppServiceProvider` or dedicated top-level provider. Domain folders don't own container. |

## The Public / Private Contract

Other code may depend on:
- `App\Domains\{Context}\Contracts\*` — interfaces
- `App\Domains\{Context}\Data\*` — DTOs
- `App\Domains\{Context}\Events\*` — events
- `App\Domains\{Context}\Enums\*` — closed enums that are part of public API

Other code may NOT depend on:
- `App\Domains\{Context}\Actions\*` — internal. (Controllers still call actions directly, but controllers are context's HTTP boundary. See below.)
- `App\Domains\{Context}\Models\*` — internal. Other contexts never import model from another context.
- `App\Domains\{Context}\Pipelines\*` — internal.
- `App\Domains\{Context}\Listeners\*` — internal.
- `App\Domains\{Context}\ValueObjects\*` — internal unless explicitly re-exported via `Data/`.

**Enforcement:** arch test (`tests/Arch/DomainBoundariesTest.php`) asserts that imports into `App\Domains\X\{Actions,Models,Pipelines,Listeners}` never come from `App\Domains\Y\*` (where `X !== Y`). See testing patterns skill for arch test pattern.

## Routes and Controllers Stay Where Laravel Expects

Routes live in `routes/web.php` | `routes/api.php`. Controllers live in `app/Http/Controllers/`. Controller is HTTP boundary — it maps HTTP request to domain action:

```php
// app/Http/Controllers/SubscriptionController.php
namespace App\Http\Controllers;

use App\Domains\Subscriptions\Actions\CreateSubscriptionAction;
use App\Http\Requests\Subscriptions\StoreSubscriptionRequest;
use Illuminate\Http\RedirectResponse;

final class SubscriptionController extends Controller
{
    public function store(
        StoreSubscriptionRequest $request,
        CreateSubscriptionAction $action,
    ): RedirectResponse {
        $subscription = $action->execute($request->toData());

        return redirect()->route('subscriptions.show', $subscription);
    }
}
```

Controller imports from `App\Domains\Subscriptions\Actions\*`. Yes, that technically breaks "internal is private." Controller is sanctioned exception because it's HTTP boundary of context — it's how outside world gets in. No other class outside `App\Domains\Subscriptions\*` may import from its `Actions/`.

**Why this split:** Laravel expects routes | controllers in specific paths and its tooling (route caching, route listing, scaffolding, docs) assumes it. Fighting that convention costs more than purity is worth.

## Domain Events vs Broadcast Events

| Use case | Type |
|---|---|
| This context tells another context "something happened, react if you want" | **Domain event** — `App\Domains\X\Events\ThingHappened`, subscribed to via listener in OTHER context (`App\Domains\Y\Listeners\HandleThingHappened`) |
| This context needs to notify browser / mobile client over websocket | **Broadcast event** — `implements ShouldBroadcast`, channel declared on event, lives in `App\Domains\X\Events\` |
| Both | Single event class that implements both (`ShouldBroadcast` + subscribed internally). One event, two transports. |

**Rule:** domain events should carry **IDs**, not full models — listeners re-fetch what they need. This keeps event serializable on queue and decouples listener from producing context's model class (listener depends on `Data/` | `Contracts/`, never on `Models/`).

```php
final class SubscriptionCreated
{
    use Dispatchable;
    use SerializesModels;

    public function __construct(public readonly int $subscriptionId) {}
}
```

## Value Objects: When to Introduce One

**Rule of thumb:** when same primitive appears in >= 3 places with same constraints.

- `int $amountCents` passed around with "must be positive" validation in three actions -> `Money` value object
- `string $email` with email-format validation in three places -> `EmailAddress` value object
- `string $currency` with ISO-4217 validation -> `Currency` value object

Value objects are `final readonly` classes that enforce invariants in their constructor (throw if invalid). They're equatable (`equals()`) and optionally stringable (`__toString()`).

```php
final readonly class BillingCycle
{
    public function __construct(public int $days)
    {
        if ($days < 1 || $days > 365) {
            throw new \InvalidArgumentException("BillingCycle must be 1-365 days, got {$days}");
        }
    }

    public function equals(self $other): bool
    {
        return $this->days === $other->days;
    }

    public function __toString(): string
    {
        return "{$this->days} days";
    }
}
```

Don't create value object for primitive that appears once. Don't create value object for something DTO already handles. Threshold is 3 uses.

## Enums: When

Closed sets. Status fields. Type discriminators. Things that will not grow at runtime.

- pass: `OrderStatus { Pending, Paid, Shipped, Cancelled }`
- pass: `SubscriptionState { Active, Paused, Cancelled }`
- pass: `NotificationChannel { Mail, Slack, Sms }`
- FAIL: List of countries (data, not enum)
- FAIL: List of product categories (user-editable, not enum)
- FAIL: User roles if app has role-management UI (user-editable, not enum)

## ddd-lite — Adding to Existing Bounded Context

When feature adds to EXISTING `app/Domains/{Context}/`:

1. **Do not create new top-level subfolders.** Drop new file into appropriate existing subfolder.
2. **Extend existing DTOs** rather than creating parallel one (`UpdateSubscriptionData` alongside `CreateSubscriptionData` is fine — two actions, two DTOs. But don't create `SubscriptionUpdate2Data`).
3. **Reuse existing models | events | value objects.** Only add new ones if decision tree says so.
4. **Tests go in existing feature test folder** (`tests/Feature/Domains/{Context}/`).

Decision tree detects `ddd-lite` automatically: if target `app/Domains/{Context}/` already exists, `ddd-lite` wins over `ddd`.

## Canonical Example — Subscriptions

Bounded context with 4 actions, 1 model, 1 event, 1 value object. Folder tree:

```
app/Domains/Subscriptions/
├── Actions/
│   ├── CreateSubscriptionAction.php
│   ├── CancelSubscriptionAction.php
│   ├── RenewSubscriptionAction.php
│   └── PauseSubscriptionAction.php
├── Data/
│   ├── CreateSubscriptionData.php
│   ├── CancelSubscriptionData.php
│   ├── RenewSubscriptionData.php
│   └── PauseSubscriptionData.php
├── Events/
│   └── SubscriptionCreated.php
├── Models/
│   └── Subscription.php
└── ValueObjects/
    └── BillingCycle.php
```

No `Contracts/` yet (no external context needs to depend on `Subscriptions` via interface). No `Enums/` yet (status is string column with cast; will promote to `SubscriptionStatus` enum if third place references it). No `Repositories/`, no `Services/`, no `ServiceProviders/`.

### CreateSubscriptionAction

```php
<?php

namespace App\Domains\Subscriptions\Actions;

use App\Domains\Subscriptions\Data\CreateSubscriptionData;
use App\Domains\Subscriptions\Events\SubscriptionCreated;
use App\Domains\Subscriptions\Models\Subscription;

/**
 * Create a subscription for a user on the given plan.
 *
 * Side effects:
 * - persists a Subscription
 * - dispatches SubscriptionCreated
 */
final class CreateSubscriptionAction
{
    public function execute(CreateSubscriptionData $data): Subscription
    {
        $subscription = Subscription::create([
            'user_id' => $data->userId,
            'plan_id' => $data->planId,
            'billing_cycle_days' => $data->billingCycle->days,
            'starts_at' => now(),
        ]);

        SubscriptionCreated::dispatch($subscription->id);

        return $subscription;
    }
}
```

### CreateSubscriptionData

```php
<?php

namespace App\Domains\Subscriptions\Data;

use App\Domains\Subscriptions\ValueObjects\BillingCycle;
use Spatie\LaravelData\Data;

final class CreateSubscriptionData extends Data
{
    public function __construct(
        public readonly int $userId,
        public readonly int $planId,
        public readonly BillingCycle $billingCycle,
    ) {}
}
```

### The Event

```php
<?php

namespace App\Domains\Subscriptions\Events;

use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

final class SubscriptionCreated
{
    use Dispatchable;
    use SerializesModels;

    public function __construct(public readonly int $subscriptionId) {}
}
```

Note: event carries ID, not model. Listeners fetch subscription via `Subscription::find($event->subscriptionId)` — but only listeners **inside** Subscriptions context. Listeners in other contexts (e.g., `Notifications`) fetch by calling method on subscriptions public contract | by reading DTO exposed via `Data/`.

## Cross-Context Communication

**Question:** how should `Domains/Billing` talk to `Domains/Notifications`?

**Answer, in priority order:**

1. **Via events.** Billing fires `InvoicePaid`. Listener in `Notifications` (`HandleInvoicePaid`) listens and calls `Notifications`' own action. Billing has zero knowledge of Notifications.
2. **Via `Contracts/`.** If Billing needs to synchronously query Notifications (e.g., "is user subscribed to billing emails?"), Notifications exposes `NotificationPreferencesContract`, Billing imports interface, container binds concrete implementation. Billing depends on interface only.
3. **Never directly.** Billing does not import `App\Domains\Notifications\Actions\*` | `App\Domains\Notifications\Models\*`.

**Preference:** option 1 (events) wins whenever semantics allow it. Async, decoupled, cheap to refactor, easy to test. Use option 2 only when you need synchronous answer AND can't stash information on Billing side.

## Anti-Patterns

- **God domains.** `app/Domains/Core/` | `app/Domains/Main/`. If you can't pick name, you don't have bounded context yet.
- **Shared models living in two contexts.** `User` belongs to one context (usually `Auth/Users` | just stays in `app/Models/User.php` at top level). Don't import `App\Domains\Billing\Models\User` from `Auth`.
- **Repositories.** `SubscriptionRepository::find($id)` wrapping `Subscription::find($id)` adds surface area with zero semantic gain.
- **Services.** `SubscriptionService::create(...)` is action with bad name.
- **Domain folders for features with <3 verbs.** `app/Domains/Feedback/Actions/SubmitFeedbackAction.php` — no, `app/Actions/Feedback/SubmitFeedbackAction.php`. Promote to domain folder when second and third verbs arrive.
- **Empty subfolders.** Don't create `Enums/` "in case we need one." Create it when first enum lands.
- **`ServiceProviders/` inside domain.** Domain is not in charge of container. Register bindings in `app/Providers/AppServiceProvider.php` | top-level provider that imports from domains.
- **Listeners in one domain reacting to events from another domain, placed in producing domain.** Listener belongs to CONSUMING context. `Notifications\Listeners\HandleInvoicePaid`, not `Billing\Listeners\HandleInvoicePaid`.
- **Cross-context model imports.** `Billing` importing `Notifications\Models\NotificationPreference`. Use contract | event.
- **Putting routes under `app/Domains/{Context}/routes.php`.** Routes live in `routes/`. Period. (A `RouteServiceProvider::loadRoutesFrom()` shim just hides violation.)
