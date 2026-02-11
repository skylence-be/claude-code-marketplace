#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

"""
PostToolUse hook: Scans edited files for debug statements, TODO/FIXME,
and hardcoded secrets. Outputs warnings to stderr (non-blocking).
"""

import json
import re
import sys
from pathlib import Path


# Debug statement patterns by language
DEBUG_PATTERNS = [
    # JavaScript / TypeScript
    (r'\bconsole\.(log|debug|info|warn|error|trace|dir)\s*\(', 'console.log statement'),
    (r'\bdebugger\b', 'debugger statement'),
    (r'\balert\s*\(', 'alert() call'),
    # PHP
    (r'\bdd\s*\(', 'dd() call'),
    (r'\bdump\s*\(', 'dump() call'),
    (r'\bvar_dump\s*\(', 'var_dump() call'),
    (r'\bprint_r\s*\(', 'print_r() call'),
    (r'\bray\s*\(', 'ray() call'),
    # Python
    (r'(?<![.\w])print\s*\(', 'print() statement'),
    (r'\bbreakpoint\s*\(', 'breakpoint() call'),
    (r'\bpdb\.set_trace\s*\(', 'pdb.set_trace() call'),
    (r'\bipdb\.set_trace\s*\(', 'ipdb.set_trace() call'),
    # Dart / Flutter
    (r'\bdebugPrint\s*\(', 'debugPrint() call'),
]

# TODO/FIXME patterns (without ticket references)
TODO_PATTERNS = [
    (r'\b(TODO|FIXME|HACK|XXX)\b(?!\s*[\(#\[])', 'TODO/FIXME without ticket reference'),
]

# Potential hardcoded secrets
SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|api[_-]?secret|auth[_-]?token|access[_-]?token|secret[_-]?key|private[_-]?key)\s*[=:]\s*["\'][^"\']{8,}', 'potential hardcoded secret'),
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}', 'potential hardcoded password'),
    (r'(?:sk|pk)[-_](?:live|test)[-_][a-zA-Z0-9]{20,}', 'potential API key (Stripe-like pattern)'),
    (r'ghp_[a-zA-Z0-9]{36}', 'potential GitHub personal access token'),
    (r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----', 'private key in source code'),
]

# File extensions to check (skip binaries, images, etc.)
CHECKABLE_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
    '.py', '.pyw',
    '.php', '.blade.php',
    '.dart',
    '.rb',
    '.go',
    '.rs',
    '.java', '.kt', '.kts',
    '.vue', '.svelte',
    '.css', '.scss', '.less',
    '.html', '.htm',
    '.json', '.yaml', '.yml', '.toml',
    '.sh', '.bash', '.zsh',
    '.md',
}


def should_check_file(file_path):
    """Determine if a file should be scanned based on extension."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    # Handle .blade.php
    if file_path.endswith('.blade.php'):
        return True

    return suffix in CHECKABLE_EXTENSIONS


def scan_content(content, file_path):
    """Scan file content for issues. Returns list of (line_num, issue) tuples."""
    issues = []
    lines = content.split('\n')

    # Determine which patterns to use based on file extension
    suffix = Path(file_path).suffix.lower()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip comments that are clearly documentation
        if stripped.startswith('//') or stripped.startswith('#') or stripped.startswith('*'):
            # Still check for secrets in comments
            for pattern, desc in SECRET_PATTERNS:
                if re.search(pattern, line):
                    issues.append((i, f'WARNING: {desc}'))
            continue

        # Check debug patterns
        for pattern, desc in DEBUG_PATTERNS:
            if re.search(pattern, line):
                issues.append((i, f'Debug: {desc}'))
                break  # One match per line is enough

        # Check TODO/FIXME patterns
        for pattern, desc in TODO_PATTERNS:
            if re.search(pattern, line):
                issues.append((i, desc))
                break

        # Check secret patterns
        for pattern, desc in SECRET_PATTERNS:
            if re.search(pattern, line):
                issues.append((i, f'SECURITY: {desc}'))
                break

    return issues


def main():
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        # Only check after Edit, Write, or MultiEdit tools
        if tool_name not in ('Edit', 'Write', 'MultiEdit'):
            sys.exit(0)

        file_path = tool_input.get('file_path', '')
        if not file_path:
            sys.exit(0)

        if not should_check_file(file_path):
            sys.exit(0)

        # Read the file content to scan
        try:
            path = Path(file_path)
            if not path.exists():
                sys.exit(0)
            content = path.read_text(encoding='utf-8', errors='ignore')
        except (OSError, UnicodeDecodeError):
            sys.exit(0)

        issues = scan_content(content, file_path)

        if issues:
            filename = Path(file_path).name
            print(f"[pro-workflow] Post-edit scan of {filename}:", file=sys.stderr)
            for line_num, issue in issues[:10]:  # Cap at 10 issues
                print(f"  line {line_num}: {issue}", file=sys.stderr)
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more issues", file=sys.stderr)

        # Always exit 0 — warnings only, never block
        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == '__main__':
    main()
