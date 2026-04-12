# Pest Browser Testing (v4)

Pest 4 introduces real browser testing — full integration tests that run in actual browsers with access to Laravel features like `Event::fake()`, `assertAuthenticated()`, and model factories.

## Setup

Browser tests live in `tests/Browser/` directory. Use `RefreshDatabase` for clean state per test.

## Browser Test Basics

```php
use App\Models\User;
use Illuminate\Support\Facades\Notification;
use App\Notifications\ResetPassword;

it('may reset the password', function () {
    Notification::fake();

    $this->actingAs(User::factory()->create());

    $page = visit('/sign-in');

    $page->assertSee('Sign In')
        ->assertNoJavaScriptErrors()
        ->click('Forgot Password?')
        ->fill('email', 'user@example.com')
        ->click('Send Reset Link')
        ->assertSee('We have emailed your password reset link!');

    Notification::assertSent(ResetPassword::class);
});
```

## Available Interactions

| Method | Purpose |
|--------|---------|
| `visit($url)` | Navigate to a page |
| `click($text)` | Click an element by text |
| `fill($field, $value)` | Fill a form field |
| `select($field, $value)` | Select a dropdown option |
| `scroll($pixels)` | Scroll the page |
| `submit()` | Submit the current form |
| `pause($ms)` | Wait for animations/transitions |

## Assertions

```php
$page->assertSee('Welcome')            // Text is visible
     ->assertDontSee('Error')           // Text is not visible
     ->assertNoJavaScriptErrors()       // No JS errors in console
     ->assertNoConsoleLogs()            // No console output
     ->assertAuthenticated();           // User is logged in
```

## Smoke Testing

Quickly validate multiple pages have no JavaScript errors:

```php
$pages = visit(['/', '/about', '/contact', '/pricing']);

$pages->assertNoJavaScriptErrors()
      ->assertNoConsoleLogs();
```

## Multi-Browser & Device Testing

```php
// Test on different browsers
it('works in Chrome', function () {
    // Default browser
    visit('/')->assertSee('Home');
});

// Test on different viewports/devices
it('works on mobile', function () {
    visit('/')
        ->resize(375, 812) // iPhone dimensions
        ->assertSee('Mobile Menu');
});
```

## Visual Regression Testing

Capture and compare screenshots to detect unintended visual changes:

```php
it('renders correctly', function () {
    visit('/dashboard')
        ->screenshot('dashboard-default');
});
```

## Test Sharding

Split tests across parallel CI processes for faster runs:

```bash
# In CI — run shard 1 of 4
php artisan test --shard=1/4

# Run shard 2 of 4
php artisan test --shard=2/4
```

## Architecture Testing

Enforce code conventions across the codebase:

```php
arch('controllers')
    ->expect('App\Http\Controllers')
    ->toExtendNothing()
    ->toHaveSuffix('Controller');

arch('models')
    ->expect('App\Models')
    ->toExtend('Illuminate\Database\Eloquent\Model');

arch('no debugging')
    ->expect(['dd', 'dump', 'ray'])
    ->not->toBeUsed();
```

## Common Pitfalls

- Not importing `use function Pest\Laravel\mock;` before using mock
- Using `assertStatus(200)` instead of `assertSuccessful()` -- always prefer semantic assertions
- Forgetting `assertNoJavaScriptErrors()` in browser tests
- Not using `RefreshDatabase` for clean state per test
- Deleting tests without approval — tests are core application code
