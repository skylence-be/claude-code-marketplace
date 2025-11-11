---
description: Create custom Gutenberg block with React
model: claude-sonnet-4-5
---

Create a custom Gutenberg block.

## Block Specification

$ARGUMENTS

## WordPress Gutenberg Block Best Practices

### 1. **Block Metadata** (blocks/my-block/block.json)

```json
{
  "$schema": "https://schemas.wp.org/wp/6.0/block.json",
  "apiVersion": 3,
  "name": "my-plugin/my-block",
  "version": "1.0.0",
  "title": "My Custom Block",
  "category": "common",
  "description": "A custom Gutenberg block",
  "keywords": ["custom", "block"],
  "icon": "smiley",
  "attributes": {
    "content": {
      "type": "string",
      "default": ""
    },
    "alignment": {
      "type": "string",
      "default": "none"
    }
  },
  "supports": {
    "html": false,
    "align": ["left", "center", "right"],
    "anchor": true,
    "className": true,
    "customClassName": true
  },
  "textdomain": "my-plugin",
  "editorScript": "file:./index.js",
  "editorStyle": "file:./index.css",
  "style": "file:./style.css"
}
```

### 2. **Edit Component** (blocks/my-block/index.js)

```jsx
import { registerBlockType } from '@wordpress/blocks';
import { useBlockProps } from '@wordpress/block-editor';
import { TextControl, AlignmentToolbar, BlockControls } from '@wordpress/components';
import { __ } from '@wordpress/i18n';
import './index.css';

registerBlockType( 'my-plugin/my-block', {
    edit: ( { attributes, setAttributes } ) => {
        const { content, alignment } = attributes;
        const blockProps = useBlockProps( {
            className: `align${ alignment }`,
        } );

        return (
            <>
                <BlockControls>
                    <AlignmentToolbar
                        value={ alignment }
                        onChange={ ( newAlignment ) =>
                            setAttributes( { alignment: newAlignment } )
                        }
                    />
                </BlockControls>

                <div { ...blockProps }>
                    <TextControl
                        label={ __( 'Block Content', 'my-plugin' ) }
                        value={ content }
                        onChange={ ( value ) =>
                            setAttributes( { content: value } )
                        }
                        placeholder={ __(
                            'Enter block content',
                            'my-plugin'
                        ) }
                    />
                </div>
            </>
        );
    },

    save: ( { attributes } ) => {
        const { content, alignment } = attributes;
        const blockProps = useBlockProps.save( {
            className: `align${ alignment }`,
        } );

        return (
            <div { ...blockProps }>
                <p>{ content }</p>
            </div>
        );
    },
} );
```

### 3. **Block Style** (blocks/my-block/index.css)

```css
.wp-block-my-plugin-my-block {
    padding: 1.5rem;
    background-color: #f5f5f5;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.wp-block-my-plugin-my-block.alignleft {
    float: left;
    width: 50%;
    margin-right: 2rem;
}

.wp-block-my-plugin-my-block.alignright {
    float: right;
    width: 50%;
    margin-left: 2rem;
}

.wp-block-my-plugin-my-block.aligncenter {
    text-align: center;
}
```

### 4. **Block Registration** (includes/class-blocks.php)

```php
<?php
namespace MyPlugin;

class Blocks {
    public function __construct() {
        add_action( 'init', [ $this, 'register_blocks' ] );
    }

    public function register_blocks() {
        // Register block scripts
        wp_register_script(
            'my-plugin-blocks',
            MY_PLUGIN_URI . 'build/blocks.js',
            [ 'wp-blocks', 'wp-i18n', 'wp-element', 'wp-editor' ],
            MY_PLUGIN_VERSION
        );

        wp_register_style(
            'my-plugin-blocks',
            MY_PLUGIN_URI . 'build/blocks.css',
            [],
            MY_PLUGIN_VERSION
        );

        // Register block from block.json
        register_block_type( MY_PLUGIN_DIR . 'blocks/my-block' );
    }
}

new Blocks();
```

### 5. **Frontend Style** (blocks/my-block/style.css)

```css
.wp-block-my-plugin-my-block {
    padding: 1.5rem;
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    line-height: 1.6;
}

.wp-block-my-plugin-my-block p {
    margin: 0;
    color: #333;
}
```

### 6. **Dynamic Block** (blocks/dynamic-block/render.php)

```php
<?php
/**
 * Dynamic block render callback
 */

$content = isset( $attributes['content'] ) ? sanitize_text_field( $attributes['content'] ) : '';
$alignment = isset( $attributes['alignment'] ) ? sanitize_text_field( $attributes['alignment'] ) : 'none';

// Fetch dynamic data
$posts = get_posts( [
    'post_type' => 'post',
    'numberposts' => 3,
] );
?>

<div class="wp-block-my-plugin-dynamic-block align<?php echo esc_attr( $alignment ); ?>">
    <h2><?php echo esc_html( $content ); ?></h2>
    <ul>
        <?php foreach ( $posts as $post ) : ?>
            <li>
                <a href="<?php echo esc_url( get_permalink( $post ) ); ?>">
                    <?php echo esc_html( $post->post_title ); ?>
                </a>
            </li>
        <?php endforeach; ?>
    </ul>
</div>
```

Generate complete Gutenberg block with React and proper WordPress integration.
