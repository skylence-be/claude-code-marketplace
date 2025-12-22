# CSRF & XSS Protection

Prevent cross-site attacks.

## CSRF Protection

### Forms
```blade
<form method="POST" action="/profile">
    @csrf
    <input type="text" name="name">
    <button type="submit">Update</button>
</form>

<!-- Also works with @method -->
<form method="POST" action="/profile">
    @csrf
    @method('PUT')
    <!-- fields -->
</form>
```

### AJAX Requests
```html
<meta name="csrf-token" content="{{ csrf_token() }}">

<script>
// jQuery
$.ajaxSetup({
    headers: {
        'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
    }
});

// Axios (auto-configured in Laravel)
axios.defaults.headers.common['X-CSRF-TOKEN'] = document.querySelector('meta[name="csrf-token"]').content;

// Fetch
fetch('/profile', {
    method: 'POST',
    headers: {
        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
</script>
```

### Exclude Routes
```php
// app/Http/Middleware/VerifyCsrfToken.php
protected $except = [
    'stripe/webhook',
    'api/*', // API routes usually use tokens instead
];
```

## XSS Prevention

### Blade Escaping
```blade
<!-- Escaped (SAFE) -->
{{ $userInput }}
{{ $comment->content }}

<!-- Unescaped (DANGEROUS - only for trusted HTML) -->
{!! $trustedHtml !!}

<!-- Vue/Alpine syntax (escaped) -->
@{{ vueVariable }}
```

### Sanitize HTML
```php
// Using HTMLPurifier
use HTMLPurifier;
use HTMLPurifier_Config;

public function sanitize(string $html): string
{
    $config = HTMLPurifier_Config::createDefault();
    $config->set('HTML.Allowed', 'p,b,i,u,a[href],ul,ol,li,br');

    $purifier = new HTMLPurifier($config);
    return $purifier->purify($html);
}

// Store sanitized
$post->content = $this->sanitize($request->content);
```

### Content Security Policy
```php
// app/Http/Middleware/AddSecurityHeaders.php
public function handle($request, Closure $next)
{
    $response = $next($request);

    $response->headers->set('X-XSS-Protection', '1; mode=block');
    $response->headers->set('X-Content-Type-Options', 'nosniff');
    $response->headers->set('X-Frame-Options', 'SAMEORIGIN');
    $response->headers->set(
        'Content-Security-Policy',
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    );

    return $response;
}
```

### Safe JSON Output
```blade
<!-- For JavaScript data -->
<script>
    const user = @json($user);
    const settings = @json($settings, JSON_HEX_TAG);
</script>
```

## Input Sanitization

```php
// Remove HTML tags
$clean = strip_tags($input);

// Allow specific tags
$clean = strip_tags($input, '<p><br><b><i>');

// Validate and sanitize
$request->validate([
    'email' => 'required|email',
    'url' => 'required|url',
    'content' => 'required|string|max:10000',
]);
```
