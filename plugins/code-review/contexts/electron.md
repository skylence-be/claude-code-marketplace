# Electron Review Rules

Technology-specific review rules for Electron desktop applications. Loaded when `electron` is detected in `package.json`.

## Detection
- `package.json` contains `electron` in `dependencies` or `devDependencies`
- `main.js`/`main.ts` with `BrowserWindow` imports
- `preload.js`/`preload.ts` files

## Anti-Patterns to Flag

### nodeIntegration Enabled in Renderer
Enabling Node.js in renderer processes exposes the full Node API to web content.
- **Severity:** Critical (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `webPreferences: { nodeIntegration: true }` in `BrowserWindow` options
- **Fix:** Keep `nodeIntegration: false` (default) and use preload scripts with `contextBridge`

### Missing contextIsolation
Disabling context isolation allows preload scripts to share scope with web content.
- **Severity:** Critical (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `webPreferences: { contextIsolation: false }`
- **Fix:** Keep `contextIsolation: true` (default) and expose APIs via `contextBridge.exposeInMainWorld()`

### Unvalidated shell.openExternal()
Opening URLs with `shell.openExternal()` without validating the URL scheme.
- **Severity:** High (security)
- **Pattern:** `shell.openExternal(url)` where `url` comes from user input or external data
- **Fix:** Validate URL scheme: `if (url.startsWith('https://')) { shell.openExternal(url) }`

### IPC Handlers Without Input Validation
`ipcMain.handle()` or `ipcMain.on()` callbacks that don't validate incoming data.
- **Severity:** High (security)
- **Pattern:** `ipcMain.handle('channel', (event, data) => { /* uses data directly */ })`
- **Fix:** Validate and sanitize all IPC arguments before processing

### Missing webSecurity
Disabling web security removes same-origin policy and other protections.
- **Severity:** Critical (security)
- **Pattern:** `webPreferences: { webSecurity: false }`
- **Fix:** Keep `webSecurity: true` (default). If needed for development, ensure it's not disabled in production builds

### Missing Content Security Policy
Loading remote content without CSP headers.
- **Severity:** High (security)
- **Pattern:** `BrowserWindow` loading remote URLs without CSP meta tag or response headers
- **Fix:** Add CSP via `session.defaultSession.webRequest.onHeadersReceived` or `<meta>` tag

### Synchronous IPC Blocking Main Process
Using `ipcRenderer.sendSync()` blocks the renderer until main process responds.
- **Severity:** Medium (performance)
- **Pattern:** `ipcRenderer.sendSync('channel', data)` in renderer code
- **Fix:** Use async `ipcRenderer.invoke('channel', data)` with `ipcMain.handle()`
