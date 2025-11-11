---
description: Create custom WordPress taxonomy
model: claude-sonnet-4-5
---

Create a custom WordPress taxonomy.

## Taxonomy Specification

$ARGUMENTS

## WordPress Taxonomy Best Practices

### 1. **Register Taxonomy** (includes/class-taxonomies.php)

```php
<?php
namespace MyPlugin;

class Taxonomies {
    public function __construct() {
        add_action( 'init', [ $this, 'register_taxonomies' ] );
    }

    public function register_taxonomies() {
        // Register custom taxonomy for portfolio
        register_taxonomy( 'portfolio_category', 'portfolio', [
            'labels' => [
                'name'          => __( 'Portfolio Categories', 'my-plugin' ),
                'singular_name' => __( 'Portfolio Category', 'my-plugin' ),
                'add_new_item'  => __( 'Add New Category', 'my-plugin' ),
            ],
            'description'        => __( 'Categorize portfolio items', 'my-plugin' ),
            'hierarchical'       => true,
            'public'             => true,
            'show_admin_column'  => true,
            'show_in_rest'       => true,
            'rest_base'          => 'portfolio-categories',
            'rewrite'            => [
                'slug'         => 'portfolio-category',
                'hierarchical' => true,
            ],
            'capabilities'       => [
                'manage_terms' => 'manage_portfolio_categories',
                'edit_terms'   => 'edit_portfolio_categories',
                'delete_terms' => 'delete_portfolio_categories',
            ],
        ] );

        // Register custom taxonomy for skills (non-hierarchical)
        register_taxonomy( 'portfolio_skill', 'portfolio', [
            'labels' => [
                'name'          => __( 'Portfolio Skills', 'my-plugin' ),
                'singular_name' => __( 'Portfolio Skill', 'my-plugin' ),
            ],
            'description'       => __( 'Skills used in portfolio items', 'my-plugin' ),
            'hierarchical'      => false,
            'public'            => true,
            'show_admin_column' => true,
            'show_in_rest'      => true,
            'rest_base'         => 'portfolio-skills',
            'rewrite'           => [ 'slug' => 'portfolio-skill' ],
        ] );
    }
}

new Taxonomies();
```

### 2. **Taxonomy Meta** (includes/class-taxonomy-meta.php)

```php
<?php
namespace MyPlugin;

class Taxonomy_Meta {
    public function __construct() {
        add_action( 'portfolio_category_add_form_fields', [ $this, 'add_term_meta_fields' ] );
        add_action( 'portfolio_category_edit_form_fields', [ $this, 'edit_term_meta_fields' ] );
        add_action( 'created_portfolio_category', [ $this, 'save_term_meta' ] );
        add_action( 'edited_portfolio_category', [ $this, 'save_term_meta' ] );
    }

    public function add_term_meta_fields( $taxonomy ) {
        ?>
        <div class="form-field">
            <label for="category_color">
                <?php esc_html_e( 'Category Color', 'my-plugin' ); ?>
            </label>
            <input
                type="color"
                id="category_color"
                name="category_color"
                value="#3498db"
            />
            <p><?php esc_html_e( 'Choose a color for this category', 'my-plugin' ); ?></p>
        </div>

        <div class="form-field">
            <label for="category_icon">
                <?php esc_html_e( 'Category Icon', 'my-plugin' ); ?>
            </label>
            <input
                type="text"
                id="category_icon"
                name="category_icon"
                placeholder="dashicons-star"
            />
            <p><?php esc_html_e( 'Use Dashicons slug', 'my-plugin' ); ?></p>
        </div>
        <?php
    }

    public function edit_term_meta_fields( $term ) {
        $color = get_term_meta( $term->term_id, 'category_color', true );
        $icon = get_term_meta( $term->term_id, 'category_icon', true );
        ?>
        <tr class="form-field">
            <th scope="row">
                <label for="category_color">
                    <?php esc_html_e( 'Category Color', 'my-plugin' ); ?>
                </label>
            </th>
            <td>
                <input
                    type="color"
                    id="category_color"
                    name="category_color"
                    value="<?php echo esc_attr( $color ); ?>"
                />
            </td>
        </tr>
        <tr class="form-field">
            <th scope="row">
                <label for="category_icon">
                    <?php esc_html_e( 'Category Icon', 'my-plugin' ); ?>
                </label>
            </th>
            <td>
                <input
                    type="text"
                    id="category_icon"
                    name="category_icon"
                    value="<?php echo esc_attr( $icon ); ?>"
                    placeholder="dashicons-star"
                />
            </td>
        </tr>
        <?php
    }

    public function save_term_meta( $term_id ) {
        // Verify nonce if needed
        // Check permissions
        if ( ! current_user_can( 'edit_portfolio_categories' ) ) {
            return;
        }

        // Save color
        if ( isset( $_POST['category_color'] ) ) {
            update_term_meta(
                $term_id,
                'category_color',
                sanitize_text_field( $_POST['category_color'] )
            );
        }

        // Save icon
        if ( isset( $_POST['category_icon'] ) ) {
            update_term_meta(
                $term_id,
                'category_icon',
                sanitize_text_field( $_POST['category_icon'] )
            );
        }
    }
}

new Taxonomy_Meta();
```

### 3. **Taxonomy Template** (template-parts/taxonomy-portfolio-category.php)

```php
<?php
/**
 * Template for portfolio category pages
 */

get_header();

$term = get_queried_object();
$color = get_term_meta( $term->term_id, 'category_color', true );
?>

<div class="container">
    <header class="page-header" style="border-color: <?php echo esc_attr( $color ); ?>;">
        <h1><?php echo esc_html( $term->name ); ?></h1>
        <?php
        if ( $term->description ) {
            echo '<p class="archive-description">' . esc_html( $term->description ) . '</p>';
        }
        ?>
    </header>

    <div class="portfolio-grid">
        <?php
        if ( have_posts() ) :
            while ( have_posts() ) :
                the_post();
                ?>
                <article class="portfolio-item">
                    <a href="<?php the_permalink(); ?>">
                        <?php
                        if ( has_post_thumbnail() ) {
                            the_post_thumbnail( 'large' );
                        }
                        ?>
                        <h3><?php the_title(); ?></h3>
                    </a>
                </article>
                <?php
            endwhile;
        else :
            echo '<p>' . esc_html__( 'No portfolio items found', 'my-plugin' ) . '</p>';
        endif;
        ?>
    </div>

    <?php the_posts_pagination(); ?>
</div>

<?php
get_footer();
```

### 4. **Query Helper** (includes/class-query-helper.php)

```php
<?php
namespace MyPlugin;

class Query_Helper {
    public static function get_portfolio_by_category( $category_slug, $args = [] ) {
        $defaults = [
            'post_type'      => 'portfolio',
            'posts_per_page' => 12,
            'tax_query'      => [
                [
                    'taxonomy' => 'portfolio_category',
                    'field'    => 'slug',
                    'terms'    => $category_slug,
                ],
            ],
        ];

        $args = wp_parse_args( $args, $defaults );

        return new \WP_Query( $args );
    }

    public static function get_portfolio_by_skill( $skill_slug, $args = [] ) {
        $defaults = [
            'post_type'      => 'portfolio',
            'posts_per_page' => 12,
            'tax_query'      => [
                [
                    'taxonomy' => 'portfolio_skill',
                    'field'    => 'slug',
                    'terms'    => $skill_slug,
                ],
            ],
        ];

        $args = wp_parse_args( $args, $defaults );

        return new \WP_Query( $args );
    }
}
```

Generate complete WordPress taxonomy with meta fields and template support.
