---
description: Create custom WordPress shortcode
model: claude-sonnet-4-5
---

Create a custom WordPress shortcode.

## Shortcode Specification

$ARGUMENTS

## WordPress Shortcode Best Practices

### 1. **Simple Shortcode** (includes/class-shortcodes.php)

```php
<?php
namespace MyPlugin;

class Shortcodes {
    public function __construct() {
        add_shortcode( 'portfolio_grid', [ $this, 'portfolio_grid_shortcode' ] );
        add_shortcode( 'portfolio_slider', [ $this, 'portfolio_slider_shortcode' ] );
        add_shortcode( 'portfolio_filter', [ $this, 'portfolio_filter_shortcode' ] );
    }

    /**
     * Portfolio Grid Shortcode
     *
     * Usage: [portfolio_grid count="6" columns="3" category="web-design"]
     */
    public function portfolio_grid_shortcode( $atts ) {
        $atts = shortcode_atts( [
            'count'    => 6,
            'columns'  => 3,
            'category' => '',
            'orderby'  => 'date',
            'order'    => 'DESC',
        ], $atts, 'portfolio_grid' );

        $args = [
            'post_type'      => 'portfolio',
            'posts_per_page' => absint( $atts['count'] ),
            'orderby'        => sanitize_text_field( $atts['orderby'] ),
            'order'          => sanitize_text_field( $atts['order'] ),
        ];

        // Add category filter if provided
        if ( ! empty( $atts['category'] ) ) {
            $args['tax_query'] = [
                [
                    'taxonomy' => 'portfolio_category',
                    'field'    => 'slug',
                    'terms'    => sanitize_text_field( $atts['category'] ),
                ],
            ];
        }

        $query = new \WP_Query( $args );

        if ( ! $query->have_posts() ) {
            return '<p>' . esc_html__( 'No portfolio items found', 'my-plugin' ) . '</p>';
        }

        ob_start();
        ?>
        <div class="portfolio-grid portfolio-grid-columns-<?php echo esc_attr( $atts['columns'] ); ?>">
            <?php
            while ( $query->have_posts() ) :
                $query->the_post();
                ?>
                <article class="portfolio-item">
                    <a href="<?php the_permalink(); ?>">
                        <?php
                        if ( has_post_thumbnail() ) {
                            the_post_thumbnail( 'large' );
                        }
                        ?>
                        <div class="portfolio-item-content">
                            <h3><?php the_title(); ?></h3>
                            <p><?php echo esc_html( wp_trim_words( get_the_excerpt(), 15 ) ); ?></p>
                        </div>
                    </a>
                </article>
                <?php
            endwhile;
            wp_reset_postdata();
            ?>
        </div>
        <?php

        return ob_get_clean();
    }

    /**
     * Portfolio Slider Shortcode
     *
     * Usage: [portfolio_slider count="5" autoplay="true" speed="3000"]
     */
    public function portfolio_slider_shortcode( $atts ) {
        $atts = shortcode_atts( [
            'count'    => 5,
            'autoplay' => 'true',
            'speed'    => 3000,
        ], $atts, 'portfolio_slider' );

        $query = new \WP_Query( [
            'post_type'      => 'portfolio',
            'posts_per_page' => absint( $atts['count'] ),
            'orderby'        => 'rand',
        ] );

        if ( ! $query->have_posts() ) {
            return '';
        }

        $slider_id = 'portfolio-slider-' . uniqid();

        ob_start();
        ?>
        <div
            id="<?php echo esc_attr( $slider_id ); ?>"
            class="portfolio-slider"
            data-autoplay="<?php echo esc_attr( $atts['autoplay'] ); ?>"
            data-speed="<?php echo esc_attr( $atts['speed'] ); ?>"
        >
            <div class="slider-wrapper">
                <?php
                while ( $query->have_posts() ) :
                    $query->the_post();
                    ?>
                    <div class="slide">
                        <a href="<?php the_permalink(); ?>">
                            <?php
                            if ( has_post_thumbnail() ) {
                                the_post_thumbnail( 'large' );
                            }
                            ?>
                            <div class="slide-content">
                                <h3><?php the_title(); ?></h3>
                            </div>
                        </a>
                    </div>
                    <?php
                endwhile;
                wp_reset_postdata();
                ?>
            </div>
            <button class="slider-prev">&#8249;</button>
            <button class="slider-next">&#8250;</button>
        </div>
        <?php

        return ob_get_clean();
    }

    /**
     * Portfolio Filter Shortcode
     *
     * Usage: [portfolio_filter]
     */
    public function portfolio_filter_shortcode( $atts ) {
        $atts = shortcode_atts( [], $atts, 'portfolio_filter' );

        // Get all portfolio categories
        $categories = get_terms( [
            'taxonomy'   => 'portfolio_category',
            'hide_empty' => true,
        ] );

        if ( is_wp_error( $categories ) || empty( $categories ) ) {
            return '';
        }

        ob_start();
        ?>
        <div class="portfolio-filter" data-filter-target=".portfolio-grid">
            <button class="filter-btn active" data-filter="*">
                <?php esc_html_e( 'All', 'my-plugin' ); ?>
            </button>
            <?php foreach ( $categories as $category ) : ?>
                <button
                    class="filter-btn"
                    data-filter=".category-<?php echo esc_attr( $category->slug ); ?>"
                >
                    <?php echo esc_html( $category->name ); ?>
                </button>
            <?php endforeach; ?>
        </div>

        <script>
        (function($) {
            $('.portfolio-filter .filter-btn').on('click', function() {
                const filter = $(this).data('filter');
                const target = $(this).closest('.portfolio-filter').data('filter-target');

                $('.portfolio-filter .filter-btn').removeClass('active');
                $(this).addClass('active');

                if (filter === '*') {
                    $(target + ' .portfolio-item').show();
                } else {
                    $(target + ' .portfolio-item').hide();
                    $(target + ' .portfolio-item' + filter).show();
                }
            });
        })(jQuery);
        </script>
        <?php

        return ob_get_clean();
    }
}

new Shortcodes();
```

### 2. **Shortcode with Nested Content**

```php
/**
 * Portfolio Tabs Shortcode
 *
 * Usage:
 * [portfolio_tabs]
 *   [portfolio_tab title="Web Design"]Content here[/portfolio_tab]
 *   [portfolio_tab title="Development"]More content[/portfolio_tab]
 * [/portfolio_tabs]
 */
class Portfolio_Tabs_Shortcode {
    private static $tab_index = 0;

    public function __construct() {
        add_shortcode( 'portfolio_tabs', [ $this, 'tabs_wrapper' ] );
        add_shortcode( 'portfolio_tab', [ $this, 'tab_content' ] );
    }

    public function tabs_wrapper( $atts, $content = null ) {
        self::$tab_index = 0;

        // Parse inner shortcodes
        $content = do_shortcode( $content );

        ob_start();
        ?>
        <div class="portfolio-tabs">
            <?php echo wp_kses_post( $content ); ?>
        </div>
        <?php

        return ob_get_clean();
    }

    public function tab_content( $atts, $content = null ) {
        $atts = shortcode_atts( [
            'title' => 'Tab ' . ( self::$tab_index + 1 ),
        ], $atts, 'portfolio_tab' );

        $tab_id = 'tab-' . self::$tab_index;
        $is_active = self::$tab_index === 0;
        self::$tab_index++;

        ob_start();
        ?>
        <div class="tab-pane <?php echo $is_active ? 'active' : ''; ?>" id="<?php echo esc_attr( $tab_id ); ?>">
            <h3><?php echo esc_html( $atts['title'] ); ?></h3>
            <div class="tab-content">
                <?php echo do_shortcode( $content ); ?>
            </div>
        </div>
        <?php

        return ob_get_clean();
    }
}

new Portfolio_Tabs_Shortcode();
```

### 3. **Shortcode Button in Editor** (includes/class-shortcode-ui.php)

```php
<?php
namespace MyPlugin;

class Shortcode_UI {
    public function __construct() {
        add_action( 'admin_footer', [ $this, 'add_shortcode_button' ] );
        add_action( 'admin_enqueue_scripts', [ $this, 'enqueue_scripts' ] );
    }

    public function enqueue_scripts( $hook ) {
        if ( 'post.php' !== $hook && 'post-new.php' !== $hook ) {
            return;
        }

        wp_enqueue_script(
            'my-plugin-shortcode-ui',
            MY_PLUGIN_URI . 'admin/js/shortcode-ui.js',
            [ 'jquery' ],
            MY_PLUGIN_VERSION,
            true
        );
    }

    public function add_shortcode_button() {
        global $pagenow;
        if ( ! in_array( $pagenow, [ 'post.php', 'post-new.php' ] ) ) {
            return;
        }
        ?>
        <script>
        (function() {
            tinymce.create('tinymce.plugins.MyPluginShortcodes', {
                init: function(ed, url) {
                    ed.addButton('my_plugin_shortcodes', {
                        title: 'Insert Portfolio Shortcode',
                        icon: 'icon dashicons-portfolio',
                        type: 'menubutton',
                        menu: [
                            {
                                text: 'Portfolio Grid',
                                onclick: function() {
                                    ed.insertContent('[portfolio_grid count="6" columns="3"]');
                                }
                            },
                            {
                                text: 'Portfolio Slider',
                                onclick: function() {
                                    ed.insertContent('[portfolio_slider count="5"]');
                                }
                            }
                        ]
                    });
                }
            });
            tinymce.PluginManager.add('my_plugin_shortcodes', tinymce.plugins.MyPluginShortcodes);
        })();
        </script>
        <?php
    }
}

new Shortcode_UI();
```

Generate complete WordPress shortcode with attributes and proper escaping.
