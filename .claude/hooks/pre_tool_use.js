#!/usr/bin/env node
/**
 * Pre-Tool Use Hook - JavaScript Version
 * Blocks dangerous operations in Laravel projects
 * Cross-platform compatible (Windows/Mac/Linux)
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Read JSON from stdin
let inputData = '';
process.stdin.on('data', chunk => inputData += chunk);

process.stdin.on('end', () => {
    try {
        const data = JSON.parse(inputData);
        const toolName = data.tool_name || '';
        const toolInput = data.tool_input || {};

        // === Security Check 1: Block .env file access ===
        if (isEnvFileAccess(toolName, toolInput)) {
            console.error('🚫 BLOCKED: Cannot access .env file containing sensitive credentials');
            console.error('Use .env.example for template files instead');
            process.exit(2); // Exit code 2 blocks the action
        }

        // === Security Check 2: Block dangerous artisan commands ===
        if (toolName === 'Bash') {
            const command = toolInput.command || '';

            // Block dangerous Laravel commands (cross-platform: php, php.bat, php.exe)
            const dangerousPatterns = [
                /php(?:\.bat|\.exe)?\s+artisan\s+db:wipe/i,
                /php(?:\.bat|\.exe)?\s+artisan\s+migrate:fresh.*--force/i,
                /php(?:\.bat|\.exe)?\s+artisan\s+migrate:reset.*--force/i,
                /rm\s+-rf\s+storage/i,
                /rm\s+-rf\s+vendor/i,
                /rm\s+-rf\s+\./i,
                /rm\s+-rf\s+\*/i,
                // Windows-specific delete commands
                /del\s+\/s\s+\/q\s+storage/i,
                /rmdir\s+\/s\s+\/q\s+storage/i,
                /rd\s+\/s\s+\/q\s+vendor/i,
            ];

            for (const pattern of dangerousPatterns) {
                if (pattern.test(command)) {
                    console.error('🚫 BLOCKED: Dangerous command detected');
                    console.error(`Command: ${command}`);
                    console.error('This operation could destroy data or your project');
                    process.exit(2); // Block the action
                }
            }
        }

        // === Security Check 3: Block editing critical Laravel files ===
        if (['Edit', 'Write'].includes(toolName)) {
            const filePath = toolInput.file_path || '';
            const criticalFiles = [
                /\.env$/,
                /config\/database\.php$/,
                /storage\/.*\.key$/,
                /\.git\/config$/,
            ];

            for (const pattern of criticalFiles) {
                if (pattern.test(filePath)) {
                    console.error('🚫 BLOCKED: Cannot modify critical file');
                    console.error(`File: ${filePath}`);
                    console.error('This file contains sensitive configuration');
                    process.exit(2); // Block the action
                }
            }
        }

        // === Log all tool uses ===
        const logDir = path.join(process.cwd(), 'logs');
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }

        const logFile = path.join(logDir, 'pre_tool_use.json');
        let logData = [];

        if (fs.existsSync(logFile)) {
            try {
                logData = JSON.parse(fs.readFileSync(logFile, 'utf8'));
            } catch (e) {
                logData = [];
            }
        }

        logData.push({
            ...data,
            timestamp: new Date().toISOString()
        });

        fs.writeFileSync(logFile, JSON.stringify(logData, null, 2));

        // All checks passed
        process.exit(0);

    } catch (error) {
        // Fail gracefully on any error
        process.exit(0);
    }
});

/**
 * Check if tool is trying to access .env files
 */
function isEnvFileAccess(toolName, toolInput) {
    if (['Read', 'Edit', 'Write'].includes(toolName)) {
        const filePath = toolInput.file_path || '';
        // Block .env but allow .env.example
        if (filePath.includes('.env') && !filePath.endsWith('.env.example')) {
            return true;
        }
    }

    if (toolName === 'Bash') {
        const command = toolInput.command || '';
        const envPatterns = [
            /cat\s+\.env\b(?!\.example)/i,
            /echo.*>\s*\.env\b(?!\.example)/i,
            /cp\s+\.env\b(?!\.example)/i,
            /mv\s+\.env\b(?!\.example)/i,
        ];

        return envPatterns.some(pattern => pattern.test(command));
    }

    return false;
}
