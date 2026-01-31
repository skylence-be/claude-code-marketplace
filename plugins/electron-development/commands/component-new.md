---
description: Create React component for Electron renderer
model: claude-sonnet-4-5
---

Create a React TypeScript component for Electron renderer.

## Component Specification

$ARGUMENTS

## Component Patterns

### 1. **Basic Component with Props**

```typescript
// components/MyComponent.tsx
import { cn } from '@/lib/utils';

interface MyComponentProps {
  title: string;
  description?: string;
  onAction?: () => void;
  className?: string;
}

export function MyComponent({
  title,
  description,
  onAction,
  className,
}: MyComponentProps) {
  return (
    <div className={cn("p-4 rounded-lg border", className)}>
      <h2 className="text-lg font-semibold">{title}</h2>
      {description && (
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      )}
      {onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          Action
        </button>
      )}
    </div>
  );
}
```

### 2. **Component with IPC Integration**

```typescript
// components/ProjectList.tsx
import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';

interface Project {
  id: number;
  name: string;
  customer: string;
}

interface ProjectListProps {
  onSelect: (project: Project) => void;
}

export function ProjectList({ onSelect }: ProjectListProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    window.electronAPI.fetchProjects()
      .then(setProjects)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-destructive bg-destructive/10 rounded-md">
        {error}
      </div>
    );
  }

  return (
    <ul className="divide-y">
      {projects.map((project) => (
        <li key={project.id}>
          <button
            onClick={() => onSelect(project)}
            className="w-full p-3 text-left hover:bg-accent transition-colors"
          >
            <div className="font-medium">{project.name}</div>
            <div className="text-sm text-muted-foreground">{project.customer}</div>
          </button>
        </li>
      ))}
    </ul>
  );
}
```

### 3. **Form Component with Validation**

```typescript
// components/SettingsForm.tsx
import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

interface Settings {
  apiUrl: string;
  apiToken: string;
  syncInterval: number;
}

interface SettingsFormProps {
  initialSettings: Settings;
  onSave: (settings: Settings) => Promise<void>;
}

export function SettingsForm({ initialSettings, onSave }: SettingsFormProps) {
  const [formData, setFormData] = useState(initialSettings);
  const [errors, setErrors] = useState<Partial<Record<keyof Settings, string>>>({});
  const [saving, setSaving] = useState(false);

  const validate = (): boolean => {
    const newErrors: typeof errors = {};

    if (!formData.apiUrl.startsWith('https://')) {
      newErrors.apiUrl = 'URL must start with https://';
    }
    if (!formData.apiToken) {
      newErrors.apiToken = 'API token is required';
    }
    if (formData.syncInterval < 1 || formData.syncInterval > 60) {
      newErrors.syncInterval = 'Interval must be 1-60 minutes';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setSaving(true);
    try {
      await onSave(formData);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="apiUrl">API URL</Label>
        <Input
          id="apiUrl"
          value={formData.apiUrl}
          onChange={(e) => setFormData({ ...formData, apiUrl: e.target.value })}
          placeholder="https://api.example.com"
        />
        {errors.apiUrl && (
          <p className="text-sm text-destructive">{errors.apiUrl}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="apiToken">API Token</Label>
        <Input
          id="apiToken"
          type="password"
          value={formData.apiToken}
          onChange={(e) => setFormData({ ...formData, apiToken: e.target.value })}
        />
        {errors.apiToken && (
          <p className="text-sm text-destructive">{errors.apiToken}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="syncInterval">Sync Interval (minutes)</Label>
        <Input
          id="syncInterval"
          type="number"
          min={1}
          max={60}
          value={formData.syncInterval}
          onChange={(e) => setFormData({ ...formData, syncInterval: Number(e.target.value) })}
        />
        {errors.syncInterval && (
          <p className="text-sm text-destructive">{errors.syncInterval}</p>
        )}
      </div>

      <Button type="submit" disabled={saving}>
        {saving ? 'Saving...' : 'Save Settings'}
      </Button>
    </form>
  );
}
```

### 4. **Component with Event Subscriptions**

```typescript
// components/TimerDisplay.tsx
import { useState, useEffect } from 'react';
import { Play, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function TimerDisplay() {
  const [elapsed, setElapsed] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    const unsubTick = window.electronAPI.onTimerTick(setElapsed);
    const unsubStop = window.electronAPI.onTimerStopped(() => {
      setIsRunning(false);
      setElapsed(0);
    });

    return () => {
      unsubTick();
      unsubStop();
    };
  }, []);

  const formatTime = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleToggle = async () => {
    if (isRunning) {
      await window.electronAPI.stopTimer();
    } else {
      await window.electronAPI.startTimer(1); // default project
      setIsRunning(true);
    }
  };

  return (
    <div className="flex items-center gap-4">
      <span className="text-3xl font-mono tabular-nums">
        {formatTime(elapsed)}
      </span>
      <Button
        variant={isRunning ? 'destructive' : 'default'}
        size="icon"
        onClick={handleToggle}
      >
        {isRunning ? <Square className="h-4 w-4" /> : <Play className="h-4 w-4" />}
      </Button>
    </div>
  );
}
```

Generate type-safe React components for Electron renderer process.
