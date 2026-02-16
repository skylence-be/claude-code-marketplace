---
name: nativephp-mobile-patterns
description: Master NativePHP Mobile v3 patterns including plugin architecture, EDGE native components, bridge functions, camera, biometrics, geolocation, push notifications, secure storage, and iOS/Android deployment. Use when building mobile apps, implementing native device features, or deploying to app stores.
category: nativephp
tags: [nativephp, mobile, ios, android, laravel, php, plugins, camera, biometrics, push-notifications]
---

# NativePHP Mobile Patterns

Comprehensive patterns for building native iOS and Android applications with NativePHP Mobile v3 and Laravel.

## When to Use This Skill

- Building mobile apps with NativePHP Mobile v3
- Implementing native device features (camera, biometrics, GPS)
- Using EDGE native components for platform-native UI
- Creating custom NativePHP mobile plugins
- Handling push notifications with Firebase
- Deploying to App Store and Google Play
- Using Jump for real-device development

## Plugin Ecosystem

### Core Plugins (Free)

| Plugin | Package | Features |
|--------|---------|----------|
| Browser | `nativephp/mobile-browser` | System browser, in-app browser, OAuth |
| Dialog | `nativephp/mobile-dialog` | Alert dialogs, toast notifications |
| Device | `nativephp/mobile-device` | Device hardware operations |
| File | `nativephp/mobile-file` | File operations |
| Microphone | `nativephp/mobile-microphone` | Audio recording, pause/resume |
| Network | `nativephp/mobile-network` | Connectivity status monitoring |
| Share | `nativephp/mobile-share` | Native share sheet |
| System | `nativephp/mobile-system` | System-level operations |

### Premium Plugins

| Plugin | Package | Features |
|--------|---------|----------|
| Biometrics | `nativephp/mobile-biometrics` | Face ID, Touch ID, Fingerprint |
| Firebase | `nativephp/mobile-firebase` | Push notifications (FCM/APNs) |
| Geolocation | `nativephp/mobile-geolocation` | GPS, permission handling |
| Scanner | `nativephp/mobile-scanner` | QR/barcode scanning |
| Secure Storage | `nativephp/mobile-secure-storage` | Keychain, EncryptedSharedPreferences |

### Installing Plugins

```bash
# Install via Composer
composer require nativephp/mobile-camera
composer require nativephp/mobile-biometrics
composer require nativephp/mobile-geolocation

# Register in NativeServiceProvider
```

### Plugin Registration

```php
// app/Providers/NativeServiceProvider.php
namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class NativeServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        // Each plugin MUST be explicitly registered
        $this->app->register(\NativePhp\MobileCamera\CameraServiceProvider::class);
        $this->app->register(\NativePhp\MobileBiometrics\BiometricsServiceProvider::class);
        $this->app->register(\NativePhp\MobileGeolocation\GeolocationServiceProvider::class);
        $this->app->register(\NativePhp\MobileDialog\DialogServiceProvider::class);
        $this->app->register(\NativePhp\MobileSecureStorage\SecureStorageServiceProvider::class);
        $this->app->register(\NativePhp\MobileFirebase\FirebaseServiceProvider::class);
    }
}
```

## EDGE Native Components

EDGE (Element Definition and Generation Engine) renders platform-native UI from Blade syntax.

### Bottom Navigation
```blade
<native:bottom-nav>
    <native:bottom-nav-item
        id="home"
        icon="home"
        label="Home"
        url="/home"
    />
    <native:bottom-nav-item
        id="search"
        icon="search"
        label="Search"
        url="/search"
    />
    <native:bottom-nav-item
        id="profile"
        icon="person"
        label="Profile"
        url="/profile"
    />
</native:bottom-nav>
```

### Top Bar
```blade
<native:top-bar title="My App" subtitle="Dashboard">
    <native:top-bar-action
        icon="settings"
        label="Settings"
        url="/settings"
    />
    <native:top-bar-action
        icon="search"
        label="Search"
        selected
    />
</native:top-bar>
```

### Side Navigation
```blade
<native:side-nav>
    <native:side-nav-header title="My App" subtitle="v1.0" />
    <native:side-nav-group title="Main">
        <native:side-nav-item
            icon="home"
            label="Home"
            url="/home"
        />
        <native:side-nav-item
            icon="inbox"
            label="Inbox"
            url="/inbox"
            badge="3"
        />
    </native:side-nav-group>
    <native:side-nav-group title="Settings">
        <native:side-nav-item
            icon="settings"
            label="Preferences"
            url="/settings"
        />
    </native:side-nav-group>
</native:side-nav>
```

### Floating Action Button
```blade
<native:fab
    icon="add"
    label="New Item"
    url="/items/create"
/>
```

### Horizontal Divider
```blade
<native:horizontal-divider />
```

EDGE components render as truly native elements (UITabBar on iOS, BottomNavigationView on Android), not web views.

## Blade Directives

```blade
{{-- Conditionally render for mobile only --}}
@mobile
    <native:bottom-nav>...</native:bottom-nav>
@endmobile

{{-- iOS-specific content --}}
@ios
    <p>Download from the App Store</p>
@endios

{{-- Android-specific content --}}
@android
    <p>Download from Google Play</p>
@endandroid
```

## Pending Builder Pattern

Mobile facades use a Pending builder pattern for configuring operations before execution:

```php
use Native\Mobile\Facades\Camera;

// Full builder chain
Camera::getPhoto()
    ->id('my-capture')              // unique identifier for this operation
    ->event(MyPhotoEvent::class)    // custom event class to dispatch
    ->remember()                     // cache the result
    ->start();                       // execute the operation
```

## #[OnNative] Attribute

The preferred way to listen to native events in Livewire (instead of `#[On('native:' . Event::class)]`):

```php
use Native\Mobile\Attributes\OnNative;
use Native\Mobile\Events\Camera\PhotoTaken;

class PhotoCapture extends Component
{
    public ?string $photoPath = null;

    public function takePhoto()
    {
        Camera::getPhoto()->start();
    }

    #[OnNative(PhotoTaken::class)]
    public function handlePhoto(PhotoTaken $event)
    {
        $this->photoPath = $event->path;
    }
}
```

Both `#[OnNative(Event::class)]` and `#[On('native:' . Event::class)]` work, but `#[OnNative]` is the canonical approach.

## Native Facade Patterns

### Camera
```php
use Native\Mobile\Facades\Camera;
use Native\Mobile\Events\Camera\PhotoTaken;
use Native\Mobile\Attributes\OnNative;

class PhotoCapture extends Component
{
    public ?string $photoPath = null;

    public function takePhoto()
    {
        // Simple call
        Camera::getPhoto();

        // Or use the Pending builder pattern
        Camera::getPhoto()
            ->id('my-capture')
            ->event(PhotoTaken::class)
            ->remember()
            ->start();
    }

    // Preferred: #[OnNative] attribute
    #[OnNative(PhotoTaken::class)]
    public function handlePhoto(PhotoTaken $event)
    {
        $this->photoPath = $event->path;
    }

    // Also works: #[On('native:' . PhotoTaken::class)]

    public function render()
    {
        return view('livewire.photo-capture');
    }
}
```

### Biometrics
```php
use Native\Mobile\Facades\Biometrics;
use Native\Mobile\Events\Biometrics\Completed;
use Native\Mobile\Events\Biometrics\Failed;

class SecureVault extends Component
{
    public bool $authenticated = false;

    public function authenticate()
    {
        Biometrics::promptForBiometricID('Verify your identity');
    }

    #[On('native:' . Completed::class)]
    public function onSuccess()
    {
        $this->authenticated = true;
    }

    #[On('native:' . Failed::class)]
    public function onFailure(string $message)
    {
        session()->flash('error', 'Authentication failed: ' . $message);
    }
}
```

### Geolocation
```php
use Native\Mobile\Facades\Geolocation;
use Native\Mobile\Events\Geolocation\LocationReceived;
use Native\Mobile\Events\Geolocation\PermissionDenied;

class LocationTracker extends Component
{
    public ?float $latitude = null;
    public ?float $longitude = null;

    public function getLocation()
    {
        Geolocation::getCurrentPosition();
    }

    #[On('native:' . LocationReceived::class)]
    public function handleLocation(float $latitude, float $longitude)
    {
        $this->latitude = $latitude;
        $this->longitude = $longitude;
    }

    #[On('native:' . PermissionDenied::class)]
    public function handleDenied()
    {
        session()->flash('error', 'Location permission denied');
    }
}
```

### Push Notifications (Firebase)
```php
use Native\Mobile\Facades\PushNotifications;
use Native\Mobile\Events\PushNotification\TokenGenerated;
use Native\Mobile\Events\PushNotification\NotificationReceived;

class NotificationSetup extends Component
{
    public function register()
    {
        PushNotifications::enrollForPushNotifications();
    }

    #[On('native:' . TokenGenerated::class)]
    public function saveToken(string $token)
    {
        // Store token on your server for sending pushes later
        auth()->user()->update(['push_token' => $token]);
    }

    #[On('native:' . NotificationReceived::class)]
    public function handleNotification(array $data)
    {
        // Handle incoming notification payload
    }
}
```

### Scanner (QR/Barcode)
```php
use Native\Mobile\Facades\Scanner;
use Native\Mobile\Events\Scanner\CodeScanned;

class QrScanner extends Component
{
    public ?string $scannedCode = null;

    public function scan()
    {
        Scanner::startScanning();
    }

    #[On('native:' . CodeScanned::class)]
    public function handleScan(string $code, string $format)
    {
        $this->scannedCode = $code;
        Scanner::stopScanning();
    }
}
```

### Secure Storage
```php
use Native\Mobile\Facades\SecureStorage;

// Store in Keychain (iOS) / EncryptedSharedPreferences (Android)
SecureStorage::set('api_token', $token);
$token = SecureStorage::get('api_token');
SecureStorage::delete('api_token');
```

### Dialog
```php
use Native\Mobile\Facades\Dialog;

// Alert dialog
Dialog::alert('Success', 'Your changes have been saved.');

// Confirmation dialog
Dialog::confirm('Delete', 'Are you sure you want to delete this item?');

// Toast notification
Dialog::toast('Item saved');
```

### Share
```php
use Native\Mobile\Facades\Share;

Share::text('Check out this app!');
Share::url('https://example.com');
Share::file($filePath);
```

### Haptics
```php
use Native\Mobile\Facades\Haptics;

Haptics::vibrate();
Haptics::impact('medium');  // light, medium, heavy
Haptics::notification('success');  // success, warning, error
```

### Device
```php
use Native\Mobile\Facades\Device;

$id = Device::getId();               // unique device identifier
$info = Device::getInfo();            // device model, OS version, etc.
$battery = Device::getBatteryInfo();  // battery level, charging status
Device::vibrate();                    // haptic vibration
Device::flashlight();                 // toggle flashlight
```

### Scanner (Extended)
```php
use Native\Mobile\Facades\Scanner;
use Native\Mobile\Events\Scanner\CodeScanned;

// Full builder with format filtering and continuous mode
Scanner::scan()
    ->prompt('Point camera at barcode')
    ->continuous()                           // keep scanning after first result
    ->formats(['qr', 'ean13', 'code128'])   // restrict to specific formats
    ->scan();

#[OnNative(CodeScanned::class)]
public function handleScan(CodeScanned $event)
{
    $code = $event->code;
    $format = $event->format;
}
```

### Microphone (Full Lifecycle)
```php
use Native\Mobile\Facades\Microphone;
use Native\Mobile\Events\Microphone\RecordingStopped;

// Start recording with builder
Microphone::record()->start();

// Control recording
Microphone::pause();
Microphone::resume();
$status = Microphone::getStatus();       // recording, paused, stopped
Microphone::stop();

$recording = Microphone::getRecording(); // get recorded audio file

#[OnNative(RecordingStopped::class)]
public function handleRecording(RecordingStopped $event)
{
    $this->audioPath = $event->path;
}
```

### MobileWallet
```php
use Native\Mobile\Facades\MobileWallet;

$available = MobileWallet::isAvailable();
$intent = MobileWallet::createPaymentIntent($amount, $currency);
MobileWallet::presentPaymentSheet();
MobileWallet::confirmPayment();
$status = MobileWallet::getPaymentStatus();
```

### Network
```php
use Native\Mobile\Facades\Network;
use Native\Mobile\Events\Network\StatusChanged;

$isConnected = Network::isConnected();
$type = Network::getConnectionType();  // wifi, cellular, none

#[On('native:' . StatusChanged::class)]
public function handleNetworkChange(bool $connected, string $type)
{
    $this->isOnline = $connected;
}
```

## JavaScript Integration

### Setup
```json
// package.json
{
    "imports": {
        "#nativephp": "./vendor/nativephp/mobile/resources/dist/native.js"
    }
}
```

### Usage
```javascript
import { On, Off, Call } from '#nativephp';

// Listen for native events
On('PhotoTaken', (data) => {
    document.getElementById('preview').src = data.path;
});

// Clean up listeners
Off('PhotoTaken', handler);

// Call native functions directly from JS
Call('Camera.GetPhoto', { quality: 80 });
```

## Event Handling Pattern

All native interactions follow the same async event pattern:

```
1. PHP/JS calls facade method  →  2. Bridge function executes natively
                                            ↓
4. Livewire/JS handles event   ←  3. Native code fires event back
```

### Livewire Event Listener
```php
use Livewire\Attributes\On;

// Convention: #[On('native:' . EventClass::class)]
#[On('native:' . PhotoTaken::class)]
public function handlePhoto(string $path) { }
```

### JavaScript Event Listener
```javascript
import { On } from '#nativephp';

On('PhotoTaken', ({ path }) => { });
```

## Custom Plugin Development

### Scaffold a Plugin
```bash
php artisan native:plugin:create vendor/my-plugin
php artisan native:plugin:register vendor/my-plugin
php artisan native:plugin:validate
```

### Plugin Manifest (nativephp.json)
```json
{
    "namespace": "MyPlugin",
    "bridge_functions": [
        {
            "name": "MyPlugin.DoAction",
            "ios": "MyPluginFunctions.DoAction",
            "android": "com.vendor.plugins.myplugin.MyPluginFunctions.DoAction"
        }
    ],
    "android": {
        "permissions": ["android.permission.CAMERA"],
        "dependencies": {
            "implementation": ["com.google.mlkit:barcode-scanning:17.2.0"]
        }
    },
    "ios": {
        "info_plist": {
            "NSCameraUsageDescription": "Camera is used for scanning"
        },
        "frameworks": ["AVFoundation"]
    }
}
```

### Bridge Function (PHP → Native)
```php
// Use nativephp_call() to invoke native code
nativephp_call('MyPlugin.DoAction', [
    'param1' => 'value1',
    'param2' => 42,
]);
```

## Development Workflow

```bash
# Install NativePHP Mobile
composer require nativephp/mobile

# Install plugins
composer require nativephp/mobile-camera nativephp/mobile-dialog

# Register plugins in NativeServiceProvider

# Start Jump dev server (test on real device without compiling)
php artisan native:jump

# Run on connected device
php artisan native:run

# Build release
php artisan native:run --build=release
```

## Deployment

### Android (Google Play)
```bash
# Generate signed AAB
php artisan native:package android \
    --build-type=bundle \
    --keystore=/path/to/keystore.jks \
    --keystore-password=password \
    --key-alias=upload \
    --key-password=password

# Upload to Play Store
php artisan native:package android \
    --upload-to-play-store \
    --play-store-track=internal
```

### iOS (App Store)
```bash
# Package for App Store
php artisan native:package ios \
    --export-method=app-store \
    --api-key-path=/path/to/AuthKey.p8 \
    --api-key-id=ABC123 \
    --certificate-path=/path/to/cert.p12 \
    --provisioning-profile-path=/path/to/profile.mobileprovision

# Upload to App Store Connect
php artisan native:package ios --upload-to-app-store
```

## Security

1. **Unique APP_KEY per device** -- generated at first install, stored securely
2. **SecureStorage** for tokens and sensitive data (Keychain / EncryptedSharedPreferences)
3. **Laravel Crypt** for larger data encryption before database storage
4. **Explicit plugin registration** -- prevents auto-inclusion of transitive dependencies
5. **Encrypted data is lost** if app is deleted or device is lost (by design)

## Complete Events Reference

### Camera Events
| Event | Constructor Properties |
|-------|----------------------|
| `Camera\PhotoTaken` | `string $path` |
| `Camera\PhotoCancelled` | -- |

### Biometrics Events
| Event | Constructor Properties |
|-------|----------------------|
| `Biometrics\Completed` | -- |
| `Biometrics\Failed` | `string $message` |

### Geolocation Events
| Event | Constructor Properties |
|-------|----------------------|
| `Geolocation\LocationReceived` | `float $latitude, float $longitude, float $accuracy` |
| `Geolocation\PermissionDenied` | -- |

### PushNotification Events
| Event | Constructor Properties |
|-------|----------------------|
| `PushNotification\TokenGenerated` | `string $token` |
| `PushNotification\NotificationReceived` | `array $data` |

### Scanner Events
| Event | Constructor Properties |
|-------|----------------------|
| `Scanner\CodeScanned` | `string $code, string $format` |

### Microphone Events
| Event | Constructor Properties |
|-------|----------------------|
| `Microphone\RecordingStopped` | `string $path` |
| `Microphone\RecordingError` | `string $message` |

### Network Events
| Event | Constructor Properties |
|-------|----------------------|
| `Network\StatusChanged` | `bool $connected, string $type` |

### Dialog Events
| Event | Constructor Properties |
|-------|----------------------|
| `Dialog\AlertDismissed` | `string $buttonId` |
| `Dialog\ConfirmResult` | `bool $confirmed` |

### Browser Events
| Event | Constructor Properties |
|-------|----------------------|
| `Browser\BrowserClosed` | -- |

## Best Practices

1. **Install only needed plugins** -- modular architecture keeps app size small
2. **Always register plugins explicitly** in NativeServiceProvider
3. **Handle permission denials** gracefully with user-facing messages
4. **Use EDGE components** for navigation and common native UI patterns
5. **Test with Jump** before building release versions
6. **Use SecureStorage** for tokens, never plain SharedPreferences/UserDefaults
7. **Follow async event pattern** -- never expect synchronous returns from native calls
8. **Clean up event listeners** in JavaScript to prevent memory leaks

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Plugin not found at runtime | Register in NativeServiceProvider explicitly |
| Native event not received | Use `#[OnNative(Event::class)]` (preferred) or `#[On('native:' . Event::class)]` |
| Camera/GPS permission denied | Handle PermissionDenied events with user guidance |
| App rejected from store | Provide usage descriptions in nativephp.json info_plist |
| Secure data lost after reinstall | Warn users; encrypted data is tied to installation |
| JS events not firing | Ensure `#nativephp` import map is configured in package.json |
