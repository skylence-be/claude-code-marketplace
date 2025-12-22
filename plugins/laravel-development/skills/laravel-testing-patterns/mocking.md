# Mocking External Services

Testing with faked services and dependencies.

## HTTP Faking

```php
use Illuminate\Support\Facades\Http;

test('external api call', function () {
    Http::fake([
        'api.example.com/*' => Http::response([
            'id' => 1,
            'name' => 'Test',
        ], 200),
    ]);

    $service = new ExternalApiService();
    $result = $service->fetchData();

    expect($result['name'])->toBe('Test');

    Http::assertSent(function ($request) {
        return $request->url() === 'https://api.example.com/data';
    });
});

test('api failure handling', function () {
    Http::fake([
        'api.example.com/*' => Http::response([], 500),
    ]);

    $service = new ExternalApiService();

    expect(fn () => $service->fetchData())
        ->toThrow(\Exception::class);
});

test('sequential responses', function () {
    Http::fake([
        'api.example.com/*' => Http::sequence()
            ->push(['status' => 'pending'], 200)
            ->push(['status' => 'complete'], 200),
    ]);

    // First call returns pending
    // Second call returns complete
});
```

## Mail Faking

```php
use Illuminate\Support\Facades\Mail;
use App\Mail\WelcomeEmail;

test('sends welcome email', function () {
    Mail::fake();

    $user = User::factory()->create();
    $user->sendWelcomeEmail();

    Mail::assertSent(WelcomeEmail::class, function ($mail) use ($user) {
        return $mail->hasTo($user->email);
    });
});

test('no emails sent', function () {
    Mail::fake();

    // Action that shouldn't send mail

    Mail::assertNothingSent();
});

test('email queued', function () {
    Mail::fake();

    $user = User::factory()->create();
    Mail::to($user)->queue(new WelcomeEmail($user));

    Mail::assertQueued(WelcomeEmail::class);
});
```

## Queue Faking

```php
use Illuminate\Support\Facades\Queue;
use App\Jobs\ProcessUser;

test('job dispatched', function () {
    Queue::fake();

    $user = User::factory()->create();
    ProcessUser::dispatch($user);

    Queue::assertPushed(ProcessUser::class);
    Queue::assertPushed(ProcessUser::class, fn ($job) => $job->user->id === $user->id);
});

test('job pushed to specific queue', function () {
    Queue::fake();

    ProcessUser::dispatch($user)->onQueue('processing');

    Queue::assertPushedOn('processing', ProcessUser::class);
});

test('no jobs dispatched', function () {
    Queue::fake();

    // Action

    Queue::assertNothingPushed();
});
```

## Event Faking

```php
use Illuminate\Support\Facades\Event;
use App\Events\UserRegistered;

test('event dispatched', function () {
    Event::fake([UserRegistered::class]);

    $user = User::factory()->create();

    Event::assertDispatched(UserRegistered::class);
    Event::assertDispatched(
        UserRegistered::class,
        fn ($event) => $event->user->id === $user->id
    );
});

test('event not dispatched', function () {
    Event::fake();

    // Action

    Event::assertNotDispatched(UserRegistered::class);
});
```

## Storage Faking

```php
use Illuminate\Support\Facades\Storage;
use Illuminate\Http\UploadedFile;

test('file upload', function () {
    Storage::fake('public');

    $file = UploadedFile::fake()->image('photo.jpg');

    post('/upload', ['file' => $file]);

    Storage::disk('public')->assertExists('photos/' . $file->hashName());
});

test('file deletion', function () {
    Storage::fake('public');

    $file = UploadedFile::fake()->image('photo.jpg');
    Storage::disk('public')->put('photos/photo.jpg', $file);

    delete('/files/photo.jpg');

    Storage::disk('public')->assertMissing('photos/photo.jpg');
});
```

## Notification Faking

```php
use Illuminate\Support\Facades\Notification;
use App\Notifications\InvoicePaid;

test('notification sent', function () {
    Notification::fake();

    $user = User::factory()->create();
    $invoice = Invoice::factory()->create(['user_id' => $user->id]);

    $user->notify(new InvoicePaid($invoice));

    Notification::assertSentTo($user, InvoicePaid::class);
});

test('notification via specific channel', function () {
    Notification::fake();

    $user->notify(new InvoicePaid($invoice));

    Notification::assertSentTo(
        $user,
        InvoicePaid::class,
        fn ($notification, $channels) => in_array('mail', $channels)
    );
});
```
