# Authentication Security

Secure user authentication patterns.

## Password Security

```php
// Hash passwords (bcrypt by default)
$user->password = Hash::make($password);

// Verify password
if (Hash::check($password, $user->password)) {
    // Password matches
}

// Check if rehash needed
if (Hash::needsRehash($user->password)) {
    $user->password = Hash::make($password);
    $user->save();
}
```

## Password Validation

```php
use Illuminate\Validation\Rules\Password;

$request->validate([
    'password' => [
        'required',
        'confirmed',
        Password::min(8)
            ->mixedCase()
            ->numbers()
            ->symbols()
            ->uncompromised(), // Check against data breaches
    ],
]);

// Configure defaults in AppServiceProvider
Password::defaults(function () {
    return Password::min(8)
        ->mixedCase()
        ->numbers()
        ->uncompromised();
});
```

## Rate Limiting Login

```php
// routes/web.php
Route::post('/login', [LoginController::class, 'login'])
    ->middleware('throttle:5,1'); // 5 attempts per minute

// Custom throttling
RateLimiter::for('login', function (Request $request) {
    return Limit::perMinute(5)->by($request->email . $request->ip());
});
```

## Session Security

```php
// config/session.php
'lifetime' => 120,           // Session timeout
'expire_on_close' => false,  // Expire when browser closes
'encrypt' => true,           // Encrypt session data
'secure' => true,            // HTTPS only
'http_only' => true,         // No JavaScript access
'same_site' => 'lax',        // CSRF protection

// Regenerate session ID after login
$request->session()->regenerate();

// Invalidate session on logout
$request->session()->invalidate();
$request->session()->regenerateToken();
```

## Two-Factor Authentication

```php
// Using Laravel Fortify
use Laravel\Fortify\Fortify;

// Enable 2FA in config/fortify.php
'features' => [
    Features::twoFactorAuthentication([
        'confirm' => true,
        'confirmPassword' => true,
    ]),
],

// Check 2FA in controller
if ($user->two_factor_secret) {
    // Redirect to 2FA challenge
}
```

## Remember Me Security

```php
// Secure remember token
if (Auth::attempt($credentials, $request->boolean('remember'))) {
    // User authenticated with remember token
}

// Logout from all devices
Auth::logoutOtherDevices($password);

// Clear remember tokens
$user->forceFill([
    'remember_token' => null,
])->save();
```

## API Token Security

```php
// Sanctum tokens with expiration
$token = $user->createToken('api-token');
$token->accessToken->expires_at = now()->addDay();
$token->accessToken->save();

// Revoke tokens on password change
$user->tokens()->delete();

// Limit token abilities
$token = $user->createToken('read-only', ['read']);
```
