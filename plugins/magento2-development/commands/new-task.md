---
description: Analyze task complexity and create actionable Magento 2 implementation plan
model: claude-sonnet-4-5
---

Analyze the following Magento 2 task and create a detailed implementation plan.

## Task Description

$ARGUMENTS

## Magento 2 Analysis Framework

### 1. **Task Classification**
- Type: Module Development / Customization / Extension / Integration / Performance / Upgrade
- Complexity: Simple / Medium / Complex
- Scope: Frontend / Backend / Full Stack
- Impact: Database / Configuration / Code / Theme

### 2. **Module Structure Analysis**

**Components Needed**
- [ ] Registration.php
- [ ] module.xml
- [ ] Controllers
- [ ] Models / Resource Models / Collections
- [ ] Blocks
- [ ] Plugins/Interceptors
- [ ] Observers
- [ ] Helpers
- [ ] UI Components
- [ ] Templates (.phtml)
- [ ] Layout XML
- [ ] di.xml (Dependency Injection)
- [ ] ACL (Access Control)
- [ ] Routes (routes.xml)
- [ ] Database schema (db_schema.xml)

### 3. **Implementation Steps**

**Phase 1: Module Setup**
- [ ] Create module directory structure
- [ ] Add registration.php
- [ ] Create module.xml
- [ ] Run setup:upgrade

**Phase 2: Database**
- [ ] Design db_schema.xml
- [ ] Create data/schema patches
- [ ] Define indexes and constraints

**Phase 3: Backend Logic**
- [ ] Implement Models/Resource Models
- [ ] Create Collections
- [ ] Add Repositories (if using service contracts)
- [ ] Implement Plugins/Observers

**Phase 4: Admin UI**
- [ ] Create admin routes
- [ ] Build UI Components (grids/forms)
- [ ] Add ACL resources
- [ ] Create admin controllers

**Phase 5: Frontend** (if applicable)
- [ ] Create frontend controllers
- [ ] Add blocks and templates
- [ ] Implement layout XML
- [ ] Add JavaScript/CSS

**Phase 6: Testing & Quality**
- [ ] Unit tests
- [ ] Integration tests
- [ ] Static tests (coding standards)
- [ ] Functional tests

Provide a clear, Magento 2-specific implementation plan.
