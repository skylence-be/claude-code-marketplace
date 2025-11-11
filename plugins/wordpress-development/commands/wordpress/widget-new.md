---
description: Create custom WordPress widget
model: claude-sonnet-4-5
---

Create a custom WordPress widget.

## Widget Specification

$ARGUMENTS

## WordPress Widget Best Practices

### 1. **Legacy Widget** (includes/class-recent-posts-widget.php)

```php
<?php
namespace MyPlugin;

class Recent_Posts_Widget extends \WP_Widget {
    public function __construct() {
        parent::__construct(
            'my_plugin_recent_posts',
            __( 'Recent Portfolio Items', 'my-plugin' ),
            [
                'description' => __( 'Display recent portfolio items', 'my-plugin' ),
            ]
        );
    }

    public function widget( $args, $instance ) {
        $title = apply_filters(
            'widget_title',
            isset( $instance['title'] ) ? $instance['title'] : __( 'Recent Portfolio', 'my-plugin' ),
            $instance,
            $this->id_base
        );

        $count = isset( $instance['count'] ) ? absint( $instance['count'] ) : 3;

        echo wp_kses_post( $args['before_widget'] );

        if ( ! empty( $title ) ) {
            echo wp_kses_post( $args['before_title'] ) . esc_html( $title ) . wp_kses_post( $args['after_title'] );
        }

        $portfolio = new \WP_Query( [
            'post_type'      => 'portfolio',
            'posts_per_page' => $count,
            'orderby'        => 'date',
            'order'          => 'DESC',
        ] );

        if ( $portfolio->have_posts() ) :
            ?>
            <ul class="recent-portfolio-list">
                <?php
                while ( $portfolio->have_posts() ) :
                    $portfolio->the_post();
                    ?>
                    <li>
                        <a href="<?php the_permalink(); ?>">
                            <?php the_title(); ?>
                        </a>
                        <span class="date">
                            <?php echo esc_html( get_the_date( 'M d, Y' ) ); ?>
                        </span>
                    </li>
                    <?php
                endwhile;
                ?>
            </ul>
            <?php
            wp_reset_postdata();
        else :
            echo '<p>' . esc_html__( 'No portfolio items found', 'my-plugin' ) . '</p>';
        endif;

        echo wp_kses_post( $args['after_widget'] );
    }

    public function form( $instance ) {
        $title = isset( $instance['title'] ) ? $instance['title'] : '';
        $count = isset( $instance['count'] ) ? absint( $instance['count'] ) : 3;
        ?>

        <p>
            <label for="<?php echo esc_attr( $this->get_field_id( 'title' ) ); ?>">
                <?php esc_html_e( 'Title:', 'my-plugin' ); ?>
            </label>
            <input
                class="widefat"
                id="<?php echo esc_attr( $this->get_field_id( 'title' ) ); ?>"
                name="<?php echo esc_attr( $this->get_field_name( 'title' ) ); ?>"
                type="text"
                value="<?php echo esc_attr( $title ); ?>"
            />
        </p>

        <p>
            <label for="<?php echo esc_attr( $this->get_field_id( 'count' ) ); ?>">
                <?php esc_html_e( 'Number of items:', 'my-plugin' ); ?>
            </label>
            <input
                class="small-text"
                id="<?php echo esc_attr( $this->get_field_id( 'count' ) ); ?>"
                name="<?php echo esc_attr( $this->get_field_name( 'count' ) ); ?>"
                type="number"
                step="1"
                min="1"
                value="<?php echo esc_attr( $count ); ?>"
            />
        </p>

        <?php
    }

    public function update( $new_instance, $old_instance ) {
        $instance = [];
        $instance['title'] = sanitize_text_field( $new_instance['title'] ?? '' );
        $instance['count'] = absint( $new_instance['count'] ?? 3 );

        return $instance;
    }
}

// Register widget
add_action( 'widgets_init', function() {
    register_widget( __NAMESPACE__ . '\\Recent_Posts_Widget' );
} );
```

### 2. **Block Widget** (includes/class-featured-portfolio-block.php)

```php
<?php
namespace MyPlugin;

class Featured_Portfolio_Block {
    public function __construct() {
        add_action( 'init', [ $this, 'register_block_widget' ] );
    }

    public function register_block_widget() {
        register_block_type( MY_PLUGIN_DIR . 'blocks/featured-portfolio' );
    }
}

new Featured_Portfolio_Block();
```

**Block Metadata** (blocks/featured-portfolio/block.json):

```json
{
  "$schema": "https://schemas.wp.org/wp/6.0/block.json",
  "apiVersion": 3,
  "name": "my-plugin/featured-portfolio",
  "version": "1.0.0",
  "title": "Featured Portfolio",
  "category": "widgets",
  "description": "Display featured portfolio items",
  "attributes": {
    "title": {
      "type": "string",
      "default": "Featured Projects"
    },
    "count": {
      "type": "integer",
      "default": 3
    }
  },
  "supports": {
    "align": ["left", "center", "right"],
    "anchor": true
  },
  "textdomain": "my-plugin",
  "editorScript": "file:./index.js",
  "render": "file:./render.php"
}
```

**Block Render** (blocks/featured-portfolio/render.php):

```php
<?php
/**
 * Featured Portfolio block render
 */

$title = isset( $attributes['title'] ) ? sanitize_text_field( $attributes['title'] ) : 'Featured Projects';
$count = isset( $attributes['count'] ) ? absint( $attributes['count'] ) : 3;

$portfolio = new \WP_Query( [
    'post_type'      => 'portfolio',
    'posts_per_page' => $count,
    'meta_key'       => 'featured',
    'meta_value'     => '1',
] );

if ( ! $portfolio->have_posts() ) {
    return;
}
?>

<div class="wp-block-my-plugin-featured-portfolio">
    <h2><?php echo esc_html( $title ); ?></h2>
    <div class="portfolio-grid">
        <?php
        while ( $portfolio->have_posts() ) :
            $portfolio->the_post();
            ?>
            <article class="portfolio-card">
                <a href="<?php the_permalink(); ?>">
                    <?php
                    if ( has_post_thumbnail() ) {
                        the_post_thumbnail( 'medium' );
                    }
                    ?>
                    <h3><?php the_title(); ?></h3>
                </a>
            </article>
            <?php
        endwhile;
        wp_reset_postdata();
        ?>
    </div>
</div>
```

### 3. **Widget Style** (assets/css/widget.css)

```css
.recent-portfolio-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.recent-portfolio-list li {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

.recent-portfolio-list li:last-child {
    border-bottom: none;
}

.recent-portfolio-list a {
    display: block;
    font-weight: 500;
    color: #2563eb;
    text-decoration: none;
}

.recent-portfolio-list a:hover {
    text-decoration: underline;
}

.recent-portfolio-list .date {
    font-size: 0.85em;
    color: #666;
    display: block;
    margin-top: 3px;
}

.wp-block-my-plugin-featured-portfolio {
    margin: 2rem 0;
}

.portfolio-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}

.portfolio-card {
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease;
}

.portfolio-card:hover {
    transform: translateY(-5px);
}
```

Generate complete WordPress widget with options and proper styling.
