---
description: WordPress code cleanup following best practices
model: claude-sonnet-4-5
---

Clean up WordPress code following best practices and coding standards.

## Code to Clean

$ARGUMENTS

## WordPress Code Cleanup Checklist

### 1. **WordPress Coding Standards**
- Follow WordPress PHP Coding Standards
- Use proper indentation (tabs, not spaces)
- Consistent naming conventions
- Remove unused variables and functions
- Proper spacing and formatting

### 2. **Security Best Practices**
- Add nonce verification to all forms
- Sanitize all input data
- Escape all output data
- Check user capabilities
- Validate data types

### 3. **Performance Optimization**
- Remove unnecessary database queries
- Use wp_cache for frequently accessed data
- Optimize loop queries
- Use transients for expensive operations
- Minimize plugin dependencies

### 4. **Code Organization**
- Use proper namespaces
- Extract complex logic to separate methods
- Follow DRY principle
- Add proper docblocks
- Organize files logically

### 5. **Common Issues to Fix**

**Direct Access Protection:**
```php
// Add to all PHP files
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
```

**Nonce Verification:**
```php
// Always verify nonces
if ( ! isset( $_POST['my_nonce'] ) ||
     ! wp_verify_nonce( $_POST['my_nonce'], 'my_action' ) ) {
    wp_die( 'Invalid request' );
}
```

**Data Sanitization:**
```php
// Sanitize user input
$title = sanitize_text_field( $_POST['title'] );
$email = sanitize_email( $_POST['email'] );
$url = esc_url_raw( $_POST['url'] );
$content = wp_kses_post( $_POST['content'] );
```

**Data Escaping:**
```php
// Escape output
echo esc_html( $title );
echo esc_attr( $value );
echo esc_url( $link );
echo wp_kses_post( $content );
```

**Database Queries:**
```php
// Use $wpdb->prepare for custom queries
global $wpdb;
$results = $wpdb->get_results( $wpdb->prepare(
    "SELECT * FROM {$wpdb->prefix}table WHERE id = %d",
    $id
) );
```

### 6. **Tools to Use**

Run PHP_CodeSniffer with WordPress standards:
```bash
phpcs --standard=WordPress path/to/file.php
phpcbf --standard=WordPress path/to/file.php
```

### 7. **Translation Ready**
- Wrap all strings in translation functions
- Use proper text domain
- Add context when needed

```php
__( 'Text', 'my-plugin' )
_e( 'Text', 'my-plugin' )
esc_html__( 'Text', 'my-plugin' )
esc_html_e( 'Text', 'my-plugin' )
_n( 'Singular', 'Plural', $count, 'my-plugin' )
_x( 'Text', 'Context', 'my-plugin' )
```

Provide specific cleanup recommendations with code examples.
