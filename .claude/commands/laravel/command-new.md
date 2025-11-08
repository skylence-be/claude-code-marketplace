---
description: Create Laravel artisan console command
model: claude-sonnet-4-5
---

Create a Laravel artisan console command.

## Command Specification

$ARGUMENTS

## Laravel Console Command Patterns

### 1. **Basic Console Command**

```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

class CleanupOldRecords extends Command
{
    protected $signature = 'cleanup:old-records';
    protected $description = 'Delete records older than 90 days';

    public function handle(): int
    {
        $this->info('Starting cleanup process...');

        $deleted = DB::table('temporary_records')
            ->where('created_at', '<', now()->subDays(90))
            ->delete();

        $this->info("Deleted {$deleted} old records.");

        return Command::SUCCESS;
    }
}
```

### 2. **Command with Arguments and Options**

```php
<?php

namespace App\Console\Commands;

use App\Models\User;
use Illuminate\Console\Command;

class CreateUser extends Command
{
    protected $signature = 'user:create
                            {email : The email address of the user}
                            {--name= : The name of the user}
                            {--admin : Make the user an administrator}
                            {--force : Skip confirmation prompts}';

    protected $description = 'Create a new user account';

    public function handle(): int
    {
        $email = $this->argument('email');
        $name = $this->option('name') ?? $this->ask('What is the user\'s name?');
        $isAdmin = $this->option('admin');

        if (!$this->option('force')) {
            if (!$this->confirm("Create user {$name} ({$email})?")) {
                $this->warn('User creation cancelled.');
                return Command::FAILURE;
            }
        }

        $user = User::create([
            'name' => $name,
            'email' => $email,
            'password' => Hash::make(Str::random(16)),
            'role' => $isAdmin ? 'admin' : 'user',
        ]);

        $this->info("User created successfully! ID: {$user->id}");

        if ($isAdmin) {
            $this->warn('User has administrator privileges.');
        }

        return Command::SUCCESS;
    }
}
```

### 3. **Interactive Command with Prompts**

```php
<?php

namespace App\Console\Commands;

use App\Models\Post;
use Illuminate\Console\Command;

class PublishPost extends Command
{
    protected $signature = 'post:publish';
    protected $description = 'Interactively publish a blog post';

    public function handle(): int
    {
        $title = $this->ask('What is the post title?');

        $category = $this->choice(
            'Select a category',
            ['Technology', 'Business', 'Lifestyle'],
            0
        );

        $tags = $this->ask('Enter tags (comma-separated)');

        $publishNow = $this->confirm('Publish immediately?', true);

        $this->table(
            ['Field', 'Value'],
            [
                ['Title', $title],
                ['Category', $category],
                ['Tags', $tags],
                ['Publish', $publishNow ? 'Yes' : 'No'],
            ]
        );

        if ($this->confirm('Continue with these settings?')) {
            $post = Post::create([
                'title' => $title,
                'category' => $category,
                'tags' => explode(',', $tags),
                'status' => $publishNow ? 'published' : 'draft',
                'published_at' => $publishNow ? now() : null,
            ]);

            $this->info('Post created successfully!');
            return Command::SUCCESS;
        }

        $this->warn('Post creation cancelled.');
        return Command::FAILURE;
    }
}
```

### 4. **Command with Progress Bar**

```php
<?php

namespace App\Console\Commands;

use App\Models\User;
use Illuminate\Console\Command;

class ProcessUsers extends Command
{
    protected $signature = 'users:process {--limit=100}';
    protected $description = 'Process user data with progress indication';

    public function handle(): int
    {
        $limit = $this->option('limit');
        $users = User::limit($limit)->get();

        $this->info("Processing {$users->count()} users...");

        $bar = $this->output->createProgressBar($users->count());
        $bar->start();

        foreach ($users as $user) {
            // Process user
            $user->processData();

            $bar->advance();
            usleep(10000); // Simulate work
        }

        $bar->finish();
        $this->newLine();
        $this->info('All users processed successfully!');

        return Command::SUCCESS;
    }
}
```

### 5. **Scheduled Command**

```php
<?php

namespace App\Console\Commands;

use App\Models\Backup;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Storage;

class BackupDatabase extends Command
{
    protected $signature = 'backup:database
                            {--compress : Compress the backup file}';

    protected $description = 'Create a database backup';

    public function handle(): int
    {
        $this->info('Starting database backup...');

        $filename = 'backup-' . now()->format('Y-m-d-H-i-s') . '.sql';

        // Execute backup
        $exitCode = $this->call('db:dump', [
            '--path' => storage_path('backups/' . $filename),
        ]);

        if ($exitCode !== 0) {
            $this->error('Backup failed!');
            return Command::FAILURE;
        }

        if ($this->option('compress')) {
            $this->info('Compressing backup...');
            // Compression logic
        }

        Backup::create([
            'filename' => $filename,
            'size' => Storage::size('backups/' . $filename),
            'compressed' => $this->option('compress'),
        ]);

        $this->info('Backup completed successfully!');

        return Command::SUCCESS;
    }
}
```

### 6. **Command Calling Other Commands**

```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

class DeployApplication extends Command
{
    protected $signature = 'app:deploy {--skip-tests}';
    protected $description = 'Deploy the application';

    public function handle(): int
    {
        $this->info('Starting deployment...');

        // Run tests unless skipped
        if (!$this->option('skip-tests')) {
            $this->call('test');
        }

        // Clear caches
        $this->call('cache:clear');
        $this->call('config:clear');
        $this->call('view:clear');

        // Optimize
        $this->call('optimize');

        // Run migrations
        if ($this->confirm('Run database migrations?')) {
            $this->call('migrate', ['--force' => true]);
        }

        $this->info('Deployment completed successfully!');

        return Command::SUCCESS;
    }
}
```

## Best Practices
- Use descriptive command signatures
- Provide helpful descriptions
- Use arguments for required data
- Use options for optional flags
- Provide user feedback with info/warn/error
- Use progress bars for long operations
- Return proper exit codes (SUCCESS/FAILURE)
- Handle errors gracefully
- Register in Console/Kernel.php (if not using auto-discovery)

Generate complete Laravel console command with proper structure.
