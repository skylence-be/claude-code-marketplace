---
description: Create custom WordPress theme with template files
model: claude-sonnet-4-5
---

Create a custom WordPress theme.

## Theme Specification

$ARGUMENTS

## WordPress Theme Best Practices

### 1. **Theme Structure** (wp-content/themes/my-theme/)

```
my-theme/
├── style.css
├── functions.php
├── index.php
├── header.php
├── footer.php
├── sidebar.php
├── single.php
├── archive.php
├── search.php
├── 404.php
├── page.php
├── front-page.php
├── template-parts/
│   ├── header/
│   ├── footer/
│   ├── content/
│   └── navigation/
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── inc/
    ├── class-loader.php
    ├── hooks.php
    └── helpers.php
```

### 2. **functions.php**

```php
<?php
/**
 * My Theme functions and definitions
 */

namespace MyTheme;

define( 'MY_THEME_VERSION', '1.0.0' );
define( 'MY_THEME_DIR', get_template_directory() );
define( 'MY_THEME_URI', get_template_directory_uri() );

/**
 * Setup theme support and features
 */
function setup_theme() {
    add_theme_support( 'title-tag' );
    add_theme_support( 'post-thumbnails' );
    add_theme_support( 'custom-logo' );
    add_theme_support( 'html5', [
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ] );

    register_nav_menus( [
        'primary' => __( 'Primary Menu', 'my-theme' ),
        'footer'  => __( 'Footer Menu', 'my-theme' ),
    ] );
}
add_action( 'after_setup_theme', __NAMESPACE__ . '\\setup_theme' );

/**
 * Enqueue scripts and styles
 */
function enqueue_assets() {
    wp_enqueue_style(
        'my-theme-style',
        MY_THEME_URI . '/assets/css/style.css',
        [],
        MY_THEME_VERSION
    );

    wp_enqueue_script(
        'my-theme-script',
        MY_THEME_URI . '/assets/js/main.js',
        [],
        MY_THEME_VERSION,
        true
    );

    wp_localize_script( 'my-theme-script', 'myTheme', [
        'ajaxurl' => admin_url( 'admin-ajax.php' ),
        'nonce'   => wp_create_nonce( 'my-theme-nonce' ),
    ] );
}
add_action( 'wp_enqueue_scripts', __NAMESPACE__ . '\\enqueue_assets' );

/**
 * Register widget areas
 */
function register_sidebars() {
    register_sidebar( [
        'name'          => __( 'Primary Sidebar', 'my-theme' ),
        'id'            => 'primary-sidebar',
        'description'   => __( 'Main sidebar', 'my-theme' ),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ] );
}
add_action( 'widgets_init', __NAMESPACE__ . '\\register_sidebars' );
```

### 3. **style.css**

```css
/*
Theme Name: My Theme
Theme URI: https://example.com
Author: Your Name
Author URI: https://example.com
Description: A custom WordPress theme
Version: 1.0.0
License: GPL v2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html
Text Domain: my-theme
Domain Path: /languages
*/

:root {
    --color-primary: #2563eb;
    --color-text: #1f2937;
    --color-bg: #ffffff;
    --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html {
    font-size: 16px;
}

body {
    font-family: var(--font-sans);
    color: var(--color-text);
    background-color: var(--color-bg);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

a {
    color: var(--color-primary);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}
```

### 4. **header.php**

```php
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
    <?php wp_body_open(); ?>

    <header class="site-header">
        <div class="container">
            <div class="site-branding">
                <?php the_custom_logo(); ?>
                <h1 class="site-title">
                    <a href="<?php echo esc_url( home_url() ); ?>">
                        <?php bloginfo( 'name' ); ?>
                    </a>
                </h1>
            </div>
            <nav class="site-navigation">
                <?php
                wp_nav_menu( [
                    'theme_location' => 'primary',
                    'fallback_cb'    => 'wp_page_menu',
                ] );
                ?>
            </nav>
        </div>
    </header>

    <main id="content">
```

### 5. **footer.php**

```php
    </main>

    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <?php
                wp_nav_menu( [
                    'theme_location' => 'footer',
                    'fallback_cb'    => false,
                ] );
                ?>
            </div>
            <div class="site-info">
                <p>&copy; <?php echo esc_html( get_bloginfo( 'name' ) ); ?> - <?php echo esc_html( date( 'Y' ) ); ?></p>
            </div>
        </div>
    </footer>

    <?php wp_footer(); ?>
</body>
</html>
```

Generate complete WordPress theme with proper structure and WordPress Coding Standards.
