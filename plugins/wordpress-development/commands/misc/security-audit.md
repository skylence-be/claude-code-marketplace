---
description: WordPress security audit and vulnerability assessment
model: claude-sonnet-4-5
---

Perform a comprehensive WordPress security audit.

## Code/Site to Audit

$ARGUMENTS

## WordPress Security Audit Checklist

### 1. **Input Validation & Sanitization**

**Check for:**
- All user inputs are sanitized
- Form submissions use nonce verification
- File uploads are validated
- Database inputs use prepared statements

**Common Vulnerabilities:**
```php
// BAD: Direct $_POST usage
$title = $_POST['title'];

// GOOD: Sanitized input
$title = sanitize_text_field( $_POST['title'] ?? '' );

// BAD: Direct database query
$wpdb->query( "SELECT * FROM table WHERE id = {$_GET['id']}" );

// GOOD: Prepared statement
$wpdb->get_results( $wpdb->prepare(
    "SELECT * FROM {$wpdb->prefix}table WHERE id = %d",
    absint( $_GET['id'] )
) );
```

### 2. **Output Escaping**

**Check for:**
- All echoed content is escaped
- Proper escaping functions used
- No raw user content displayed

**Escaping Functions:**
```php
// For HTML content
echo esc_html( $text );

// For attributes
echo '<input value="' . esc_attr( $value ) . '">';

// For URLs
echo '<a href="' . esc_url( $url ) . '">';

// For JavaScript
echo '<script>var data = ' . wp_json_encode( $data ) . ';</script>';

// For HTML with allowed tags
echo wp_kses_post( $content );
```

### 3. **Authentication & Authorization**

**Check for:**
```php
// Verify user is logged in
if ( ! is_user_logged_in() ) {
    wp_die( 'Access denied' );
}

// Check specific capability
if ( ! current_user_can( 'edit_posts' ) ) {
    wp_die( 'Insufficient permissions' );
}

// Check if user can edit specific post
if ( ! current_user_can( 'edit_post', $post_id ) ) {
    wp_die( 'Access denied' );
}
```

### 4. **Nonce Verification**

**Check for:**
- All forms include nonce fields
- All AJAX requests verify nonces
- Nonces are checked on form submission

```php
// Generate nonce
wp_nonce_field( 'my_action', 'my_nonce' );

// Verify nonce
if ( ! isset( $_POST['my_nonce'] ) ||
     ! wp_verify_nonce( $_POST['my_nonce'], 'my_action' ) ) {
    wp_die( 'Invalid nonce' );
}

// AJAX nonce
wp_localize_script( 'my-script', 'myData', [
    'nonce' => wp_create_nonce( 'my-ajax-nonce' ),
] );

// Verify AJAX nonce
check_ajax_referer( 'my-ajax-nonce' );
```

### 5. **SQL Injection Prevention**

**Check for:**
```php
// BAD: String concatenation
$wpdb->query( "DELETE FROM table WHERE id = " . $_GET['id'] );

// GOOD: Prepared statements
$wpdb->query( $wpdb->prepare(
    "DELETE FROM {$wpdb->prefix}table WHERE id = %d",
    absint( $_GET['id'] )
) );

// Use proper format specifiers
%s - string
%d - integer
%f - float
```

### 6. **XSS Prevention**

**Check for:**
- No raw output of user data
- Proper escaping in templates
- Content Security Policy headers

```php
// BAD: Direct output
echo $_POST['message'];

// GOOD: Escaped output
echo esc_html( $_POST['message'] ?? '' );

// BAD: Unescaped attribute
<div data-info="<?php echo $user_input; ?>">

// GOOD: Escaped attribute
<div data-info="<?php echo esc_attr( $user_input ); ?>">
```

### 7. **CSRF Prevention**

**Check for:**
- All state-changing operations use nonces
- GET requests don't modify data
- Referer checking where appropriate

```php
// Check referer
check_admin_referer( 'my-action', 'my-nonce' );

// AJAX referer check
check_ajax_referer( 'my-action' );
```

### 8. **File Upload Security**

**Check for:**
```php
// Validate file type
$allowed_types = [ 'image/jpeg', 'image/png' ];
if ( ! in_array( $_FILES['file']['type'], $allowed_types ) ) {
    wp_die( 'Invalid file type' );
}

// Validate file size
$max_size = 2 * 1024 * 1024; // 2MB
if ( $_FILES['file']['size'] > $max_size ) {
    wp_die( 'File too large' );
}

// Use WordPress upload handler
require_once ABSPATH . 'wp-admin/includes/file.php';
$file = wp_handle_upload( $_FILES['file'], [ 'test_form' => false ] );
```

### 9. **Direct File Access**

**Check for:**
```php
// Add to all PHP files
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// Or use wp_die()
if ( ! defined( 'WPINC' ) ) {
    wp_die( 'Direct access not allowed' );
}
```

### 10. **Database Prefix**

**Check for:**
- Use `$wpdb->prefix` instead of hardcoded `wp_`
- Never assume default table names

```php
// BAD
$wpdb->query( "SELECT * FROM wp_users" );

// GOOD
$wpdb->get_results( "SELECT * FROM {$wpdb->users}" );
```

### 11. **Password & Secret Storage**

**Check for:**
- No plain text passwords
- Use wp_hash_password() for passwords
- Secrets stored in wp-config.php
- No hardcoded API keys

```php
// Hash password
$hashed = wp_hash_password( $password );

// Verify password
wp_check_password( $password, $hash );

// Store secrets in wp-config.php
define( 'MY_API_KEY', 'secret-key-here' );
```

### 12. **API Endpoint Security**

**Check for REST API endpoints:**
```php
register_rest_route( 'my-plugin/v1', '/endpoint', [
    'methods'             => 'POST',
    'callback'            => 'my_callback',
    'permission_callback' => function() {
        return current_user_can( 'edit_posts' );
    },
    'args'                => [
        'data' => [
            'required'          => true,
            'sanitize_callback' => 'sanitize_text_field',
            'validate_callback' => 'is_string',
        ],
    ],
] );
```

### 13. **Common Vulnerabilities to Check**

- [ ] SQL Injection
- [ ] XSS (Cross-Site Scripting)
- [ ] CSRF (Cross-Site Request Forgery)
- [ ] Remote Code Execution
- [ ] Local File Inclusion
- [ ] Unauthorized Access
- [ ] Information Disclosure
- [ ] Insecure Direct Object References

### 14. **Security Tools**

Run security scans:
```bash
# WP-CLI security scan
wp plugin verify-checksums --all

# Theme check
wp theme verify-checksums --all

# Check for vulnerabilities
wp vuln status
```

Provide detailed security assessment with specific vulnerabilities and fixes.
