#!/usr/bin/env php
<?php
/**
 * Session Start Hook - PHP Version
 * Displays Laravel project context when Claude Code starts
 * Cross-platform compatible (Windows/Mac/Linux)
 */

// Read JSON input from stdin
$input = json_decode(file_get_contents('php://stdin'), true);

// Extract session info
$sessionId = $input['session_id'] ?? 'unknown';
$source = $input['source'] ?? 'unknown'; // "startup", "resume", or "clear"

/**
 * Detect PHP command based on platform
 */
function getPhpCommand() {
    // Check if we're on Windows
    $isWindows = strtoupper(substr(PHP_OS, 0, 3)) === 'WIN';

    if ($isWindows) {
        // Try php.bat first, then php.exe, then just php
        exec('where php.bat 2>nul', $output, $code);
        if ($code === 0 && !empty($output)) return 'php.bat';

        exec('where php.exe 2>nul', $output, $code);
        if ($code === 0 && !empty($output)) return 'php.exe';
    }

    // Default to 'php' for Unix-like systems or if Windows check fails
    return 'php';
}

// Detect PHP command
$phpCmd = getPhpCommand();

// Build context message
$context = [];
$context[] = "=== Laravel Project Context ===";
$context[] = "Session: " . substr($sessionId, 0, 8) . "...";
$context[] = "Source: {$source}";
$context[] = "Platform: " . PHP_OS . " (using: {$phpCmd})";

// Check Laravel version from composer.lock
if (file_exists('composer.lock')) {
    $composerLock = json_decode(file_get_contents('composer.lock'), true);
    foreach ($composerLock['packages'] ?? [] as $package) {
        if ($package['name'] === 'laravel/framework') {
            $context[] = "Laravel: {$package['version']}";
            break;
        }
    }
}

// Check git branch
exec('git rev-parse --abbrev-ref HEAD 2>&1', $branchOutput, $branchCode);
if ($branchCode === 0 && !empty($branchOutput[0])) {
    $context[] = "Branch: " . trim($branchOutput[0]);
}

// Check for uncommitted changes
exec('git status --porcelain 2>&1', $statusOutput, $statusCode);
if ($statusCode === 0) {
    $changes = array_filter($statusOutput);
    if (count($changes) > 0) {
        $context[] = "⚠️  Uncommitted changes: " . count($changes) . " files";
    }
}

// Check for pending migrations
exec("{$phpCmd} artisan migrate:status 2>&1", $migrateOutput, $migrateCode);
if ($migrateCode === 0) {
    $pending = 0;
    foreach ($migrateOutput as $line) {
        if (str_contains($line, 'Pending')) {
            $pending++;
        }
    }
    if ($pending > 0) {
        $context[] = "⚠️  Pending migrations: {$pending}";
    }
}

// Check .env file (just check if it exists, don't read it)
if (!file_exists('.env')) {
    $context[] = "⚠️  No .env file found!";
} else {
    // Check environment from .env
    $envLines = file('.env', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($envLines as $line) {
        if (strpos(trim($line), 'APP_ENV=') === 0) {
            $env = trim(str_replace('APP_ENV=', '', $line));
            $context[] = "Environment: {$env}";
            break;
        }
    }
}

// Check if there are failed jobs (if using database queue)
if (file_exists('database/database.sqlite') || (file_exists('.env') && str_contains(file_get_contents('.env'), 'DB_CONNECTION'))) {
    exec("{$phpCmd} artisan queue:failed 2>&1", $queueOutput, $queueCode);
    if ($queueCode === 0 && count($queueOutput) > 0) {
        // Count lines that look like job entries (skip headers)
        $failedCount = max(0, count($queueOutput) - 2);
        if ($failedCount > 0) {
            $context[] = "⚠️  Failed queue jobs: {$failedCount}";
        }
    }
}

$context[] = "================================";

// Output context
echo implode("\n", $context) . "\n";

// Create logs directory and log this session start
if (!is_dir('logs')) {
    mkdir('logs', 0755, true);
}

$logFile = 'logs/session_start.json';
$logData = [];
if (file_exists($logFile)) {
    $logData = json_decode(file_get_contents($logFile), true) ?? [];
}
$logData[] = array_merge($input, ['timestamp' => date('Y-m-d H:i:s')]);
file_put_contents($logFile, json_encode($logData, JSON_PRETTY_PRINT));

exit(0);
