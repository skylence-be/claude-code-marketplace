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
import re
import sys
import tempfile
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def log_user_prompt(session_id, input_data):
    """Log user prompt to logs directory."""
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'user_prompt_submit.json'

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


# Legacy function removed - now handled by manage_session_data


def manage_session_data(session_id, prompt, name_agent=False):
    """Manage session data in the new JSON structure."""
    import subprocess

    # Ensure sessions directory exists
    sessions_dir = Path(".claude/data/sessions")
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Load or create session file
    session_file = sessions_dir / f"{session_id}.json"

    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            session_data = {"session_id": session_id, "prompts": []}
    else:
        session_data = {"session_id": session_id, "prompts": []}

    # Add the new prompt
    session_data["prompts"].append(prompt)

    # Generate agent name if requested and not already present
    if name_agent and "agent_name" not in session_data:
        # Try Ollama first (preferred)
        try:
            result = subprocess.run(
                ["uv", "run", ".claude/hooks/utils/llm/ollama.py", "--agent-name"],
                capture_output=True,
                text=True,
                timeout=5  # Shorter timeout for local Ollama
            )

            if result.returncode == 0 and result.stdout.strip():
                agent_name = result.stdout.strip()
                # Check if it's a valid name (not an error message)
                if len(agent_name.split()) == 1 and agent_name.isalnum():
                    session_data["agent_name"] = agent_name
                else:
                    raise Exception("Invalid name from Ollama")
        except Exception:
            # Fall back to Anthropic if Ollama fails
            try:
                result = subprocess.run(
                    ["uv", "run", ".claude/hooks/utils/llm/anth.py", "--agent-name"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 and result.stdout.strip():
                    agent_name = result.stdout.strip()
                    # Validate the name
                    if len(agent_name.split()) == 1 and agent_name.isalnum():
                        session_data["agent_name"] = agent_name
            except Exception:
                # If both fail, don't block the prompt
                pass

    # Save the updated session data
    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    except Exception:
        # Silently fail if we can't write the file
        pass


def validate_prompt(prompt):
    """
    Validate the user prompt for security or policy violations.
    Returns tuple (is_valid, reason).
    """
    # Example validation rules (customize as needed)
    blocked_patterns = [
        # Add any patterns you want to block
        # Example: ('rm -rf /', 'Dangerous command detected'),
    ]

    prompt_lower = prompt.lower()

    for pattern, reason in blocked_patterns:
        if pattern.lower() in prompt_lower:
            return False, reason

    return True, None


def detect_corrections(prompt, session_id):
    """
    Detect correction language in user prompts (e.g., 'wrong', 'undo', 'wait', 'actually').
    Tracks correction count in session data.
    """
    correction_patterns = [
        r'\b(wrong|incorrect|mistake|messed up)\b',
        r'\b(undo|revert|rollback|go back)\b',
        r'\b(wait|stop|hold on|no no)\b',
        r'\b(actually|instead|rather|not what i)\b',
        r'\b(that\'s not|that was not|that isn\'t)\b',
        r'\b(fix that|fix this|redo|try again)\b',
    ]

    prompt_lower = prompt.lower()
    is_correction = any(re.search(p, prompt_lower) for p in correction_patterns)

    if not is_correction:
        return

    # Track correction count in session data
    sessions_dir = Path('.claude/data/sessions')
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session_file = sessions_dir / f"{session_id}.json"

    session_data = {}
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            session_data = {}

    corrections_count = session_data.get('corrections_count', 0) + 1
    session_data['corrections_count'] = corrections_count

    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    except OSError:
        pass

    print(f"[pro-workflow] Correction detected (#{corrections_count} this session). Consider capturing with: [LEARN] Category: Rule", file=sys.stderr)


def detect_drift(prompt, session_id):
    """
    Track original intent keywords from first prompt. After 6+ edits,
    warn if the current prompt's relevance to original intent drops below 20%.
    Uses simple keyword overlap as a heuristic.
    """
    # Use temp directory for ephemeral drift state
    drift_dir = Path(tempfile.gettempdir()) / 'pro-workflow'
    drift_dir.mkdir(parents=True, exist_ok=True)
    drift_file = drift_dir / f'intent-{session_id}.json'

    drift_data = {}
    if drift_file.exists():
        try:
            with open(drift_file, 'r') as f:
                drift_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            drift_data = {}

    # Extract meaningful words (skip common stop words)
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'and', 'but', 'or',
        'nor', 'not', 'so', 'yet', 'both', 'either', 'neither', 'each',
        'every', 'all', 'any', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'only', 'own', 'same', 'than', 'too', 'very',
        'just', 'because', 'if', 'when', 'where', 'how', 'what', 'which',
        'who', 'whom', 'this', 'that', 'these', 'those', 'i', 'me', 'my',
        'we', 'us', 'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her',
        'it', 'its', 'they', 'them', 'their', 'please', 'thanks', 'thank',
    }

    def extract_keywords(text):
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        return set(w for w in words if w not in stop_words)

    current_keywords = extract_keywords(prompt)

    if 'original_keywords' not in drift_data:
        # First prompt — store as original intent
        drift_data['original_keywords'] = list(current_keywords)
        drift_data['prompt_count'] = 1
    else:
        drift_data['prompt_count'] = drift_data.get('prompt_count', 0) + 1

    try:
        with open(drift_file, 'w') as f:
            json.dump(drift_data, f, indent=2)
    except OSError:
        pass

    # Only check for drift after 6+ prompts
    if drift_data.get('prompt_count', 0) < 6:
        return

    # Also check edit count from session data
    sessions_dir = Path('.claude/data/sessions')
    session_file = sessions_dir / f"{session_id}.json"
    edit_count = 0
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                sd = json.load(f)
                edit_count = sd.get('edit_count', 0)
        except (json.JSONDecodeError, ValueError, OSError):
            pass

    if edit_count < 6:
        return

    # Calculate relevance
    original_keywords = set(drift_data.get('original_keywords', []))
    if not original_keywords or not current_keywords:
        return

    overlap = original_keywords & current_keywords
    relevance = len(overlap) / len(original_keywords) * 100

    if relevance < 20:
        print(f"[pro-workflow] Drift detected: current prompt has {relevance:.0f}% relevance to original intent.", file=sys.stderr)
        print(f"[pro-workflow] Original keywords: {', '.join(sorted(list(original_keywords)[:8]))}", file=sys.stderr)
        print(f"[pro-workflow] Consider refocusing or starting a new session.", file=sys.stderr)


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--validate', action='store_true',
                          help='Enable prompt validation')
        parser.add_argument('--log-only', action='store_true',
                          help='Only log prompts, no validation or blocking')
        parser.add_argument('--store-last-prompt', action='store_true',
                          help='Store the last prompt for status line display')
        parser.add_argument('--name-agent', action='store_true',
                          help='Generate an agent name for the session')
        parser.add_argument('--detect-corrections', action='store_true',
                          help='Detect correction language in prompts')
        parser.add_argument('--detect-drift', action='store_true',
                          help='Detect drift from original intent')
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Extract session_id and prompt
        session_id = input_data.get('session_id', 'unknown')
        prompt = input_data.get('prompt', '')

        # Log the user prompt
        log_user_prompt(session_id, input_data)

        # Manage session data with JSON structure
        if args.store_last_prompt or args.name_agent:
            manage_session_data(session_id, prompt, name_agent=args.name_agent)

        # Validate prompt if requested and not in log-only mode
        if args.validate and not args.log_only:
            is_valid, reason = validate_prompt(prompt)
            if not is_valid:
                # Exit code 2 blocks the prompt with error message
                print(f"Prompt blocked: {reason}", file=sys.stderr)
                sys.exit(2)

        # Detect correction language
        if args.detect_corrections:
            try:
                detect_corrections(prompt, session_id)
            except Exception:
                pass  # Never block on detection failure

        # Detect drift from original intent
        if args.detect_drift:
            try:
                detect_drift(prompt, session_id)
            except Exception:
                pass  # Never block on detection failure

        # Add context information (optional)
        # You can print additional context that will be added to the prompt
        # Example: print(f"Current time: {datetime.now()}")

        # Success - prompt will be processed
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()
