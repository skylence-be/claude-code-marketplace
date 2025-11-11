---
description: Create custom WordPress REST API endpoint
model: claude-sonnet-4-5
---

Create a custom WordPress REST API endpoint.

## REST Endpoint Specification

$ARGUMENTS

## WordPress REST API Best Practices

### 1. **Register Custom Endpoints** (includes/class-rest-api.php)

```php
<?php
namespace MyPlugin;

class REST_API {
    public function __construct() {
        add_action( 'rest_api_init', [ $this, 'register_routes' ] );
    }

    public function register_routes() {
        // GET endpoint
        register_rest_route( 'my-plugin/v1', '/portfolio', [
            'methods'             => \WP_REST_Server::READABLE,
            'callback'            => [ $this, 'get_portfolio_items' ],
            'permission_callback' => '__return_true',
            'args'                => [
                'page' => [
                    'default'           => 1,
                    'sanitize_callback' => 'absint',
                    'validate_callback' => function( $param ) {
                        return is_numeric( $param ) && $param > 0;
                    },
                ],
                'per_page' => [
                    'default'           => 10,
                    'sanitize_callback' => 'absint',
                ],
            ],
        ] );

        // POST endpoint
        register_rest_route( 'my-plugin/v1', '/portfolio', [
            'methods'             => \WP_REST_Server::CREATABLE,
            'callback'            => [ $this, 'create_portfolio_item' ],
            'permission_callback' => [ $this, 'check_permissions' ],
            'args'                => [
                'title' => [
                    'required'          => true,
                    'sanitize_callback' => 'sanitize_text_field',
                    'validate_callback' => function( $param ) {
                        return ! empty( $param );
                    },
                ],
                'content' => [
                    'required'          => true,
                    'sanitize_callback' => 'wp_kses_post',
                ],
            ],
        ] );

        // GET single item
        register_rest_route( 'my-plugin/v1', '/portfolio/(?P<id>\d+)', [
            'methods'             => \WP_REST_Server::READABLE,
            'callback'            => [ $this, 'get_single_item' ],
            'permission_callback' => '__return_true',
            'args'                => [
                'id' => [
                    'sanitize_callback' => 'absint',
                    'validate_callback' => function( $param ) {
                        return is_numeric( $param );
                    },
                ],
            ],
        ] );

        // DELETE endpoint
        register_rest_route( 'my-plugin/v1', '/portfolio/(?P<id>\d+)', [
            'methods'             => \WP_REST_Server::DELETABLE,
            'callback'            => [ $this, 'delete_portfolio_item' ],
            'permission_callback' => [ $this, 'check_permissions' ],
        ] );
    }

    public function get_portfolio_items( $request ) {
        $page = $request->get_param( 'page' );
        $per_page = $request->get_param( 'per_page' );

        $query = new \WP_Query( [
            'post_type'      => 'portfolio',
            'posts_per_page' => $per_page,
            'paged'          => $page,
            'post_status'    => 'publish',
        ] );

        if ( ! $query->have_posts() ) {
            return new \WP_REST_Response( [], 200 );
        }

        $items = [];
        foreach ( $query->posts as $post ) {
            $items[] = $this->format_item( $post );
        }

        $response = new \WP_REST_Response( $items, 200 );

        // Add pagination headers
        $total = $query->found_posts;
        $max_pages = $query->max_num_pages;

        $response->header( 'X-WP-Total', $total );
        $response->header( 'X-WP-TotalPages', $max_pages );

        return $response;
    }

    public function get_single_item( $request ) {
        $post_id = $request->get_param( 'id' );
        $post = get_post( $post_id );

        if ( ! $post || 'portfolio' !== $post->post_type ) {
            return new \WP_Error(
                'rest_not_found',
                __( 'Portfolio item not found', 'my-plugin' ),
                [ 'status' => 404 ]
            );
        }

        return new \WP_REST_Response( $this->format_item( $post ), 200 );
    }

    public function create_portfolio_item( $request ) {
        $title = $request->get_param( 'title' );
        $content = $request->get_param( 'content' );

        $post_id = wp_insert_post( [
            'post_type'    => 'portfolio',
            'post_title'   => $title,
            'post_content' => $content,
            'post_status'  => 'draft',
            'post_author'  => get_current_user_id(),
        ] );

        if ( is_wp_error( $post_id ) ) {
            return new \WP_Error(
                'rest_create_failed',
                __( 'Failed to create portfolio item', 'my-plugin' ),
                [ 'status' => 500 ]
            );
        }

        $post = get_post( $post_id );
        return new \WP_REST_Response( $this->format_item( $post ), 201 );
    }

    public function delete_portfolio_item( $request ) {
        $post_id = $request->get_param( 'id' );
        $post = get_post( $post_id );

        if ( ! $post || 'portfolio' !== $post->post_type ) {
            return new \WP_Error(
                'rest_not_found',
                __( 'Portfolio item not found', 'my-plugin' ),
                [ 'status' => 404 ]
            );
        }

        $result = wp_delete_post( $post_id, true );

        if ( ! $result ) {
            return new \WP_Error(
                'rest_delete_failed',
                __( 'Failed to delete portfolio item', 'my-plugin' ),
                [ 'status' => 500 ]
            );
        }

        return new \WP_REST_Response( [
            'message' => __( 'Portfolio item deleted', 'my-plugin' ),
        ], 200 );
    }

    public function check_permissions( $request ) {
        // Check if user is logged in
        if ( ! is_user_logged_in() ) {
            return false;
        }

        // Check capabilities
        return current_user_can( 'edit_posts' );
    }

    private function format_item( $post ) {
        return [
            'id'           => $post->ID,
            'title'        => $post->post_title,
            'content'      => apply_filters( 'the_content', $post->post_content ),
            'excerpt'      => $post->post_excerpt,
            'date'         => get_the_date( 'c', $post ),
            'modified'     => get_the_modified_date( 'c', $post ),
            'author'       => [
                'id'   => $post->post_author,
                'name' => get_the_author_meta( 'display_name', $post->post_author ),
            ],
            'featured_image' => get_the_post_thumbnail_url( $post->ID, 'large' ),
            'meta'         => [
                'url'    => get_post_meta( $post->ID, 'portfolio_url', true ),
                'client' => get_post_meta( $post->ID, 'portfolio_client', true ),
            ],
        ];
    }
}

new REST_API();
```

### 2. **JavaScript Client** (assets/js/api-client.js)

```javascript
class PortfolioAPI {
    constructor() {
        this.baseUrl = window.location.origin + '/wp-json/my-plugin/v1';
        this.nonce = myPluginData.nonce;
    }

    async getItems(page = 1, perPage = 10) {
        try {
            const response = await fetch(
                `${this.baseUrl}/portfolio?page=${page}&per_page=${perPage}`
            );

            if (!response.ok) {
                throw new Error('Failed to fetch items');
            }

            const data = await response.json();
            const total = response.headers.get('X-WP-Total');
            const totalPages = response.headers.get('X-WP-TotalPages');

            return {
                items: data,
                total: parseInt(total),
                totalPages: parseInt(totalPages),
            };
        } catch (error) {
            console.error('Error fetching items:', error);
            throw error;
        }
    }

    async getItem(id) {
        try {
            const response = await fetch(`${this.baseUrl}/portfolio/${id}`);

            if (!response.ok) {
                throw new Error('Item not found');
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching item:', error);
            throw error;
        }
    }

    async createItem(data) {
        try {
            const response = await fetch(`${this.baseUrl}/portfolio`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': this.nonce,
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                throw new Error('Failed to create item');
            }

            return await response.json();
        } catch (error) {
            console.error('Error creating item:', error);
            throw error;
        }
    }

    async deleteItem(id) {
        try {
            const response = await fetch(`${this.baseUrl}/portfolio/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-WP-Nonce': this.nonce,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to delete item');
            }

            return await response.json();
        } catch (error) {
            console.error('Error deleting item:', error);
            throw error;
        }
    }
}

// Usage example
const api = new PortfolioAPI();
api.getItems(1, 10).then(result => {
    console.log('Items:', result.items);
});
```

Generate complete WordPress REST API endpoints with authentication and validation.
