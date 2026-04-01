# WordPress Review Rules

Technology-specific review rules for WordPress 6.0+ themes and plugins. Loaded when WordPress-specific files or functions are detected.

## Detection
- `wp-config.php` exists or `style.css` with WordPress theme headers
- `functions.php` with WordPress hooks (`add_action`, `add_filter`)
- Files using `wp_` prefixed functions
- Plugin header comment in main PHP file

## Anti-Patterns to Flag

### Missing Nonce Verification
Form handlers or AJAX endpoints that don't verify nonces (CSRF protection).
- **Severity:** Critical (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `$_POST` or `$_GET` access in hook callbacks without `wp_verify_nonce()` or `check_admin_referer()`
- **Fix:** Add `wp_verify_nonce($_POST['_wpnonce'], 'action_name')` before processing

### Unescaped Output
Echoing variables without proper escaping functions.
- **Severity:** Critical (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `echo $variable`, `echo $data['field']`, `<?= $value ?>` without `esc_html()`, `esc_attr()`, `esc_url()`
- **Fix:** Use appropriate escaping: `echo esc_html($variable)`, `echo esc_attr($value)`, `echo esc_url($url)`

### Direct Database Query Without prepare()
Using `$wpdb->query()` with interpolated variables instead of `$wpdb->prepare()`.
- **Severity:** Critical (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `$wpdb->query("SELECT * FROM ... WHERE id = $id")` or `$wpdb->get_results("... $variable ...")`
- **Fix:** `$wpdb->get_results($wpdb->prepare("SELECT * FROM ... WHERE id = %d", $id))`

### Missing Capability Checks
Actions that modify data without checking user capabilities.
- **Severity:** High (security)
- **Pattern:** Admin actions, AJAX handlers, or REST endpoints without `current_user_can('capability')`
- **Fix:** Add `if (!current_user_can('edit_posts')) { wp_die('Unauthorized'); }` before processing

### Using extract() on User Input
`extract()` on `$_POST`, `$_GET`, or unvalidated data creates variables in local scope.
- **Severity:** High (security)
- **Pattern:** `extract($_POST)`, `extract($_GET)`, `extract($atts)` without prior validation
- **Fix:** Access values explicitly: `$value = $_POST['key']` with sanitization

### Missing Input Sanitization
Processing `$_POST`/`$_GET`/`$_REQUEST` data without `sanitize_*` functions.
- **Severity:** High (security)
- **Pattern:** Direct use of `$_POST['field']` without `sanitize_text_field()`, `sanitize_email()`, `absint()`, etc.
- **Fix:** `$value = sanitize_text_field(wp_unslash($_POST['field']))`

### Enqueuing Assets Outside Proper Hooks
Loading scripts/styles outside `wp_enqueue_scripts`, `admin_enqueue_scripts`, or `login_enqueue_scripts`.
- **Severity:** Medium
- **Pattern:** `wp_enqueue_script()` or `wp_enqueue_style()` called directly in templates or outside hook callbacks
- **Fix:** Wrap in `add_action('wp_enqueue_scripts', function() { ... })`

### Direct File System Access
Using PHP file functions instead of `WP_Filesystem` API.
- **Severity:** Medium
- **Pattern:** `file_get_contents()`, `file_put_contents()`, `fopen()`, `fwrite()` in plugin/theme code
- **Fix:** Use `WP_Filesystem` API: `$wp_filesystem->get_contents($file)`
