---
description: Create NativePHP mobile plugin with bridge functions
model: claude-sonnet-4-5
---

Create a custom NativePHP mobile plugin with PHP facades, Swift/Kotlin bridge functions, and event handling.

## Plugin Specification

$ARGUMENTS

## Plugin Patterns

### 1. **Basic Plugin Structure**

```
my-plugin/
├── composer.json
├── nativephp.json
├── src/
│   ├── MyPluginServiceProvider.php
│   ├── Facades/
│   │   └── MyPlugin.php
│   ├── Events/
│   │   ├── ActionCompleted.php
│   │   └── ActionFailed.php
│   └── MyPluginManager.php
├── resources/
│   ├── android/src/com/vendor/plugins/myplugin/
│   │   └── MyPluginFunctions.kt
│   ├── ios/Sources/
│   │   └── MyPluginFunctions.swift
│   └── js/
│       └── index.js
```

### 2. **composer.json**

```json
{
    "name": "vendor/nativephp-my-plugin",
    "description": "My custom NativePHP plugin",
    "type": "nativephp-plugin",
    "require": {
        "php": "^8.2",
        "nativephp/mobile": "^3.0"
    },
    "autoload": {
        "psr-4": {
            "Vendor\\MyPlugin\\": "src/"
        }
    },
    "extra": {
        "laravel": {
            "providers": [
                "Vendor\\MyPlugin\\MyPluginServiceProvider"
            ]
        }
    }
}
```

### 3. **Plugin Manifest (nativephp.json)**

```json
{
    "namespace": "MyPlugin",
    "bridge_functions": [
        {
            "name": "MyPlugin.DoSomething",
            "ios": "MyPluginFunctions.DoSomething",
            "android": "com.vendor.plugins.myplugin.MyPluginFunctions.DoSomething"
        },
        {
            "name": "MyPlugin.GetStatus",
            "ios": "MyPluginFunctions.GetStatus",
            "android": "com.vendor.plugins.myplugin.MyPluginFunctions.GetStatus"
        }
    ],
    "android": {
        "permissions": [
            "android.permission.INTERNET"
        ],
        "dependencies": {
            "implementation": []
        }
    },
    "ios": {
        "info_plist": {},
        "frameworks": []
    }
}
```

### 4. **Service Provider**

```php
<?php

namespace Vendor\MyPlugin;

use Illuminate\Support\ServiceProvider;

class MyPluginServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->singleton('my-plugin', function ($app) {
            return new MyPluginManager();
        });
    }

    public function boot(): void
    {
        //
    }
}
```

### 5. **Facade**

```php
<?php

namespace Vendor\MyPlugin\Facades;

use Illuminate\Support\Facades\Facade;

class MyPlugin extends Facade
{
    protected static function getFacadeAccessor(): string
    {
        return 'my-plugin';
    }
}
```

### 6. **Manager (calls bridge functions)**

```php
<?php

namespace Vendor\MyPlugin;

class MyPluginManager
{
    public function doSomething(string $param): void
    {
        nativephp_call('MyPlugin.DoSomething', [
            'param' => $param,
        ]);
    }

    public function getStatus(): void
    {
        nativephp_call('MyPlugin.GetStatus');
    }
}
```

### 7. **Events**

```php
<?php

namespace Vendor\MyPlugin\Events;

use Illuminate\Foundation\Events\Dispatchable;

class ActionCompleted
{
    use Dispatchable;

    public function __construct(
        public string $result,
    ) {}
}
```

### 8. **Swift Bridge Function (iOS)**

```swift
// resources/ios/Sources/MyPluginFunctions.swift
import Foundation

class MyPluginFunctions {
    static func DoSomething(args: [String: Any]) {
        guard let param = args["param"] as? String else { return }

        // Native iOS implementation
        DispatchQueue.main.async {
            // Perform native action
            let result = performAction(param)

            // Send result back to PHP
            NativePhpBridge.sendEvent("ActionCompleted", data: [
                "result": result
            ])
        }
    }

    static func GetStatus(args: [String: Any]) {
        let status = getCurrentStatus()

        NativePhpBridge.sendEvent("StatusReceived", data: [
            "status": status
        ])
    }
}
```

### 9. **Kotlin Bridge Function (Android)**

```kotlin
// resources/android/src/com/vendor/plugins/myplugin/MyPluginFunctions.kt
package com.vendor.plugins.myplugin

import com.nativephp.mobile.NativePhpBridge

class MyPluginFunctions {
    companion object {
        @JvmStatic
        fun DoSomething(args: Map<String, Any>) {
            val param = args["param"] as? String ?: return

            // Native Android implementation
            val result = performAction(param)

            // Send result back to PHP
            NativePhpBridge.sendEvent("ActionCompleted", mapOf(
                "result" to result
            ))
        }

        @JvmStatic
        fun GetStatus(args: Map<String, Any>) {
            val status = getCurrentStatus()

            NativePhpBridge.sendEvent("StatusReceived", mapOf(
                "status" to status
            ))
        }
    }
}
```

### 10. **Using the Plugin in Livewire**

```php
use Livewire\Component;
use Livewire\Attributes\On;
use Vendor\MyPlugin\Facades\MyPlugin;
use Vendor\MyPlugin\Events\ActionCompleted;

class MyComponent extends Component
{
    public ?string $result = null;

    public function triggerAction()
    {
        MyPlugin::doSomething('hello');
    }

    #[On('native:' . ActionCompleted::class)]
    public function handleResult(string $result)
    {
        $this->result = $result;
    }
}
```

Generate a complete NativePHP mobile plugin with all necessary files: composer.json, nativephp.json manifest, service provider, facade, manager, events, and Swift/Kotlin bridge functions.
