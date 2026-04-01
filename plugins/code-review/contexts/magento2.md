# Magento 2 Review Rules

Technology-specific review rules for Magento 2 / Adobe Commerce. Loaded when `magento/framework` is detected in `composer.json`.

## Detection
- `composer.json` contains `magento/framework` in `require`
- `app/code/` or `app/design/` directory structure
- Files using `Magento\` namespace

## Anti-Patterns to Flag

### Direct ObjectManager Usage
Using `ObjectManager::getInstance()` instead of dependency injection.
- **Severity:** High (maintainability)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `\Magento\Framework\App\ObjectManager::getInstance()->get(...)` or `->create(...)`
- **Fix:** Inject the dependency via constructor DI and `di.xml`
- **Exception:** In `InstallSchema`/`UpgradeSchema` scripts where DI isn't available

### Missing ACL Checks in Admin Controllers
Admin controllers that don't implement `_isAllowed()` or use the `ACL` resource.
- **Severity:** High (security)
- **Pattern:** Controller extending `\Magento\Backend\App\Action` without `const ADMIN_RESOURCE` or `_isAllowed()` method
- **Fix:** Define `const ADMIN_RESOURCE = 'Vendor_Module::resource'` and ensure ACL resource exists in `acl.xml`

### Plugin on Final or Private Methods
Interceptor plugins targeting `final` or `private` methods silently fail.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** Plugin class with `before/around/after` methods targeting a method that is `final` or `private` on the target class
- **Fix:** Use a preference (class rewrite) or observer instead

### Missing di.xml Configuration
New classes with constructor dependencies but no `di.xml` configuration for interface bindings.
- **Severity:** Medium
- **Pattern:** Constructor accepts an interface type but no `<preference>` or `<type>` in `di.xml` maps the interface
- **Fix:** Add `<preference for="Interface" type="Implementation" />` in `di.xml`

### Not Using Service Contracts
Direct use of resource models or collections instead of repository interfaces.
- **Severity:** Medium (maintainability)
- **Pattern:** `$collection = $this->collectionFactory->create()` in controllers or API classes
- **Fix:** Use repository interface: `$this->productRepository->getList($searchCriteria)`

### Direct Database Queries
Using `$connection->query()` or raw SQL instead of repository/collection patterns.
- **Severity:** High (security + maintainability)
- **Pattern:** `$connection->query("SELECT ...")` or `$connection->rawQuery(...)`
- **Fix:** Use repository APIs, collections, or at minimum `$connection->select()` with bound parameters

### Missing Cache Type Declaration
Custom cache without proper cache type registration.
- **Severity:** Medium
- **Pattern:** Using `\Magento\Framework\App\Cache\Type\FrontendPool` without a registered cache type in `cache.xml`
- **Fix:** Create `etc/cache.xml` with cache type definition

### Non-Standard Module Naming
Module names not following `Vendor_Module` convention.
- **Severity:** Low
- **Pattern:** Module registration without proper vendor prefix, or lowercase module names
- **Check:** `registration.php` and `module.xml` for proper naming
