---
description: Create WordPress plugin with activation/deactivation hooks
model: claude-sonnet-4-5
---

Create a WordPress plugin.

## Plugin Specification

$ARGUMENTS

## WordPress Plugin Best Practices

### 1. **Plugin Structure** (wp-content/plugins/my-plugin/)

```
my-plugin/
├── my-plugin.php (main file)
├── readme.txt
├── includes/
│   ├── class-plugin.php
│   ├── class-admin.php
│   ├── class-frontend.php
│   └── hooks.php
├── admin/
│   ├── css/
│   ├── js/
│   └── partials/
├── public/
│   ├── css/
│   ├── js/
│   └── partials/
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
```

### 2. **Main Plugin File** (my-plugin.php)

```php
<?php
/**
 * Plugin Name: My Plugin
 * Plugin URI: https://example.com
 * Description: Plugin description
 * Version: 1.0.0
 * Author: Your Name
 * Author URI: https://example.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: my-plugin
 * Domain Path: /languages
 * Requires at least: 5.9
 * Requires PHP: 7.4
 */

namespace MyPlugin;

// Prevent direct access
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

define( 'MY_PLUGIN_VERSION', '1.0.0' );
define( 'MY_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
define( 'MY_PLUGIN_URI', plugin_dir_url( __FILE__ ) );

/**
 * Activation hook
 */
register_activation_hook( __FILE__, function() {
    // Check WordPress version
    if ( version_compare( get_bloginfo( 'version' ), '5.9', '<' ) ) {
        wp_die(
            esc_html__( 'This plugin requires WordPress 5.9 or higher.', 'my-plugin' )
        );
    }

    // Create database tables if needed
    require_once MY_PLUGIN_DIR . 'includes/class-installer.php';
    Installer::install();

    // Flush rewrite rules
    flush_rewrite_rules();

    // Set initial options
    update_option( 'my_plugin_activated', time() );
});

/**
 * Deactivation hook
 */
register_deactivation_hook( __FILE__, function() {
    // Clean up temporary data
    // Flush rewrite rules
    flush_rewrite_rules();

    // Do not delete user data on deactivation
    // Only delete on uninstall
});

/**
 * Uninstall hook (best practice: use uninstall.php file)
 */
register_uninstall_hook( __FILE__, function() {
    // Delete all plugin data
    delete_option( 'my_plugin_activated' );
});

/**
 * Load plugin
 */
function init() {
    // Load text domain
    load_plugin_textdomain(
        'my-plugin',
        false,
        dirname( plugin_basename( __FILE__ ) ) . '/languages'
    );

    // Require plugin files
    require_once MY_PLUGIN_DIR . 'includes/class-plugin.php';

    // Initialize plugin
    Plugin::instance();
}
add_action( 'plugins_loaded', __NAMESPACE__ . '\\init' );
```

### 3. **Main Plugin Class** (includes/class-plugin.php)

```php
<?php
namespace MyPlugin;

class Plugin {
    private static $instance = null;

    public static function instance() {
        if ( is_null( self::$instance ) ) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        $this->load_dependencies();
        $this->define_hooks();
    }

    private function load_dependencies() {
        require_once MY_PLUGIN_DIR . 'includes/class-admin.php';
        require_once MY_PLUGIN_DIR . 'includes/class-frontend.php';
    }

    private function define_hooks() {
        add_action( 'admin_enqueue_scripts', [ $this, 'enqueue_admin_assets' ] );
        add_action( 'wp_enqueue_scripts', [ $this, 'enqueue_frontend_assets' ] );
        add_action( 'wp_ajax_my_plugin_action', [ $this, 'handle_ajax' ] );
    }

    public function enqueue_admin_assets() {
        wp_enqueue_style(
            'my-plugin-admin',
            MY_PLUGIN_URI . 'admin/css/style.css',
            [],
            MY_PLUGIN_VERSION
        );
    }

    public function enqueue_frontend_assets() {
        wp_enqueue_style(
            'my-plugin-style',
            MY_PLUGIN_URI . 'public/css/style.css',
            [],
            MY_PLUGIN_VERSION
        );

        wp_enqueue_script(
            'my-plugin-script',
            MY_PLUGIN_URI . 'public/js/script.js',
            [ 'jquery' ],
            MY_PLUGIN_VERSION,
            true
        );

        wp_localize_script( 'my-plugin-script', 'myPlugin', [
            'ajaxurl' => admin_url( 'admin-ajax.php' ),
            'nonce'   => wp_create_nonce( 'my-plugin-nonce' ),
        ] );
    }

    public function handle_ajax() {
        // Verify nonce
        check_ajax_referer( 'my-plugin-nonce' );

        // Verify user capabilities
        if ( ! current_user_can( 'edit_posts' ) ) {
            wp_send_json_error( [ 'message' => 'Unauthorized' ], 403 );
        }

        // Sanitize input
        $data = sanitize_text_field( $_POST['data'] ?? '' );

        // Process request
        wp_send_json_success( [ 'message' => 'Success' ] );
    }
}
```

### 4. **Uninstall File** (uninstall.php)

```php
<?php
/**
 * Fired when the plugin is uninstalled
 */

if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
    exit;
}

// Delete all plugin options
delete_option( 'my_plugin_activated' );
delete_option( 'my_plugin_settings' );

// Delete posts meta
delete_post_meta_by_key( '_my_plugin_meta' );

// Drop custom tables if any
global $wpdb;
$wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}my_plugin_table" );
```

Generate complete WordPress plugin with proper structure and activation hooks.
