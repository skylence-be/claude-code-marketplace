# Documentation

Comments, docblocks, and documentation standards.

## When to Comment

```php
// Comment WHY, not WHAT
// Bad: Increment counter
$counter++;

// Good: Compensate for zero-indexed array
$position = $index + 1;

// Comment complex business logic
// Users with more than 10 orders get priority processing
// due to SLA requirements from enterprise contracts
if ($user->orders_count > 10) {
    $this->priorityQueue->push($order);
}
```

## Docblocks

```php
/**
 * Calculate the total price including taxes and discounts.
 *
 * @param  float  $subtotal  The base price before modifications
 * @param  float  $taxRate  Tax rate as decimal (e.g., 0.21 for 21%)
 * @param  float|null  $discount  Optional discount amount
 * @return float The final calculated price
 *
 * @throws InvalidArgumentException If subtotal is negative
 */
public function calculateTotal(
    float $subtotal,
    float $taxRate,
    ?float $discount = null
): float {
    if ($subtotal < 0) {
        throw new InvalidArgumentException('Subtotal cannot be negative');
    }

    $total = $subtotal * (1 + $taxRate);

    if ($discount !== null) {
        $total -= $discount;
    }

    return max(0, $total);
}
```

## Class Docblocks

```php
/**
 * Service for processing user orders.
 *
 * This service handles the complete order lifecycle including
 * validation, payment processing, and notification dispatch.
 *
 * @see OrderController For HTTP layer handling
 * @see Order For the order model
 */
final class OrderService
{
    // ...
}
```

## Property Documentation

```php
class OrderService
{
    /**
     * Maximum retry attempts for failed payments.
     */
    private const MAX_RETRIES = 3;

    /**
     * Cache duration for order summaries (in seconds).
     */
    private int $cacheDuration = 3600;

    /**
     * @var array<int, Order> Pending orders indexed by ID
     */
    private array $pendingOrders = [];
}
```

## Type Annotations

```php
// When types can't be expressed in PHP
/**
 * @param  array{name: string, email: string, age?: int}  $data
 * @return Collection<int, User>
 */
public function createUsers(array $data): Collection
{
    // ...
}

// Generic collections
/**
 * @template T
 * @param  T  $item
 * @return Collection<int, T>
 */
public function wrap($item): Collection
{
    return collect([$item]);
}
```

## TODO Comments

```php
// Use standard format for tracking
// TODO: Implement caching layer for expensive queries
// FIXME: This breaks when user has no email
// HACK: Temporary workaround for Laravel bug #12345
// NOTE: This approach is intentional due to legacy constraints

// Include ticket references when applicable
// TODO(PROJ-123): Migrate to new payment gateway
```

## Deprecation

```php
/**
 * Process the order.
 *
 * @deprecated 2.0.0 Use OrderProcessor::handle() instead
 * @see OrderProcessor::handle()
 */
public function processOrder(Order $order): void
{
    trigger_error(
        'processOrder() is deprecated, use OrderProcessor::handle()',
        E_USER_DEPRECATED
    );

    app(OrderProcessor::class)->handle($order);
}
```

## API Documentation

```php
/**
 * @OA\Get(
 *     path="/api/posts",
 *     summary="List all posts",
 *     tags={"Posts"},
 *     @OA\Parameter(
 *         name="page",
 *         in="query",
 *         description="Page number",
 *         @OA\Schema(type="integer")
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Successful response",
 *         @OA\JsonContent(ref="#/components/schemas/PostCollection")
 *     )
 * )
 */
public function index(): AnonymousResourceCollection
{
    return PostResource::collection(Post::paginate());
}
```

## Minimal Comments

```php
// Let code speak for itself when possible
// Self-documenting method names eliminate need for comments

// Instead of:
// Check if the user is an admin
if ($user->role === 'admin') { }

// Use:
if ($user->isAdmin()) { }

// Instead of:
// Get active users created in the last 30 days
$users = User::where('status', 'active')
    ->where('created_at', '>', now()->subDays(30))
    ->get();

// Use:
$users = User::active()->recent()->get();
```
