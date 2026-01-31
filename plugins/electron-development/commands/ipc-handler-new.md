---
description: Create Electron IPC handler with preload bridge
model: claude-sonnet-4-5
---

Create a complete IPC handler with main process handler and preload bridge.

## Handler Specification

$ARGUMENTS

## IPC Handler Patterns

### 1. **Request-Response Handler (invoke/handle)**

```typescript
// types.ts - Add to IPC channel types
export interface IpcInvokeChannels {
  // ... existing channels
  'projects:list': { args: []; return: Project[] };
  'projects:get': { args: [number]; return: Project };
  'projects:create': { args: [CreateProjectInput]; return: Project };
  'projects:update': { args: [number, UpdateProjectInput]; return: Project };
  'projects:delete': { args: [number]; return: void };
}
```

```typescript
// main.ts - IPC handlers
import { ipcMain } from 'electron';
import { ProjectService } from './services/project';

const projectService = new ProjectService();

ipcMain.handle('projects:list', async () => {
  return projectService.list();
});

ipcMain.handle('projects:get', async (_event, id: number) => {
  const project = await projectService.get(id);
  if (!project) {
    throw new Error(`Project ${id} not found`);
  }
  return project;
});

ipcMain.handle('projects:create', async (_event, input: CreateProjectInput) => {
  // Validate input
  if (!input.name?.trim()) {
    throw new Error('Project name is required');
  }
  return projectService.create(input);
});

ipcMain.handle('projects:update', async (_event, id: number, input: UpdateProjectInput) => {
  return projectService.update(id, input);
});

ipcMain.handle('projects:delete', async (_event, id: number) => {
  await projectService.delete(id);
});
```

```typescript
// preload.ts - Context bridge
contextBridge.exposeInMainWorld('electronAPI', {
  // ... existing API
  projects: {
    list: () => ipcRenderer.invoke('projects:list'),
    get: (id: number) => ipcRenderer.invoke('projects:get', id),
    create: (input: CreateProjectInput) => ipcRenderer.invoke('projects:create', input),
    update: (id: number, input: UpdateProjectInput) => ipcRenderer.invoke('projects:update', id, input),
    delete: (id: number) => ipcRenderer.invoke('projects:delete', id),
  },
});
```

### 2. **Event Subscription (send/on)**

```typescript
// types.ts - Event channel types
export interface IpcSendChannels {
  // ... existing channels
  'sync:started': void;
  'sync:progress': { current: number; total: number };
  'sync:completed': { count: number; duration: number };
  'sync:error': { message: string; code: string };
}
```

```typescript
// main.ts - Event emitter
class SyncService {
  private mainWindow: BrowserWindow;

  constructor(mainWindow: BrowserWindow) {
    this.mainWindow = mainWindow;
  }

  async sync(): Promise<void> {
    this.emit('sync:started');

    const items = await this.fetchItems();
    let processed = 0;

    for (const item of items) {
      try {
        await this.processItem(item);
        processed++;
        this.emit('sync:progress', { current: processed, total: items.length });
      } catch (error) {
        this.emit('sync:error', {
          message: error instanceof Error ? error.message : 'Unknown error',
          code: 'SYNC_ITEM_FAILED',
        });
      }
    }

    this.emit('sync:completed', { count: processed, duration: Date.now() - start });
  }

  private emit<K extends keyof IpcSendChannels>(
    channel: K,
    data?: IpcSendChannels[K]
  ): void {
    this.mainWindow.webContents.send(channel, data);
  }
}
```

```typescript
// preload.ts - Event subscriptions
function createEventSubscription<K extends keyof IpcSendChannels>(channel: K) {
  return (callback: (data: IpcSendChannels[K]) => void): (() => void) => {
    const handler = (_event: Electron.IpcRendererEvent, data: IpcSendChannels[K]) => {
      callback(data);
    };
    ipcRenderer.on(channel, handler);
    return () => ipcRenderer.removeListener(channel, handler);
  };
}

contextBridge.exposeInMainWorld('electronAPI', {
  // ... existing API
  sync: {
    start: () => ipcRenderer.invoke('sync:start'),
    onStarted: createEventSubscription('sync:started'),
    onProgress: createEventSubscription('sync:progress'),
    onCompleted: createEventSubscription('sync:completed'),
    onError: createEventSubscription('sync:error'),
  },
});
```

### 3. **Bidirectional Communication Pattern**

```typescript
// For real-time features like notifications, updates, etc.

// types.ts
export interface IpcInvokeChannels {
  'notifications:list': { args: []; return: Notification[] };
  'notifications:markRead': { args: [string]; return: void };
  'notifications:subscribe': { args: []; return: void };
  'notifications:unsubscribe': { args: []; return: void };
}

export interface IpcSendChannels {
  'notification:new': Notification;
  'notification:updated': Notification;
}
```

```typescript
// main.ts - Bidirectional handler
class NotificationManager {
  private subscribers = new Set<BrowserWindow>();
  private pollInterval: NodeJS.Timeout | null = null;

  subscribe(window: BrowserWindow): void {
    this.subscribers.add(window);
    if (!this.pollInterval) {
      this.startPolling();
    }
  }

  unsubscribe(window: BrowserWindow): void {
    this.subscribers.delete(window);
    if (this.subscribers.size === 0 && this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  private startPolling(): void {
    this.pollInterval = setInterval(async () => {
      const newNotifications = await this.fetchNew();
      for (const notification of newNotifications) {
        this.broadcast('notification:new', notification);
      }
    }, 30000);
  }

  private broadcast<K extends keyof IpcSendChannels>(
    channel: K,
    data: IpcSendChannels[K]
  ): void {
    for (const window of this.subscribers) {
      if (!window.isDestroyed()) {
        window.webContents.send(channel, data);
      }
    }
  }
}

const notificationManager = new NotificationManager();

ipcMain.handle('notifications:subscribe', (event) => {
  const window = BrowserWindow.fromWebContents(event.sender);
  if (window) {
    notificationManager.subscribe(window);
  }
});

ipcMain.handle('notifications:unsubscribe', (event) => {
  const window = BrowserWindow.fromWebContents(event.sender);
  if (window) {
    notificationManager.unsubscribe(window);
  }
});
```

### 4. **Service Layer Pattern**

```typescript
// services/api.ts - Base service with error handling
export class ApiService {
  private baseUrl: string;
  private token: string;

  constructor(baseUrl: string, token: string) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  protected async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    try {
      const response = await fetch(url, { ...options, headers });

      if (!response.ok) {
        const error = await response.text();
        throw new ApiError(response.status, error);
      }

      return response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new NetworkError(error instanceof Error ? error.message : 'Network error');
    }
  }
}

// services/project.ts - Specific service
export class ProjectService extends ApiService {
  async list(): Promise<Project[]> {
    return this.request<Project[]>('/projects');
  }

  async get(id: number): Promise<Project> {
    return this.request<Project>(`/projects/${id}`);
  }

  async create(input: CreateProjectInput): Promise<Project> {
    return this.request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }
}
```

Generate complete IPC handlers with type safety and proper error handling.
