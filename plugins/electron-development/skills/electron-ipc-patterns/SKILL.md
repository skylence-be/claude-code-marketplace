---
name: electron-ipc-patterns
description: Master Electron IPC communication patterns including secure context bridges, typed channels, bidirectional messaging, and main/renderer process coordination. Use when implementing IPC handlers, creating preload scripts, or designing cross-process communication.
category: electron
tags: [electron, ipc, security, typescript, preload]
---

# Electron IPC Patterns

Secure, type-safe patterns for Electron inter-process communication.

## When to Use This Skill

- Designing IPC channel architecture
- Creating secure preload scripts with contextBridge
- Implementing main process handlers
- Building renderer-to-main communication
- Setting up event subscriptions from main to renderer
- Type-safe IPC with TypeScript

## Security Fundamentals

### Required Security Settings
```typescript
// main.ts - BrowserWindow creation
const mainWindow = new BrowserWindow({
  webPreferences: {
    preload: path.join(__dirname, 'preload.js'),
    contextIsolation: true,      // REQUIRED: Isolates preload from renderer
    nodeIntegration: false,      // REQUIRED: No Node.js in renderer
    sandbox: true,               // RECOMMENDED: Additional sandboxing
    webSecurity: true,           // REQUIRED: Enforce same-origin policy
  },
});
```

### Why These Matter
| Setting | Purpose |
|---------|---------|
| `contextIsolation: true` | Prevents renderer from accessing preload's Node.js context |
| `nodeIntegration: false` | Blocks require() and Node APIs in renderer |
| `sandbox: true` | Limits preload script capabilities |
| `webSecurity: true` | Prevents cross-origin attacks |

## IPC Channel Types

### Type Definitions
```typescript
// types.ts - Central IPC type definitions

// Request-Response pattern (ipcMain.handle / ipcRenderer.invoke)
export interface IpcInvokeChannels {
  'settings:get': { args: []; return: Settings };
  'settings:save': { args: [Settings]; return: void };
  'timer:start': { args: [number]; return: TimeEntry };
  'timer:stop': { args: []; return: TimeEntry };
  'api:fetch-projects': { args: []; return: Project[] };
}

// Main-to-Renderer events (mainWindow.webContents.send)
export interface IpcSendChannels {
  'timer:tick': number;  // elapsed seconds
  'timer:stopped': TimeEntry;
  'update:available': UpdateInfo;
  'error:global': { message: string; code: string };
}

// Renderer-to-Main one-way (ipcRenderer.send)
export interface IpcOnChannels {
  'window:minimize': void;
  'window:close': void;
  'log:error': { message: string; stack?: string };
}
```

## Preload Script Pattern

### Secure Context Bridge
```typescript
// preload.ts
import { contextBridge, ipcRenderer } from 'electron';
import type { IpcInvokeChannels, IpcSendChannels } from './types';

// Type-safe invoke wrapper
function invoke<K extends keyof IpcInvokeChannels>(
  channel: K,
  ...args: IpcInvokeChannels[K]['args']
): Promise<IpcInvokeChannels[K]['return']> {
  return ipcRenderer.invoke(channel, ...args);
}

// Type-safe event subscription
function on<K extends keyof IpcSendChannels>(
  channel: K,
  callback: (data: IpcSendChannels[K]) => void
): () => void {
  const handler = (_event: Electron.IpcRendererEvent, data: IpcSendChannels[K]) => {
    callback(data);
  };
  ipcRenderer.on(channel, handler);
  return () => ipcRenderer.removeListener(channel, handler);
}

// Expose minimal, typed API
contextBridge.exposeInMainWorld('electronAPI', {
  // Settings
  getSettings: () => invoke('settings:get'),
  saveSettings: (settings: Settings) => invoke('settings:save', settings),

  // Timer
  startTimer: (projectId: number) => invoke('timer:start', projectId),
  stopTimer: () => invoke('timer:stop'),

  // Events
  onTimerTick: (cb: (elapsed: number) => void) => on('timer:tick', cb),
  onTimerStopped: (cb: (entry: TimeEntry) => void) => on('timer:stopped', cb),
  onUpdateAvailable: (cb: (info: UpdateInfo) => void) => on('update:available', cb),

  // Window controls
  minimize: () => ipcRenderer.send('window:minimize'),
  close: () => ipcRenderer.send('window:close'),
});
```

### Window Type Declaration
```typescript
// renderer.d.ts - Augment window type
export interface ElectronAPI {
  getSettings(): Promise<Settings>;
  saveSettings(settings: Settings): Promise<void>;
  startTimer(projectId: number): Promise<TimeEntry>;
  stopTimer(): Promise<TimeEntry>;
  onTimerTick(callback: (elapsed: number) => void): () => void;
  onTimerStopped(callback: (entry: TimeEntry) => void): () => void;
  onUpdateAvailable(callback: (info: UpdateInfo) => void): () => void;
  minimize(): void;
  close(): void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
```

## Main Process Handlers

### Handle Pattern (Request-Response)
```typescript
// main.ts
import { ipcMain, BrowserWindow } from 'electron';
import { store } from './services/store';
import { TimerService } from './services/timer';

const timerService = new TimerService();

// Settings handlers
ipcMain.handle('settings:get', async () => {
  return store.get('settings', defaultSettings);
});

ipcMain.handle('settings:save', async (_event, settings: Settings) => {
  // Validate before saving
  if (!isValidSettings(settings)) {
    throw new Error('Invalid settings');
  }
  store.set('settings', settings);
});

// Timer handlers
ipcMain.handle('timer:start', async (_event, projectId: number) => {
  return timerService.start(projectId);
});

ipcMain.handle('timer:stop', async () => {
  return timerService.stop();
});
```

### On Pattern (One-Way from Renderer)
```typescript
// Window control handlers
ipcMain.on('window:minimize', (event) => {
  const window = BrowserWindow.fromWebContents(event.sender);
  window?.minimize();
});

ipcMain.on('window:close', (event) => {
  const window = BrowserWindow.fromWebContents(event.sender);
  window?.close();
});

ipcMain.on('log:error', (_event, { message, stack }) => {
  console.error('Renderer error:', message, stack);
});
```

### Sending to Renderer
```typescript
// Send events from main to renderer
class TimerService {
  private interval: NodeJS.Timeout | null = null;
  private elapsed = 0;

  start(projectId: number): TimeEntry {
    this.elapsed = 0;
    this.interval = setInterval(() => {
      this.elapsed++;
      // Send to all windows
      BrowserWindow.getAllWindows().forEach((win) => {
        win.webContents.send('timer:tick', this.elapsed);
      });
    }, 1000);

    return { projectId, startTime: new Date() };
  }

  stop(): TimeEntry {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    const entry = { elapsed: this.elapsed, endTime: new Date() };

    BrowserWindow.getAllWindows().forEach((win) => {
      win.webContents.send('timer:stopped', entry);
    });

    return entry;
  }
}
```

## React Integration

### Using IPC in Components
```typescript
// components/TimerDisplay.tsx
import { useState, useEffect } from 'react';

export function TimerDisplay() {
  const [elapsed, setElapsed] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    // Subscribe to timer ticks
    const unsubscribe = window.electronAPI.onTimerTick((seconds) => {
      setElapsed(seconds);
      setIsRunning(true);
    });

    // Subscribe to timer stop
    const unsubStop = window.electronAPI.onTimerStopped(() => {
      setIsRunning(false);
    });

    return () => {
      unsubscribe();
      unsubStop();
    };
  }, []);

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="text-2xl font-mono">
      {isRunning ? formatTime(elapsed) : '--:--:--'}
    </div>
  );
}
```

### Custom Hook for IPC
```typescript
// hooks/useSettings.ts
import { useState, useEffect, useCallback } from 'react';

export function useSettings() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    window.electronAPI.getSettings()
      .then(setSettings)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  const save = useCallback(async (newSettings: Settings) => {
    setLoading(true);
    try {
      await window.electronAPI.saveSettings(newSettings);
      setSettings(newSettings);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Save failed'));
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { settings, loading, error, save };
}
```

## Error Handling

### Main Process
```typescript
ipcMain.handle('api:fetch-projects', async () => {
  try {
    const response = await fetch(apiUrl, { headers });
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    // Log on main process
    console.error('Failed to fetch projects:', error);
    // Re-throw with serializable error
    throw new Error(error instanceof Error ? error.message : 'Unknown error');
  }
});
```

### Renderer Process
```typescript
async function loadProjects() {
  try {
    const projects = await window.electronAPI.fetchProjects();
    setProjects(projects);
  } catch (error) {
    // Show user-friendly error
    setError(error instanceof Error ? error.message : 'Failed to load projects');
  }
}
```

## Best Practices

1. **Minimize exposed API** - Only expose what renderer needs
2. **Validate all inputs** - Check data in main process handlers
3. **Use invoke/handle** - Prefer promises over send/on for request-response
4. **Type everything** - Full TypeScript coverage for IPC
5. **Return cleanup functions** - Allow unsubscribing from events
6. **Handle errors** - Catch and serialize errors properly
7. **Never trust renderer** - Treat all IPC data as untrusted input
