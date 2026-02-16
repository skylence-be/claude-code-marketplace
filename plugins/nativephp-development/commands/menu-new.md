---
description: Create NativePHP menu or menu bar configuration
model: claude-sonnet-4-5
---

Create a NativePHP application menu, context menu, or menu bar (system tray) configuration.

## Menu Specification

$ARGUMENTS

## Menu Patterns

### 1. **Application Menu**

```php
use Native\Laravel\Facades\Menu;

Menu::create(
    Menu::app(),
    Menu::make(
        Menu::label('New Document')->hotkey('CmdOrCtrl+N')
            ->event(NewDocumentEvent::class),
        Menu::label('Open...')->hotkey('CmdOrCtrl+O')
            ->event(OpenDocumentEvent::class),
        Menu::separator(),
        Menu::label('Save')->hotkey('CmdOrCtrl+S')
            ->event(SaveDocumentEvent::class),
        Menu::label('Save As...')->hotkey('CmdOrCtrl+Shift+S')
            ->event(SaveAsDocumentEvent::class),
        Menu::separator(),
        Menu::label('Export as PDF')->hotkey('CmdOrCtrl+E')
            ->event(ExportPdfEvent::class),
    )->label('File'),
    Menu::edit(),
    Menu::view(),
    Menu::make(
        Menu::label('Documentation')
            ->link('https://docs.example.com'),
        Menu::separator(),
        Menu::label('About')
            ->event(ShowAboutEvent::class),
    )->label('Help'),
    Menu::window(),
);
```

### 2. **Menu Bar / System Tray Application**

```php
use Native\Laravel\Facades\MenuBar;
use Native\Laravel\Facades\Menu;

MenuBar::create()
    ->icon(public_path('icons/tray-icon.png'))
    ->route('menubar.dashboard')
    ->width(380)->height(500)
    ->showDockIcon()
    ->label('Active')
    ->tooltip('My App - Click to open')
    ->withContextMenu(
        Menu::make(
            Menu::label('Open Dashboard')
                ->event(OpenDashboardEvent::class),
            Menu::separator(),
            Menu::checkbox('Auto-Sync', checked: true)
                ->event(ToggleAutoSyncEvent::class),
            Menu::checkbox('Notifications', checked: true)
                ->event(ToggleNotificationsEvent::class),
            Menu::separator(),
            Menu::make(
                Menu::label('Settings')
                    ->event(OpenSettingsEvent::class),
                Menu::label('Check for Updates')
                    ->event(CheckUpdatesEvent::class),
            )->label('More'),
            Menu::separator(),
            Menu::label('Quit')->hotkey('CmdOrCtrl+Q')
                ->event(QuitEvent::class),
        )
    )
    ->alwaysOnTop();
```

### 3. **Dynamic Context Menu**

```php
use Native\Laravel\Facades\Menu;

// In a controller or service
public function updateMenu(string $status)
{
    Menu::create(
        Menu::app(),
        Menu::make(
            Menu::label("Status: {$status}")->enabled(false),
            Menu::separator(),
            $status === 'running'
                ? Menu::label('Stop')->event(StopEvent::class)
                : Menu::label('Start')->event(StartEvent::class),
            Menu::separator(),
            Menu::label('Settings')->hotkey('CmdOrCtrl+,')
                ->route('settings'),
        )->label('App'),
    );
}
```

### 4. **Menu with Roles (Standard Actions)**

```php
use Native\Laravel\Facades\Menu;

Menu::create(
    Menu::app(),
    Menu::make(
        Menu::label('New')->hotkey('CmdOrCtrl+N')
            ->event(NewEvent::class),
        Menu::separator(),
        // Standard file operations
        Menu::label('Close Window')->hotkey('CmdOrCtrl+W')
            ->role('close'),
    )->label('File'),
    // Standard edit menu with undo, redo, cut, copy, paste
    Menu::edit(),
    // Standard view menu with reload, zoom, fullscreen
    Menu::view(),
    // Standard window menu
    Menu::window(),
);
```

### 5. **Menu Event Handlers**

```php
// Event class
namespace App\Events;

use Illuminate\Foundation\Events\Dispatchable;

class NewDocumentEvent
{
    use Dispatchable;
}

// Listener
namespace App\Listeners;

use App\Events\NewDocumentEvent;
use Native\Laravel\Facades\Window;

class HandleNewDocument
{
    public function handle(NewDocumentEvent $event): void
    {
        $document = Document::create(['title' => 'Untitled']);

        Window::open("editor-{$document->id}")
            ->width(900)->height(700)
            ->route('documents.edit', ['document' => $document]);
    }
}
```

Generate complete menu configuration with all items, hotkeys, events, and any associated event classes and listeners.
