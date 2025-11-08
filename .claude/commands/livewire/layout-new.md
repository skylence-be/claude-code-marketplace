---
description: Create Livewire 4 layout template
model: claude-sonnet-4-5
---

Create a Livewire 4 layout template.

## Layout Specification

$ARGUMENTS

## Livewire Layout Patterns

### 1. **Basic App Layout**

```blade
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">

    <title>{{ $title ?? config('app.name') }}</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="font-sans antialiased">
    <div class="min-h-screen bg-gray-100">
        <!-- Navigation -->
        <nav class="bg-white border-b border-gray-100">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex">
                        <!-- Logo -->
                        <div class="flex-shrink-0 flex items-center">
                            <a href="/">
                                <x-application-logo class="block h-10 w-auto" />
                            </a>
                        </div>

                        <!-- Navigation Links -->
                        <div class="hidden space-x-8 sm:-my-px sm:ml-10 sm:flex">
                            <x-nav-link href="/" :active="request()->is('/')">
                                Dashboard
                            </x-nav-link>
                        </div>
                    </div>

                    <!-- Settings Dropdown -->
                    @auth
                        <div class="hidden sm:flex sm:items-center sm:ml-6">
                            <livewire:user-dropdown />
                        </div>
                    @endauth
                </div>
            </div>
        </nav>

        <!-- Page Heading -->
        @if (isset($header))
            <header class="bg-white shadow">
                <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                    {{ $header }}
                </div>
            </header>
        @endif

        <!-- Page Content -->
        <main>
            {{ $slot }}
        </main>
    </div>

    @livewireScripts
</body>
</html>
```

### 2. **Layout with Sidebar**

```blade
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ $title ?? config('app.name') }}</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="font-sans antialiased">
    <div class="flex h-screen bg-gray-100">
        <!-- Sidebar -->
        <div class="hidden md:flex md:flex-shrink-0">
            <div class="flex flex-col w-64">
                <div class="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-gray-800">
                    <!-- Sidebar Header -->
                    <div class="flex items-center flex-shrink-0 px-4">
                        <span class="text-white text-lg font-semibold">
                            {{ config('app.name') }}
                        </span>
                    </div>

                    <!-- Sidebar Navigation -->
                    <nav class="mt-5 flex-1 px-2 space-y-1">
                        <x-sidebar-link href="/dashboard" :active="request()->is('dashboard')">
                            Dashboard
                        </x-sidebar-link>
                        <x-sidebar-link href="/posts" :active="request()->is('posts*')">
                            Posts
                        </x-sidebar-link>
                        <x-sidebar-link href="/settings" :active="request()->is('settings*')">
                            Settings
                        </x-sidebar-link>
                    </nav>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex flex-col flex-1 overflow-hidden">
            <!-- Top Navigation -->
            <header class="bg-white shadow">
                <div class="flex justify-between items-center px-4 py-4">
                    <h1 class="text-2xl font-semibold text-gray-900">
                        {{ $heading ?? 'Dashboard' }}
                    </h1>

                    @auth
                        <livewire:user-menu />
                    @endauth
                </div>
            </header>

            <!-- Page Content -->
            <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100">
                <div class="container mx-auto px-6 py-8">
                    {{ $slot }}
                </div>
            </main>
        </div>
    </div>

    @livewireScripts
</body>
</html>
```

### 3. **Guest Layout**

```blade
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ $title ?? 'Welcome' }}</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="font-sans antialiased">
    <div class="min-h-screen flex flex-col sm:justify-center items-center pt-6 sm:pt-0 bg-gray-100">
        <div>
            <a href="/">
                <x-application-logo class="w-20 h-20 fill-current text-gray-500" />
            </a>
        </div>

        <div class="w-full sm:max-w-md mt-6 px-6 py-4 bg-white shadow-md overflow-hidden sm:rounded-lg">
            {{ $slot }}
        </div>
    </div>

    @livewireScripts
</body>
</html>
```

### 4. **Dashboard Layout with Notifications**

```blade
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ $title ?? config('app.name') }}</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="font-sans antialiased">
    <div class="min-h-screen bg-gray-100">
        <!-- Navigation -->
        <livewire:navigation />

        <!-- Page Header -->
        @if (isset($header))
            <header class="bg-white shadow">
                <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                        {{ $header }}
                    </h2>

                    @if (isset($actions))
                        <div>
                            {{ $actions }}
                        </div>
                    @endif
                </div>
            </header>
        @endif

        <!-- Flash Messages -->
        <livewire:flash-messages />

        <!-- Page Content -->
        <main class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                {{ $slot }}
            </div>
        </main>

        <!-- Footer -->
        <footer class="bg-white border-t border-gray-200">
            <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <p class="text-center text-sm text-gray-500">
                    &copy; {{ date('Y') }} {{ config('app.name') }}. All rights reserved.
                </p>
            </div>
        </footer>
    </div>

    @livewireScripts
</body>
</html>
```

### 5. **Layout with Laravel Reverb (Real-time)**

```blade
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ $title ?? config('app.name') }}</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="font-sans antialiased">
    <div class="min-h-screen bg-gray-100">
        <livewire:navigation />

        <!-- Real-time Notifications -->
        <livewire:notification-banner />

        <main>
            {{ $slot }}
        </main>
    </div>

    @livewireScripts

    <script>
        // Echo setup for real-time updates
        window.Echo.private('user.{{ auth()->id() }}')
            .notification((notification) => {
                Livewire.dispatch('notification-received', { notification });
            });
    </script>
</body>
</html>
```

### 6. **Admin Layout with Breadcrumbs**

```blade
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ $title ?? 'Admin' }} - {{ config('app.name') }}</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="font-sans antialiased">
    <div class="min-h-screen bg-gray-50">
        <!-- Admin Navigation -->
        <livewire:admin.navigation />

        <div class="flex">
            <!-- Admin Sidebar -->
            <livewire:admin.sidebar />

            <!-- Main Content -->
            <div class="flex-1">
                <!-- Breadcrumbs -->
                @if (isset($breadcrumbs))
                    <div class="bg-white border-b border-gray-200 px-6 py-3">
                        <nav class="flex" aria-label="Breadcrumb">
                            {{ $breadcrumbs }}
                        </nav>
                    </div>
                @endif

                <!-- Page Content -->
                <main class="p-6">
                    {{ $slot }}
                </main>
            </div>
        </div>
    </div>

    @livewireScripts
</body>
</html>
```

## Best Practices
- Include meta tags (viewport, CSRF token)
- Use @livewireStyles and @livewireScripts
- Include @vite for asset compilation
- Structure layouts with semantic HTML
- Make layouts responsive
- Include navigation components
- Add flash message areas
- Consider SEO with proper title tags
- Use slots for flexible content areas
- Include footer information

## Layout Features
- Navigation bars (top, side, both)
- User menus and dropdowns
- Flash messages and notifications
- Breadcrumbs for navigation
- Responsive mobile menus
- Footer sections
- Real-time notification areas
- Multiple content slots (header, actions, etc.)

Generate complete Livewire 4 layout template with proper structure.
