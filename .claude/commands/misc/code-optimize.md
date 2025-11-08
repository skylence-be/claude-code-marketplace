---
description: Optimize Laravel/Livewire code for performance
model: claude-sonnet-4-5
---

Analyze and optimize Laravel/Livewire code for performance.

## Code to Optimize

$ARGUMENTS

## Laravel/Livewire Performance Optimization

### 1. **Database Queries**
- Use eager loading to avoid N+1 queries
- Add database indexes
- Use `select()` to load only needed columns
- Implement query caching

### 2. **Livewire Optimization**
- Use `#[Computed]` for expensive operations
- Implement lazy loading for heavy components
- Use `wire:key` for list items
- Debounce input events

### 3. **Caching**
- Cache expensive queries
- Use Redis for session/cache
- Implement route caching
- Use view caching

### 4. **Queue Jobs**
- Move slow operations to queue jobs
- Use queue batching
- Implement job chaining

### 5. **Response Optimization**
- Use HTTP caching headers
- Implement response caching
- Compress responses

Provide specific optimization recommendations.
