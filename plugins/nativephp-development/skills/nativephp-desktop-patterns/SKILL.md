---
name: nativephp-desktop-patterns
description: Master NativePHP Desktop v2 patterns including window management, menus, system tray, notifications, dialogs, clipboard, global shortcuts, child processes, auto-updates, and cross-platform desktop development. Use when building desktop applications, implementing native OS features, or packaging apps for distribution.
category: nativephp
tags: [nativephp, desktop, electron, laravel, php, windows, menus, tray, notifications]
---

# NativePHP Desktop Patterns

Comprehensive patterns for building native desktop applications with NativePHP and Laravel.

## When to Use This Skill

- Building desktop apps with NativePHP Desktop v2
- Implementing window management and multi-window layouts
- Creating application menus and system tray apps
- Using native dialogs, notifications, and clipboard
- Registering global keyboard shortcuts
- Managing child processes and background queues
- Building and distributing desktop applications
- Implementing auto-update functionality

## Namespace Note

- **v1 (laravel package)**: `Native\Laravel\*` (e.g. `Native\Laravel\Facades\Window`)
- **v2 (desktop package)**: `Native\Desktop\*` (e.g. `Native\Desktop\Facades\Window`)

The examples below use v1 namespaces for compatibility. For v2 projects, replace `Native\Laravel` with `Native\Desktop`.

## Quick Reference

| Facade | Namespace (v1 / v2) | Purpose |
|--------|---------------------|---------|
| `Alert` | `Native\Laravel\Facades\Alert` | Native alert/message box dialogs |
| `App` | `Native\Laravel\Facades\App` | Application lifecycle and OS integration |
| `Window` | `Native\Laravel\Facades\Window` | Window lifecycle and management |
| `Menu` | `Native\Laravel\Facades\Menu` | Application and context menus |
| `MenuBar` | `Native\Laravel\Facades\MenuBar` | System tray / menu bar apps |
| `ContextMenu` | `Native\Laravel\Facades\ContextMenu` | Right-click context menus |
| `Notification` | `Native\Laravel\Facades\Notification` | OS notifications |
| `Dialog` | `Native\Laravel\Dialog` | File open/save/folder dialogs |
| `Clipboard` | `Native\Laravel\Facades\Clipboard` | Text, HTML, image clipboard |
| `GlobalShortcut` | `Native\Laravel\Facades\GlobalShortcut` | System-wide hotkeys |
| `Shell` | `Native\Laravel\Facades\Shell` | File reveal, open, trash |
| `System` | `Native\Laravel\Facades\System` | Encryption, Touch ID, printers |
| `ChildProcess` | `Native\Laravel\Facades\ChildProcess` | Background process management |
| `PowerMonitor` | `Native\Laravel\Facades\PowerMonitor` | Battery, idle, thermal state |
| `Screen` | `Native\Laravel\Facades\Screen` | Display and cursor info |
| `AutoUpdater` | `Native\Laravel\Facades\AutoUpdater` | App update management |
| `QueueWorker` | `Native\Laravel\Facades\QueueWorker` | Background job processing |
| `Dock` | `Native\Laravel\Facades\Dock` | macOS Dock control |
| `Process` | `Native\Laravel\Facades\Process` | System process info |
| `Settings` | `Native\Laravel\Facades\Settings` | Persistent app settings (key-value) |
| `ProgressBar` | `Native\Laravel\Facades\ProgressBar` | Window taskbar progress |

## Alert Facade

```php
use Native\Laravel\Facades\Alert;

// Simple alert
Alert::new()
    ->type('info')         // 'none', 'info', 'error', 'question', 'warning'
    ->title('Alert Title')
    ->detail('Detailed message text')
    ->buttons(['OK', 'Cancel'])
    ->defaultId(0)
    ->cancelId(1)
    ->show();

// Quick error alert
Alert::error('Something went wrong', 'Error details here');
```

## App Facade

```php
use Native\Laravel\Facades\App;

App::quit();
App::relaunch();
App::focus();
App::hide();
$hidden = App::isHidden();
$locale = App::getLocale();         // e.g. 'en-US'
$ver = App::version();
App::badgeCount(5);                 // set dock/taskbar badge
App::addRecentDocument($path);
$docs = App::recentDocuments();
App::clearRecentDocuments();
$bundled = App::isRunningBundled(); // true in production build
App::openAtLogin(true);             // launch on system startup
App::showEmojiPanel();              // open OS emoji picker
```

## Context Menu

```php
use Native\Laravel\Facades\ContextMenu;

// Register a context menu for right-click
ContextMenu::register(
    Menu::make(
        Menu::label('Cut')->hotkey('CmdOrCtrl+X'),
        Menu::label('Copy')->hotkey('CmdOrCtrl+C'),
        Menu::label('Paste')->hotkey('CmdOrCtrl+V'),
    )
);

// Remove context menu
ContextMenu::remove();
```

## Dock (macOS)

```php
use Native\Laravel\Facades\Dock;

$bounceId = Dock::bounce();        // bounce dock icon, returns bounce ID
Dock::cancelBounce($bounceId);
Dock::badge('3');                   // set badge text
Dock::icon($path);                  // set custom dock icon
Dock::menu(Menu::make(...));        // set dock menu
Dock::show();
Dock::hide();
```

## Process Facade

```php
use Native\Laravel\Facades\Process;

$arch = Process::arch();            // e.g. 'x64', 'arm64'
$platform = Process::platform();    // e.g. 'darwin', 'win32', 'linux'
$uptime = Process::uptime();        // system uptime in seconds
Process::fresh();                   // restart the app process
```

## Settings Facade

```php
use Native\Laravel\Facades\Settings;

Settings::set('theme', 'dark');
$theme = Settings::get('theme');           // returns 'dark'
$default = Settings::get('missing', 'fallback');  // with default
Settings::forget('theme');
Settings::clear();                         // remove all settings
```

## ProgressBar Facade

```php
use Native\Laravel\Facades\ProgressBar;

// Update window taskbar progress (0.0 to 1.0, or -1 to hide)
ProgressBar::update(0.5);          // 50% progress
ProgressBar::update(-1);           // hide progress bar
```

## Window Management

### Opening Windows
```php
use Native\Laravel\Facades\Window;

// Basic window
Window::open('main')
    ->width(1200)->height(800)
    ->route('dashboard');

// Fully configured window
Window::open('editor')
    ->width(900)->height(700)
    ->minWidth(600)->minHeight(400)
    ->position(100, 100)
    ->route('editor.show', ['id' => $id])
    ->rememberState()        // persist size/position across restarts
    ->titleBarHidden()       // frameless window with traffic lights
    ->resizable()
    ->closable()
    ->focusable()
    ->alwaysOnTop();

// External URL with navigation restriction
Window::open('docs')
    ->url('https://docs.example.com')
    ->preventLeaveDomain();  // or ->preventLeavePage()
```

### Window Operations
```php
Window::close('settings');
Window::resize(800, 600, 'main');
Window::position(100, 100, 'main');
Window::minimize('main');
Window::maximize('main');
Window::current();          // get focused window info
Window::all();              // get all open windows
```

### Window Events
| Event | Triggered When |
|-------|---------------|
| `WindowShown` | Window becomes visible |
| `WindowHidden` | Window is hidden |
| `WindowClosed` | Window is closed |
| `WindowFocused` | Window gains focus |
| `WindowBlurred` | Window loses focus |
| `WindowMinimized` | Window is minimized |
| `WindowMaximized` | Window is maximized |
| `WindowResized` | Window is resized |

## Application Menus

### Standard Menu
```php
use Native\Laravel\Facades\Menu;

Menu::create(
    Menu::app(),       // macOS app menu (About, Preferences, Quit)
    Menu::file(),      // Standard File menu
    Menu::edit(),      // Standard Edit menu (undo, copy, paste)
    Menu::view(),      // Standard View menu (reload, zoom, fullscreen)
    Menu::window(),    // Standard Window menu
);
```

### Custom Menu Items
```php
// Text label with hotkey and event
Menu::label('New Document')->hotkey('CmdOrCtrl+N')
    ->event(NewDocumentEvent::class);

// Checkbox item
Menu::checkbox('Dark Mode', checked: true)
    ->event(ToggleDarkModeEvent::class);

// Link to URL
Menu::link('https://docs.example.com', 'Documentation');

// Link to route
Menu::route('settings', 'Settings');

// Separator
Menu::separator();

// Submenu
Menu::make(
    Menu::label('Option 1')->event(Option1Event::class),
    Menu::label('Option 2')->event(Option2Event::class),
)->label('Submenu');

// Disabled item (display only)
Menu::label('Status: Connected')->enabled(false);
```

### Hotkey Modifiers
| Modifier | macOS | Windows/Linux |
|----------|-------|--------------|
| `Command` | Cmd | - |
| `Control` | Ctrl | Ctrl |
| `CmdOrCtrl` | Cmd | Ctrl |
| `Alt` / `Option` | Option | Alt |
| `Shift` | Shift | Shift |
| `Super` / `Meta` | Cmd | Win |

## Menu Bar / System Tray

```php
use Native\Laravel\Facades\MenuBar;

MenuBar::create()
    ->icon(public_path('icons/tray.png'))
    ->route('menubar.index')
    ->width(400)->height(500)
    ->showDockIcon()           // show in macOS dock
    ->label('Status Text')     // text next to icon (macOS)
    ->tooltip('Hover text')
    ->withContextMenu(Menu::make(...))
    ->alwaysOnTop();

// Control visibility
MenuBar::show();
MenuBar::hide();
```

## Notifications

```php
use Native\Laravel\Facades\Notification;

Notification::title('Download Complete')
    ->message('Your file has been downloaded successfully.')
    ->event(NotificationClickedEvent::class)
    ->show();
```

## Dialogs

```php
use Native\Laravel\Dialog;

// Open file(s)
$paths = Dialog::new()
    ->title('Select Files')
    ->filter('Images', ['jpg', 'png', 'gif'])
    ->filter('Documents', ['pdf', 'docx'])
    ->multiple()
    ->withHiddenFiles()
    ->asSheet()               // macOS sheet dialog
    ->open();

// Save file
$path = Dialog::new()
    ->title('Save As')
    ->defaultPath('~/Documents/export.csv')
    ->filter('CSV', ['csv'])
    ->save();

// Select folder
$folder = Dialog::new()->folders()->open();
```

## Clipboard

```php
use Native\Laravel\Facades\Clipboard;

// Read
$text = Clipboard::text();

// Write
Clipboard::text('Copied text');
Clipboard::html('<b>Bold text</b>');
Clipboard::image('path/to/image.png');

// Clear
Clipboard::clear();
```

## Global Shortcuts

```php
use Native\Laravel\Facades\GlobalShortcut;

// Register
GlobalShortcut::key('CmdOrCtrl+Shift+A')
    ->event(MyShortcutEvent::class)
    ->register();

// Unregister
GlobalShortcut::key('CmdOrCtrl+Shift+A')->unregister();
```

## Shell Operations

```php
use Native\Laravel\Facades\Shell;

Shell::openFile($path);         // open with default app
Shell::showInFolder($path);     // reveal in Finder/Explorer
Shell::trashFile($path);        // move to trash
Shell::openExternal($url);      // open URL in browser
```

## System

```php
use Native\Laravel\Facades\System;

// Encryption (OS-level)
$encrypted = System::encrypt($data);
$decrypted = System::decrypt($encrypted);
$canEncrypt = System::canEncrypt();

// Biometric (macOS)
$authenticated = System::promptTouchID('Confirm action');

// Printing
$printers = System::printers();
System::print($html);
$pdf = System::printToPDF($html);

// System info
$timezone = System::timezone();
$theme = System::theme();       // 'light', 'dark', or 'system'
```

## Child Processes

```php
use Native\Laravel\Facades\ChildProcess;

// Start processes
ChildProcess::start('command', alias: 'name');
ChildProcess::php('script.php', alias: 'php-script');
ChildProcess::artisan('queue:work', alias: 'worker');
ChildProcess::node('script.js', alias: 'node-script');  // v2

// Manage processes
$process = ChildProcess::get('name');
ChildProcess::restart('name');
ChildProcess::stop('name');
$all = ChildProcess::all();
```

## Power Monitor

```php
use Native\Laravel\Facades\PowerMonitor;

$idleState = PowerMonitor::getSystemIdleState(300);  // ACTIVE, IDLE, LOCKED
$idleTime = PowerMonitor::getSystemIdleTime();        // seconds
$thermal = PowerMonitor::getCurrentThermalState();     // NOMINAL, FAIR, SERIOUS, CRITICAL
$onBattery = PowerMonitor::isOnBatteryPower();
```

## Queue Workers

```php
use Native\Laravel\Facades\QueueWorker;

QueueWorker::up(alias: 'worker');
QueueWorker::down(alias: 'worker');
```

Configure in `config/nativephp.php`:
```php
'queue_workers' => [
    'default' => [
        'queues' => ['default'],
        'memory_limit' => 128,
        'timeout' => 60,
        'sleep' => 3,
    ],
],
```

## Event Broadcasting

```php
// Broadcast event from PHP
use Illuminate\Contracts\Broadcasting\ShouldBroadcastNow;

class DataUpdated implements ShouldBroadcastNow
{
    public function __construct(public array $data) {}

    public function broadcastOn(): array
    {
        return ['nativephp'];
    }
}

// Listen in JavaScript
Native.on("App\\Events\\DataUpdated", (payload) => {
    updateUI(payload.data);
});

// Listen in Livewire
#[On('native:'.DataUpdated::class)]
public function handleDataUpdated(array $data)
{
    $this->refresh();
}
```

## Auto-Updater

```php
use Native\Laravel\Facades\AutoUpdater;

AutoUpdater::checkForUpdates();
AutoUpdater::quitAndInstall();
```

Configure provider in `config/nativephp.php`:
```php
'updater' => [
    'enabled' => true,
    'default' => 'github',  // or 's3', 'spaces'
],
```

## Complete Events Reference (47 Events)

### App Events
| Event | Properties |
|-------|-----------|
| `ApplicationBooted` | -- |
| `OpenFile` | `string $path` |
| `OpenedFromURL` | `string $url` |

### AutoUpdater Events
| Event | Properties |
|-------|-----------|
| `CheckingForUpdate` | -- |
| `DownloadProgress` | `float $percent, int $bytesPerSecond, int $transferred, int $total` |
| `Error` | `string $message` |
| `UpdateAvailable` | `string $version` |
| `UpdateCancelled` | -- |
| `UpdateDownloaded` | `string $version` |
| `UpdateNotAvailable` | -- |

### ChildProcess Events
| Event | Properties |
|-------|-----------|
| `ErrorReceived` | `string $alias, string $error` |
| `MessageReceived` | `string $alias, string $message` |
| `ProcessExited` | `string $alias, int $code` |
| `ProcessSpawned` | `string $alias, int $pid` |
| `StartupError` | `string $alias, string $error` |

### Menu Events
| Event | Properties |
|-------|-----------|
| `MenuItemClicked` | `string $id` |

### MenuBar Events
| Event | Properties |
|-------|-----------|
| `MenuBarClicked` | -- |
| `MenuBarCreated` | -- |
| `MenuBarDoubleClicked` | -- |
| `MenuBarDroppedFiles` | `array $files` |
| `MenuBarHidden` | -- |
| `MenuBarRightClicked` | -- |
| `MenuBarShown` | -- |

### Notification Events
| Event | Properties |
|-------|-----------|
| `NotificationActionClicked` | `string $actionId` |
| `NotificationClicked` | -- |
| `NotificationClosed` | -- |
| `NotificationReply` | `string $reply` |

### PowerMonitor Events
| Event | Properties |
|-------|-----------|
| `PowerStateChanged` | `string $state` |
| `ScreenLocked` | -- |
| `ScreenUnlocked` | -- |
| `Shutdown` | -- |
| `SpeedLimitChanged` | `int $limit` |
| `ThermalStateChanged` | `string $state` |
| `UserDidBecomeActive` | -- |
| `UserDidResignActive` | -- |

### Settings Events
| Event | Properties |
|-------|-----------|
| `SettingChanged` | `string $key, mixed $value` |

### Window Events
| Event | Properties |
|-------|-----------|
| `WindowBlurred` | `string $id` |
| `WindowClosed` | `string $id` |
| `WindowFocused` | `string $id` |
| `WindowHidden` | `string $id` |
| `WindowMaximized` | `string $id` |
| `WindowMinimized` | `string $id` |
| `WindowResized` | `string $id, int $width, int $height` |
| `WindowShown` | `string $id` |

## Test Fakes (6 Fakes)

NativePHP Desktop provides 6 fake test doubles:

### WindowManagerFake
```php
use Native\Laravel\Facades\Window;

Window::fake();

// Assertions
Window::assertOpened('window-id');
Window::assertClosed('window-id');
Window::assertHidden('window-id');
Window::assertShown('window-id');
Window::assertOpenedCount(2);
Window::assertClosedCount(1);

// Stub return values
Window::alwaysReturnWindows([$windowObject]);
```

### ShellFake
```php
use Native\Laravel\Facades\Shell;

Shell::fake();

Shell::assertShowInFolder('/path/to/file');
Shell::assertOpenedFile('/path/to/file');
Shell::assertTrashedFile('/path/to/file');
Shell::assertOpenedExternal('https://example.com');
```

### ChildProcessFake
```php
use Native\Laravel\Facades\ChildProcess;

ChildProcess::fake();

ChildProcess::assertStarted('alias');
ChildProcess::assertPhp('script.php');
ChildProcess::assertArtisan('queue:work');
ChildProcess::assertNode('script.js');
ChildProcess::assertStop('alias');
ChildProcess::assertRestart('alias');
ChildProcess::assertMessage('alias');
```

### GlobalShortcutFake
```php
use Native\Laravel\Facades\GlobalShortcut;

GlobalShortcut::fake();

GlobalShortcut::assertKey('CmdOrCtrl+N');
GlobalShortcut::assertEvent(MyEvent::class);
GlobalShortcut::assertRegisteredCount(3);
GlobalShortcut::assertUnregisteredCount(1);
```

### PowerMonitorFake
```php
use Native\Laravel\Facades\PowerMonitor;

PowerMonitor::fake();

PowerMonitor::assertGetSystemIdleState();
PowerMonitor::assertGetSystemIdleStateCount(2);
```

### QueueWorkerFake
```php
use Native\Laravel\Facades\QueueWorker;

QueueWorker::fake();

QueueWorker::assertUp();
QueueWorker::assertDown();
```

## Enums

```php
use Native\Laravel\Enums\PowerStatesEnum;
// PowerStatesEnum::AC, PowerStatesEnum::BATTERY

use Native\Laravel\Enums\RolesEnum;
// RolesEnum has 20 values for menu item roles:
// UNDO, REDO, CUT, COPY, PASTE, PASTE_AND_MATCH_STYLE, DELETE,
// SELECT_ALL, RELOAD, FORCE_RELOAD, TOGGLE_DEV_TOOLS, RESET_ZOOM,
// ZOOM_IN, ZOOM_OUT, TOGGLE_FULLSCREEN, WINDOW_MENU, MINIMIZE,
// CLOSE, HELP, ABOUT, SERVICES, HIDE, HIDE_OTHERS, UNHIDE, QUIT,
// ZOOM, FRONT, APP_MENU, FILE_MENU, EDIT_MENU, VIEW_MENU, WINDOW_MENU

use Native\Laravel\Enums\SystemIdleStatesEnum;
// SystemIdleStatesEnum::ACTIVE, ::IDLE, ::LOCKED, ::UNKNOWN

use Native\Laravel\Enums\SystemThemesEnum;
// SystemThemesEnum::SYSTEM, ::LIGHT, ::DARK

use Native\Laravel\Enums\ThermalStatesEnum;
// ThermalStatesEnum::UNKNOWN, ::NOMINAL, ::FAIR, ::SERIOUS, ::CRITICAL
```

## Filesystem Disks

NativePHP configures Laravel filesystem disks for common OS directories:

```php
// Available in config/filesystems.php automatically
Storage::disk('user_home')->path('');     // ~/
Storage::disk('app_data')->path('');      // app data directory
Storage::disk('user_data')->path('');     // user data directory
Storage::disk('desktop')->path('');       // ~/Desktop
Storage::disk('documents')->path('');     // ~/Documents
Storage::disk('downloads')->path('');     // ~/Downloads
Storage::disk('music')->path('');         // ~/Music
Storage::disk('pictures')->path('');      // ~/Pictures
Storage::disk('videos')->path('');        // ~/Videos
Storage::disk('recent')->path('');        // recent files directory
Storage::disk('extras')->path('');        // bundled extras directory
```

Use these disks to read/write files in platform-appropriate locations without hardcoding paths.

## Artisan Commands

```bash
php artisan native:install          # Install NativePHP
php artisan native:run              # Run app (dev mode)
php artisan native:build            # Build for current platform
php artisan native:build win        # Build for Windows
php artisan native:build mac        # Build for macOS
php artisan native:build linux      # Build for Linux
php artisan native:migrate          # Run migrations
php artisan native:migrate:fresh    # Fresh migrations
php artisan native:db:seed          # Seed database
```

## Best Practices

1. **Always use `rememberState()`** for main windows to persist user preferences
2. **Increment version** in `config/nativephp.php` for every build (triggers migrations)
3. **Use queues** for network requests and heavy computation, not for simple UI operations
4. **Set `APP_DEBUG=false`** in production builds
5. **Clean secrets** with `cleanup_env_keys` before building
6. **Code sign** applications for macOS auto-updates and trust
7. **Use SQLite** as the only supported database engine
8. **Handle window events** to save state and clean up resources
9. **Test with fakes** instead of running Electron during tests

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| App shows blank window | Ensure route exists and `native:run` server is running |
| Menus not updating | Call `Menu::create()` again with new items |
| Secrets in build | Add patterns to `cleanup_env_keys` in config |
| Migrations not running | Increment `version` in config |
| v1 namespace errors | Migrate from `Native\Laravel` to `Native\Desktop` (v2) |
| Window state not saved | Add `->rememberState()` to window config |
