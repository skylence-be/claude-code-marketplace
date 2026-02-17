# NativePHP Blueprint Best Practices Research

> Compiled from official NativePHP documentation, community examples, and developer blog posts (February 2026)

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Desktop Architecture (v2)](#2-desktop-architecture)
3. [Mobile Architecture (v3)](#3-mobile-architecture)
4. [Electron vs Tauri Decisions](#4-electron-vs-tauri)
5. [Window Management and Lifecycle](#5-window-management)
6. [Menu, System Tray, and MenuBar](#6-menus-and-tray)
7. [File System and Native APIs](#7-native-apis)
8. [Database and Storage Strategies](#8-database-and-storage)
9. [Security Best Practices](#9-security)
10. [Authentication Patterns](#10-authentication)
11. [Laravel/Livewire Integration](#11-laravel-livewire-integration)
12. [Plugin System (Mobile v3)](#12-plugin-system)
13. [Testing Approaches](#13-testing)
14. [Deployment and Distribution](#14-deployment)
15. [Cross-Platform Considerations](#15-cross-platform)
16. [Offline-First Patterns](#16-offline-first)
17. [Community Use Cases](#17-use-cases)

---

## 1. Platform Overview

NativePHP enables Laravel developers to build desktop and mobile applications using PHP, Blade, and Livewire.

### Desktop (v2 -- Electron)
- PHP runs inside Electron with a bundled PHP binary
- Full access to native APIs (windows, menus, file system, notifications, hotkeys, etc.)
- Auto-updater built in
- macOS, Windows, Linux support

### Mobile (v3 -- Native)
- PHP runs as a C extension inside Swift (iOS) and Kotlin (Android)
- Plugin-based architecture for native capabilities
- OTA updates without app store re-submission
- iOS and Android support

### Key Differences

| Feature | Desktop v2 | Mobile v3 |
|---------|-----------|-----------|
| Runtime | Electron (Node.js + Chromium) | Native (Swift/Kotlin + PHP C extension) |
| Native Access | Direct via facades | Plugin-based architecture |
| Database | SQLite (default) | SQLite only (security decision) |
| Updates | Built-in auto-updater | OTA + app store |
| APP_KEY | Shipped with app (insecure) | Unique per-device (secure) |

Sources:
- [NativePHP Desktop v2](https://nativephp.com/docs/desktop/2/getting-started/introduction)
- [NativePHP Mobile v3](https://nativephp.com/docs/mobile/3/getting-started/introduction)

---

## 2. Desktop Architecture (v2)

### Application Structure

Standard Laravel project with NativePHP additions:

```
app/
├── Providers/
│   └── NativeAppServiceProvider.php  # Boot windows, menus, hotkeys
├── Events/                            # Native + custom events
├── Listeners/                         # React to native events
config/
└── nativephp.php                      # Version, app_id, cleanup_env_keys
```

### NativeAppServiceProvider

The central bootstrap for your desktop app:
- Configure windows on `boot()`
- Register global hotkeys
- Set up application menus
- Configure MenuBar/system tray

### Configuration (`config/nativephp.php`)

Key options:
- `version` -- App version (triggers auto-update + migration runs)
- `app_id` -- Reverse domain identifier (e.g., `com.myapp.desktop`)
- `provider` -- NativeAppServiceProvider class
- `cleanup_env_keys` -- Variables to strip from production builds (supports wildcards)
- `deep_link.scheme` -- URL scheme for deep linking
- `prebuild` / `postbuild` -- Build hook commands

Sources:
- [NativePHP Desktop Configuration](https://nativephp.com/docs/desktop/2/getting-started/configuration)

---

## 3. Mobile Architecture (v3)

### Plugin-First Philosophy

All native functionality flows through plugins. The core package is a minimal shell.

### Configuration (`config/nativephp.php` -- Mobile)

Additional mobile-specific options:
- Permissions: `biometric`, `camera`, `location`, `microphone`, `push_notifications`, `storage_access`, `scanner`, `vibrate`
- iPad support toggle
- All permissions disabled by default (opt-in)

### Platform Detection

```php
System::isIos()     // true on iOS
System::isAndroid() // true on Android
```

### Development Workflow

- `php artisan native:run` -- Compile and run
- `php artisan native:watch` -- Watch mode with hot reloading
- **Jump app** -- Test on real device via QR code without compiling
- `NATIVEPHP_APP_VERSION=DEBUG` for always-refresh during development

Sources:
- [NativePHP Mobile v3 Configuration](https://nativephp.com/docs/mobile/3/getting-started/configuration)
- [NativePHP Mobile v3 Development](https://nativephp.com/docs/mobile/3/getting-started/development)

---

## 4. Electron vs Tauri Decisions

NativePHP Desktop v2 uses **Electron** (v38). Tauri support was explored but required significantly more investment.

### Decision Framework

**Choose Electron when:**
- Full Node.js ecosystem needed
- Existing Node packages required
- Advanced multi-window workflows
- Proven-at-scale stability needed

**Choose Tauri when:**
- App size and startup time critical (120MB -> 8MB)
- 70% faster cold-start times needed
- Users keep app open all day (resource efficiency)
- Minimal footprint required

Sources:
- [NativePHP in 2025 Discussion](https://github.com/orgs/NativePHP/discussions/497)
- [DoltHub: Electron vs Tauri](https://www.dolthub.com/blog/2025-11-13-electron-vs-tauri/)

---

## 5. Window Management and Lifecycle

### Opening Windows

```php
Window::open()->width(800)->height(800);
Window::open('settings')->route('settings')->width(600)->height(400);
```

### Configuration Options

**Dimensional**: `width()`, `height()`, `minWidth()`, `minHeight()`, `maxWidth()`, `maxHeight()`, `position($x, $y)`

**Behavioral**: `resizable(false)`, `movable(false)`, `focusable(false)`, `alwaysOnTop()`, `closable()`

**Visual**: `backgroundColor('#hex')`, `titleBarHidden()`, `fullscreen()`

**Navigation**: `preventLeaveDomain()`, `preventLeavePage()`, `suppressNewWindows()`

### State Persistence

```php
Window::open()->rememberState();
```

### Window Events

`WindowShown`, `WindowClosed`, `WindowFocused`, `WindowBlurred`, `WindowMinimized`, `WindowMaximized`, `WindowResized`

Sources:
- [NativePHP Windows v2 Docs](https://nativephp.com/docs/desktop/2/the-basics/windows)

---

## 6. Menu, System Tray, and MenuBar

### MenuBar Patterns

**Standalone menu-bar-only app** (hides dock icon):
```php
MenuBar::create();
```

**MenuBar alongside windows** (shows dock icon):
```php
MenuBar::create()->showDockIcon();
```

**Configuration**: `label()`, `icon()`, `contextMenu()`

### Best Practice: Menu-Bar-Only Apps

For utility apps (CI/CD monitors, clipboard managers), menu-bar-only keeps the app minimal. Dock icon hidden automatically.

Sources:
- [NativePHP Menu Bar Docs](https://nativephp.com/docs/desktop/1/the-basics/menu-bar)

---

## 7. File System and Native APIs

### Desktop Native APIs

| Feature | Facade | Key Methods |
|---------|--------|-------------|
| Clipboard | `Clipboard` | `text()`, `write()`, `clear()` |
| Notifications | `Notification` | OS-level notifications with click events |
| Global Hotkeys | `GlobalShortcut` | `key('CmdOrCtrl+Shift+A')->event(...)` |
| System Info | `System` | `timezone()`, `theme()`, `printers()`, `canEncrypt()` |
| TouchID | `System` | `promptTouchID()` (macOS) |
| Dialogs | `Dialog` | `openFile()`, `saveFile()`, `openDirectory()` |
| Files | `Storage` | `user_home`, `desktop`, `documents`, `downloads` |

### Mobile Native APIs (v3 Plugins)

| Plugin | Capability |
|--------|-----------|
| Biometrics | Face ID / fingerprint |
| Camera | Photo/video capture |
| Geolocation | GPS coordinates |
| Microphone | Audio recording |
| Scanner | QR/barcode scanning |
| Secure Storage | Encrypted keychain/keystore |
| Browser | In-app browser with OAuth |
| Firebase | Push notifications |
| Network | Connectivity status |
| Sharing | Social sharing sheet |

Sources:
- [NativePHP Files Docs](https://nativephp.com/docs/desktop/1/digging-deeper/files)
- [NativePHP Mobile Plugins](https://nativephp.com/docs/mobile/3/plugins/introduction)

---

## 8. Database and Storage Strategies

### SQLite-Only Design

NativePHP exclusively uses SQLite. This is deliberate:

**Desktop**: Auto-creates `nativephp.sqlite` in appdata. Migrations run on version change.

**Mobile**: SQLite-only is a **security decision** -- prevents accidentally embedding production DB credentials in distributed binaries.

### Migration Management

```bash
php artisan native:migrate
php artisan native:migrate:fresh  # WARNING: Destroys all data
php artisan native:db:seed
```

**Critical**: Always test migrations on production builds before releasing updates.

### Seed Migrations (Mobile Best Practice)

Use migrations that seed data (tracked, versioned, execute once) instead of traditional seeders.

### Data Sync Pattern

```
User Action -> Write to Local SQLite -> Update UI Immediately
                                     -> Queue Sync Job
Network Available -> Process Sync Queue -> Push to API
API Response -> Update Local State if Needed
```

Sources:
- [NativePHP Desktop Databases](https://nativephp.com/docs/desktop/1/digging-deeper/databases)
- [NativePHP Mobile Databases v2](https://nativephp.com/docs/mobile/2/concepts/databases)

---

## 9. Security Best Practices

### Fundamental Principle

> Treat every distributed application as running in a **potentially hostile environment**.

### Environment File Protection

`.env` is bundled and accessible. Mitigation:
```php
'cleanup_env_keys' => [
    'AWS_*', 'DO_SPACES_*', '*_SECRET',
    'NATIVEPHP_APPLE_ID', 'NATIVEPHP_APPLE_ID_PASS',
]
```

Never store production API keys in `.env`. Create a backend API for sensitive operations.

### APP_KEY Differences

- **Desktop**: Shipped with app -- NOT secure. Generate unique keys per installation.
- **Mobile v3**: Unique per-device, stored securely. `Crypt` facade is safe.

### Secure Storage

Use `SecureStorage` for sensitive data (API tokens, credentials):
- Leverages native Keystore (Android) / Keychain (iOS/macOS)
- Encrypts/decrypts automatically
- Limited to small text data (few KB)

### Web Server Security (Desktop)

- Pre-shared auth keys between PHP and Electron
- `PreventRegularBrowserAccess` middleware
- `contextIsolation` enabled, `nodeIntegration` disabled (v2)
- Always use HTTPS for external communications

Sources:
- [NativePHP Desktop Security v2](https://nativephp.com/docs/desktop/2/digging-deeper/security)
- [NativePHP Mobile Security v3](https://nativephp.com/docs/mobile/3/concepts/security)

---

## 10. Authentication Patterns

### Mobile Authentication Flow

1. User authenticates against your API
2. Store auth token (short lifespan) + refresh token (30 days) in `SecureStorage`
3. Verify token on each app launch
4. Refresh when expired
5. Force re-auth when both tokens expire

### Laravel Sanctum Integration

```php
$token = $user->createToken('mobile-app');
```

**Important**: Enable token expiration for mobile apps (Sanctum tokens don't expire by default).

### OAuth Implementation

1. Set `NATIVEPHP_DEEPLINK_SCHEME` to unique identifier
2. Use `Browser::auth()` for secure authorization code exchange
3. Pre-register redirect URLs with OAuth provider

Sources:
- [NativePHP Mobile Authentication v3](https://nativephp.com/docs/mobile/3/concepts/authentication)

---

## 11. Laravel/Livewire Integration

### Broadcasting

NativePHP broadcasts native events and custom events through Laravel's event system.

### Custom Events

```php
class TaskCompleted implements ShouldBroadcastNow
{
    public function broadcastOn() { return ['nativephp']; }
}
```

### Listening in JavaScript

```javascript
window.Native.on('App\\Events\\TaskCompleted', (data) => { ... });
```

### Listening in Livewire

```php
#[On('native:'.WindowFocused::class)]
public function handleFocus() { ... }

// Mobile
#[OnNative(CameraPhotoTaken::class)]
public function handlePhoto($data) { ... }
```

### Mobile JavaScript APIs

```javascript
import { On, Off, Microphone, Events } from '#nativephp';
Microphone.record();
On(Events.Microphone.MicrophoneRecorded, handleRecording);
```

### Best Practice: Background Tasks

1. Trigger queued job from UI
2. Job processes in background
3. Dispatch `ShouldBroadcastNow` event when done
4. UI receives event and updates reactively

Sources:
- [NativePHP Broadcasting Docs](https://nativephp.com/docs/desktop/1/digging-deeper/broadcasting)
- [NativePHP Mobile Events v3](https://nativephp.com/docs/mobile/3/the-basics/events)

---

## 12. Plugin System (Mobile v3)

### Plugin Structure

```
my-plugin/
  composer.json          # type: "nativephp-plugin"
  nativephp.json         # Manifest: bridge functions, events, permissions
  src/
    Facades/
    Events/
    MyPluginServiceProvider.php
  resources/
    android/src/         # Kotlin bridge functions
    ios/Sources/         # Swift implementations
    js/                  # JavaScript client library
```

### Plugin Lifecycle

1. `composer require vendor/nativephp-plugin-name`
2. PHP service provider auto-discovers
3. `php artisan native:plugin:register vendor/plugin-name`
4. `php artisan native:run` -- compiles Swift/Kotlin into app
5. Use via facades: `PluginName::doSomething(['option' => 'value'])`

### Creating Plugins

```bash
php artisan native:plugin:create
```

NativePHP offers a Plugin Development Kit that integrates with Claude Code for AI-assisted generation.

Sources:
- [NativePHP Plugin Introduction v3](https://nativephp.com/docs/mobile/3/plugins/introduction)
- [NativePHP Creating Plugins v3](https://nativephp.com/docs/mobile/3/plugins/creating-plugins)

---

## 13. Testing Approaches

### Testing Layers

1. **Unit tests**: Standard Laravel PHPUnit/Pest for business logic
2. **Browser testing**: Hot reloading pushes changes to devices/simulators
3. **Jump app testing**: QR code on real device without compiling
4. **Simulator/emulator testing**: iOS Simulator and Android emulators
5. **Real device testing**: **Highly recommended** before app store submission

### Desktop v2 Testing

- **Shell Fake**: Intercept and test shell operations
- Standard browser dev tools available through Electron

### Testing Gaps

No comprehensive native feature mocking (camera, biometrics, geolocation). Must test on real or emulated devices.

Sources:
- [NativePHP Mobile Development v3](https://nativephp.com/docs/mobile/3/getting-started/development)

---

## 14. Deployment and Distribution

### Desktop Build

```bash
php artisan native:build {platform}  # mac, win, linux
```

Pre/post build hooks in `config/nativephp.php`:
```php
'prebuild' => ['npm run build', 'php artisan optimize'],
```

### Desktop Code Signing

**macOS**: Required: `NATIVEPHP_APPLE_ID`, `NATIVEPHP_APPLE_ID_PASS`, `NATIVEPHP_APPLE_TEAM_ID`. Notarization is mandatory.

**Windows**: Azure Trusted Signing (recommended) or traditional certificate.

### Desktop Auto-Update

Built-in auto-updater. Configure URL, check for updates, download, replace. `php artisan native:publish` to upload builds.

### Mobile Build (5 phases)

1. **Release build**: `php artisan native:run --build=release`
2. **Device testing**: Test on real hardware
3. **Packaging**: `php artisan native:package` (handles signing)
4. **Store submission**: Submit for Apple/Google review
5. **Publishing**: Release to stores

### Mobile Credentials

**Android**: `php artisan native:credentials android` -- auto-generates keystores. `--upload-to-play-store` for direct upload.

**iOS**: App Store Connect API key, distribution certificate, provisioning profile. `--upload-to-app-store` for direct upload.

### OTA Updates (Mobile)

Deploy changes instantly without app store re-approval.

Sources:
- [NativePHP Desktop Building v1](https://nativephp.com/docs/desktop/1/publishing/building)
- [NativePHP Mobile Deployment v3](https://nativephp.com/docs/mobile/3/getting-started/deployment)

---

## 15. Cross-Platform Considerations

### Platform-Specific Features

- `hide()` / `isHidden()` -- macOS only
- `TouchID` -- macOS only
- `badgeCount()` -- macOS/Linux only
- `openAtLogin()` -- macOS/Windows only

### Cross-Platform Shortcuts

Use `CmdOrCtrl` modifier (maps to Cmd on macOS, Ctrl on Windows/Linux).

### Mobile Cross-Platform

- Single Laravel codebase for iOS and Android
- Plugin system handles platform differences
- `System::isIos()` / `System::isAndroid()` for branching

### Build Recommendations

Use CI/CD with platform-specific runners for each target OS.

Sources:
- [NativePHP System Docs](https://nativephp.com/docs/desktop/1/the-basics/system)

---

## 16. Offline-First Patterns

### Architecture

Local storage is primary source of truth. Network is a background sync layer.

### Implementation

1. **SQLite as primary store** -- default, no config needed
2. **Laravel caching** -- speed up frequently used data
3. **Queue sync jobs** -- dispatch when connectivity returns
4. **Conflict resolution** -- last-write-wins, CRDTs, or manual

### Pattern

```
User Action -> Write to Local SQLite -> Update UI Immediately
                                     -> Queue Sync Job
Network Available -> Process Sync Queue -> Push to API
API Response -> Update Local State if Needed
```

Sources:
- [Offline First: SQLite and Caching in Desktop Apps](https://www.thecodingdev.com/2025/04/offline-first-using-sqlite-and-caching.html)

---

## 17. Community Use Cases

### Desktop Apps
- Self-hosted password manager
- Laravel log viewer
- S3 file browser
- GitHub CI/CD menu bar monitor
- Email debugger (local SMTP)
- PHP Sandbox
- AI rewriting tool
- Laravel Tinker GUI

### Mobile Apps
- PaddleLog (activity tracker)
- RacketMix (tournament management with live scoring)
- Qreate (offline QR code creator/scanner)

### Strong Use Cases
- Internal tools and dashboards for PHP/Laravel teams
- MVPs and prototypes needing native distribution
- "Wrap our web app for the store" scenarios
- Offline-first requirements
- Developer tools and utilities
- Menu-bar-only utility apps

Sources:
- [NativePHP Showcase](https://nativephp.com/showcase)
- [awesome-nativephp GitHub](https://github.com/NativePHP/awesome-nativephp)

---

## Blueprint Planning Checklist

1. **Platform targets**: Desktop only? Mobile only? Both?
2. **UI framework**: Livewire, Inertia + Vue/React, or plain Blade?
3. **Data strategy**: SQLite-only local? API-synced? Offline-first with sync?
4. **Security model**: What needs SecureStorage? How does auth flow? Never ship secrets in `.env`.
5. **Plugin selection (mobile)**: Only install what you need. Each compiles native code.
6. **Window architecture (desktop)**: Single window? Multi-window? Menu-bar only?
7. **Update strategy**: Auto-updater for desktop? OTA for mobile?
8. **Build/CI pipeline**: Platform-specific runners, code signing, build hooks.
9. **Testing plan**: Laravel unit tests for logic, device testing for native features.
10. **Cross-platform budget**: Some features are platform-specific. Plan for graceful degradation.
