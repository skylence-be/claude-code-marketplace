# File Uploads

Filament 4 FileUpload component with image editing and validation.

## Basic Image Upload

```php
use Filament\Forms;

Forms\Components\FileUpload::make('image')
    ->image()
    ->required()
    ->directory('uploads')
    ->disk('public')
    ->maxSize(2048) // 2MB in KB
    ->acceptedFileTypes(['image/jpeg', 'image/png', 'image/webp']);
```

## Image Editor

```php
Forms\Components\FileUpload::make('featured_image')
    ->image()
    ->imageEditor() // Enable built-in editor
    ->imageEditorAspectRatios([
        null, // Free crop
        '16:9',
        '4:3',
        '1:1',
    ])
    ->imageEditorMode(2) // 1 = contain, 2 = cover, 3 = none
    ->imageEditorViewportWidth('1920')
    ->imageEditorViewportHeight('1080')
    ->imageEditorEmptyFillColor('#ffffff')
    ->circleCropper() // For avatars
    ->directory('images/featured')
    ->visibility('public')
    ->disk('public');
```

## Avatar Upload

```php
Forms\Components\FileUpload::make('avatar')
    ->image()
    ->avatar() // Circular preview
    ->imageEditor()
    ->circleCropper()
    ->directory('avatars')
    ->maxSize(1024)
    ->imagePreviewHeight('150');
```

## Multiple File Upload

```php
Forms\Components\FileUpload::make('gallery')
    ->multiple()
    ->image()
    ->reorderable() // Drag to reorder
    ->appendFiles() // Add to existing instead of replace
    ->maxFiles(10)
    ->minFiles(1)
    ->directory('galleries')
    ->disk('public')
    ->maxSize(5120)
    ->panelLayout('grid'); // Grid preview layout
```

## Document Upload

```php
Forms\Components\FileUpload::make('documents')
    ->multiple()
    ->directory('documents')
    ->disk('private')
    ->visibility('private')
    ->maxSize(10240) // 10MB
    ->acceptedFileTypes([
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ])
    ->previewable(false) // No preview for documents
    ->downloadable()
    ->openable();
```

## Upload Configuration

```php
Forms\Components\FileUpload::make('file')
    // Storage
    ->disk('public')
    ->directory('uploads')
    ->visibility('public')

    // Validation
    ->maxSize(5120) // KB
    ->minSize(100)  // KB
    ->acceptedFileTypes(['image/*', 'application/pdf'])

    // Image specific
    ->image()
    ->imageResizeMode('cover')
    ->imageCropAspectRatio('16:9')
    ->imageResizeTargetWidth(1920)
    ->imageResizeTargetHeight(1080)

    // Preview
    ->imagePreviewHeight('250')
    ->loadingIndicatorPosition('center')
    ->panelAspectRatio('2:1')
    ->panelLayout('integrated') // or 'compact', 'grid'

    // Actions
    ->downloadable()
    ->openable()
    ->previewable()
    ->deletable()
    ->reorderable() // For multiple

    // Button positions
    ->removeUploadedFileButtonPosition('right')
    ->uploadButtonPosition('left')
    ->uploadProgressIndicatorPosition('left');
```

## Custom File Names

```php
Forms\Components\FileUpload::make('image')
    ->image()
    ->directory('uploads')

    // Generate custom filename
    ->getUploadedFileNameForStorageUsing(
        fn ($file): string => (string) str(Str::uuid())
            ->append('.')
            ->append($file->getClientOriginalExtension())
    )

    // Or use original name
    ->preserveFilenames()

    // Or store as hash
    ->storeFileNamesIn('original_filename');
```

## S3/Cloud Storage

```php
Forms\Components\FileUpload::make('file')
    ->disk('s3')
    ->directory('uploads/' . now()->format('Y/m'))
    ->visibility('public')
    ->maxSize(10240)
    ->downloadable();
```

## Validation Helpers

```php
Forms\Components\FileUpload::make('image')
    ->image()

    // Dimensions validation
    ->imageResizeMode('contain')
    ->imageCropAspectRatio('1:1')
    ->imageResizeTargetWidth(500)
    ->imageResizeTargetHeight(500)

    // Or use rules
    ->rules([
        'dimensions:min_width=100,min_height=100,max_width=2000,max_height=2000',
    ]);

Forms\Components\FileUpload::make('document')
    ->acceptedFileTypes(['application/pdf'])
    ->rules(['mimes:pdf'])
    ->maxSize(5120);
```

## Existing File Handling

```php
Forms\Components\FileUpload::make('image')
    ->image()
    ->directory('images')

    // Show existing files from database
    ->getUploadedFileNameForStorageUsing(
        function ($file, $get) {
            // Preserve existing filename if editing
            $existing = $get('image');
            if ($existing && !is_array($existing)) {
                return basename($existing);
            }
            return $file->hashName();
        }
    );
```

## Upload Events

```php
Forms\Components\FileUpload::make('file')
    ->afterStateUpdated(function ($state) {
        // Process after upload
        if ($state) {
            // $state is the path to uploaded file
            \Log::info('File uploaded: ' . $state);
        }
    });
```

## Performance Options

```php
Forms\Components\FileUpload::make('image')
    ->image()
    ->directory('images')

    // Don't check if file exists (faster)
    ->checkFileExistence(false)

    // Lazy load previews
    ->loadingIndicatorPosition('center')

    // Limit preview size
    ->imagePreviewHeight('100');
```

## Complete Example

```php
Forms\Components\Section::make('Media')
    ->schema([
        Forms\Components\FileUpload::make('featured_image')
            ->label('Featured Image')
            ->image()
            ->imageEditor()
            ->imageEditorAspectRatios(['16:9', '4:3', '1:1'])
            ->directory('posts/featured')
            ->disk('public')
            ->visibility('public')
            ->maxSize(2048)
            ->acceptedFileTypes(['image/jpeg', 'image/png', 'image/webp'])
            ->imagePreviewHeight('200')
            ->downloadable()
            ->openable()
            ->columnSpanFull()
            ->helperText('Recommended size: 1200x630 pixels'),

        Forms\Components\FileUpload::make('gallery')
            ->label('Image Gallery')
            ->multiple()
            ->image()
            ->reorderable()
            ->appendFiles()
            ->maxFiles(10)
            ->directory('posts/gallery')
            ->disk('public')
            ->maxSize(2048)
            ->panelLayout('grid')
            ->downloadable()
            ->columnSpanFull(),

        Forms\Components\FileUpload::make('attachments')
            ->label('Attachments')
            ->multiple()
            ->directory('posts/attachments')
            ->disk('private')
            ->visibility('private')
            ->maxSize(10240)
            ->acceptedFileTypes([
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            ])
            ->downloadable()
            ->openable()
            ->columnSpanFull(),
    ]);
```
