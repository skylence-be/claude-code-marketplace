---
description: Create NativeAppServiceProvider with bootstrap configuration
model: claude-sonnet-4-5
---

Create a NativeAppServiceProvider with window, menu, shortcuts, and PHP INI configuration for a NativePHP application.

## Provider Specification

$ARGUMENTS

## Provider Patterns

### 1. **Standard Desktop Application**

```php
<?php

namespace App\Providers;

use Native\Laravel\Contracts\ProvidesPhpIni;
use Native\Laravel\Facades\Window;
use Native\Laravel\Facades\Menu;
use Native\Laravel\Facades\GlobalShortcut;

class NativeAppServiceProvider implements ProvidesPhpIni
{
    public function boot(): void
    {
        // Main application window
        Window::open()
            ->width(1200)->height(800)
            ->minWidth(800)->minHeight(600)
            ->rememberState()
            ->route('dashboard');

        // Application menu
        Menu::create(
            Menu::app(),
            Menu::file(),
            Menu::edit(),
            Menu::view(),
            Menu::window(),
        );

        // Global shortcuts
        GlobalShortcut::key('CmdOrCtrl+Shift+Space')
            ->event(\App\Events\QuickCaptureEvent::class)
            ->register();
    }

    public function phpIni(): array
    {
        return [
            'memory_limit' => '256M',
            'display_errors' => '0',
            'max_execution_time' => '120',
        ];
    }
}
```

### 2. **Menu Bar / Tray Application**

```php
<?php

namespace App\Providers;

use Native\Laravel\Contracts\ProvidesPhpIni;
use Native\Laravel\Facades\MenuBar;
use Native\Laravel\Facades\Menu;
use Native\Laravel\Facades\GlobalShortcut;

class NativeAppServiceProvider implements ProvidesPhpIni
{
    public function boot(): void
    {
        // Menu bar app (no main window)
        MenuBar::create()
            ->icon(public_path('icons/tray.png'))
            ->route('menubar.index')
            ->width(380)->height(500)
            ->showDockIcon()
            ->tooltip('My Tray App')
            ->withContextMenu(
                Menu::make(
                    Menu::label('Open')
                        ->event(\App\Events\OpenAppEvent::class),
                    Menu::separator(),
                    Menu::label('Quit')->hotkey('CmdOrCtrl+Q')
                        ->event(\App\Events\QuitEvent::class),
                )
            );

        // Activation shortcut
        GlobalShortcut::key('CmdOrCtrl+Shift+K')
            ->event(\App\Events\ToggleMenuBarEvent::class)
            ->register();
    }

    public function phpIni(): array
    {
        return [
            'memory_limit' => '128M',
            'display_errors' => '0',
        ];
    }
}
```

### 3. **Multi-Window Application**

```php
<?php

namespace App\Providers;

use Native\Laravel\Contracts\ProvidesPhpIni;
use Native\Laravel\Facades\Window;
use Native\Laravel\Facades\Menu;
use Native\Laravel\Facades\GlobalShortcut;

class NativeAppServiceProvider implements ProvidesPhpIni
{
    public function boot(): void
    {
        // Main window
        Window::open('main')
            ->width(1400)->height(900)
            ->minWidth(1000)->minHeight(700)
            ->rememberState()
            ->route('dashboard');

        // Sidebar / tool panel
        Window::open('tools')
            ->width(300)->height(600)
            ->position(50, 100)
            ->route('tools.index')
            ->alwaysOnTop()
            ->titleBarHidden();

        // Application menus
        Menu::create(
            Menu::app(),
            Menu::make(
                Menu::label('New Project')->hotkey('CmdOrCtrl+N')
                    ->event(\App\Events\NewProjectEvent::class),
                Menu::label('Open Project...')->hotkey('CmdOrCtrl+O')
                    ->event(\App\Events\OpenProjectEvent::class),
                Menu::separator(),
                Menu::label('Save')->hotkey('CmdOrCtrl+S')
                    ->event(\App\Events\SaveEvent::class),
            )->label('File'),
            Menu::edit(),
            Menu::view(),
            Menu::make(
                Menu::label('Toggle Tools Panel')->hotkey('CmdOrCtrl+T')
                    ->event(\App\Events\ToggleToolsEvent::class),
            )->label('Window'),
        );

        // Global shortcuts
        GlobalShortcut::key('CmdOrCtrl+Shift+N')
            ->event(\App\Events\QuickCreateEvent::class)
            ->register();
    }

    public function phpIni(): array
    {
        return [
            'memory_limit' => '512M',
            'display_errors' => '0',
            'max_execution_time' => '300',
        ];
    }
}
```

### 4. **Mobile Application Provider**

```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class NativeServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        // Register mobile plugins explicitly
        $this->app->register(\NativePhp\MobileCamera\CameraServiceProvider::class);
        $this->app->register(\NativePhp\MobileBiometrics\BiometricsServiceProvider::class);
        $this->app->register(\NativePhp\MobileDialog\DialogServiceProvider::class);
        $this->app->register(\NativePhp\MobileGeolocation\GeolocationServiceProvider::class);
        $this->app->register(\NativePhp\MobileSecureStorage\SecureStorageServiceProvider::class);
        $this->app->register(\NativePhp\MobileFirebase\FirebaseServiceProvider::class);
    }
}
```

Generate a complete NativeAppServiceProvider (desktop) or NativeServiceProvider (mobile) with all necessary configuration for the specified application type.
