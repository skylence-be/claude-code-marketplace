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
import random
import subprocess
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def get_completion_messages():
    """Return list of friendly completion messages."""
    return [
        "Work complete!",
        "All done!",
        "Task finished!",
        "Job complete!",
        "Ready for next task!"
    ]


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"

    # Check for ElevenLabs API key (highest priority)
    if os.getenv('ELEVENLABS_API_KEY'):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)

    # Check for OpenAI API key (second priority)
    if os.getenv('OPENAI_API_KEY'):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)

    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return str(pyttsx3_script)

    return None


def get_llm_completion_message():
    """
    Generate completion message using available LLM services.
    Priority order: OpenAI > Anthropic > Ollama > fallback to random message

    Returns:
        str: Generated or fallback completion message
    """
    # Get current script directory and construct utils/llm path
    script_dir = Path(__file__).parent
    llm_dir = script_dir / "utils" / "llm"

    # Try OpenAI first (highest priority)
    if os.getenv('OPENAI_API_KEY'):
        oai_script = llm_dir / "oai.py"
        if oai_script.exists():
            try:
                result = subprocess.run([
                    "uv", "run", str(oai_script), "--completion"
                ],
                capture_output=True,
                text=True,
                timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Anthropic second
    if os.getenv('ANTHROPIC_API_KEY'):
        anth_script = llm_dir / "anth.py"
        if anth_script.exists():
            try:
                result = subprocess.run([
                    "uv", "run", str(anth_script), "--completion"
                ],
                capture_output=True,
                text=True,
                timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Ollama third (local LLM)
    ollama_script = llm_dir / "ollama.py"
    if ollama_script.exists():
        try:
            result = subprocess.run([
                "uv", "run", str(ollama_script), "--completion"
            ],
            capture_output=True,
            text=True,
            timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

    # Fallback to random predefined message
    messages = get_completion_messages()
    return random.choice(messages)

def announce_completion():
    """Announce completion using the best available TTS service."""
    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            return  # No TTS scripts available

        # Get completion message (LLM-generated or fallback)
        completion_message = get_llm_completion_message()

        # Call the TTS script with the completion message
        subprocess.run([
            "uv", "run", tts_script, completion_message
        ],
        capture_output=True,  # Suppress output
        timeout=10  # 10-second timeout
        )

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # Fail silently if TTS encounters issues
        pass
    except Exception:
        # Fail silently for any other errors
        pass


def capture_learnings(input_data):
    """
    Parse [LEARN] blocks from the response and append to learnings.json.
    Format: [LEARN] Category: Rule text
    Optional follow-up lines: Mistake: ..., Correction: ...
    """
    # Get the transcript to find recent response content
    transcript_path = input_data.get('transcript_path', '')
    if not transcript_path or not os.path.exists(transcript_path):
        return

    # Read the last few lines of the transcript to find [LEARN] blocks
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()

        # Look through the last 50 lines for [LEARN] blocks
        recent_text = ''
        for line in lines[-50:]:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    # Look in assistant messages
                    if entry.get('type') == 'assistant':
                        content = entry.get('message', {}).get('content', '')
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get('type') == 'text':
                                    recent_text += block.get('text', '') + '\n'
                        elif isinstance(content, str):
                            recent_text += content + '\n'
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass

    except (OSError, UnicodeDecodeError):
        return

    if not recent_text:
        return

    # Parse [LEARN] blocks
    learn_pattern = r'\[LEARN\]\s*(\w[\w-]*):\s*(.+?)(?:\n|$)'
    matches = re.findall(learn_pattern, recent_text)

    if not matches:
        return

    # Load existing learnings
    learnings_path = Path('.claude/data/learnings.json')
    learnings_path.parent.mkdir(parents=True, exist_ok=True)

    learnings = []
    if learnings_path.exists():
        try:
            with open(learnings_path, 'r') as f:
                learnings = json.load(f)
        except (json.JSONDecodeError, ValueError):
            learnings = []

    project = os.path.basename(os.getcwd())
    new_count = 0

    for category, rule in matches:
        # Check for duplicate rules
        rule = rule.strip()
        is_duplicate = any(
            l.get('rule', '').strip().lower() == rule.lower() and
            l.get('category', '').lower() == category.lower()
            for l in learnings
        )
        if is_duplicate:
            # Increment times_applied for existing rule
            for l in learnings:
                if (l.get('rule', '').strip().lower() == rule.lower() and
                    l.get('category', '').lower() == category.lower()):
                    l['times_applied'] = l.get('times_applied', 0) + 1
                    break
            continue

        # Look for optional Mistake/Correction lines following the [LEARN] tag
        mistake = ''
        correction = ''
        learn_idx = recent_text.find(f'[LEARN] {category}: {rule}')
        if learn_idx >= 0:
            after = recent_text[learn_idx + len(f'[LEARN] {category}: {rule}'):]
            mistake_match = re.search(r'Mistake:\s*(.+?)(?:\n|$)', after[:200])
            correction_match = re.search(r'Correction:\s*(.+?)(?:\n|$)', after[:200])
            if mistake_match:
                mistake = mistake_match.group(1).strip()
            if correction_match:
                correction = correction_match.group(1).strip()

        learnings.append({
            'date': datetime.now().isoformat(),
            'project': project,
            'category': category,
            'rule': rule,
            'mistake': mistake,
            'correction': correction,
            'times_applied': 0
        })
        new_count += 1

    if new_count > 0 or any(True for _ in matches):
        try:
            with open(learnings_path, 'w') as f:
                json.dump(learnings, f, indent=2)
            if new_count > 0:
                print(f"[pro-workflow] Captured {new_count} new learning(s) from [LEARN] tags.", file=sys.stderr)
        except OSError:
            pass


def check_session_reminder(input_data):
    """
    Track response count per session. Remind to wrap up every 20 responses.
    """
    session_id = input_data.get('session_id', 'unknown')

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

    response_count = session_data.get('response_count', 0) + 1
    session_data['response_count'] = response_count

    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    except OSError:
        pass

    if response_count > 0 and response_count % 20 == 0:
        print(f"[pro-workflow] {response_count} responses this session. Consider running /pro-workflow:wrap-up to capture learnings.", file=sys.stderr)


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--chat', action='store_true', help='Copy transcript to chat.json')
        parser.add_argument('--notify', action='store_true', help='Enable TTS completion announcement')
        parser.add_argument('--learn-capture', action='store_true',
                          help='Parse [LEARN] blocks from responses and save to learnings.json')
        parser.add_argument('--session-check', action='store_true',
                          help='Periodic wrap-up reminders every 20 responses')
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Extract required fields
        session_id = input_data.get("session_id", "")
        stop_hook_active = input_data.get("stop_hook_active", False)

        # Ensure log directory exists
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "stop.json")

        # Read existing log data or initialize empty list
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Append new data
        log_data.append(input_data)

        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        # Handle --chat switch
        if args.chat and 'transcript_path' in input_data:
            transcript_path = input_data['transcript_path']
            if os.path.exists(transcript_path):
                # Read .jsonl file and convert to JSON array
                chat_data = []
                try:
                    with open(transcript_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    chat_data.append(json.loads(line))
                                except json.JSONDecodeError:
                                    pass  # Skip invalid lines

                    # Write to logs/chat.json
                    chat_file = os.path.join(log_dir, 'chat.json')
                    with open(chat_file, 'w') as f:
                        json.dump(chat_data, f, indent=2)
                except Exception:
                    pass  # Fail silently

        # Capture learnings from [LEARN] tags
        if args.learn_capture:
            try:
                capture_learnings(input_data)
            except Exception:
                pass  # Never block on learning capture failure

        # Session check — periodic wrap-up reminders
        if args.session_check:
            try:
                check_session_reminder(input_data)
            except Exception:
                pass  # Never block on session check failure

        # Announce completion via TTS (only if --notify flag is set)
        if args.notify:
            announce_completion()

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
