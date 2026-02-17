---
name: electron-blueprint
description: Structured planning format for Electron desktop apps — bridges requirements to production-ready code. Use when planning complex Electron implementations, creating detailed specifications, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
category: electron
tags: [electron, blueprint, desktop, planning, architecture]
related_skills: [electron-ipc-patterns]
---

# Electron Blueprint

Electron Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Electron desktop applications. It bridges the gap between high-level requirements and production-ready code across main process, renderer process, preload scripts, and native integrations.

## When to Use This Skill

- Planning complex Electron desktop application architectures
- Creating detailed specifications before writing code
- Designing IPC contracts between main and renderer processes
- Mapping out window management, native integrations, and security policies
- Documenting build and distribution strategies across platforms
- Ensuring all details are captured (process boundaries, IPC channels, security settings)
- Avoiding vague plans that lead to insecure or poorly architected desktop apps

## Blueprint Plan Structure

A complete Blueprint includes these sections:

### 1. Overview & Key Decisions

```markdown
# Desktop Note-Taking App

A cross-platform desktop note-taking app with local-first storage and optional cloud sync.

## Key Decisions
- Local-first: all notes stored on the file system as Markdown files
- Electron 40 target (Chromium 144, Node.js 24)
- Build tooling: electron-vite + electron-builder
- Frontend: React 19 + TypeScript + Tailwind CSS
- State: Zustand in renderer, electron-store for persistence
- IPC: invoke/handle for all data operations, send/on for push events only
- Security: contextIsolation + sandbox enabled, restrictive CSP, no nodeIntegration
```

### 2. User Flows

Document step-by-step interactions:

```markdown
## User Flows

### Creating a Note
1. User clicks "New Note" button or presses CmdOrCtrl+N
2. App creates a new untitled Markdown file in the notes directory
3. Editor opens with focus in the title field
4. As user types, content auto-saves every 2 seconds (debounced)
5. File watcher detects save and updates the sidebar note list
6. Status bar shows "Saved" indicator

### Searching Notes
1. User presses CmdOrCtrl+K to open search palette
2. Types search query (searches title + content)
3. Main process performs full-text search across all .md files
4. Results stream to renderer as they are found
5. User selects a result to open that note
```

### 3. Project Setup

Sequential commands for scaffolding:

```markdown
## Commands

npm create @quick-start/electron note-app -- --template react-ts
cd note-app
npm install electron-store electron-updater electron-log
npm install -D @playwright/test electron-playwright-helpers
```

### 4. Process Architecture

Define what runs where:

```markdown
## Process Architecture

### Main Process (electron/main/index.ts)
- Application lifecycle (app.whenReady, app.on('window-all-closed'))
- BrowserWindow creation and management
- IPC handler registration
- File system operations (read, write, search notes)
- System tray setup
- Application menu construction
- Auto-update orchestration
- electron-store for preferences

### Renderer Process (src/)
- React UI rendering
- Markdown editor component (CodeMirror or Monaco)
- Note list sidebar
- Search palette
- Settings panel
- All data access through window.electronAPI only

### Preload Script (electron/preload/index.ts)
- contextBridge.exposeInMainWorld with typed API
- One wrapper method per IPC channel
- Cleanup-returning event subscription helpers
```

### 5. IPC Contracts

Define every IPC channel with types and direction:

```markdown
## IPC Contracts

### Request-Response (invoke/handle)

| Channel | Args | Return | Description |
|---------|------|--------|-------------|
| notes:list | [] | NoteMetadata[] | List all notes with metadata |
| notes:read | [id: string] | NoteContent | Read note content by ID |
| notes:create | [] | NoteContent | Create new empty note |
| notes:save | [id: string, content: string] | void | Save note content |
| notes:delete | [id: string] | void | Move note to trash |
| notes:search | [query: string] | SearchResult[] | Full-text search |
| settings:get | [] | AppSettings | Load app settings |
| settings:set | [settings: Partial<AppSettings>] | void | Update settings |
| dialog:open-folder | [] | string | null | Open folder picker |
| app:get-version | [] | string | Get app version |

### Main-to-Renderer Events (webContents.send)

| Channel | Payload | Description |
|---------|---------|-------------|
| notes:external-change | { id: string } | File changed outside app |
| update:available | UpdateInfo | New version available |
| update:downloaded | UpdateInfo | Update ready to install |
| tray:new-note | void | User clicked "New Note" in tray |

### Renderer-to-Main One-Way (send/on)

| Channel | Payload | Description |
|---------|---------|-------------|
| window:minimize | void | Minimize window |
| window:maximize | void | Toggle maximize |
| window:close | void | Close window |
| log:error | { message: string, stack?: string } | Log renderer error |
```

### 6. Window Management

```markdown
## Window Management

### Main Window
- Default size: 1200x800, min: 800x600
- Remember position and size (electron-store)
- Show on ready-to-show (no white flash)
- macOS: hide on close (keep in dock), quit via CmdOrCtrl+Q or tray
- Windows/Linux: quit on last window close

### Settings Window (optional, or use in-app panel)
- Modal child of main window
- Fixed size: 600x500
- No menu bar

### Window State Persistence
- Save bounds on move/resize (debounced 500ms)
- Restore on next launch
- Validate restored bounds are within current display
```

### 7. Native Integrations

```markdown
## Native Integrations

### System Tray
- Icon: 16x16 template image (macOS), 16x16 PNG (Windows/Linux)
- Context menu: Show App, New Note, separator, Quit
- Double-click: show and focus main window
- Tooltip: "NoteApp"

### Application Menu
- File: New Note (CmdOrCtrl+N), Open Folder, separator, Quit
- Edit: Undo, Redo, separator, Cut, Copy, Paste, Select All
- View: Toggle Sidebar, Zoom In, Zoom Out, Reset Zoom, separator, Toggle DevTools (dev only)
- Help: About, Check for Updates
- macOS: prepend app menu with About, Preferences, Services, Hide, Quit

### Notifications
- Show on: auto-update downloaded ("Update ready — restart to apply")
- Click handler: trigger quitAndInstall

### File Associations
- Register .md file association
- Handle open-file event (macOS) and second-instance argv (Windows/Linux)
```

### 8. State Management

```markdown
## State Management

### Renderer State (Zustand)
- currentNoteId: string | null
- noteList: NoteMetadata[]
- editorContent: string
- searchQuery: string
- searchResults: SearchResult[]
- sidebarOpen: boolean
- theme: 'light' | 'dark' | 'system'

### Persisted State (electron-store in main process)
- windowBounds: { x, y, width, height }
- notesDirectory: string
- theme: 'light' | 'dark' | 'system'
- lastOpenNoteId: string | null
- recentNotes: string[] (last 10 IDs)

### Sync Pattern
- Renderer requests state via invoke on mount
- User actions dispatch invoke calls to main process
- Main process pushes updates via webContents.send for external changes
- Renderer Zustand store updates on IPC event
```

### 9. Security

```markdown
## Security

### BrowserWindow Defaults
- contextIsolation: true
- nodeIntegration: false
- sandbox: true
- webSecurity: true
- webviewTag: false
- navigateOnDragDrop: false

### Content Security Policy
default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'

### IPC Validation
- Every ipcMain.handle validates argument types
- File paths validated against notes directory (no path traversal)
- No raw ipcRenderer exposed via contextBridge

### Navigation Restrictions
- will-navigate: preventDefault for all non-self origins
- setWindowOpenHandler: deny all, open external URLs via shell.openExternal
```

### 10. Build & Distribution

```markdown
## Build & Distribution

### Build Tool: electron-vite + electron-builder

### electron-builder.yml
appId: com.example.noteapp
productName: NoteApp
directories:
  output: release
asar: true
mac:
  category: public.app-category.productivity
  hardenedRuntime: true
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  notarize: true
  target: [dmg, zip]
win:
  target: [nsis]
linux:
  target: [AppImage, deb]
publish:
  provider: github

### Code Signing
- macOS: Developer ID certificate, notarization via Apple
- Windows: CSC_LINK + CSC_KEY_PASSWORD (or Azure Trusted Signing)
- CI: GitHub Actions matrix (macos-latest, windows-latest, ubuntu-latest)

### Auto-Updates
- electron-updater with GitHub Releases provider
- Check on launch (background), notify user, install on restart
- autoDownload: false (user confirms download)
```

### 11. Testing Strategy

```markdown
## Testing

### Unit Tests (Vitest)
- IPC handler logic (mock Electron APIs)
- File service (read, write, search, delete)
- Settings validation
- Note metadata parsing

### Component Tests (Vitest + Testing Library)
- Editor component renders and accepts input
- Note list displays items and handles selection
- Search palette filters results
- Settings panel saves preferences

### E2E Tests (Playwright)
- App launches and shows main window
- Create, edit, and delete a note
- Search finds note by content
- Window state persists across restart
- System tray context menu works
- Auto-update notification displays

### CI Matrix
- macOS, Windows, Linux
- xvfb-run for Linux headless
```

### 12. Verification Checklist

```markdown
## Verification

### Manual Testing
1. [ ] App launches without white flash
2. [ ] Create a new note, type content, verify auto-save
3. [ ] Close and reopen app -- note persists
4. [ ] Search finds note by title and content
5. [ ] System tray icon appears with correct context menu
6. [ ] CmdOrCtrl+N creates new note
7. [ ] Window position/size restored on relaunch
8. [ ] External file change triggers refresh in sidebar
9. [ ] Settings panel saves and applies theme
10. [ ] Auto-update notification appears (test with staging channel)

### Automated
npm run test           # Unit + component tests
npm run test:e2e       # Playwright E2E tests
npx electronegativity -i ./dist  # Security scan
npm audit              # Dependency audit
```

## Vague Plan vs Blueprint: Critical Differences

A vague plan answers "what to build" but leaves "how" to interpretation. A Blueprint provides **implementation-ready specifications** with exact code patterns, IPC contracts, and security configurations.

**VAGUE PLAN (Before Blueprint)**

```markdown
## Note-Taking App
- Markdown editor
- File system storage
- Search functionality
- System tray
- Auto-save
- Auto-updates
```

**Problems with the vague plan:**
- No IPC channel definitions or type contracts
- No security settings specified
- No process boundary decisions (what runs where)
- No window management details
- No build/distribution configuration
- No validation or error handling patterns
- Agent will guess at architecture and likely produce insecure code

**BLUEPRINT (Implementation-Ready)**

**IPC Contract -- notes:save**
**Channel**: `notes:save`
**Direction**: Renderer to Main (invoke/handle)
**Docs**: https://www.electronjs.org/docs/latest/tutorial/ipc

Preload exposure:

```typescript
// electron/preload/index.ts
contextBridge.exposeInMainWorld('electronAPI', {
  saveNote: (id: string, content: string) =>
    ipcRenderer.invoke('notes:save', id, content),
});
```

Main process handler with validation:

```typescript
// electron/main/ipc/note-handlers.ts
import { ipcMain } from 'electron';
import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

const saveNoteSchema = z.object({
  id: z.string().uuid(),
  content: z.string().max(1_000_000),
});

ipcMain.handle('notes:save', async (_event, id: string, content: string) => {
  const parsed = saveNoteSchema.parse({ id, content });

  const notesDir = store.get('notesDirectory');
  const filePath = path.join(notesDir, `${parsed.id}.md`);

  // Prevent path traversal
  if (!filePath.startsWith(notesDir)) {
    throw new Error('Invalid file path');
  }

  await fs.writeFile(filePath, parsed.content, 'utf-8');
});
```

Renderer usage with auto-save:

```typescript
// src/hooks/useAutoSave.ts
import { useEffect, useRef } from 'react';

export function useAutoSave(noteId: string | null, content: string) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (!noteId) return;

    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(async () => {
      await window.electronAPI.saveNote(noteId, content);
    }, 2000);

    return () => clearTimeout(timeoutRef.current);
  }, [noteId, content]);
}
```

**BrowserWindow Configuration:**

```typescript
// electron/main/windows/main-window.ts
import { BrowserWindow, screen } from 'electron';
import path from 'path';
import Store from 'electron-store';

const store = new Store();

export function createMainWindow(): BrowserWindow {
  const savedBounds = store.get('windowBounds', {
    width: 1200,
    height: 800,
  });

  // Validate bounds are within a visible display
  const displays = screen.getAllDisplays();
  const isVisible = displays.some((display) => {
    const { x, y, width, height } = display.workArea;
    return (
      savedBounds.x >= x &&
      savedBounds.y >= y &&
      savedBounds.x < x + width &&
      savedBounds.y < y + height
    );
  });

  const win = new BrowserWindow({
    ...(isVisible ? savedBounds : { width: 1200, height: 800 }),
    minWidth: 800,
    minHeight: 600,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      webviewTag: false,
      navigateOnDragDrop: false,
    },
  });

  win.once('ready-to-show', () => win.show());

  // Persist window bounds on move/resize
  let boundsTimeout: ReturnType<typeof setTimeout>;
  const saveBounds = () => {
    clearTimeout(boundsTimeout);
    boundsTimeout = setTimeout(() => {
      store.set('windowBounds', win.getBounds());
    }, 500);
  };
  win.on('move', saveBounds);
  win.on('resize', saveBounds);

  return win;
}
```

## Build Tool Selection

| Factor | electron-vite + electron-builder | Electron Forge |
|--------|----------------------------------|----------------|
| HMR for main/preload | Yes (auto-restart) | Limited |
| Vite-native | Yes | Experimental (v7.5.0+) |
| Packaging | Via electron-builder | Built-in (@electron/packager) |
| Code signing | Via electron-builder | Built-in |
| Auto-updates | Via electron-updater | Built-in |
| Official support | Community | Electron team |
| Maturity | Stable, widely used | Stable, official |

**Decision rule**: Use `electron-vite + electron-builder` for best developer experience and fastest builds. Use `Electron Forge` if official toolchain support and a single unified tool matters more.

## State Management Decision Tree

| Scenario | Recommended Approach | Library |
|----------|---------------------|---------|
| User preferences (theme, window size) | Key-value persistence in main process | `electron-store` |
| Simple app state, single window | Zustand in renderer, IPC for persistence | `zustand` |
| Multi-window shared state | Main process as source of truth, IPC sync | `zustand` + `zutron` |
| Complex relational data | SQLite in main process, query via IPC | `better-sqlite3` |
| Secrets (API keys, tokens) | Platform secure storage | `safeStorage` / `keytar` |
| Redux-based frontend | Redux with cross-process sync | `electron-redux` |
| Framework-agnostic sync | Transport layer across processes | `@statesync/electron` |

## IPC Pattern Reference

| Pattern | Preload | Main | Use When |
|---------|---------|------|----------|
| Request-Response | `ipcRenderer.invoke(channel, ...args)` | `ipcMain.handle(channel, handler)` | Data fetching, CRUD operations |
| Fire-and-Forget | `ipcRenderer.send(channel, ...args)` | `ipcMain.on(channel, handler)` | Logging, analytics, window controls |
| Main-to-Renderer Push | `ipcRenderer.on(channel, handler)` | `win.webContents.send(channel, data)` | Progress updates, external changes, notifications |
| Bidirectional Stream | MessagePort via `ipcRenderer.postMessage` | MessagePort via `UtilityProcess` | High-frequency data, real-time sync |

**Critical IPC rules:**
- Always use `invoke`/`handle` for request-response (returns a Promise, propagates errors)
- Use `send`/`on` only for fire-and-forget (no return value, no error propagation)
- Never expose raw `ipcRenderer` via contextBridge
- Validate all arguments in the main process handler
- Return cleanup functions from event subscriptions in preload

## Security Checklist

Every Blueprint must verify these items before implementation:

| # | Check | Status |
|---|-------|--------|
| 1 | `contextIsolation: true` in all BrowserWindows | Required |
| 2 | `nodeIntegration: false` in all BrowserWindows | Required |
| 3 | `sandbox: true` in all BrowserWindows | Required |
| 4 | `webSecurity: true` in all BrowserWindows | Required |
| 5 | `webviewTag: false` unless explicitly needed | Required |
| 6 | CSP meta tag in index.html | Required |
| 7 | `will-navigate` handler prevents untrusted navigation | Required |
| 8 | `setWindowOpenHandler` denies all popups | Required |
| 9 | Preload exposes specific methods, not raw ipcRenderer | Required |
| 10 | All IPC handlers validate argument types | Required |
| 11 | File paths validated against allowed directories | Required |
| 12 | Secrets stored via safeStorage or system keychain, not plaintext | Required |
| 13 | HTTPS only for all external requests | Required |
| 14 | `navigateOnDragDrop: false` | Recommended |
| 15 | ASAR packaging enabled | Recommended |
| 16 | Hardened runtime enabled (macOS) | Recommended |
| 17 | DevTools disabled in production | Recommended |
| 18 | Electron version within supported window (latest 3 majors) | Required |

## Performance Optimization Rules

### Startup Performance

| Rule | What to Check | Fix |
|------|--------------|-----|
| Lazy load modules | All `require()` / `import` calls at top of main process | Use dynamic `import()` for non-essential modules |
| Show on ready-to-show | `BrowserWindow({ show: true })` | Set `show: false`, listen for `ready-to-show` event |
| Code split renderer | Single large bundle | Route-based dynamic imports in React/Vue |
| Defer non-critical init | System tray, menus, updates initialized at startup | Initialize after window is shown |
| Bundle dependencies | Many `require()` calls to `node_modules` | Use Vite/esbuild to bundle main process code |

### Runtime Performance

| Rule | What to Check | Fix |
|------|--------------|-----|
| Offload heavy work | CPU-intensive code in main process | Move to `UtilityProcess` or worker thread |
| Debounce IPC calls | High-frequency IPC (typing, scrolling) | Debounce in renderer before sending |
| Clean up listeners | IPC listeners not removed on component unmount | Return and call cleanup functions |
| Avoid memory leaks | Detached DOM trees, uncleaned event handlers | Profile with Chrome DevTools heap snapshots |
| Minimize IPC payload | Large objects sent across IPC boundary | Send only what changed; use IDs instead of full objects |

### Memory Management

| Metric | Acceptable | Concerning | Action |
|--------|-----------|------------|--------|
| Baseline RSS | 100-200 MB | > 300 MB | Profile and reduce bundle size |
| Heap growth over time | Stable | Steadily increasing | Heap snapshot comparison, find leak |
| Per-window overhead | ~50 MB | > 100 MB | Check for duplicate data in each renderer |

## Common Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Pattern |
|-------------|----------------|-----------------|
| `nodeIntegration: true` | XSS gives attacker full system access | Keep `false`, use IPC for all Node.js operations |
| Exposing raw `ipcRenderer` | Renderer can call any IPC channel | Expose specific methods via `contextBridge` |
| `webSecurity: false` | Disables same-origin policy | Keep `true`, configure CSP instead |
| `remote` module | Security and performance issues | Use IPC `invoke`/`handle` pattern |
| Single monolithic IPC file | Unmaintainable at scale | Organize handlers by domain (`ipc/file-handlers.ts`, `ipc/window-handlers.ts`) |
| Eager loading all modules | Startup time bloat (up to 50% of startup is `require()`) | Dynamic `import()` for non-essential modules |
| Blocking main process | UI freezes across all windows | Use `UtilityProcess` for heavy computation |
| `BrowserWindow({ show: true })` | White flash on startup | Set `show: false`, show on `ready-to-show` |
| Plaintext secret storage | Secrets readable by any process under same user | Use `safeStorage` or system keychain |
| Uncleaned IPC listeners | Memory leaks in renderer | Return cleanup function from preload subscription helpers |
| No IPC argument validation | Injection and type confusion attacks | Validate with Zod/Joi in every handler |
| Loading content over HTTP | MITM attack injects malicious JS | HTTPS only for all external resources |
| Shipping DevTools in production | Users can access app internals | Disable DevTools shortcuts in production builds |
| Not using ASAR packaging | Source code visible as individual files | Enable ASAR in electron-builder config |
| Outdated Electron version | Unpatched CVEs in Chromium/Node.js | Stay within latest 3 supported major versions |

## Common Code Patterns

### Typed Preload Script

```typescript
// electron/preload/index.ts
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  // Request-Response
  notes: {
    list: () => ipcRenderer.invoke('notes:list'),
    read: (id: string) => ipcRenderer.invoke('notes:read', id),
    create: () => ipcRenderer.invoke('notes:create'),
    save: (id: string, content: string) =>
      ipcRenderer.invoke('notes:save', id, content),
    delete: (id: string) => ipcRenderer.invoke('notes:delete', id),
    search: (query: string) => ipcRenderer.invoke('notes:search', query),
  },

  settings: {
    get: () => ipcRenderer.invoke('settings:get'),
    set: (settings: Record<string, unknown>) =>
      ipcRenderer.invoke('settings:set', settings),
  },

  // Events (return cleanup function)
  onExternalChange: (cb: (data: { id: string }) => void) => {
    const handler = (_e: Electron.IpcRendererEvent, data: { id: string }) =>
      cb(data);
    ipcRenderer.on('notes:external-change', handler);
    return () => ipcRenderer.removeListener('notes:external-change', handler);
  },

  onUpdateAvailable: (cb: (info: unknown) => void) => {
    const handler = (_e: Electron.IpcRendererEvent, info: unknown) => cb(info);
    ipcRenderer.on('update:available', handler);
    return () => ipcRenderer.removeListener('update:available', handler);
  },

  // Window controls (fire-and-forget)
  window: {
    minimize: () => ipcRenderer.send('window:minimize'),
    maximize: () => ipcRenderer.send('window:maximize'),
    close: () => ipcRenderer.send('window:close'),
  },
});
```

### Window Type Declaration

```typescript
// src/types/electron.d.ts
export interface ElectronAPI {
  notes: {
    list(): Promise<NoteMetadata[]>;
    read(id: string): Promise<NoteContent>;
    create(): Promise<NoteContent>;
    save(id: string, content: string): Promise<void>;
    delete(id: string): Promise<void>;
    search(query: string): Promise<SearchResult[]>;
  };
  settings: {
    get(): Promise<AppSettings>;
    set(settings: Partial<AppSettings>): Promise<void>;
  };
  onExternalChange(cb: (data: { id: string }) => void): () => void;
  onUpdateAvailable(cb: (info: UpdateInfo) => void): () => void;
  window: {
    minimize(): void;
    maximize(): void;
    close(): void;
  };
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
```

### IPC Handler Module Pattern

```typescript
// electron/main/ipc/note-handlers.ts
import { ipcMain } from 'electron';
import { z } from 'zod';
import { NoteService } from '../services/note-service';

export function registerNoteHandlers(noteService: NoteService): void {
  ipcMain.handle('notes:list', async () => {
    return noteService.listNotes();
  });

  ipcMain.handle('notes:read', async (_event, id: string) => {
    z.string().uuid().parse(id);
    return noteService.readNote(id);
  });

  ipcMain.handle('notes:create', async () => {
    return noteService.createNote();
  });

  ipcMain.handle('notes:save', async (_event, id: string, content: string) => {
    z.string().uuid().parse(id);
    z.string().max(1_000_000).parse(content);
    return noteService.saveNote(id, content);
  });

  ipcMain.handle('notes:delete', async (_event, id: string) => {
    z.string().uuid().parse(id);
    return noteService.deleteNote(id);
  });

  ipcMain.handle('notes:search', async (_event, query: string) => {
    z.string().min(1).max(200).parse(query);
    return noteService.searchNotes(query);
  });
}
```

### Main Process Entry Point

```typescript
// electron/main/index.ts
import { app, BrowserWindow } from 'electron';
import { createMainWindow } from './windows/main-window';
import { createTray } from './tray';
import { createApplicationMenu } from './menu';
import { registerNoteHandlers } from './ipc/note-handlers';
import { registerSettingsHandlers } from './ipc/settings-handlers';
import { registerWindowHandlers } from './ipc/window-handlers';
import { NoteService } from './services/note-service';
import { setupAutoUpdater } from './services/updater';
import { setupNavigationSecurity } from './security';

let mainWindow: BrowserWindow | null = null;

app.whenReady().then(async () => {
  // Initialize services
  const noteService = new NoteService();

  // Register IPC handlers before creating windows
  registerNoteHandlers(noteService);
  registerSettingsHandlers();
  registerWindowHandlers();

  // Create main window
  mainWindow = createMainWindow();

  // Defer non-critical initialization
  mainWindow.once('ready-to-show', () => {
    mainWindow!.show();
    createTray(mainWindow!);
    createApplicationMenu();
    setupAutoUpdater(mainWindow!);
  });

  // Security: restrict navigation and popups
  setupNavigationSecurity();
});

// macOS: re-create window when dock icon clicked
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    mainWindow = createMainWindow();
  } else {
    mainWindow?.show();
  }
});

// Windows/Linux: quit when all windows closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

### Navigation Security Setup

```typescript
// electron/main/security.ts
import { app, shell } from 'electron';

const ALLOWED_ORIGINS = new Set(['file://']);

export function setupNavigationSecurity(): void {
  app.on('web-contents-created', (_event, contents) => {
    // Prevent navigation to untrusted URLs
    contents.on('will-navigate', (event, url) => {
      const parsed = new URL(url);
      if (!ALLOWED_ORIGINS.has(parsed.origin)) {
        event.preventDefault();
      }
    });

    // Prevent new window creation -- open external URLs in default browser
    contents.setWindowOpenHandler(({ url }) => {
      if (url.startsWith('https://')) {
        shell.openExternal(url);
      }
      return { action: 'deny' };
    });
  });
}
```

### System Tray Setup

```typescript
// electron/main/tray.ts
import { Tray, Menu, nativeImage, BrowserWindow } from 'electron';
import path from 'path';

let tray: Tray | null = null;

export function createTray(mainWindow: BrowserWindow): void {
  const iconPath = path.join(__dirname, '../../resources/tray-icon.png');
  const icon = nativeImage.createFromPath(iconPath).resize({
    width: 16,
    height: 16,
  });

  tray = new Tray(icon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show App',
      click: () => {
        mainWindow.show();
        mainWindow.focus();
      },
    },
    {
      label: 'New Note',
      click: () => {
        mainWindow.show();
        mainWindow.webContents.send('tray:new-note');
      },
    },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ]);

  tray.setToolTip('NoteApp');
  tray.setContextMenu(contextMenu);
  tray.on('double-click', () => {
    mainWindow.show();
    mainWindow.focus();
  });
}
```

### Auto-Update Service

```typescript
// electron/main/services/updater.ts
import { autoUpdater } from 'electron-updater';
import log from 'electron-log';
import { BrowserWindow, ipcMain } from 'electron';

export function setupAutoUpdater(mainWindow: BrowserWindow): void {
  autoUpdater.logger = log;
  autoUpdater.autoDownload = false;

  autoUpdater.checkForUpdates();

  autoUpdater.on('update-available', (info) => {
    mainWindow.webContents.send('update:available', info);
  });

  autoUpdater.on('update-downloaded', (info) => {
    mainWindow.webContents.send('update:downloaded', info);
  });

  ipcMain.on('update:install', () => {
    autoUpdater.quitAndInstall();
  });
}
```

### React Hook for IPC Events

```typescript
// src/hooks/useIpcEvent.ts
import { useEffect } from 'react';

export function useIpcEvent<T>(
  subscribe: (cb: (data: T) => void) => () => void,
  handler: (data: T) => void,
  deps: React.DependencyList = []
): void {
  useEffect(() => {
    const cleanup = subscribe(handler);
    return cleanup;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}

// Usage:
// useIpcEvent(window.electronAPI.onExternalChange, (data) => {
//   refreshNoteList();
// });
```

### electron-vite Configuration

```typescript
// electron.vite.config.ts
import { defineConfig, externalizeDepsPlugin } from 'electron-vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'electron/main/index.ts'),
        },
      },
    },
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'electron/preload/index.ts'),
        },
      },
    },
  },
  renderer: {
    root: '.',
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'index.html'),
        },
      },
    },
    plugins: [react()],
  },
});
```

### CSP Meta Tag for index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta
      http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'"
    />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>NoteApp</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## File Inventory Template

Every Blueprint should end with a categorized file list:

```markdown
## Files

### Electron Main Process (7)
- electron/main/index.ts                    # App entry point and lifecycle
- electron/main/security.ts                 # Navigation and popup restrictions
- electron/main/tray.ts                     # System tray setup
- electron/main/menu.ts                     # Application menu
- electron/main/ipc/note-handlers.ts        # Note CRUD IPC handlers
- electron/main/ipc/settings-handlers.ts    # Settings IPC handlers
- electron/main/ipc/window-handlers.ts      # Window control IPC handlers

### Electron Services (3)
- electron/main/services/note-service.ts    # File-based note CRUD
- electron/main/services/updater.ts         # Auto-update orchestration
- electron/main/services/search-service.ts  # Full-text search

### Electron Preload (1)
- electron/preload/index.ts                 # contextBridge API

### Renderer - Pages (3)
- src/pages/EditorPage.tsx                  # Main editor view
- src/pages/SettingsPage.tsx                # Settings panel
- src/pages/SearchPage.tsx                  # Search results view

### Renderer - Components (6)
- src/components/Sidebar.tsx                # Note list sidebar
- src/components/Editor.tsx                 # Markdown editor
- src/components/SearchPalette.tsx          # CmdOrCtrl+K search modal
- src/components/TitleBar.tsx               # Custom title bar
- src/components/StatusBar.tsx              # Save indicator, word count
- src/components/UpdateBanner.tsx           # Auto-update notification

### Renderer - Hooks (4)
- src/hooks/useAutoSave.ts                 # Debounced auto-save
- src/hooks/useIpcEvent.ts                 # IPC event subscription helper
- src/hooks/useSettings.ts                 # Settings load/save
- src/hooks/useNotes.ts                    # Note list and CRUD

### Renderer - Store (1)
- src/stores/app-store.ts                  # Zustand store

### Shared Types (1)
- src/types/electron.d.ts                  # Window.electronAPI type declaration

### Configuration (5)
- electron.vite.config.ts                  # Build configuration
- electron-builder.yml                     # Packaging and distribution
- tsconfig.json                            # Root TypeScript config
- tsconfig.node.json                       # Main process TypeScript config
- tsconfig.web.json                        # Renderer TypeScript config

### Static Assets (4)
- resources/icon.png                       # App icon (1024x1024)
- resources/icon.icns                      # macOS icon
- resources/icon.ico                       # Windows icon
- resources/tray-icon.png                  # System tray icon (16x16)

### Build (2)
- build/entitlements.mac.plist             # macOS entitlements
- build/entitlements.mac.inherit.plist     # macOS child process entitlements

### Tests (4)
- tests/unit/note-service.test.ts          # Note service unit tests
- tests/unit/settings-handlers.test.ts     # Settings handler tests
- tests/components/Editor.test.tsx         # Editor component tests
- tests/e2e/app.spec.ts                   # Playwright E2E tests

### CI/CD (1)
- .github/workflows/build.yml             # Build, test, and release pipeline
```

## Testing Patterns

### E2E: App Launch and Window Title

```typescript
// tests/e2e/app.spec.ts
import { test, expect, _electron as electron } from '@playwright/test';

test('app launches and shows main window', async () => {
  const electronApp = await electron.launch({ args: ['.'] });
  const window = await electronApp.firstWindow();
  await window.waitForLoadState('domcontentloaded');

  const title = await window.title();
  expect(title).toBe('NoteApp');

  await electronApp.close();
});
```

### E2E: Create and Edit a Note

```typescript
test('creates a new note and saves content', async () => {
  const electronApp = await electron.launch({ args: ['.'] });
  const window = await electronApp.firstWindow();
  await window.waitForLoadState('domcontentloaded');

  // Create new note
  await window.click('[data-testid="new-note-button"]');

  // Type in editor
  const editor = window.locator('[data-testid="editor"]');
  await editor.fill('# My Test Note\n\nHello world.');

  // Wait for auto-save (2s debounce + buffer)
  await window.waitForTimeout(3000);

  // Verify note appears in sidebar
  const sidebar = window.locator('[data-testid="note-list"]');
  await expect(sidebar.locator('text=My Test Note')).toBeVisible();

  await electronApp.close();
});
```

### E2E: Evaluate Main Process

```typescript
test('returns correct app version', async () => {
  const electronApp = await electron.launch({ args: ['.'] });

  const version = await electronApp.evaluate(async ({ app }) => {
    return app.getVersion();
  });

  expect(version).toMatch(/^\d+\.\d+\.\d+$/);

  await electronApp.close();
});
```

### Unit: IPC Handler Logic

```typescript
// tests/unit/note-service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NoteService } from '../../electron/main/services/note-service';
import fs from 'fs/promises';

vi.mock('fs/promises');

describe('NoteService', () => {
  let service: NoteService;

  beforeEach(() => {
    service = new NoteService('/tmp/test-notes');
    vi.clearAllMocks();
  });

  it('creates a new note with UUID filename', async () => {
    const note = await service.createNote();

    expect(note.id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/
    );
    expect(fs.writeFile).toHaveBeenCalledWith(
      expect.stringContaining(note.id),
      '',
      'utf-8'
    );
  });

  it('rejects path traversal in note ID', async () => {
    await expect(service.readNote('../etc/passwd')).rejects.toThrow(
      'Invalid note ID'
    );
  });

  it('searches notes by content', async () => {
    vi.mocked(fs.readdir).mockResolvedValue(['a.md', 'b.md'] as any);
    vi.mocked(fs.readFile)
      .mockResolvedValueOnce('# Hello world' as any)
      .mockResolvedValueOnce('# Goodbye world' as any);

    const results = await service.searchNotes('hello');

    expect(results).toHaveLength(1);
    expect(results[0].title).toBe('Hello world');
  });
});
```

### Component: Editor

```typescript
// tests/components/Editor.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Editor } from '../../src/components/Editor';

// Mock window.electronAPI
beforeEach(() => {
  window.electronAPI = {
    notes: {
      save: vi.fn().mockResolvedValue(undefined),
      read: vi.fn().mockResolvedValue({ id: '1', content: '# Test' }),
      list: vi.fn(),
      create: vi.fn(),
      delete: vi.fn(),
      search: vi.fn(),
    },
    settings: { get: vi.fn(), set: vi.fn() },
    onExternalChange: vi.fn(() => () => {}),
    onUpdateAvailable: vi.fn(() => () => {}),
    window: { minimize: vi.fn(), maximize: vi.fn(), close: vi.fn() },
  } as any;
});

describe('Editor', () => {
  it('renders note content', async () => {
    render(<Editor noteId="1" />);
    expect(await screen.findByText('# Test')).toBeInTheDocument();
  });

  it('triggers auto-save on content change', async () => {
    vi.useFakeTimers();
    render(<Editor noteId="1" />);

    const editor = await screen.findByRole('textbox');
    fireEvent.change(editor, { target: { value: '# Updated' } });

    // Fast-forward past debounce
    vi.advanceTimersByTime(2500);

    expect(window.electronAPI.notes.save).toHaveBeenCalledWith(
      '1',
      '# Updated'
    );
    vi.useRealTimers();
  });
});
```

### CI/CD Pipeline

```yaml
# .github/workflows/build.yml
name: Build & Release

on:
  push:
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: npm run test

  build:
    needs: test
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

      - name: Install Playwright (E2E)
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npx playwright test
        env:
          CI: true

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

## Best Practices

1. **Define process boundaries first** -- decide what runs in main vs renderer before writing any code
2. **Type every IPC channel** -- define arg types and return types in a shared `types/` file
3. **One handler file per domain** -- `note-handlers.ts`, `settings-handlers.ts`, not one monolithic file
4. **Validate all IPC inputs** -- use Zod or similar schema validation in every `ipcMain.handle`
5. **Return cleanup functions** -- every preload event subscription must return an unsubscribe function
6. **Show on ready-to-show** -- never show a BrowserWindow immediately; wait for content to render
7. **Defer non-critical init** -- tray, menus, and updates can initialize after the window is visible
8. **Persist window state** -- save and restore position/size; validate against current display bounds
9. **Use electron-store for config** -- not for real-time state; only for preferences and settings
10. **Security is non-negotiable** -- contextIsolation, sandbox, CSP, navigation restrictions always enabled
11. **Lazy load in main process** -- dynamic `import()` for modules not needed at startup
12. **Plan the file inventory** -- list every file with its purpose before generating code
13. **Test across platforms** -- CI matrix with macOS, Windows, Linux; use `xvfb-run` for Linux headless
14. **Code sign all platforms** -- macOS requires signing for auto-updates; Windows prevents SmartScreen warnings
15. **Include build config** -- `electron-builder.yml` and `electron.vite.config.ts` are part of the Blueprint
