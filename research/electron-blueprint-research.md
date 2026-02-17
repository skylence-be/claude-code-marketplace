# Electron Blueprint Best Practices Research

> Compiled from official Electron documentation, community guides, security research, and developer blog posts (February 2026)

## Table of Contents

1. [Latest Electron Version](#1-latest-electron-version)
2. [Architecture Best Practices](#2-architecture-best-practices)
3. [Security Best Practices](#3-security-best-practices)
4. [Performance Optimization](#4-performance-optimization)
5. [Project Structure](#5-project-structure)
6. [Build Tooling](#6-build-tooling)
7. [State Management](#7-state-management)
8. [Auto-Updates](#8-auto-updates)
9. [Testing Strategies](#9-testing-strategies)
10. [Native Integrations](#10-native-integrations)
11. [Build & Distribution](#11-build--distribution)
12. [Common Anti-Patterns](#12-common-anti-patterns)
13. [Community Conventions](#13-community-conventions)

---

## 1. Latest Electron Version

### Current Stable: Electron 40 (v40.4.1)

As of February 2026, Electron 40 is the current stable release.

| Component | Version |
|-----------|---------|
| Electron | 40.4.1 |
| Chromium | 144.0.7559.173 |
| Node.js | 24.11.1 |
| V8 | 14.4 |

### Release Cadence

A new major stable version is released every 8 weeks, in tandem with every other Chromium major version. The official support policy covers the latest 3 stable releases.

### Currently Supported Versions

| Version | Chromium | Node.js | End of Life |
|---------|----------|---------|-------------|
| 40 | 144 | 24.11.1 | June 30, 2026 |
| 39 | 142 | 22.20.0 | May 5, 2026 |
| 38 | 140 | 22.18.0 | March 10, 2026 |

### Key Features by Version

**Electron 40:**
- RGBAF16 output format with scRGB HDR color space support for Offscreen Rendering
- `app.isHardwareAccelerationEnabled()` API
- `bypassCustomProtocolHandlers` option added to `net.request`
- Upgraded to Chromium 144, Node.js 24.11.1, V8 14.4

**Electron 39:**
- ASAR integrity is now **stable** (previously experimental) -- validates `app.asar` at runtime against a build-time hash; app terminates on mismatch
- `disclaim` option added to UtilityProcess API for TCC disclaiming on macOS
- CoreAudio Tap API support for audio capture in `desktopCapturer`
- Upgraded to Chromium 142, Node.js 22.20.0, V8 14.2

**Electron 38:**
- Dropped macOS 11 support (macOS 12+ required)
- Removed `ELECTRON_OZONE_PLATFORM_HINT` environment variable
- Removed the `plugin-crashed` event
- Upgraded to Chromium 140, Node.js 22.18.0, V8 14.0

**Electron 37:**
- New `-electron-corner-smoothing` CSS property for squircle-style rounded corners (macOS-inspired)
- Utility process unhandled rejection behavior change
- `process.exit()` now kills utility processes synchronously
- WebUSB/WebSerial blocklist support changes

### Breaking Changes Summary (Recent Versions)

- **Electron 39**: `window.open` popups are now always resizable; shared texture OSR paint event data structure changed
- **Electron 38**: macOS 11 dropped; `plugin-crashed` event removed
- **Electron 37**: Utility process crashes on unhandled rejections
- **Electron 20+**: Sandbox enabled by default for renderers
- **Electron 14**: `remote` module removed from core (moved to `@electron/remote`)
- **Electron 12**: `contextIsolation` enabled by default

Sources:
- [Electron Releases](https://releases.electronjs.org/)
- [Electron Timelines](https://www.electronjs.org/docs/latest/tutorial/electron-timelines)
- [Electron 40.0.0 Blog Post](https://www.electronjs.org/blog/electron-40-0)
- [Electron 39.0.0 Release](https://releases.electronjs.org/release/v39.0.0)
- [Electron Breaking Changes](https://www.electronjs.org/docs/latest/breaking-changes)
- [endoflife.date - Electron](https://endoflife.date/electron)

---

## 2. Architecture Best Practices

### Process Model

Electron uses a multi-process architecture inherited from Chromium:

| Process | Role | Node.js Access | DOM Access |
|---------|------|----------------|------------|
| **Main** | App lifecycle, native APIs, window management | Full | None |
| **Renderer** | UI rendering (one per window) | None (sandboxed) | Full |
| **Preload** | Bridge between main and renderer | Limited (contextBridge) | Limited |
| **Utility** | CPU-intensive tasks, untrusted services | Full | None |

### Main Process Responsibilities

- Application lifecycle management (`app.on('ready')`, `app.on('window-all-closed')`)
- Creating and managing `BrowserWindow` instances
- System tray, menus, dialogs, notifications
- File system operations and native OS integrations
- IPC message handling (`ipcMain.handle()`, `ipcMain.on()`)
- Auto-update orchestration

### Renderer Process Responsibilities

- UI rendering with HTML/CSS/JavaScript
- Frontend framework code (React, Vue, Svelte, etc.)
- User interaction handling
- Communicating with main process exclusively via IPC

### Preload Scripts

Preload scripts bridge the gap between isolated renderer processes and the main process:

```javascript
// preload.ts
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  // One method per IPC message -- never expose raw ipcRenderer
  loadPreferences: () => ipcRenderer.invoke('load-prefs'),
  savePreferences: (prefs) => ipcRenderer.invoke('save-prefs', prefs),
  onUpdateAvailable: (callback) => {
    ipcRenderer.on('update-available', (_event, info) => callback(info));
  },
});
```

**Critical Rules:**
- Never expose `ipcRenderer` directly via contextBridge
- Provide one wrapper method per IPC message
- Never expose raw Electron APIs to the renderer
- Preload scripts must be a single bundled file when sandbox is enabled

### Context Isolation

Context isolation (enabled by default since Electron 12) runs Electron APIs and preload scripts in a separate JavaScript context from the renderer's web content:

```javascript
const win = new BrowserWindow({
  webPreferences: {
    contextIsolation: true,    // default: true (since Electron 12)
    nodeIntegration: false,     // default: false
    sandbox: true,              // default: true (since Electron 20)
    preload: path.join(__dirname, 'preload.js'),
  },
});
```

### IPC Communication Patterns

**Pattern 1: Renderer to Main (Request/Response)**
```javascript
// preload.ts
contextBridge.exposeInMainWorld('api', {
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
});

// main.ts
ipcMain.handle('get-system-info', async () => {
  return { platform: process.platform, arch: process.arch };
});

// renderer.ts
const info = await window.api.getSystemInfo();
```

**Pattern 2: Main to Renderer (Push)**
```javascript
// main.ts
win.webContents.send('update-progress', { percent: 50 });

// preload.ts
contextBridge.exposeInMainWorld('api', {
  onUpdateProgress: (callback) => {
    ipcRenderer.on('update-progress', (_event, data) => callback(data));
  },
});
```

**Pattern 3: Renderer to Main (One-way Fire-and-Forget)**
```javascript
// preload.ts
contextBridge.exposeInMainWorld('api', {
  logEvent: (event) => ipcRenderer.send('log-event', event),
});

// main.ts
ipcMain.on('log-event', (_event, data) => {
  logger.info(data);
});
```

### IPC Input Validation

Every `ipcMain.on` and `ipcMain.handle` should validate:
- `event.sender.getURL()` against an origin allowlist
- Arguments with a schema validator (e.g., Zod, Joi)

```javascript
ipcMain.handle('save-file', async (event, filePath, content) => {
  const senderURL = event.sender.getURL();
  if (!isAllowedOrigin(senderURL)) throw new Error('Unauthorized');
  if (typeof filePath !== 'string' || typeof content !== 'string') {
    throw new Error('Invalid arguments');
  }
  // ... safe to proceed
});
```

### Utility Process

For CPU-intensive or crash-prone work, use the `UtilityProcess` API instead of blocking the main process:

```javascript
import { utilityProcess } from 'electron';

const child = utilityProcess.fork(path.join(__dirname, 'heavy-task.js'));
child.postMessage({ type: 'start', data: payload });
child.on('message', (result) => { /* handle result */ });
```

Key differences from Node.js `child_process.fork`:
- Uses Chromium's Services API (not Node.js)
- Can establish `MessagePort` channels directly with renderer processes
- Better integration with Electron's process model

Sources:
- [Electron Process Model](https://www.electronjs.org/docs/latest/tutorial/process-model)
- [Electron IPC Tutorial](https://www.electronjs.org/docs/latest/tutorial/ipc)
- [Electron contextBridge API](https://www.electronjs.org/docs/latest/api/context-bridge)
- [Electron Context Isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation)
- [Electron Using Preload Scripts](https://www.electronjs.org/docs/latest/tutorial/tutorial-preload)
- [Electron UtilityProcess API](https://www.electronjs.org/docs/latest/api/utility-process)
- [Advanced Electron.js Architecture - LogRocket](https://blog.logrocket.com/advanced-electron-js-architecture/)

---

## 3. Security Best Practices

### Fundamental Principle

> Your Electron application's security is the result of the overall security of the framework foundation (Chromium, Node.js), Electron itself, all NPM dependencies, and your code. Common web vulnerabilities like XSS have a **higher security impact** in Electron because they can grant attackers full system access.

### Security Checklist

#### 1. Keep Electron Updated

Always run the latest supported Electron version. Critical CVEs (e.g., CVE-2025-10585, a V8 type-confusion bug) require immediate upgrades. Add CI gates to block builds on outdated versions.

#### 2. Secure webPreferences Defaults

```javascript
const win = new BrowserWindow({
  webPreferences: {
    nodeIntegration: false,       // NEVER enable for remote content
    contextIsolation: true,       // Isolate preload from renderer
    sandbox: true,                // Restrict renderer capabilities
    webSecurity: true,            // Enforce same-origin policy
    allowRunningInsecureContent: false, // Block HTTP on HTTPS pages
    webviewTag: false,            // Disable <webview> unless needed
    navigateOnDragDrop: false,    // Prevent drag-drop navigation
    preload: path.join(__dirname, 'preload.js'),
  },
});
```

#### 3. Content Security Policy (CSP)

Define a restrictive CSP to mitigate XSS:

```html
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.yourapp.com;">
```

**Rules:**
- Start with `default-src 'self'`
- Avoid `'unsafe-eval'` -- review code for `eval()` calls; update third-party libraries that require it
- Use nonces for dynamic scripts when using Webpack/Vite
- Only add additional sources where absolutely necessary

#### 4. Navigation and URL Validation

```javascript
app.on('web-contents-created', (_event, contents) => {
  // Prevent navigation to untrusted URLs
  contents.on('will-navigate', (event, url) => {
    const parsed = new URL(url);
    if (parsed.origin !== 'https://yourapp.com') {
      event.preventDefault();
    }
  });

  // Prevent new window creation
  contents.setWindowOpenHandler(({ url }) => {
    if (isSafeUrl(url)) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });
});
```

#### 5. Disable the `remote` Module

The `remote` module was removed from Electron core in v14 and moved to `@electron/remote`. **Do not use it.** It has both security and performance implications. Use IPC patterns instead.

#### 6. HTTPS-Only Transport

Never load content over plain HTTP. Man-in-the-middle attacks on HTTP connections can inject malicious JavaScript, which is catastrophic when Node.js integration exists anywhere in the process chain.

#### 7. ASAR Integrity (Electron 39+)

Enable ASAR integrity to validate your packaged `app.asar` at runtime against a build-time hash. If tampering is detected, the app terminates:

```json
// package.json (electron-builder)
{
  "build": {
    "asar": true,
    "asarUnpack": ["node_modules/native-addon/**"]
  }
}
```

Electron Forge and Electron Packager set this up automatically when ASAR is enabled.

#### 8. Evaluate Dependencies

- Audit npm dependencies regularly (`npm audit`)
- Choose well-maintained, trusted libraries
- Pin dependency versions
- Use tools like Electronegativity to scan for security anti-patterns

#### 9. Local Data Protection

- Use platform secure storage (Keychain on macOS, DPAPI on Windows, libsecret on Linux) via `safeStorage` or `keytar`
- Enforce owner-only file permissions
- Encrypt sensitive data at rest
- Require auth for any local IPC or HTTP endpoints

#### 10. Hardened Runtime (macOS)

Enable `hardenedRuntime` in your build configuration to restrict application capabilities at the OS level.

### Security Tools

- **Electronegativity**: AST/DOM parser that identifies security misconfigurations and anti-patterns in Electron apps
- **`npm audit`**: Built-in dependency vulnerability scanner
- **Snyk / Socket**: Supply chain security scanners

Sources:
- [Electron Security Tutorial](https://www.electronjs.org/docs/latest/tutorial/security)
- [Electron ASAR Integrity](https://www.electronjs.org/docs/latest/tutorial/asar-integrity)
- [Electron WebPreferences](https://www.electronjs.org/docs/latest/api/structures/web-preferences)
- [Electronegativity Wiki](https://github.com/doyensec/electronegativity/wiki/)
- [Doyensec Electron Security Checklist (PDF)](https://doyensec.com/resources/us-17-Carettoni-Electronegativity-A-Study-Of-Electron-Security-wp.pdf)
- [Cobalt - Hunting Common Misconfigurations in Electron Apps](https://www.cobalt.io/blog/common-misconfigurations-electron-apps-part-1)
- [Breach to Barrier: Strengthening Apps with the Sandbox](https://www.electronjs.org/blog/breach-to-barrier)

---

## 4. Performance Optimization

### Startup Time

The single biggest startup bottleneck is `require()` -- it can consume up to 50% of total startup time.

#### Strategy 1: Lazy Loading / Deferred Imports

```javascript
// BAD: Eager loading everything at startup
const heavy = require('heavy-module');

// GOOD: Load only when needed
let heavy;
function doHeavyWork() {
  if (!heavy) heavy = require('heavy-module');
  return heavy.process();
}
```

#### Strategy 2: Code Splitting

Route-based code splitting loads only the code necessary for the current view:
- Real-world results: startup time reduced from ~10s to ~3s
- Use Vite/Webpack dynamic imports: `const Module = await import('./module')`

#### Strategy 3: V8 Snapshots

V8 snapshots serialize a pre-initialized heap of your dependencies into a binary file:
- The Atom team reduced startup time by **50%** using V8 snapshots
- VSCode has used V8 snapshots since 2017
- Tools: `electron-link` (preprocess modules) + `electron-mksnapshot` (generate snapshot)
- Modules loaded from snapshots skip `require()` entirely

#### Strategy 4: Prerendering

Wait for `DOMContentLoaded` before executing non-UI-critical code. Show the window only when content is ready:

```javascript
const win = new BrowserWindow({ show: false });
win.once('ready-to-show', () => {
  win.show(); // No white flash
});
```

#### Strategy 5: Bundle Optimization

Use bundlers (Vite, esbuild, Webpack) to:
- Tree-shake unused code
- Consolidate dependencies into optimized bundles
- Minimize the number of `require()` calls

### Memory Management

- Electron apps typically start at ~150MB baseline
- Prevent memory leaks by cleaning up IPC listeners and event handlers
- Manage object lifecycles explicitly; avoid detached DOM trees
- Monitor both heap and RSS memory (JavaScript heap vs. native module usage)

### Memory Leak Detection

Use Chrome DevTools (built into Electron) for profiling:

1. **Heap Snapshots**: Take snapshots before and after operations; compare retained objects
2. **Allocation Instrumentation**: Track memory allocations over time to isolate leaks
3. **Performance Tab**: Monitor CPU and memory usage in real-time

```javascript
// Enable DevTools in development
if (isDev) {
  win.webContents.openDevTools();
}
```

### Real-World Performance Lessons

From Slack, Notion, and VSCode:
- **Profile first, optimize second** -- find the most resource-hungry code and target it specifically
- **Avoid loading unused data** -- do not parse/store information that is not needed
- **Stagger initialization** -- align expensive operations with the user's journey, not app startup
- **Use UtilityProcess for heavy computation** -- keep the main process responsive

Sources:
- [Electron Performance Tutorial](https://www.electronjs.org/docs/latest/tutorial/performance)
- [How to Make Your Electron App Launch 1,000ms Faster](https://www.devas.life/how-to-make-your-electron-app-launch-1000ms-faster/)
- [Building High-Performance Electron Apps - Johnny Le](https://www.johnnyle.io/read/electron-performance)
- [6 Ways Slack, Notion, and VSCode Improved Electron App Performance](https://palette.dev/blog/improving-performance-of-electron-apps)
- [Electron App Performance - Brainhub](https://brainhub.eu/library/electron-app-performance)
- [Performance Optimization - Memory, Bundle Size, Profiling](https://www.emadibrahim.com/electron-guide/performance)
- [V8 Snapshot Experiment](https://github.com/RaisinTen/electron-snapshot-experiment)

---

## 5. Project Structure

### Recommended Directory Layout

#### Standard Structure (electron-vite)

```
project-root/
├── electron/                    # Electron-specific code
│   ├── main/
│   │   ├── index.ts            # Main process entry point
│   │   ├── ipc/                # IPC handlers organized by domain
│   │   │   ├── file-handlers.ts
│   │   │   ├── window-handlers.ts
│   │   │   └── app-handlers.ts
│   │   ├── windows/            # Window creation and management
│   │   │   ├── main-window.ts
│   │   │   └── settings-window.ts
│   │   ├── services/           # Business logic (updates, storage, etc.)
│   │   ├── menu/               # Application and context menus
│   │   └── utils/              # Main process utilities
│   └── preload/
│       ├── index.ts            # Preload script entry point
│       └── api.ts              # contextBridge API definitions
├── src/                         # Renderer process (React/Vue/Svelte)
│   ├── components/
│   ├── pages/
│   ├── hooks/                  # or composables/
│   ├── stores/
│   ├── styles/
│   ├── App.tsx
│   └── main.tsx
├── resources/                   # Static assets (icons, images)
│   ├── icon.png
│   ├── icon.icns
│   └── icon.ico
├── electron.vite.config.ts     # electron-vite configuration
├── electron-builder.yml        # Build/distribution configuration
├── tsconfig.json               # Root TypeScript config
├── tsconfig.node.json          # Node/main process TS config
├── tsconfig.web.json           # Renderer process TS config
├── package.json
└── index.html                  # Renderer HTML template
```

#### Alternative: Electron Forge Structure

```
project-root/
├── src/
│   ├── main.ts                 # Main process
│   ├── preload.ts              # Preload script
│   └── renderer/               # Renderer code
│       ├── index.html
│       ├── index.ts
│       └── ...
├── forge.config.ts             # Electron Forge configuration
├── tsconfig.json
└── package.json
```

### TypeScript Configuration

**Root tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  }
}
```

**Main process (tsconfig.node.json):**
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "module": "ESNext",
    "outDir": "./dist/main",
    "lib": ["ESNext"],
    "types": ["node"]
  },
  "include": ["electron/**/*"]
}
```

**Renderer process (tsconfig.web.json):**
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "module": "ESNext",
    "outDir": "./dist/renderer",
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx"
  },
  "include": ["src/**/*"]
}
```

### Key Structural Principles

1. **Separate main and renderer code** -- they run in different environments with different APIs
2. **Organize IPC handlers by domain** -- avoid a single monolithic IPC file
3. **Keep preload scripts minimal** -- only expose what the renderer truly needs
4. **Co-locate window management** -- each window type gets its own module
5. **Share TypeScript types** -- use a shared `types/` directory for IPC message shapes

Sources:
- [Electron Source Code Directory Structure](https://www.electronjs.org/docs/latest/development/source-code-directory-structure)
- [electron-vite Getting Started](https://electron-vite.org/guide/)
- [Electron.JS Files Structure and Best Practices](https://hassanagmir.com/blogs/electronjs-files-structure-and-best-practices)
- [Advanced Electron.js Architecture - LogRocket](https://blog.logrocket.com/advanced-electron-js-architecture/)
- [electron-vite Project Structure](https://electron-vite.org/guide/dev)

---

## 6. Build Tooling

### Comparison: electron-forge vs electron-vite vs electron-builder

| Feature | Electron Forge | electron-vite | electron-builder |
|---------|---------------|--------------|-----------------|
| **Role** | All-in-one scaffolding, building, distributing | Build tooling (Vite-based) | Packaging and distribution |
| **Official** | Yes (Electron team) | Community | Community |
| **Scaffolding** | Yes | Yes | No |
| **Dev Server** | Yes | Yes (with HMR) | No |
| **HMR for Main/Preload** | Limited | Yes (auto-restart) | No |
| **Packaging** | Yes (@electron/packager) | No (pairs with electron-builder) | Yes |
| **Code Signing** | Yes | No (via electron-builder) | Yes |
| **Auto-Update** | Yes | No (via electron-builder) | Yes |
| **Vite Support** | Experimental (v7.5.0+) | Native | N/A |

### Electron Forge

The **official** tool recommended in Electron documentation:

```bash
npm init electron-app@latest my-app -- --template=vite-typescript
```

- Unified interface for create, build, package, publish
- Templates: Vite, Vite + TypeScript, Webpack, Webpack + TypeScript
- Built-in packaging via `@electron/packager`
- Built-in signing via `@electron/osx-sign` and `@electron/notarize`
- Vite support marked experimental as of v7.5.0

### electron-vite

**Next-generation build tooling** focused on developer experience:

```bash
npm create @quick-start/electron my-app
```

- Native Vite integration with HMR for all processes (main, preload, renderer)
- Auto-restarts main/preload on changes (no manual restart needed)
- Unified configuration in `electron.vite.config.ts`
- Supports CommonJS and ESM syntax
- Pairs with electron-builder for packaging/distribution

```typescript
// electron.vite.config.ts
import { defineConfig, externalizeDepsPlugin } from 'electron-vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
  },
  renderer: {
    plugins: [react()],
  },
});
```

### electron-builder

**The de facto standard for packaging and distribution:**

```yaml
# electron-builder.yml
appId: com.company.app
productName: MyApp
directories:
  output: release
mac:
  category: public.app-category.developer-tools
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  target:
    - dmg
    - zip
win:
  target:
    - nsis
    - portable
linux:
  target:
    - AppImage
    - deb
    - snap
asar: true
publish:
  provider: github
```

### Recommended Combination

**For new projects:** `electron-vite` + `electron-builder`
- Best developer experience with full HMR
- Mature packaging and distribution via electron-builder
- Fastest build times with Vite

**For official toolchain preference:** `electron-forge` (Vite + TypeScript template)
- Single unified tool for everything
- Official support and documentation
- Vite support is improving but still experimental

Sources:
- [Electron Forge](https://www.electronforge.io/)
- [electron-vite](https://electron-vite.org/)
- [electron-builder](https://www.electron.build/)
- [Electron Forge vs electron-vite FAQ](https://electron-vite.github.io/faq/electron-forge.html)
- [Electron Application Distribution](https://www.electronjs.org/docs/latest/tutorial/application-distribution)

---

## 7. State Management

### Approaches

#### 1. electron-store (Config Persistence)

`electron-store` is a key-value config persistence library, not a real-time state sync solution:

```javascript
// main.ts
import Store from 'electron-store';

const store = new Store({
  defaults: {
    windowBounds: { width: 800, height: 600 },
    theme: 'system',
  },
  schema: {
    theme: { type: 'string', enum: ['light', 'dark', 'system'] },
  },
});

ipcMain.handle('get-setting', (_event, key) => store.get(key));
ipcMain.handle('set-setting', (_event, key, value) => store.set(key, value));
```

Best for: user preferences, window state, simple configuration.

#### 2. Main Process as Source of Truth

The recommended pattern for real-time state:

```
Renderer -> IPC Action -> Main Process Store -> Broadcast to All Renderers
```

- Main process holds the canonical state
- Renderers pull snapshots on demand via `ipcRenderer.invoke()`
- Main pushes updates to renderers via `webContents.send()`
- Revision gate prevents stale updates

#### 3. Zustand + Zutron (Modern Approach)

Zutron provides streamlined Electron state management built on Zustand:

```javascript
// main.ts -- Zustand store in main process
import { createStore } from 'zustand/vanilla';

const store = createStore((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));

// Renderer gets synced state automatically via IPC bridge
```

#### 4. @statesync/electron (Framework-Agnostic)

A transport layer that syncs any state manager across processes:
- Works with Redux, Zustand, Jotai, MobX, Pinia, Svelte stores
- Supports mixing frameworks across different windows
- Adapter-based architecture

#### 5. Redux + electron-redux

For Redux-based applications:
- Actions from renderer processes dispatch across IPC to main process store
- Main process handles actions and updates application state
- State changes broadcast back to all renderer processes

### Persistence Patterns

| Pattern | Library | Use Case |
|---------|---------|----------|
| Key-value config | `electron-store` | User preferences, settings |
| SQLite database | `better-sqlite3` | Structured relational data |
| File-based | `fs` (via IPC) | Documents, exports |
| Encrypted secrets | `safeStorage` | Tokens, passwords, API keys |
| System keychain | `keytar` | Cross-platform credential storage |

### Best Practice: IPC-Based State Sync

```javascript
// Shared types
interface AppState {
  user: User | null;
  preferences: Preferences;
}

// main.ts
let state: AppState = loadInitialState();

ipcMain.handle('get-state', () => state);
ipcMain.handle('update-state', (_event, patch: Partial<AppState>) => {
  state = { ...state, ...patch };
  // Broadcast to all windows
  BrowserWindow.getAllWindows().forEach((win) => {
    win.webContents.send('state-changed', state);
  });
  // Persist
  persistState(state);
});
```

Sources:
- [Zutron - Streamlined Electron State Management](https://github.com/goosewobbler/zutron)
- [@statesync/electron](https://777genius.github.io/state-sync/api/electron/)
- [Creating a Synchronized Store - BigBinary](https://www.bigbinary.com/blog/sync-store-main-renderer-electron)
- [Syncing State between Electron Contexts - Bruno Scheufler](https://brunoscheufler.com/blog/2023-10-29-syncing-state-between-electron-contexts)
- [electron-redux](https://github.com/klarna/electron-redux)

---

## 8. Auto-Updates

### electron-updater (via electron-builder)

The most widely used auto-update solution:

```javascript
// main.ts
import { autoUpdater } from 'electron-updater';
import log from 'electron-log';

autoUpdater.logger = log;
autoUpdater.autoDownload = false;

app.on('ready', () => {
  autoUpdater.checkForUpdates();
});

autoUpdater.on('update-available', (info) => {
  // Notify renderer, prompt user
  mainWindow.webContents.send('update-available', info);
});

autoUpdater.on('update-downloaded', (info) => {
  // Prompt user to restart
  mainWindow.webContents.send('update-downloaded', info);
});

// Called when user accepts
ipcMain.on('install-update', () => {
  autoUpdater.quitAndInstall();
});
```

### Update Providers

```yaml
# electron-builder.yml
publish:
  - provider: github          # GitHub Releases
  - provider: s3               # Amazon S3
  - provider: generic          # Any static file server
    url: https://updates.yourapp.com
```

### Code Signing Requirements

- **macOS**: Apps **must** be code-signed for auto-updates to work
- **Windows**: Code signing is recommended (prevents SmartScreen warnings)
- **Linux**: No code signing requirement for updates

### Differential Updates

electron-builder supports **blockmap-based differential downloads**:
- Downloads only changed blocks rather than the entire binary
- Still downloads several MBs for small changes

For true **delta updates** (binary diffing, ~KB-sized patches):
- `electron-delta`: Plugin for electron-builder using binary diffing
- `electron-differential-updater`: Mac differential update on zip

### Update Flow Best Practice

```
App Launch
  -> Check for updates (background)
  -> If update available:
     -> Download in background (differential if supported)
     -> Notify user (non-blocking)
     -> User approves restart
     -> quitAndInstall()
```

### Code Signing Setup

**macOS:**
```bash
# Environment variables for CI/CD
APPLE_ID=your@email.com
APPLE_PASSWORD=app-specific-password    # or @keychain:AC_PASSWORD
APPLE_TEAM_ID=XXXXXXXXXX
CSC_LINK=path/to/certificate.p12
CSC_KEY_PASSWORD=certificate-password
```

**Windows:**
```bash
CSC_LINK=path/to/certificate.pfx
CSC_KEY_PASSWORD=certificate-password
# Or for Azure Trusted Signing:
WIN_CSC_LINK=azure://...
```

### Staged Rollouts

Implement staged rollouts by checking a remote configuration before applying updates:

```javascript
autoUpdater.on('update-available', async (info) => {
  const rollout = await fetch('https://api.yourapp.com/rollout');
  const { percentage } = await rollout.json();
  if (Math.random() * 100 < percentage) {
    autoUpdater.downloadUpdate();
  }
});
```

Sources:
- [Electron Updating Applications](https://www.electronjs.org/docs/latest/tutorial/updates)
- [electron-builder Auto Update](https://www.electron.build/auto-update.html)
- [Electron Code Signing](https://www.electronjs.org/docs/latest/tutorial/code-signing)
- [electron-delta](https://electrondelta.com/docs/)
- [Implementing Auto-Updates with electron-updater](https://blog.nishikanta.in/implementing-auto-updates-in-electron-with-electron-updater)
- [Simon Willison - Signing and Notarizing Electron Apps](https://til.simonwillison.net/electron/sign-notarize-electron-macos)

---

## 9. Testing Strategies

### Testing Layers

| Layer | Tool | What to Test |
|-------|------|-------------|
| **Unit (Main Process)** | Vitest / Jest | IPC handlers, business logic, utilities |
| **Unit (Renderer)** | Vitest / Jest + Testing Library | Components, hooks, state logic |
| **Integration** | Vitest | IPC round-trips, service interactions |
| **E2E** | Playwright | Full app workflows, multi-window scenarios |
| **E2E (Alternative)** | WebDriverIO | Cross-platform Electron testing |

### Spectron Deprecation

Spectron was officially deprecated in February 2022. The Electron team recommends **Playwright** and **WebDriverIO** as replacements.

### Playwright for Electron

Playwright has **official experimental Electron support** via Chrome DevTools Protocol (CDP):

```typescript
// e2e/app.spec.ts
import { test, expect, _electron as electron } from '@playwright/test';

test('app launches and shows title', async () => {
  const electronApp = await electron.launch({
    args: ['.'],  // Path to main script
  });

  // Get the first window
  const window = await electronApp.firstWindow();

  // Wait for the window to load
  await window.waitForLoadState('domcontentloaded');

  // Test the title
  const title = await window.title();
  expect(title).toBe('My App');

  // Interact with elements
  await window.click('#settings-button');
  await expect(window.locator('#settings-panel')).toBeVisible();

  // Evaluate in main process
  const appPath = await electronApp.evaluate(async ({ app }) => {
    return app.getAppPath();
  });
  expect(appPath).toBeTruthy();

  await electronApp.close();
});
```

### Helper Library: electron-playwright-helpers

```typescript
import {
  findLatestBuild,
  parseElectronApp,
} from 'electron-playwright-helpers';

test.beforeAll(async () => {
  const latestBuild = findLatestBuild();
  const appInfo = parseElectronApp(latestBuild);
  electronApp = await electron.launch({
    args: [appInfo.main],
    executablePath: appInfo.executable,
  });
});
```

### WebDriverIO (Spectron Successor)

WebDriverIO's `@wdio/electron-service` is the spiritual successor to Spectron:

```javascript
// wdio.conf.ts
export const config = {
  services: ['electron'],
  capabilities: [{
    browserName: 'electron',
    'wdio:electronServiceOptions': {
      appBinaryPath: './dist/MyApp.app/Contents/MacOS/MyApp',
      appArgs: ['--no-sandbox'],
    },
  }],
};
```

### Unit Testing Main Process

```typescript
// main/handlers/__tests__/file-handlers.test.ts
import { describe, it, expect, vi } from 'vitest';
import { handleSaveFile } from '../file-handlers';

describe('file handlers', () => {
  it('saves file to specified path', async () => {
    const mockFs = vi.mock('fs/promises');
    const result = await handleSaveFile(null, '/tmp/test.txt', 'content');
    expect(mockFs.writeFile).toHaveBeenCalledWith('/tmp/test.txt', 'content');
    expect(result).toEqual({ success: true });
  });
});
```

### CI/CD Testing

Run E2E tests in CI with Playwright:

```yaml
# GitHub Actions
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run build
      - run: npx playwright test
```

For Linux CI, use `xvfb-run` for headless display:
```bash
xvfb-run --auto-servernum npm run test:e2e
```

Sources:
- [Electron Automated Testing](https://www.electronjs.org/docs/latest/tutorial/automated-testing)
- [Playwright Electron API](https://playwright.dev/docs/api/class-electron)
- [Spectron Deprecation Notice](https://www.electronjs.org/blog/spectron-deprecation-notice)
- [WebDriverIO Electron Service](https://webdriver.io/docs/wdio-electron-service/)
- [electron-playwright-helpers](https://www.npmjs.com/package/electron-playwright-helpers)
- [Testing Electron Apps with Playwright - Simon Willison](https://til.simonwillison.net/electron/testing-electron-playwright)
- [Running E2E Tests in Electron with Playwright in Docker](https://blog.dangl.me/archive/running-fully-automated-e2e-tests-in-electron-in-a-docker-container-with-playwright/)

---

## 10. Native Integrations

### System Tray

```javascript
import { Tray, Menu, nativeImage } from 'electron';

let tray: Tray;

app.whenReady().then(() => {
  const icon = nativeImage.createFromPath('resources/tray-icon.png');
  tray = new Tray(icon.resize({ width: 16, height: 16 }));

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show App', click: () => mainWindow.show() },
    { label: 'Check for Updates', click: () => autoUpdater.checkForUpdates() },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ]);

  tray.setToolTip('My App');
  tray.setContextMenu(contextMenu);
  tray.on('double-click', () => mainWindow.show());
});
```

### Native Menus

```javascript
import { Menu, MenuItem } from 'electron';

const template: Electron.MenuItemConstructorOptions[] = [
  {
    label: 'File',
    submenu: [
      { label: 'New', accelerator: 'CmdOrCtrl+N', click: handleNew },
      { label: 'Open', accelerator: 'CmdOrCtrl+O', click: handleOpen },
      { type: 'separator' },
      { role: 'quit' },
    ],
  },
  {
    label: 'Edit',
    submenu: [
      { role: 'undo' },
      { role: 'redo' },
      { type: 'separator' },
      { role: 'cut' },
      { role: 'copy' },
      { role: 'paste' },
      { role: 'selectAll' },
    ],
  },
];

// macOS: Insert app menu
if (process.platform === 'darwin') {
  template.unshift({
    label: app.name,
    submenu: [
      { role: 'about' },
      { type: 'separator' },
      { role: 'services' },
      { type: 'separator' },
      { role: 'hide' },
      { role: 'hideOthers' },
      { role: 'unhide' },
      { type: 'separator' },
      { role: 'quit' },
    ],
  });
}

Menu.setApplicationMenu(Menu.buildFromTemplate(template));
```

### Notifications

```javascript
// Main process
import { Notification } from 'electron';

function showNotification(title: string, body: string) {
  const notification = new Notification({ title, body });
  notification.on('click', () => {
    mainWindow.show();
    mainWindow.focus();
  });
  notification.show();
}

// Via IPC from renderer
ipcMain.handle('show-notification', (_event, title, body) => {
  showNotification(title, body);
});
```

### Clipboard

```javascript
// preload.ts
contextBridge.exposeInMainWorld('clipboard', {
  readText: () => ipcRenderer.invoke('clipboard-read'),
  writeText: (text: string) => ipcRenderer.invoke('clipboard-write', text),
});

// main.ts
import { clipboard } from 'electron';

ipcMain.handle('clipboard-read', () => clipboard.readText());
ipcMain.handle('clipboard-write', (_event, text) => clipboard.writeText(text));
```

### File Dialogs

```javascript
import { dialog } from 'electron';

ipcMain.handle('open-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Documents', extensions: ['txt', 'md', 'json'] },
      { name: 'All Files', extensions: ['*'] },
    ],
  });
  if (!result.canceled) {
    return fs.readFileSync(result.filePaths[0], 'utf-8');
  }
  return null;
});

ipcMain.handle('save-file', async (_event, content) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [{ name: 'Text', extensions: ['txt'] }],
  });
  if (!result.canceled && result.filePath) {
    fs.writeFileSync(result.filePath, content);
    return true;
  }
  return false;
});
```

### Native File Drag & Drop

**Dragging files into the app:**
```javascript
// Renderer
document.addEventListener('drop', (e) => {
  e.preventDefault();
  for (const file of e.dataTransfer.files) {
    console.log(file.path); // Electron adds .path attribute
  }
});

document.addEventListener('dragover', (e) => e.preventDefault());
```

**Dragging files out of the app:**
```javascript
// preload.ts
contextBridge.exposeInMainWorld('electron', {
  startDrag: (filePath: string) => ipcRenderer.send('ondragstart', filePath),
});

// main.ts
ipcMain.on('ondragstart', (event, filePath) => {
  event.sender.startDrag({
    file: filePath,
    icon: nativeImage.createFromPath('resources/drag-icon.png'),
  });
});
```

### Shell Integration

```javascript
import { shell } from 'electron';

// Open URL in default browser
shell.openExternal('https://example.com');

// Open file in default application
shell.openPath('/path/to/file.pdf');

// Show file in file manager
shell.showItemInFolder('/path/to/file.txt');

// Move file to trash
shell.trashItem('/path/to/file.txt');
```

### Deep Linking

```javascript
// Register protocol handler
if (process.defaultApp) {
  app.setAsDefaultProtocolClient('myapp', process.execPath, [path.resolve(process.argv[1])]);
} else {
  app.setAsDefaultProtocolClient('myapp');
}

// Handle deep link (macOS)
app.on('open-url', (event, url) => {
  event.preventDefault();
  handleDeepLink(url); // myapp://action/param
});

// Handle deep link (Windows/Linux -- single instance)
const gotLock = app.requestSingleInstanceLock();
app.on('second-instance', (_event, argv) => {
  const url = argv.find((arg) => arg.startsWith('myapp://'));
  if (url) handleDeepLink(url);
});
```

Sources:
- [Electron Native File Drag & Drop](https://www.electronjs.org/docs/latest/tutorial/native-file-drag-drop)
- [Electron Notifications](https://www.electronjs.org/docs/latest/tutorial/notifications)
- [Electron Tray API](https://www.electronjs.org/docs/latest/api/tray)
- [Electron Menu API](https://www.electronjs.org/docs/latest/api/menu)
- [Electron clipboard API](https://www.electronjs.org/docs/latest/api/clipboard)
- [Electron dialog API](https://www.electronjs.org/docs/latest/api/dialog)
- [Electron shell API](https://www.electronjs.org/docs/latest/api/shell)

---

## 11. Build & Distribution

### ASAR Packaging

ASAR (Atom Shell Archive) concatenates files without compression, enabling random file access:

```yaml
# electron-builder.yml
asar: true
asarUnpack:
  - "node_modules/native-addon/**"   # Native modules need unpacking
  - "resources/**"                    # Large resources
```

**ASAR Integrity (Electron 39+):**
- Validates `app.asar` at runtime against a build-time hash
- App terminates on mismatch (detects tampering)
- Enabled automatically by Electron Forge and Electron Packager

### Code Signing

**macOS (required for distribution):**

```yaml
# electron-builder.yml
mac:
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  notarize: true
```

Entitlements file (`build/entitlements.mac.plist`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
  </dict>
</plist>
```

**Windows:**
- Traditional certificate (.pfx): Set `CSC_LINK` and `CSC_KEY_PASSWORD`
- Azure Trusted Signing (recommended for 2025+): Modern cloud-based signing
- EV certificates eliminate SmartScreen warnings

**Linux:**
- No code signing required for most distribution methods
- Snap Store has its own signing process

### macOS Notarization

Notarization is **mandatory** for macOS distribution:
1. App is code-signed with a Developer ID certificate
2. Binary is uploaded to Apple's notarization service
3. Apple scans for malware and returns a ticket
4. Ticket is stapled to the app

```bash
# Environment variables for CI/CD
APPLE_ID=developer@example.com
APPLE_APP_SPECIFIC_PASSWORD=xxxx-xxxx-xxxx-xxxx
APPLE_TEAM_ID=XXXXXXXXXX
```

### CI/CD Pipeline

**GitHub Actions Example:**

```yaml
name: Build & Release

on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: macos-latest
            platform: mac
          - os: windows-latest
            platform: win
          - os: ubuntu-latest
            platform: linux
    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci
      - run: npm run build

      - name: Build Electron app
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CSC_LINK: ${{ secrets.CSC_LINK }}
          CSC_KEY_PASSWORD: ${{ secrets.CSC_KEY_PASSWORD }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        run: npx electron-builder --${{ matrix.platform }} --publish always
```

**Key CI/CD Principles:**
- Run platform-specific builds on matching runners (macOS on macOS, etc.)
- Use `fail-fast: false` so all platforms complete even if one fails
- Store signing credentials as encrypted secrets
- Publish artifacts to GitHub Releases, S3, or custom server

### Output Formats

| Platform | Formats |
|----------|---------|
| **macOS** | DMG, ZIP, PKG |
| **Windows** | NSIS installer, NSIS Web, Portable, AppX (Store), MSI, Squirrel |
| **Linux** | AppImage, Snap, DEB, RPM, Flatpak, Pacman |

Sources:
- [Electron Application Packaging](https://www.electronjs.org/docs/latest/tutorial/application-distribution)
- [Electron Code Signing](https://www.electronjs.org/docs/latest/tutorial/code-signing)
- [Electron ASAR Archives](https://www.electronjs.org/docs/latest/tutorial/asar-archives)
- [electron-builder Documentation](https://www.electron.build/)
- [electron-vite Distribution Guide](https://electron-vite.org/guide/distribution)
- [electron/notarize](https://github.com/electron/notarize)
- [macOS Code Signing Example](https://github.com/omkarcloud/macos-code-signing-example)

---

## 12. Common Anti-Patterns

### Security Anti-Patterns

#### 1. Enabling `nodeIntegration` in Renderers
**Never** enable `nodeIntegration` in any renderer that loads remote content. XSS vulnerabilities combined with Node.js access give attackers full system control.

```javascript
// DANGEROUS -- never do this
new BrowserWindow({
  webPreferences: { nodeIntegration: true, contextIsolation: false },
});
```

#### 2. Exposing Raw `ipcRenderer`
```javascript
// DANGEROUS -- exposes entire IPC event system
contextBridge.exposeInMainWorld('ipc', ipcRenderer);

// SAFE -- expose specific methods only
contextBridge.exposeInMainWorld('api', {
  loadData: () => ipcRenderer.invoke('load-data'),
});
```

#### 3. Disabling `webSecurity`
Setting `webSecurity: false` disables same-origin policy and allows mixed content. Never disable in production.

#### 4. Loading Content Over HTTP
Plain HTTP is vulnerable to MITM attacks. Always use HTTPS for external resources.

#### 5. Using the `remote` Module
Even `@electron/remote` has security and performance implications. Use IPC patterns instead.

#### 6. Not Validating Navigation
Without `will-navigate` handlers, attackers can redirect your app to malicious pages.

#### 7. Unchecked IPC Arguments
IPC handlers that do not validate arguments or check `event.sender` origins are vulnerable to injection.

### Performance Anti-Patterns

#### 8. Eager Loading Everything at Startup
```javascript
// BAD: Loads all modules at startup
const moduleA = require('module-a');
const moduleB = require('module-b');
const moduleC = require('module-c');

// GOOD: Lazy load on demand
async function doWork() {
  const moduleA = await import('module-a');
  return moduleA.process();
}
```

#### 9. Blocking the Main Process
Heavy computation in the main process freezes the entire app. Use `UtilityProcess` or worker threads.

#### 10. Memory Leaks from IPC Listeners
Not cleaning up `ipcRenderer.on()` listeners when components unmount causes memory leaks:

```javascript
// BAD: Never cleaned up
ipcRenderer.on('update', callback);

// GOOD: Clean up on unmount (via preload wrapper)
const removeListener = window.api.onUpdate(callback);
// Call removeListener() when component unmounts
```

#### 11. Loading Unnecessary Data
Parsing and storing data in memory that the app does not actually need wastes resources. Load data on demand.

#### 12. Not Profiling Before Optimizing
The most successful performance strategy is: **profile first, find the bottleneck, then optimize**. Blind optimization wastes effort.

### Architecture Anti-Patterns

#### 13. Monolithic IPC Handler File
A single file with hundreds of `ipcMain.handle()` calls becomes unmaintainable. Organize handlers by domain.

#### 14. Direct File System Access from Renderer
Even with `nodeIntegration`, file system operations should go through IPC to the main process for validation and sandboxing.

#### 15. Storing Secrets in plaintext
API keys, tokens, and credentials stored in plain config files (JSON, `electron-store`) are readable by any process running under the same user. Use `safeStorage` or system keychain.

### Tooling Anti-Patterns

#### 16. Not Using ASAR Packaging
Without ASAR, your entire source code is visible as individual files. Always package with ASAR.

#### 17. Shipping DevTools in Production
Remove or disable DevTools shortcuts in production builds to prevent users from accessing internals.

#### 18. Outdated Electron Versions
Running versions outside the supported window (latest 3 majors) leaves known CVEs unpatched.

Sources:
- [Electron Security Tutorial](https://www.electronjs.org/docs/latest/tutorial/security)
- [Cobalt - Hunting Common Misconfigurations](https://www.cobalt.io/blog/common-misconfigurations-electron-apps-part-1)
- [NCC Group - Avoiding Pitfalls Developing with Electron](https://www.nccgroup.com/research-blog/avoiding-pitfalls-developing-with-electron/)
- [Electronegativity Wiki](https://github.com/doyensec/electronegativity/wiki/)
- [Electron Performance Tutorial](https://www.electronjs.org/docs/latest/tutorial/performance)

---

## 13. Community Conventions

### Popular Boilerplates

| Boilerplate | Stack | Notes |
|------------|-------|-------|
| [electron-vite (create template)](https://electron-vite.org/) | Vite + React/Vue/Svelte/Vanilla + TS | Best DX, fast builds |
| [electron-react-boilerplate](https://github.com/electron-react-boilerplate/electron-react-boilerplate) | React + Webpack + electron-builder | Production-ready, most popular |
| [vite-electron-builder](https://github.com/cawa-93/vite-electron-builder) | Vite + TS + Vue/React/Angular/Svelte | Security-focused |
| [secure-electron-template](https://github.com/nicedoc/electron-template) | React + Redux + i18next | Security best practices built in |
| [electron-vue-vite](https://github.com/electron-vite/electron-vite-vue) | Vue 3 + Vite 5 | Simple, modern |
| [sindresorhus/electron-boilerplate](https://github.com/sindresorhus/electron-boilerplate) | Minimal | Good starting point for custom setups |

### Recommended Libraries

**Core Development:**
| Library | Purpose |
|---------|---------|
| `electron-vite` | Build tooling with Vite HMR |
| `electron-builder` | Packaging, signing, publishing |
| `electron-updater` | Auto-update mechanism |
| `electron-log` | Structured logging |
| `electron-store` | Key-value persistence |

**UI / Frontend:**
| Library | Purpose |
|---------|---------|
| `@radix-ui/*` | Accessible UI primitives |
| `tailwindcss` | Utility-first CSS |
| `lucide-react` / `heroicons` | Icon sets |
| `framer-motion` | Animations |

**State Management:**
| Library | Purpose |
|---------|---------|
| `zustand` + `zutron` | Lightweight state sync |
| `@statesync/electron` | Framework-agnostic state sync |
| `electron-redux` | Redux across processes |

**Security:**
| Library | Purpose |
|---------|---------|
| `electronegativity` | Security misconfiguration scanner |
| `keytar` / `safeStorage` | Credential storage |
| `helmet` | CSP headers (if serving HTTP) |

**Development:**
| Library | Purpose |
|---------|---------|
| `electron-debug` | Debug shortcuts and menus |
| `electron-reloader` | Auto-reload on changes |
| `electron-devtools-installer` | React/Vue DevTools in Electron |
| `electron-dl` | File download with progress |

**Testing:**
| Library | Purpose |
|---------|---------|
| `@playwright/test` | E2E testing |
| `electron-playwright-helpers` | E2E test utilities |
| `@wdio/electron-service` | WebDriverIO E2E testing |
| `vitest` | Unit and integration testing |

### Ecosystem Tools

- **Electron Fiddle**: Interactive playground for prototyping Electron apps
- **Electron Forge**: Official all-in-one CLI
- **Devtron**: DevTools extension for inspecting Electron apps (deprecated but still referenced)
- **electron-release-server**: Self-hosted release management
- **update.electronjs.org**: Free auto-update service for open-source apps

### Community Resources

- [Electron Discord](https://discord.com/invite/electronjs)
- [Electron GitHub Discussions](https://github.com/electron/electron/discussions)
- [awesome-electron](https://github.com/sindresorhus/awesome-electron)
- [Electron Fiddle](https://www.electronjs.org/fiddle)

Sources:
- [Top Tools and Libraries to Use with Electron in 2025](https://www.capitalcompute.com/top-tools-and-libraries-to-use-with-electron-in-2025/)
- [Electron Boilerplates and CLIs](https://www.electronjs.org/docs/latest/tutorial/boilerplates-and-clis)
- [Why Electron Still Wins in 2025 - SwayAlgo](https://swayalgo.com/why-electron-js-still-wins-in-2025/)
- [Electron Development Guide - Brainhub](https://brainhub.eu/guides/electron-development)

---

## Blueprint Planning Checklist

1. **Electron version**: Target Electron 40+ (Chromium 144, Node.js 24). Stay within the 3-version support window.
2. **Build tooling**: `electron-vite` + `electron-builder` for best DX, or `electron-forge` for official toolchain.
3. **Security posture**: Enable `contextIsolation`, `sandbox`, disable `nodeIntegration`. Set restrictive CSP. Validate all IPC inputs.
4. **Architecture**: Main process owns state and native APIs. Renderer is UI-only. Preload exposes minimal typed API via `contextBridge`.
5. **IPC design**: One handler per action, strongly typed, with input validation. Use `invoke`/`handle` for request/response, `send`/`on` for fire-and-forget.
6. **State strategy**: `electron-store` for config persistence. Zustand + Zutron or custom IPC-based sync for real-time state.
7. **Performance budget**: Lazy load modules, use code splitting, consider V8 snapshots for large apps. Show window on `ready-to-show`.
8. **Auto-update plan**: `electron-updater` with differential downloads. Code signing is mandatory for macOS. Consider `electron-delta` for bandwidth-critical apps.
9. **Testing plan**: Vitest for unit/integration, Playwright for E2E. CI matrix across macOS/Windows/Linux.
10. **Distribution matrix**: DMG + ZIP (macOS), NSIS (Windows), AppImage + DEB (Linux). Code sign all platforms. Notarize macOS.
11. **Security tooling**: Run `electronegativity`, `npm audit`, and dependency scanning in CI.
12. **Native features scope**: System tray, notifications, file dialogs, menus, clipboard, deep links -- decide what you need upfront.
