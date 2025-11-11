---
description: Create custom post type with meta boxes
model: claude-sonnet-4-5
---

Create a custom WordPress post type.

## Post Type Specification

$ARGUMENTS

## WordPress Custom Post Type Best Practices

### 1. **Register Post Type** (includes/class-post-types.php)

```php
<?php
namespace MyPlugin;

class Post_Types {
    public function __construct() {
        add_action( 'init', [ $this, 'register_post_types' ] );
        add_action( 'init', [ $this, 'register_meta_fields' ] );
    }

    public function register_post_types() {
        register_post_type( 'portfolio', [
            'labels' => [
                'name'          => __( 'Portfolio Items', 'my-plugin' ),
                'singular_name' => __( 'Portfolio Item', 'my-plugin' ),
                'add_new_item'  => __( 'Add New Portfolio Item', 'my-plugin' ),
            ],
            'description'   => __( 'Portfolio showcase', 'my-plugin' ),
            'public'        => true,
            'show_in_rest'  => true,
            'has_archive'   => true,
            'rewrite'       => [ 'slug' => 'portfolio' ],
            'supports'      => [ 'title', 'editor', 'thumbnail', 'custom-fields' ],
            'menu_position' => 5,
            'menu_icon'     => 'dashicons-image-alt2',
            'capability_type' => 'post',
            'capabilities'  => [
                'create_posts' => 'create_portfolio',
                'edit_posts'   => 'edit_portfolio',
                'delete_posts' => 'delete_portfolio',
            ],
        ] );
    }

    public function register_meta_fields() {
        // Register meta fields for REST API
        register_meta( 'post', 'portfolio_url', [
            'type'           => 'string',
            'description'    => 'Portfolio item URL',
            'single'         => true,
            'show_in_rest'   => true,
            'sanitize_callback' => 'sanitize_url',
        ] );

        register_meta( 'post', 'portfolio_client', [
            'type'           => 'string',
            'description'    => 'Client name',
            'single'         => true,
            'show_in_rest'   => true,
            'sanitize_callback' => 'sanitize_text_field',
        ] );
    }
}

new Post_Types();
```

### 2. **Meta Boxes** (includes/class-meta-boxes.php)

```php
<?php
namespace MyPlugin;

class Meta_Boxes {
    public function __construct() {
        add_action( 'add_meta_boxes', [ $this, 'add_meta_boxes' ] );
        add_action( 'save_post_portfolio', [ $this, 'save_meta_boxes' ] );
    }

    public function add_meta_boxes() {
        add_meta_box(
            'portfolio_details',
            __( 'Portfolio Details', 'my-plugin' ),
            [ $this, 'render_portfolio_meta_box' ],
            'portfolio',
            'normal',
            'high'
        );
    }

    public function render_portfolio_meta_box( $post ) {
        wp_nonce_field( 'portfolio_meta_nonce', 'portfolio_nonce' );

        $portfolio_url = get_post_meta( $post->ID, 'portfolio_url', true );
        $portfolio_client = get_post_meta( $post->ID, 'portfolio_client', true );
        ?>

        <div class="portfolio-meta-box">
            <div class="meta-field">
                <label for="portfolio_url">
                    <?php esc_html_e( 'Portfolio URL', 'my-plugin' ); ?>
                </label>
                <input
                    type="url"
                    id="portfolio_url"
                    name="portfolio_url"
                    value="<?php echo esc_attr( $portfolio_url ); ?>"
                    class="widefat"
                    placeholder="https://example.com"
                />
            </div>

            <div class="meta-field">
                <label for="portfolio_client">
                    <?php esc_html_e( 'Client Name', 'my-plugin' ); ?>
                </label>
                <input
                    type="text"
                    id="portfolio_client"
                    name="portfolio_client"
                    value="<?php echo esc_attr( $portfolio_client ); ?>"
                    class="widefat"
                    placeholder="Client name"
                />
            </div>
        </div>

        <style>
            .portfolio-meta-box .meta-field {
                margin-bottom: 15px;
            }
            .portfolio-meta-box label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
        </style>
        <?php
    }

    public function save_meta_boxes( $post_id ) {
        // Verify nonce
        if ( ! isset( $_POST['portfolio_nonce'] ) ||
             ! wp_verify_nonce( $_POST['portfolio_nonce'], 'portfolio_meta_nonce' ) ) {
            return;
        }

        // Check user capability
        if ( ! current_user_can( 'edit_post', $post_id ) ) {
            return;
        }

        // Save portfolio_url
        if ( isset( $_POST['portfolio_url'] ) ) {
            update_post_meta(
                $post_id,
                'portfolio_url',
                sanitize_url( $_POST['portfolio_url'] )
            );
        }

        // Save portfolio_client
        if ( isset( $_POST['portfolio_client'] ) ) {
            update_post_meta(
                $post_id,
                'portfolio_client',
                sanitize_text_field( $_POST['portfolio_client'] )
            );
        }
    }
}

new Meta_Boxes();
```

### 3. **Custom Columns** (includes/class-post-columns.php)

```php
<?php
namespace MyPlugin;

class Post_Columns {
    public function __construct() {
        add_filter( 'manage_portfolio_posts_columns', [ $this, 'set_columns' ] );
        add_action( 'manage_portfolio_posts_custom_column', [ $this, 'render_column' ], 10, 2 );
    }

    public function set_columns( $columns ) {
        $new_columns = [];
        $new_columns['cb'] = $columns['cb'];
        $new_columns['title'] = $columns['title'];
        $new_columns['portfolio_client'] = __( 'Client', 'my-plugin' );
        $new_columns['portfolio_url'] = __( 'URL', 'my-plugin' );
        $new_columns['date'] = $columns['date'];
        return $new_columns;
    }

    public function render_column( $column, $post_id ) {
        switch ( $column ) {
            case 'portfolio_client':
                $client = get_post_meta( $post_id, 'portfolio_client', true );
                echo esc_html( $client ?: '-' );
                break;

            case 'portfolio_url':
                $url = get_post_meta( $post_id, 'portfolio_url', true );
                if ( $url ) {
                    printf(
                        '<a href="%s" target="_blank">%s</a>',
                        esc_url( $url ),
                        esc_html( $url )
                    );
                } else {
                    echo '-';
                }
                break;
        }
    }
}

new Post_Columns();
```

Generate complete WordPress custom post type with meta boxes and columns.
