---
description: Optimize Magento 2 code for performance
model: claude-sonnet-4-5
---

Analyze and optimize Magento 2 code for performance.

## Code to Optimize

$ARGUMENTS

## Magento 2 Performance Optimization

### 1. **Database Queries**
- Use collections efficiently with filters
- Add proper indexes to custom tables
- Use `addFieldToSelect()` instead of loading full objects
- Implement lazy loading

### 2. **Caching**
- Implement cache tags properly
- Use built-in cache types
- Add custom cache types if needed
- Invalidate cache appropriately

### 3. **Object Loading**
- Use repositories instead of factories
- Implement object pooling
- Avoid loading in loops
- Use `getCollection()` for multiple items

### 4. **Event Observers**
- Make observers fast and focused
- Avoid heavy processing in observers
- Use plugins instead when appropriate

### 5. **Full Page Cache**
- Make blocks cacheable
- Use cache tags correctly
- Implement hole punching for dynamic content

Provide specific optimization recommendations for Magento 2.
