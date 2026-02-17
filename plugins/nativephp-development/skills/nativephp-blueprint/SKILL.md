---
name: nativephp-blueprint
description: Master NativePHP Blueprint - the AI planning format for generating accurate, production-ready NativePHP code for Desktop v2 and Mobile v3. Use when planning native app implementations, creating detailed specifications, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
category: nativephp
tags: [nativephp, blueprint, ai, planning, architecture, specification, desktop, mobile]
related_skills: [nativephp-desktop-patterns, nativephp-mobile-patterns, nativephp-testing-patterns]
---

# NativePHP Blueprint

NativePHP Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for NativePHP Desktop v2 and Mobile v3 projects. It bridges the gap between high-level requirements and production-ready native application code.

## When to Use This Skill

- Planning complex NativePHP desktop or mobile applications
- Creating detailed specifications before writing code
- Generating comprehensive native app architectures
- Documenting window management, plugin selection, and native API usage
- Ensuring all details are captured (providers, events, plugins, security)
- Avoiding vague plans that lead to vague code
- Deciding between Desktop, Mobile, or cross-platform targets

## Blueprint Plan Structure

A complete Blueprint includes these sections:

### 1. Overview & Key Decisions

```markdown
# Desktop File Manager

A desktop application for browsing, searching, and managing files across local and cloud storage.

## Key Decisions
- Platform: Desktop v2 (Electron) -- macOS, Windows, Linux
- UI: Livewire 3 with Blade components
- Database: SQLite for bookmarks, recent files, preferences
- Multi-window: Main browser + settings + preview windows
- Menu bar: Quick-access tray icon with recent files
- Update strategy: Built-in auto-updater via S3
```

### 2. Platform Target

Declare the platform explicitly with rationale:

```markdown
## Platform

### Target: Desktop v2 (Electron)
**Rationale**: File system access, multi-window layout, menu bar integration, and OS-level dialogs are core requirements. These are desktop-native features not available on mobile.

### Supported OS
- macOS 12+ (primary)
- Windows 10+ (secondary)
- Linux (Ubuntu 22.04+, best-effort)
```

### 3. NativeAppServiceProvider

The central bootstrap for the app:

```markdown
## NativeAppServiceProvider

### boot()
1. Open main window: route('files.index'), 1200x800, minWidth 800, minHeight 600, rememberState
2. Register menu bar: icon('files'), contextMenu with recent files
3. Register global hotkeys:
   - CmdOrCtrl+N: new window
   - CmdOrCtrl+Shift+F: global search dialog
4. Set up application menu with File, Edit, View, Help groups
```

### 4. Window Architecture

```markdown
## Windows

### Main Window (files)
| Property | Value |
|----------|-------|
| Route | files.index |
| Width | 1200 |
| Height | 800 |
| Min Width | 800 |
| Min Height | 600 |
| Resizable | yes |
| Remember State | yes |
| Title Bar | hidden (custom) |

### Settings Window (settings)
| Property | Value |
|----------|-------|
| Route | settings.index |
| Width | 600 |
| Height | 500 |
| Resizable | no |
| Always On Top | yes |
| Closable | yes |

### Preview Window (preview)
| Property | Value |
|----------|-------|
| Route | files.preview |
| Width | 800 |
| Height | 600 |
| Title Bar | default |
| Remember State | yes |
```

### 5. Models & Database

```markdown
## Models

### Bookmark
**Table**: bookmarks

| Column | Type | Constraints |
|--------|------|-------------|
| id | uuid | primary |
| path | string | required |
| label | string | required |
| icon | string | nullable |
| sort_order | integer | default: 0 |

**Traits**: HasUuids

### RecentFile
**Table**: recent_files

| Column | Type | Constraints |
|--------|------|-------------|
| id | uuid | primary |
| path | string | required |
| opened_at | timestamp | required |

**Traits**: HasUuids
```

### 6. Artisan Commands

```markdown
## Commands

php artisan install:broadcasting --no-interaction
php artisan make:model Bookmark -mf --no-interaction
php artisan make:model RecentFile -mf --no-interaction
php artisan make:model Preference -mf --no-interaction
php artisan make:event FileOpened --no-interaction
php artisan make:event FileRenamed --no-interaction
php artisan make:listener LogRecentFile --no-interaction
```

### 7. Events & Listeners

```markdown
## Events

### Native Events Handled
| Event | Listener | Action |
|-------|----------|--------|
| WindowFocused | RefreshFileList | Re-scan directory for external changes |
| WindowClosed('preview') | CleanupPreview | Release file handles |

### Custom Events
| Event | Broadcasts | Payload |
|-------|-----------|---------|
| FileOpened | ShouldBroadcastNow | path, timestamp |
| SyncCompleted | ShouldBroadcastNow | files_synced, errors |
```

### 8. Native API Usage

```markdown
## Native APIs

### Dialogs
- Dialog::openFile(): File open picker with type filters
- Dialog::openDirectory(): Folder selection for root browsing
- Dialog::saveFile(): Export/save-as operations

### Clipboard
- Clipboard::write(): Copy file paths
- Clipboard::text(): Paste paths for navigation

### Notifications
- OS notification on sync complete
- OS notification on large file operation complete

### Global Shortcuts
| Shortcut | Action |
|----------|--------|
| CmdOrCtrl+N | Open new browser window |
| CmdOrCtrl+Shift+F | Open global search |
| CmdOrCtrl+, | Open settings |
```

### 9. Security Model

```markdown
## Security

### Environment Cleanup
cleanup_env_keys: ['AWS_*', 'DO_*', '*_SECRET', 'NATIVEPHP_APPLE_*']

### Sensitive Storage
- Cloud API tokens: SecureStorage (Keychain/Keystore)
- User preferences: SQLite (non-sensitive)
- File bookmarks: SQLite (non-sensitive)

### APP_KEY Strategy
- Desktop: Generate unique key on first launch, store in SecureStorage
- Never ship production keys in .env

### Middleware
- PreventRegularBrowserAccess on all routes
```

### 10. Configuration

```markdown
## Config (config/nativephp.php)

| Key | Value | Notes |
|-----|-------|-------|
| version | 1.0.0 | Triggers auto-update + migrations |
| app_id | com.myapp.filemanager | Reverse domain |
| cleanup_env_keys | ['AWS_*', '*_SECRET'] | Strip from builds |
| deep_link.scheme | filemanager | filemanager://open?path=... |
| prebuild | ['npm run build'] | Compile assets before build |
```

### 11. Testing Strategy

```markdown
## Testing

### Unit Tests (Pest)
- Bookmark CRUD operations
- RecentFile tracking and cleanup
- Preference storage and retrieval

### Facade Fake Tests
- Window::fake() -- verify windows opened with correct config
- Dialog::fake() -- verify file dialogs triggered
- Clipboard::fake() -- verify clipboard operations

### Browser Tests
- File list renders correctly
- Navigation between directories
- Bookmark add/remove from sidebar

### Manual Device Testing
1. [ ] macOS: Window management, menu bar, TouchID
2. [ ] Windows: Tray icon, shortcuts, file dialogs
3. [ ] Linux: Basic window operations, notifications
```

### 12. Build & Distribution

```markdown
## Build

### Desktop
php artisan native:build mac
php artisan native:build win
php artisan native:build linux

### Code Signing
- macOS: NATIVEPHP_APPLE_ID, NATIVEPHP_APPLE_ID_PASS, NATIVEPHP_APPLE_TEAM_ID
- Windows: Azure Trusted Signing

### Auto-Update
- Host builds on S3/CDN
- Version in config/nativephp.php triggers update check
- Users notified via OS notification
```

### 13. Verification Checklist

```markdown
## Verification

### Manual Testing
1. [ ] Main window opens at correct size
2. [ ] Settings window opens as modal
3. [ ] Preview window shows file content
4. [ ] Menu bar icon appears with context menu
5. [ ] Global shortcuts work (Cmd+N, Cmd+Shift+F)
6. [ ] File dialogs open native OS pickers
7. [ ] Bookmarks persist across restarts
8. [ ] Auto-update triggers on version change
9. [ ] Code signing verified on macOS and Windows

### Automated
php artisan test --filter=BookmarkTest
php artisan test --filter=RecentFileTest
php artisan test --filter=WindowConfigTest
```

## Vague Plan vs Blueprint: Critical Differences

A vague plan answers "what to build" but leaves "how" to interpretation. A Blueprint provides **implementation-ready specifications** with exact code patterns.

### VAGUE PLAN (Before Blueprint)

```markdown
## File Manager App
- Browse files and folders
- Bookmarks sidebar
- Preview pane
- Cloud sync
- Menu bar icon
```

**Problems:**
- No window configuration or sizing
- No NativeAppServiceProvider bootstrap plan
- No native API mapping (which dialogs, which shortcuts)
- No security model (how are cloud tokens stored?)
- No event/listener wiring
- No platform-specific considerations

### BLUEPRINT (Implementation-Ready)

**File Manager App**
- **Platform**: Desktop v2 (Electron) -- macOS, Windows, Linux
- **Docs**: https://nativephp.com/docs/desktop/2/getting-started/introduction

**NativeAppServiceProvider::boot()**:

```php
Window::open('files')
    ->route('files.index')
    ->width(1200)
    ->height(800)
    ->minWidth(800)
    ->minHeight(600)
    ->titleBarHidden()
    ->rememberState();

MenuBar::create()
    ->icon(storage_path('app/icons/tray.png'))
    ->showDockIcon()
    ->contextMenu(
        Menu::make()
            ->label('Recent Files')
            ->submenu(
                Menu::make()
                    ->event(ShowRecentFiles::class)
            )
            ->separator()
            ->label('Quit')
            ->quit()
    );

GlobalShortcut::key('CmdOrCtrl+N')
    ->event(OpenNewWindow::class)
    ->register();

GlobalShortcut::key('CmdOrCtrl+Shift+F')
    ->event(OpenGlobalSearch::class)
    ->register();
```

**File Open Dialog**:

```php
Dialog::new()
    ->title('Open File')
    ->asSheet(Window::current())
    ->addFilter('Documents', ['pdf', 'docx', 'txt'])
    ->addFilter('Images', ['png', 'jpg', 'gif'])
    ->open();
```

**Security: Cloud Token Storage**:

```php
// Store token after OAuth flow
SecureStorage::set('cloud_api_token', $token);

// Retrieve on each API call
$token = SecureStorage::get('cloud_api_token');

// Never in .env, never in SQLite
```

## Platform Decision Framework

Before writing any Blueprint, decide the target platform. This is the single most important architectural decision.

### Decision Matrix

| Requirement | Desktop v2 | Mobile v3 | Both |
|-------------|-----------|-----------|------|
| File system access | Yes | Limited | Desktop primary |
| Multi-window UI | Yes | No | Desktop only |
| Menu bar / system tray | Yes | No | Desktop only |
| Camera / biometrics | Limited (TouchID) | Full plugin suite | Mobile primary |
| GPS / geolocation | No | Yes (plugin) | Mobile only |
| Push notifications | OS-level | Firebase plugin | Both (different APIs) |
| App store distribution | No (direct download) | Yes | Platform-specific |
| OTA updates | Auto-updater | Yes | Both (different mechanisms) |
| Offline-first | SQLite default | SQLite only | Same pattern |

### Platform Declaration Template

```markdown
## Platform Target

### Primary: [Desktop v2 / Mobile v3 / Both]
**Rationale**: [Why this platform fits the use case]

### Desktop Config (if applicable)
- Electron runtime
- Supported OS: [macOS, Windows, Linux]
- Window architecture: [single / multi-window / menu-bar-only]

### Mobile Config (if applicable)
- iOS [minimum version] + Android [minimum API level]
- Required plugins: [list]
- Required permissions: [list]
- iPad support: [yes/no]
```

## Window Architecture Patterns

### Single Window App

Best for focused tools (note apps, viewers, dashboards):

```php
// NativeAppServiceProvider::boot()
Window::open()
    ->route('dashboard')
    ->width(1024)
    ->height(768)
    ->rememberState();
```

### Multi-Window App

Best for productivity apps (file managers, IDEs, email clients):

```php
// NativeAppServiceProvider::boot()
Window::open('main')
    ->route('main')
    ->width(1200)
    ->height(800)
    ->rememberState();

// Opened on demand
Window::open('settings')
    ->route('settings')
    ->width(600)
    ->height(400)
    ->alwaysOnTop();

Window::open('preview')
    ->route('preview', ['file' => $path])
    ->width(800)
    ->height(600);
```

### Menu-Bar-Only App

Best for utilities (monitors, clipboard managers, quick launchers):

```php
// NativeAppServiceProvider::boot()
// No Window::open() call -- menu bar only, dock icon hidden
MenuBar::create()
    ->icon(storage_path('app/icons/menubar.png'))
    ->label('Status: OK')
    ->contextMenu(
        Menu::make()
            ->label('Dashboard')
            ->event(OpenDashboard::class)
            ->separator()
            ->label('Preferences...')
            ->event(OpenPreferences::class)
            ->separator()
            ->label('Quit')
            ->quit()
    );
```

## Plugin Selection Guide (Mobile v3)

Every plugin compiles native Swift/Kotlin code into the binary. Only install what you need.

### Plugin Selection by Feature

| Need | Plugin | Permission | Notes |
|------|--------|------------|-------|
| Face ID / fingerprint | Biometrics | `biometric` | iOS Face ID + Android fingerprint |
| Take photos/video | Camera | `camera` | Photo/video capture |
| GPS coordinates | Geolocation | `location` | Foreground location |
| Record audio | Microphone | `microphone` | Audio recording |
| Scan QR/barcodes | Scanner | `scanner` | Camera-based scanning |
| Store secrets | Secure Storage | none | Keychain (iOS) / Keystore (Android) |
| In-app browser | Browser | none | OAuth redirect support |
| Push notifications | Firebase | `push_notifications` | FCM for both platforms |
| Network status | Network | none | Online/offline detection |
| Social sharing | Sharing | none | Native share sheet |
| Haptic feedback | Vibrate | `vibrate` | Vibration patterns |

### Installation Pattern

```bash
composer require nativephp/plugin-biometrics
composer require nativephp/plugin-camera
php artisan native:plugin:register nativephp/plugin-biometrics
php artisan native:plugin:register nativephp/plugin-camera
```

### Permission Declaration (config/nativephp.php)

```php
'permissions' => [
    'biometric' => true,
    'camera' => true,
    'location' => false,    // Not needed -- don't enable
    'microphone' => false,
    'push_notifications' => true,
    'storage_access' => false,
    'scanner' => false,
    'vibrate' => false,
],
```

**Rule**: Default all permissions to `false`. Only enable what the Blueprint requires.

## Database and Storage Strategy

### SQLite-Only Design

NativePHP uses SQLite exclusively. This is a deliberate security decision -- prevents embedding production DB credentials in distributed binaries.

### Storage Decision Matrix

| Data Type | Storage | Why |
|-----------|---------|-----|
| User content (notes, files, records) | SQLite | Persistent, queryable, migrated |
| API tokens, secrets | SecureStorage | OS-level encryption (Keychain/Keystore) |
| User preferences | SQLite | Non-sensitive, queryable |
| Cached API responses | SQLite or Laravel Cache | Ephemeral, rebuildable |
| Session data | SQLite | Persistent across restarts |
| Large binary files | File system (Storage facade) | Not suitable for SQLite |

### Migration Strategy

**Critical Rules:**
1. Migrations run on version change (`config/nativephp.php` `version`)
2. Always test migrations on production builds before release
3. Never use `migrate:fresh` in production — destroys user data
4. Use seed migrations (not seeders) for default data on mobile

**Seed Migration Example:**

```php
// database/migrations/2026_01_01_000001_seed_default_categories.php
public function up(): void
{
    DB::table('categories')->insert([
        ['name' => 'Personal', 'icon' => 'user', 'sort_order' => 0],
        ['name' => 'Work', 'icon' => 'briefcase', 'sort_order' => 1],
        ['name' => 'Archive', 'icon' => 'archive', 'sort_order' => 2],
    ]);
}
```

### Offline-First Sync Pattern

```php
// 1. Write locally first
$note = Note::create([
    'title' => $title,
    'body' => $body,
    'synced' => false,
]);

// 2. Queue sync job
SyncNote::dispatch($note);

// 3. Sync job attempts API push
class SyncNote implements ShouldQueue
{
    public function handle(): void
    {
        $response = Http::withToken(SecureStorage::get('api_token'))
            ->post('https://api.example.com/notes', $this->note->toArray());

        if ($response->successful()) {
            $this->note->update(['synced' => true, 'remote_id' => $response->json('id')]);
        }
    }

    public function failed(): void
    {
        // Re-queue for later -- network unavailable
    }
}

// 4. Broadcast completion to UI
class SyncCompleted implements ShouldBroadcastNow
{
    public function __construct(public int $synced, public int $failed) {}
    public function broadcastOn(): array { return ['nativephp']; }
}
```

## Security Model

### APP_KEY Differences

| Platform | APP_KEY Behavior | Security Level | Recommendation |
|----------|-----------------|----------------|----------------|
| Desktop v2 | Shipped with app | NOT secure | Generate unique key per installation |
| Mobile v3 | Unique per device | Secure | `Crypt` facade is safe to use |

### Desktop APP_KEY Mitigation

```php
// On first launch, generate and persist a unique key
if (! SecureStorage::get('app_encryption_key')) {
    $key = Str::random(32);
    SecureStorage::set('app_encryption_key', $key);
}
```

### Environment Cleanup (Desktop)

```php
// config/nativephp.php
'cleanup_env_keys' => [
    'AWS_*',
    'DO_SPACES_*',
    '*_SECRET',
    'NATIVEPHP_APPLE_ID',
    'NATIVEPHP_APPLE_ID_PASS',
    'STRIPE_*',
    'MAIL_*',
],
```

**Rule**: Wildcards supported. Strip anything that should not ship in a distributed binary.

### SecureStorage Usage

```php
use Native\Laravel\Facades\SecureStorage;

// Store sensitive data
SecureStorage::set('api_token', $token);
SecureStorage::set('refresh_token', $refreshToken);

// Retrieve
$token = SecureStorage::get('api_token');

// Delete
SecureStorage::delete('api_token');
```

**Limits**: Small text data only (a few KB). Not for files or large blobs.

### Security Checklist

| Check | Desktop v2 | Mobile v3 |
|-------|-----------|-----------|
| APP_KEY unique per install | Generate on first launch | Automatic |
| Secrets in SecureStorage | Yes (Keychain) | Yes (Keychain/Keystore) |
| cleanup_env_keys configured | Required | N/A (no .env shipped) |
| PreventRegularBrowserAccess | Required middleware | N/A |
| No production DB credentials | Never ship in .env | SQLite only |
| HTTPS for external calls | Always | Always |
| contextIsolation enabled | Default in v2 | N/A |
| nodeIntegration disabled | Default in v2 | N/A |

## Authentication Patterns

### Mobile Authentication Flow

```markdown
## Auth Flow

1. User opens app -> check SecureStorage for auth_token
2. If token exists -> verify against API -> proceed or force re-auth
3. If no token -> show login screen
4. On login success:
   - Store auth_token (short lifespan, e.g. 60 min) in SecureStorage
   - Store refresh_token (30 days) in SecureStorage
5. On each API call:
   - Attach auth_token
   - If 401 -> use refresh_token to get new auth_token
   - If refresh fails -> force re-auth
```

### Laravel Sanctum Integration

```php
// API side: create token with expiration
$token = $user->createToken('mobile-app', expiresAt: now()->addHour());

// Mobile side: store token
SecureStorage::set('auth_token', $token->plainTextToken);
SecureStorage::set('refresh_token', $refreshToken);

// Mobile side: attach to requests
Http::withToken(SecureStorage::get('auth_token'))
    ->get('https://api.example.com/user');
```

**Important**: Sanctum tokens do not expire by default. Always set `expiresAt` for mobile apps.

### OAuth Implementation

```php
// 1. Configure deep link scheme in config/nativephp.php
'deep_link' => [
    'scheme' => 'myapp',  // myapp://oauth/callback
],

// 2. Initiate OAuth with Browser::auth()
Browser::auth('https://provider.com/oauth/authorize?' . http_build_query([
    'client_id' => config('services.provider.client_id'),
    'redirect_uri' => 'myapp://oauth/callback',
    'response_type' => 'code',
    'scope' => 'read write',
]));

// 3. Handle callback in routes/web.php
Route::get('/oauth/callback', function (Request $request) {
    $code = $request->query('code');
    // Exchange code for token via API
    $response = Http::post('https://provider.com/oauth/token', [
        'grant_type' => 'authorization_code',
        'code' => $code,
        'redirect_uri' => 'myapp://oauth/callback',
        'client_id' => config('services.provider.client_id'),
        'client_secret' => config('services.provider.client_secret'),
    ]);
    SecureStorage::set('oauth_token', $response->json('access_token'));
    return redirect('/dashboard');
});
```

## Laravel/Livewire Integration

### Broadcasting Native Events

NativePHP broadcasts native events through Laravel's event system. Listen in Livewire:

```php
use Livewire\Attributes\On;
use Native\Laravel\Events\Windows\WindowFocused;

class FileList extends Component
{
    #[On('native:' . WindowFocused::class)]
    public function refreshOnFocus(): void
    {
        // Re-scan directory when window regains focus
        $this->files = $this->scanDirectory($this->currentPath);
    }
}
```

### Custom Event Broadcasting

```php
// Define event
class SyncCompleted implements ShouldBroadcastNow
{
    public function __construct(
        public int $filesSynced,
        public int $errors,
    ) {}

    public function broadcastOn(): array
    {
        return ['nativephp'];
    }
}

// Dispatch from queue job
event(new SyncCompleted(filesSynced: 42, errors: 0));
```

### Listening in JavaScript (Desktop)

```javascript
window.Native.on('App\\Events\\SyncCompleted', (data) => {
    console.log(`Synced ${data.filesSynced} files`);
});
```

### Mobile Event Listening (Livewire)

```php
use NativePHP\Livewire\Attributes\OnNative;
use NativePHP\Camera\Events\CameraPhotoTaken;

class PhotoCapture extends Component
{
    #[OnNative(CameraPhotoTaken::class)]
    public function handlePhoto(array $data): void
    {
        $this->photoPath = $data['path'];
    }
}
```

### Mobile JavaScript APIs

```javascript
import { On, Off, Microphone, Events } from '#nativephp';

// Start recording
Microphone.record();

// Listen for result
On(Events.Microphone.MicrophoneRecorded, (data) => {
    // Handle audio data
});
```

### Background Task Pattern

```php
// 1. User triggers action in Livewire component
public function startSync(): void
{
    $this->syncing = true;
    SyncAllFiles::dispatch();
}

// 2. Job processes in background
class SyncAllFiles implements ShouldQueue
{
    public function handle(): void
    {
        $synced = 0;
        foreach (File::unsyncedFiles() as $file) {
            // sync logic...
            $synced++;
        }
        event(new SyncCompleted(filesSynced: $synced, errors: 0));
    }
}

// 3. Livewire receives broadcast and updates UI
#[On('native:App\\Events\\SyncCompleted')]
public function handleSyncComplete(int $filesSynced): void
{
    $this->syncing = false;
    $this->syncedCount = $filesSynced;
}
```

## Testing Approaches

### Testing Layers

| Layer | Tool | What It Tests | When to Use |
|-------|------|---------------|-------------|
| Unit | Pest / PHPUnit | Business logic, models, services | Always |
| Facade Fakes | NativePHP fakes | Native API calls (windows, dialogs) | Desktop v2 |
| Browser (hot reload) | native:watch | UI rendering, Livewire interactions | During development |
| Jump App | QR code on device | Real device behavior without compile | Mobile v3 development |
| Simulator/Emulator | Xcode / Android Studio | Platform-specific behavior | Before release |
| Real Device | Physical hardware | Full native experience | Before app store submission |

### Facade Fake Testing (Desktop)

```php
use Native\Laravel\Facades\Window;
use Native\Laravel\Facades\Dialog;
use Native\Laravel\Facades\Clipboard;

it('opens settings window with correct dimensions', function () {
    Window::fake();

    // Trigger action that opens settings
    $this->post('/settings/open');

    Window::assertOpened('settings');
    Window::assertOpened('settings', function ($window) {
        return $window->width === 600 && $window->height === 400;
    });
});

it('copies file path to clipboard', function () {
    Clipboard::fake();

    $this->post('/files/copy-path', ['path' => '/home/user/doc.pdf']);

    Clipboard::assertCopied('/home/user/doc.pdf');
});
```

### Event Testing

```php
use Illuminate\Support\Facades\Event;

it('dispatches FileOpened event when file is opened', function () {
    Event::fake([FileOpened::class]);

    $this->post('/files/open', ['path' => '/home/user/doc.pdf']);

    Event::assertDispatched(FileOpened::class, function ($event) {
        return $event->path === '/home/user/doc.pdf';
    });
});
```

### Model & Database Testing

```php
it('limits recent files to 50 entries', function () {
    RecentFile::factory()->count(50)->create();

    $new = RecentFile::create(['path' => '/new/file.txt', 'opened_at' => now()]);

    expect(RecentFile::count())->toBe(50);
    expect(RecentFile::oldest('opened_at')->first()->path)->not->toBe('/new/file.txt');
});
```

### Manual Device Testing Checklist

```markdown
## Device Testing

### Desktop (per OS)
- [ ] Window opens at correct dimensions
- [ ] Menu bar icon visible and functional
- [ ] Global shortcuts registered and working
- [ ] File dialogs use native OS pickers
- [ ] Notifications appear in OS notification center
- [ ] Auto-updater detects new version
- [ ] App persists window state across restarts

### Mobile (per platform)
- [ ] Biometric prompt appears and authenticates
- [ ] Camera opens and returns photo
- [ ] Push notification received and handled
- [ ] Offline mode works (airplane mode test)
- [ ] App resumes correctly from background
- [ ] OTA update applies without reinstall
```

## Deployment and Distribution

### Desktop Build Commands

```bash
# Build for each platform
php artisan native:build mac
php artisan native:build win
php artisan native:build linux

# With pre-build hooks (configured in config/nativephp.php)
# 'prebuild' => ['npm run build', 'php artisan optimize'],
```

### Desktop Code Signing

```markdown
## Code Signing

### macOS (required for distribution)
Environment variables:
- NATIVEPHP_APPLE_ID: Apple Developer account email
- NATIVEPHP_APPLE_ID_PASS: App-specific password
- NATIVEPHP_APPLE_TEAM_ID: Developer Team ID
Notarization is mandatory for macOS distribution.

### Windows
Azure Trusted Signing (recommended) or traditional code signing certificate.
```

### Desktop Auto-Update

```markdown
## Auto-Update Strategy

1. Host builds on S3, CDN, or custom server
2. Bump `version` in config/nativephp.php
3. Run `php artisan native:publish` to upload
4. App checks for updates automatically
5. User prompted to install or auto-installs on next launch
```

### Mobile Build Pipeline (5 Phases)

```markdown
## Mobile Deployment

### Phase 1: Release Build
php artisan native:run --build=release

### Phase 2: Device Testing
Test on real iOS and Android devices. Do NOT skip this.

### Phase 3: Packaging
php artisan native:package
# Handles code signing automatically

### Phase 4: Store Submission
# Android
php artisan native:credentials android --upload-to-play-store

# iOS
# Requires: App Store Connect API key, distribution certificate, provisioning profile
php artisan native:credentials ios --upload-to-app-store

### Phase 5: OTA Updates
Deploy PHP/Blade/Livewire changes without app store re-submission.
Only native code changes (Swift/Kotlin) require store re-review.
```

## Cross-Platform Considerations

### Platform-Specific Features (Desktop)

| Feature | macOS | Windows | Linux |
|---------|-------|---------|-------|
| `hide()` / `isHidden()` | Yes | No | No |
| TouchID / biometrics | Yes | No | No |
| `badgeCount()` | Yes | No | Yes |
| `openAtLogin()` | Yes | Yes | No |
| System tray | Yes | Yes | Yes |
| Notifications | Yes | Yes | Yes |
| Global shortcuts | Yes | Yes | Yes |

### Cross-Platform Shortcut Pattern

Always use `CmdOrCtrl` for keyboard shortcuts:

```php
GlobalShortcut::key('CmdOrCtrl+Shift+F')
    ->event(OpenSearch::class)
    ->register();
// Maps to Cmd on macOS, Ctrl on Windows/Linux
```

### Mobile Cross-Platform

```php
// Platform branching when needed
if (System::isIos()) {
    // iOS-specific behavior (e.g., haptics style)
}

if (System::isAndroid()) {
    // Android-specific behavior (e.g., back button handling)
}
```

### Graceful Degradation Pattern

```php
// Check capability before using
if (System::canPromptTouchID()) {
    $authenticated = System::promptTouchID('Confirm your identity');
} else {
    // Fall back to password entry
    return redirect('/auth/password');
}
```

## Common Planning Mistakes Checklist

| Mistake | Impact | Fix |
|---------|--------|-----|
| No platform declaration | Agent guesses Desktop vs Mobile | Declare platform + rationale in section 1 |
| Missing NativeAppServiceProvider | No windows, menus, or hotkeys boot | Plan boot() with every window, menu, shortcut |
| Shipping secrets in .env | API keys exposed in distributed binary | Use cleanup_env_keys + SecureStorage |
| Using MySQL/Postgres | Connection fails on user devices | SQLite only -- NativePHP design decision |
| Enabling all mobile permissions | App store rejection, user distrust | Default false, enable only what Blueprint requires |
| No window sizing constraints | UI breaks on small screens | Always set minWidth, minHeight |
| Missing rememberState() | User loses window position on restart | Add to main window at minimum |
| No auto-update plan | Users stuck on old versions | Configure updater (desktop) or OTA (mobile) |
| Skipping device testing | Native features fail on real hardware | Always test on physical devices before release |
| No offline handling | App crashes without network | Design for SQLite-first, sync in background |
| Desktop APP_KEY shipped as-is | Encryption compromised for all users | Generate unique key per installation |
| Using seeders on mobile | Data not inserted on user devices | Use seed migrations instead |
| No event/listener plan | Native events unhandled, UI stale | Map every native event to a listener or Livewire handler |
| Vague security section | Token storage unclear | Specify exactly what goes in SecureStorage vs SQLite |

## Best Practices

1. **Declare platform first** -- Desktop v2, Mobile v3, or Both. This shapes every subsequent decision.
2. **Plan NativeAppServiceProvider completely** -- Every window, menu, shortcut, and tray icon must be specified.
3. **Map native APIs explicitly** -- List every Dialog, Clipboard, Notification, and Shortcut call with parameters.
4. **Use SecureStorage for secrets** -- API tokens, encryption keys, OAuth tokens. Never SQLite, never `.env`.
5. **Configure cleanup_env_keys** -- Strip all sensitive variables from desktop builds using wildcards.
6. **Design offline-first** -- Write to SQLite immediately, sync in background, handle network failures gracefully.
7. **Use seed migrations on mobile** -- Traditional seeders do not run on user devices. Seed via migrations.
8. **Plan window architecture** -- Single, multi-window, or menu-bar-only. Include dimensions, constraints, and behavior.
9. **Select plugins minimally** -- Each mobile plugin compiles native code. Only install what the Blueprint requires.
10. **Test on real devices** -- Facade fakes and simulators catch logic bugs, but native features require physical hardware.
11. **Plan events and broadcasting** -- Map native events to Livewire handlers. Use `ShouldBroadcastNow` for background-to-UI communication.
12. **Include build and signing** -- Specify platform build commands, signing credentials, and update strategy.
13. **Version carefully** -- Bumping `version` in config triggers migrations. Test migration paths before release.
14. **File inventory** -- Categorized list of all files the implementation will create or modify.

## Anti-Patterns to Avoid

| Vague | Blueprint |
|-------|-----------|
| "open a window" | `Window::open('main')->route('dashboard')->width(1200)->height(800)->minWidth(800)->rememberState()` |
| "add menu bar" | `MenuBar::create()->icon(storage_path('...'))->showDockIcon()->contextMenu(Menu::make()->...)` |
| "store the token" | `SecureStorage::set('auth_token', $token)` with retrieval, refresh, and expiry logic |
| "handle file picking" | `Dialog::new()->title('Open')->addFilter('Docs', ['pdf','docx'])->open()` |
| "sync data" | Write to SQLite -> Queue SyncJob -> API push -> Broadcast SyncCompleted -> Livewire updates |
| "add keyboard shortcut" | `GlobalShortcut::key('CmdOrCtrl+Shift+F')->event(OpenSearch::class)->register()` |
| "send notifications" | `Notification::title('Sync Complete')->message('42 files synced')->show()` |
| "secure the app" | cleanup_env_keys config + SecureStorage for tokens + PreventRegularBrowserAccess middleware |
| "add biometrics" | `composer require nativephp/plugin-biometrics` + permission config + `Biometrics::authenticate()` |
| "deploy to stores" | 5-phase pipeline: release build -> device test -> package -> store submit -> OTA updates |

## Common Patterns

### Window with State Persistence

```php
Window::open('main')
    ->route('dashboard')
    ->width(1200)
    ->height(800)
    ->minWidth(800)
    ->minHeight(600)
    ->rememberState();
```

### Menu Bar with Context Menu

```php
MenuBar::create()
    ->icon(storage_path('app/icons/tray.png'))
    ->showDockIcon()
    ->contextMenu(
        Menu::make()
            ->label('Open Dashboard')
            ->event(OpenDashboard::class)
            ->separator()
            ->label('Sync Now')
            ->event(TriggerSync::class)
            ->separator()
            ->label('Quit')
            ->quit()
    );
```

### Global Shortcut Registration

```php
GlobalShortcut::key('CmdOrCtrl+N')
    ->event(CreateNewItem::class)
    ->register();

GlobalShortcut::key('CmdOrCtrl+Shift+F')
    ->event(OpenGlobalSearch::class)
    ->register();
```

### SecureStorage Token Management

```php
// Store after authentication
SecureStorage::set('auth_token', $response->json('token'));
SecureStorage::set('refresh_token', $response->json('refresh_token'));
SecureStorage::set('token_expires_at', now()->addHour()->toISOString());

// Check and refresh
$expiresAt = Carbon::parse(SecureStorage::get('token_expires_at'));
if ($expiresAt->isPast()) {
    $response = Http::post('https://api.example.com/refresh', [
        'refresh_token' => SecureStorage::get('refresh_token'),
    ]);
    SecureStorage::set('auth_token', $response->json('token'));
    SecureStorage::set('token_expires_at', now()->addHour()->toISOString());
}
```

### Offline-First Write Pattern

```php
// Always write locally first
$record = Note::create([
    'title' => $request->title,
    'body' => $request->body,
    'synced' => false,
]);

// Queue background sync
SyncNote::dispatch($record);

// UI shows immediately -- no waiting for network
```

### Native Event to Livewire

```php
use Livewire\Attributes\On;
use Native\Laravel\Events\Windows\WindowFocused;

class Dashboard extends Component
{
    #[On('native:' . WindowFocused::class)]
    public function refresh(): void
    {
        $this->records = Record::latest()->get();
    }
}
```

### Platform-Aware Feature

```php
// Graceful degradation for platform-specific features
public function authenticate(): bool
{
    if (System::canPromptTouchID()) {
        return System::promptTouchID('Verify your identity');
    }

    // Fall back to password
    return $this->verifyPassword();
}
```

### Mobile Plugin Usage Pattern

```php
use NativePHP\Camera\Facades\Camera;
use NativePHP\Camera\Events\CameraPhotoTaken;

// Trigger camera
Camera::takePhoto();

// Handle in Livewire
#[OnNative(CameraPhotoTaken::class)]
public function handlePhoto(array $data): void
{
    $this->photoPath = $data['path'];
    $this->save();
}
```

## File Inventory Template

Every Blueprint should end with a categorized file list:

```markdown
## Files

### Configuration (1)
- config/nativephp.php

### Providers (1)
- app/Providers/NativeAppServiceProvider.php

### Models (3)
- app/Models/Bookmark.php
- app/Models/RecentFile.php
- app/Models/Preference.php

### Events (3)
- app/Events/FileOpened.php
- app/Events/FileRenamed.php
- app/Events/SyncCompleted.php

### Listeners (2)
- app/Listeners/LogRecentFile.php
- app/Listeners/RefreshFileList.php

### Livewire Components (4)
- app/Livewire/FileList.php
- app/Livewire/Sidebar.php
- app/Livewire/Preview.php
- app/Livewire/Settings.php

### Views (5)
- resources/views/livewire/file-list.blade.php
- resources/views/livewire/sidebar.blade.php
- resources/views/livewire/preview.blade.php
- resources/views/livewire/settings.blade.php
- resources/views/layouts/app.blade.php

### Migrations (3)
- database/migrations/xxxx_create_bookmarks_table.php
- database/migrations/xxxx_create_recent_files_table.php
- database/migrations/xxxx_create_preferences_table.php

### Factories (3)
- database/factories/BookmarkFactory.php
- database/factories/RecentFileFactory.php
- database/factories/PreferenceFactory.php

### Tests (4)
- tests/Feature/BookmarkTest.php
- tests/Feature/RecentFileTest.php
- tests/Feature/FileListTest.php
- tests/Feature/WindowConfigTest.php
```
