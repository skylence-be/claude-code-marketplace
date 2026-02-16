---
name: nativephp-testing-patterns
description: Master NativePHP testing with facade fakes, assertion methods, and integration testing strategies for desktop and mobile applications. Use when writing tests for NativePHP apps, mocking native facades, or implementing TDD for desktop/mobile features.
category: nativephp
tags: [nativephp, testing, pest, phpunit, fakes, desktop, mobile, laravel]
---

# NativePHP Testing Patterns

Patterns for testing NativePHP desktop and mobile applications using facade fakes and Laravel testing tools.

## When to Use This Skill

- Writing tests for NativePHP desktop features
- Mocking native facades (Window, Shell, etc.) with fakes
- Testing event handling for native interactions
- Integration testing with Laravel's test framework
- Implementing TDD for NativePHP applications

## Testing Philosophy

NativePHP provides **fake test doubles** for native facades, eliminating the need to run Electron or native shells during tests. Tests run in standard PHPUnit/Pest with the same API as production code.

## Desktop Facade Fakes (6 Fakes)

NativePHP Desktop provides exactly 6 test fake classes: `WindowManagerFake`, `ShellFake`, `ChildProcessFake`, `GlobalShortcutFake`, `PowerMonitorFake`, `QueueWorkerFake`.

### WindowManagerFake
```php
use Native\Laravel\Facades\Window;

test('opens editor window for document', function () {
    Window::fake();

    $document = Document::factory()->create();
    $this->post("/documents/{$document->id}/open");

    // Available assertions
    Window::assertOpened("editor-{$document->id}");
    Window::assertClosed('settings');
    Window::assertHidden('panel');
    Window::assertShown('panel');
    Window::assertOpenedCount(1);
    Window::assertClosedCount(0);
});

test('stubs window return values', function () {
    Window::fake();
    Window::alwaysReturnWindows([$windowObject]);

    // Now Window::all() and Window::current() return stubbed values
});
```

### ShellFake
```php
use Native\Laravel\Facades\Shell;

test('performs shell operations', function () {
    Shell::fake();

    $this->post('/files/reveal', ['path' => '/Documents/report.pdf']);
    $this->post('/files/trash', ['path' => '/tmp/old.txt']);
    $this->post('/links/open', ['url' => 'https://example.com']);

    // Available assertions
    Shell::assertShowInFolder('/Documents/report.pdf');
    Shell::assertOpenedFile('/path/to/file');
    Shell::assertTrashedFile('/tmp/old.txt');
    Shell::assertOpenedExternal('https://example.com');
});
```

### ChildProcessFake
```php
use Native\Laravel\Facades\ChildProcess;

test('starts background processes', function () {
    ChildProcess::fake();

    ChildProcess::php('scripts/import.php', alias: 'importer');
    ChildProcess::artisan('queue:work', alias: 'worker');
    ChildProcess::node('scripts/watcher.js', alias: 'watcher');

    // Available assertions
    ChildProcess::assertStarted('importer');
    ChildProcess::assertPhp('scripts/import.php');
    ChildProcess::assertArtisan('queue:work');
    ChildProcess::assertNode('scripts/watcher.js');
    ChildProcess::assertStop('importer');
    ChildProcess::assertRestart('importer');
    ChildProcess::assertMessage('importer');
});
```

### GlobalShortcutFake
```php
use Native\Laravel\Facades\GlobalShortcut;

test('registers global shortcuts', function () {
    GlobalShortcut::fake();

    GlobalShortcut::key('CmdOrCtrl+N')
        ->event(NewDocEvent::class)
        ->register();

    // Available assertions
    GlobalShortcut::assertKey('CmdOrCtrl+N');
    GlobalShortcut::assertEvent(NewDocEvent::class);
    GlobalShortcut::assertRegisteredCount(1);
    GlobalShortcut::assertUnregisteredCount(0);
});
```

### PowerMonitorFake
```php
use Native\Laravel\Facades\PowerMonitor;

test('checks system idle state', function () {
    PowerMonitor::fake();

    $state = PowerMonitor::getSystemIdleState(300);

    // Available assertions
    PowerMonitor::assertGetSystemIdleState();
    PowerMonitor::assertGetSystemIdleStateCount(1);
});
```

### QueueWorkerFake
```php
use Native\Laravel\Facades\QueueWorker;

test('manages queue workers', function () {
    QueueWorker::fake();

    QueueWorker::up(alias: 'default');

    // Available assertions
    QueueWorker::assertUp();
    QueueWorker::assertDown();
});
```

### Notification Testing
```php
use Native\Laravel\Facades\Notification;

test('sends notification on task completion', function () {
    Notification::fake();

    $task = Task::factory()->create();
    $task->markComplete();

    Notification::assertSent();
});
```

## Event Testing

### Testing Native Event Handlers
```php
use App\Events\WindowFocusedHandler;
use Native\Laravel\Events\Windows\WindowFocused;

test('refreshes data when window is focused', function () {
    $component = Livewire::test(Dashboard::class);

    $component->dispatch('native:' . WindowFocused::class);

    $component->assertSet('lastRefreshed', now());
});
```

### Testing Broadcasting
```php
use Illuminate\Support\Facades\Event;
use App\Events\DataUpdated;

test('broadcasts data update event', function () {
    Event::fake([DataUpdated::class]);

    $this->post('/data/update', ['value' => 'new']);

    Event::assertDispatched(DataUpdated::class, function ($event) {
        return $event->data['value'] === 'new';
    });
});
```

## Livewire Component Testing

### Testing Native Event Listeners
```php
use Livewire\Livewire;
use Native\Mobile\Events\Camera\PhotoTaken;

test('handles photo taken event', function () {
    $component = Livewire::test(PhotoCapture::class);

    $component->dispatch('native:' . PhotoTaken::class, path: '/tmp/photo.jpg');

    $component->assertSet('photoPath', '/tmp/photo.jpg');
});
```

### Testing Facade Calls in Components
```php
use Livewire\Livewire;
use Native\Mobile\Facades\Camera;

test('triggers camera when capture button clicked', function () {
    Camera::fake();

    $component = Livewire::test(PhotoCapture::class);

    $component->call('takePhoto');

    Camera::assertCalled('getPhoto');
});
```

### Testing Biometric Authentication Flow
```php
use Livewire\Livewire;
use Native\Mobile\Events\Biometrics\Completed;
use Native\Mobile\Events\Biometrics\Failed;

test('grants access after biometric success', function () {
    $component = Livewire::test(SecureVault::class);

    $component->dispatch('native:' . Completed::class);

    $component->assertSet('authenticated', true);
});

test('shows error after biometric failure', function () {
    $component = Livewire::test(SecureVault::class);

    $component->dispatch('native:' . Failed::class, message: 'User cancelled');

    $component->assertSet('authenticated', false);
    $component->assertSessionHas('error');
});
```

## Service and Controller Testing

### Testing Controllers That Use Native Facades
```php
use Native\Laravel\Facades\Window;
use Native\Laravel\Facades\Notification;

test('creates document and opens editor window', function () {
    Window::fake();

    $response = $this->post('/documents', [
        'title' => 'My Document',
        'content' => 'Hello world',
    ]);

    $response->assertRedirect();

    $document = Document::latest()->first();
    expect($document->title)->toBe('My Document');

    Window::assertOpened("editor-{$document->id}");
});

test('import completes with notification', function () {
    Notification::fake();

    $this->post('/import', [
        'file' => UploadedFile::fake()->create('data.csv', 100),
    ]);

    Notification::assertSent();
});
```

### Testing Menu Event Handlers
```php
use App\Events\NewDocumentEvent;
use Native\Laravel\Facades\Window;

test('new document menu event creates document and opens window', function () {
    Window::fake();

    event(new NewDocumentEvent());

    $document = Document::latest()->first();
    expect($document)->not->toBeNull();
    expect($document->title)->toBe('Untitled');

    Window::assertOpened("editor-{$document->id}");
});
```

## Database Testing

### SQLite Test Configuration
```php
// phpunit.xml or pest.php
// NativePHP uses SQLite, so tests should mirror this
<env name="DB_CONNECTION" value="sqlite"/>
<env name="DB_DATABASE" value=":memory:"/>
```

### Migration Testing
```php
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(RefreshDatabase::class);

test('user settings are persisted', function () {
    $user = User::factory()->create();

    $this->actingAs($user)
        ->post('/settings', ['theme' => 'dark']);

    expect($user->fresh()->settings->theme)->toBe('dark');
});
```

## Testing Patterns Summary

### What to Test
| Area | Approach |
|------|----------|
| Window management | `Window::fake()` + `assertOpened()` / `assertClosed()` / `assertHidden()` / `assertShown()` |
| Shell operations | `Shell::fake()` + `assertShowInFolder()` / `assertOpenedFile()` / `assertTrashedFile()` / `assertOpenedExternal()` |
| Child processes | `ChildProcess::fake()` + `assertStarted()` / `assertPhp()` / `assertArtisan()` / `assertNode()` |
| Global shortcuts | `GlobalShortcut::fake()` + `assertKey()` / `assertEvent()` / `assertRegisteredCount()` |
| Power monitor | `PowerMonitor::fake()` + `assertGetSystemIdleState()` |
| Queue workers | `QueueWorker::fake()` + `assertUp()` / `assertDown()` |
| Notifications | `Notification::fake()` + `assertSent()` |
| Native events | Dispatch events in Livewire tests, assert state changes |
| Broadcasting | `Event::fake()` + `assertDispatched()` |
| Menu handlers | Trigger event, assert side effects |
| Mobile facades | Facade-specific fakes where available |
| Database | `RefreshDatabase` with SQLite in-memory |

### What NOT to Test
- Electron/native shell behavior (tested by NativePHP itself)
- Bridge function internals (tested by plugin authors)
- OS-level notification rendering
- Actual file dialogs or system tray display

## Best Practices

1. **Always use fakes** -- never require Electron/native shell for tests
2. **Test the PHP side** -- facade calls, event handling, state changes
3. **Use SQLite in-memory** for database tests (mirrors production)
4. **Test event flows end-to-end** -- trigger action → assert facade called → dispatch event → assert state change
5. **Use Pest** for concise, readable test syntax
6. **Group native tests** in a dedicated `tests/Feature/Native/` directory
7. **Test error paths** -- permission denied, failed operations, cancelled dialogs
8. **Mock external services** -- API calls, file systems, network operations
