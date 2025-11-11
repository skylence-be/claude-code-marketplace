---
description: Clean up Magento 2 code following best practices
model: claude-sonnet-4-5
---

Clean up Magento 2 code following coding standards and best practices.

## Code to Clean

$ARGUMENTS

## Magento 2 Code Quality Standards

### 1. **Coding Standards**
- Follow Magento Coding Standard (based on PSR-2)
- Use proper namespacing
- Follow naming conventions
- Add proper DocBlocks

### 2. **Dependency Injection**
- Use constructor injection
- Avoid ObjectManager direct usage
- Use factories and repositories
- Implement interfaces properly

### 3. **Service Contracts**
- Use API interfaces
- Implement proper data interfaces
- Use repositories for data access

### 4. **Best Practices**
- Remove unused code
- Extract complex logic to helper methods
- Use proper exception handling
- Add logging where appropriate

Run `vendor/bin/phpcs` and `vendor/bin/phpmd` to verify standards.

Provide specific cleanup recommendations for Magento 2.
