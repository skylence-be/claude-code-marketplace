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


def log_pre_compact(input_data):
    """Log pre-compact event to logs directory."""
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'pre_compact.json'

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


def backup_transcript(transcript_path, trigger):
    """Create a backup of the transcript before compaction."""
    try:
        if not os.path.exists(transcript_path):
            return

        # Create backup directory
        backup_dir = Path("logs") / "transcript_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate backup filename with timestamp and trigger type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = Path(transcript_path).stem
        backup_name = f"{session_name}_pre_compact_{trigger}_{timestamp}.jsonl"
        backup_path = backup_dir / backup_name

        # Copy transcript to backup
        import shutil
        shutil.copy2(transcript_path, backup_path)

        return str(backup_path)
    except Exception:
        return None


def save_context_snapshot(session_id):
    """
    Save a context snapshot before compaction so SessionStart can re-inject it.
    This is the key mechanism for surviving context loss after compaction.
    """
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
    }

    # Git state
    try:
        branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, timeout=5
        )
        if branch.returncode == 0:
            snapshot["git_branch"] = branch.stdout.strip()

        # Modified files in this session (staged + unstaged)
        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, timeout=5
        )
        if status.returncode == 0 and status.stdout.strip():
            files = [line[3:].strip() for line in status.stdout.strip().split('\n') if line.strip()]
            snapshot["modified_files"] = files[:30]  # Cap at 30

        # Recent commits (last 5)
        log = subprocess.run(
            ['git', 'log', '--oneline', '-5'],
            capture_output=True, text=True, timeout=5
        )
        if log.returncode == 0:
            snapshot["recent_commits"] = log.stdout.strip()
    except Exception:
        pass

    # Detect technology stack from project files
    stack = []
    if Path("composer.json").exists():
        try:
            with open("composer.json", 'r') as f:
                composer = json.load(f)
                require = composer.get("require", {})
                if "laravel/framework" in require:
                    stack.append("Laravel")
                if "livewire/livewire" in require:
                    stack.append("Livewire")
                if "filament/filament" in require:
                    stack.append("Filament")
        except Exception:
            stack.append("PHP")
    if Path("package.json").exists():
        try:
            with open("package.json", 'r') as f:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "vue" in deps or "nuxt" in deps:
                    stack.append("Vue/Nuxt")
                if "@angular/core" in deps:
                    stack.append("Angular")
                if "electron" in deps:
                    stack.append("Electron")
                if "typescript" in deps:
                    stack.append("TypeScript")
                if "tailwindcss" in deps:
                    stack.append("Tailwind")
        except Exception:
            pass
    if Path("pubspec.yaml").exists():
        stack.append("Flutter")
    if stack:
        snapshot["tech_stack"] = stack

    # Load top learnings
    learnings_path = Path('.claude/data/learnings.json')
    if learnings_path.exists():
        try:
            with open(learnings_path, 'r') as f:
                learnings = json.load(f)
            project = os.path.basename(os.getcwd())
            project_learnings = [
                l for l in learnings
                if l.get('project', '').lower() == project.lower()
            ]
            if not project_learnings:
                project_learnings = learnings
            project_learnings.sort(
                key=lambda l: (l.get('times_applied', 0), l.get('date', '')),
                reverse=True
            )
            top = project_learnings[:10]
            if top:
                snapshot["learnings"] = [
                    f"[{l.get('category', 'General')}] {l.get('rule', '')}"
                    for l in top
                ]
        except Exception:
            pass

    # Load session data (edit count, agent name, etc.)
    session_dir = Path('.claude/data/sessions')
    session_file = session_dir / f"{session_id}.json"
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            snapshot["edit_count"] = session_data.get("edit_count", 0)
            snapshot["response_count"] = session_data.get("response_count", 0)
            snapshot["agent_name"] = session_data.get("agent_name", "")
            # Save the last few prompts for task continuity
            prompts = session_data.get("prompts", [])
            if prompts:
                snapshot["recent_prompts"] = prompts[-3:]  # Last 3 prompts
        except Exception:
            pass

    # Write snapshot to a known location for SessionStart to pick up
    snapshot_dir = Path('.claude/data')
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / 'pre_compact_snapshot.json'
    try:
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot, f, indent=2)
    except Exception:
        pass

    return snapshot


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--backup', action='store_true',
                          help='Create backup of transcript before compaction')
        parser.add_argument('--save-context', action='store_true',
                          help='Save context snapshot for post-compaction recovery')
        parser.add_argument('--verbose', action='store_true',
                          help='Print verbose output')
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Extract fields
        session_id = input_data.get('session_id', 'unknown')
        transcript_path = input_data.get('transcript_path', '')
        trigger = input_data.get('trigger', 'unknown')  # "manual" or "auto"
        custom_instructions = input_data.get('custom_instructions', '')

        # Log the pre-compact event
        log_pre_compact(input_data)

        # Create backup if requested
        backup_path = None
        if args.backup and transcript_path:
            backup_path = backup_transcript(transcript_path, trigger)

        # Save context snapshot for post-compaction recovery
        snapshot = None
        if args.save_context:
            snapshot = save_context_snapshot(session_id)

        # Provide feedback based on trigger type
        if args.verbose:
            if trigger == "manual":
                message = f"Preparing for manual compaction (session: {session_id[:8]}...)"
                if custom_instructions:
                    message += f"\nCustom instructions: {custom_instructions[:100]}..."
            else:  # auto
                message = f"Auto-compaction triggered due to full context window (session: {session_id[:8]}...)"

            if backup_path:
                message += f"\nTranscript backed up to: {backup_path}"

            if snapshot:
                message += f"\nContext snapshot saved for post-compaction recovery"

            print(message)

        # Success - compaction will proceed
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()
