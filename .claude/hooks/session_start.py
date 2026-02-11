#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def log_session_start(input_data):
    """Log session start event to logs directory."""
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'session_start.json'

    # Read existing log data or initialize empty list
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    # Append the entire input data
    log_data.append(input_data)

    # Write back to file with formatting
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def get_git_status():
    """Get current git status information."""
    try:
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        # Get uncommitted changes count
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if status_result.returncode == 0:
            changes = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
            uncommitted_count = len(changes)
        else:
            uncommitted_count = 0

        return current_branch, uncommitted_count
    except Exception:
        return None, None


def get_recent_issues():
    """Get recent GitHub issues if gh CLI is available."""
    try:
        # Check if gh is available
        gh_check = subprocess.run(['which', 'gh'], capture_output=True)
        if gh_check.returncode != 0:
            return None

        # Get recent open issues
        result = subprocess.run(
            ['gh', 'issue', 'list', '--limit', '5', '--state', 'open'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def load_development_context(source):
    """Load relevant development context based on session source."""
    context_parts = []

    # Add timestamp
    context_parts.append(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    context_parts.append(f"Session source: {source}")

    # Add git information
    branch, changes = get_git_status()
    if branch:
        context_parts.append(f"Git branch: {branch}")
        if changes > 0:
            context_parts.append(f"Uncommitted changes: {changes} files")

    # Load project-specific context files if they exist
    context_files = [
        ".claude/CONTEXT.md",
        ".claude/TODO.md",
        "TODO.md",
        ".github/ISSUE_TEMPLATE.md"
    ]

    for file_path in context_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        context_parts.append(f"\n--- Content from {file_path} ---")
                        context_parts.append(content[:1000])  # Limit to first 1000 chars
            except Exception:
                pass

    # Add recent issues if available
    issues = get_recent_issues()
    if issues:
        context_parts.append("\n--- Recent GitHub Issues ---")
        context_parts.append(issues)

    return "\n".join(context_parts)


def load_learnings():
    """
    Load recent project-scoped learnings from .claude/data/learnings.json
    and display them as session context.
    """
    learnings_path = Path('.claude/data/learnings.json')
    if not learnings_path.exists():
        return None

    try:
        with open(learnings_path, 'r') as f:
            learnings = json.load(f)
    except (json.JSONDecodeError, ValueError, OSError):
        return None

    if not learnings:
        return None

    project = os.path.basename(os.getcwd())

    # Filter to current project learnings, sorted by most applied + most recent
    project_learnings = [
        l for l in learnings
        if l.get('project', '').lower() == project.lower()
    ]

    if not project_learnings:
        # Fall back to all learnings if none for this project
        project_learnings = learnings

    # Sort: most applied first, then most recent
    project_learnings.sort(
        key=lambda l: (l.get('times_applied', 0), l.get('date', '')),
        reverse=True
    )

    # Take the top 10 most relevant
    top_learnings = project_learnings[:10]

    if not top_learnings:
        return None

    lines = [f"[pro-workflow] {len(top_learnings)} learnings loaded for this project:"]
    for l in top_learnings:
        category = l.get('category', 'General')
        rule = l.get('rule', '')
        times = l.get('times_applied', 0)
        suffix = f" (applied {times}x)" if times > 0 else ""
        lines.append(f"  [{category}] {rule}{suffix}")

    return "\n".join(lines)


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--load-context', action='store_true',
                          help='Load development context at session start')
        parser.add_argument('--announce', action='store_true',
                          help='Announce session start via TTS')
        parser.add_argument('--load-learnings', action='store_true',
                          help='Load recent learnings from .claude/data/learnings.json')
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Extract fields
        session_id = input_data.get('session_id', 'unknown')
        source = input_data.get('source', 'unknown')  # "startup", "resume", or "clear"

        # Log the session start event
        log_session_start(input_data)

        # Collect context parts
        context_parts = []

        # Load development context if requested
        if args.load_context:
            context = load_development_context(source)
            if context:
                context_parts.append(context)

        # Load learnings if requested
        if args.load_learnings:
            try:
                learnings_context = load_learnings()
                if learnings_context:
                    context_parts.append(learnings_context)
            except Exception:
                pass  # Never block session start on learning load failure

        # Output combined context
        if context_parts:
            combined_context = "\n\n".join(context_parts)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": combined_context
                }
            }
            print(json.dumps(output))
            sys.exit(0)

        # Announce session start if requested
        if args.announce:
            try:
                # Try to use TTS to announce session start
                script_dir = Path(__file__).parent
                tts_script = script_dir / "utils" / "tts" / "pyttsx3_tts.py"

                if tts_script.exists():
                    messages = {
                        "startup": "Claude Code session started",
                        "resume": "Resuming previous session",
                        "clear": "Starting fresh session"
                    }
                    message = messages.get(source, "Session started")

                    subprocess.run(
                        ["uv", "run", str(tts_script), message],
                        capture_output=True,
                        timeout=5
                    )
            except Exception:
                pass

        # Success
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()
