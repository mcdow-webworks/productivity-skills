#!/usr/bin/env python3
"""
Fast note capture using Claude Haiku 4.5 for category inference.
Part of productivity-skills/note-taking

Usage: python quick_note.py "your note content"
"""

import json
import os
import sys
import subprocess
from pathlib import Path

try:
    from anthropic import Anthropic
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Configuration
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 30
TIMEOUT = 2.0  # seconds
MAX_RETRIES = 1
MAX_INPUT_LENGTH = 1000

VALID_CATEGORIES = ["Work", "Learning", "Meeting", "Idea", "Decision", "Question", "Reference", "Note"]
DEFAULT_CATEGORY = "Note"

SYSTEM_PROMPT = """You are a note categorizer. Given a note, return ONLY the category name.

Categories: Work, Learning, Meeting, Idea, Decision, Question, Reference, Note

Rules:
- Work: tasks, bugs, implementations, deployments, fixing things
- Meeting: calls, discussions, people mentioned by name
- Learning: discoveries, tutorials, TILs, "learned", "realized"
- Idea: "what if", brainstorms, future possibilities
- Decision: "will", "decided", commitments, plans
- Question: uncertainties, "how to", investigations
- Reference: bookmarks, links, documentation, records
- Note: general observations (default)

Return ONLY the category name, nothing else."""


def infer_category(note_text: str) -> tuple:
    """
    Infer category from note text using Claude Haiku 4.5.

    Returns:
        tuple: (category: str, api_success: bool)
    """
    if not ANTHROPIC_AVAILABLE:
        return DEFAULT_CATEGORY, False

    if not os.environ.get("ANTHROPIC_API_KEY"):
        return DEFAULT_CATEGORY, False

    try:
        client = Anthropic(timeout=TIMEOUT, max_retries=MAX_RETRIES)
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=0.0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": note_text[:MAX_INPUT_LENGTH]}]
        )
        category = response.content[0].text.strip()

        # Validate category
        if category in VALID_CATEGORIES:
            return category, True

        # Try to extract category if response contains extra text
        for valid_cat in VALID_CATEGORIES:
            if valid_cat.lower() in category.lower():
                return valid_cat, True

        return DEFAULT_CATEGORY, True  # API worked but invalid category

    except anthropic.APITimeoutError:
        return DEFAULT_CATEGORY, False
    except anthropic.APIConnectionError:
        return DEFAULT_CATEGORY, False
    except anthropic.AuthenticationError:
        print("Error: Invalid ANTHROPIC_API_KEY", file=sys.stderr)
        return DEFAULT_CATEGORY, False
    except anthropic.APIError as e:
        print(f"Warning: API error - {e}", file=sys.stderr)
        return DEFAULT_CATEGORY, False
    except Exception as e:
        print(f"Warning: Unexpected error - {e}", file=sys.stderr)
        return DEFAULT_CATEGORY, False


def add_note(category: str, content: str) -> dict:
    """
    Add note using notes_manager.py.

    Args:
        category: The note category (Work, Learning, etc.)
        content: The full note content

    Returns:
        dict: Result from notes_manager.py
    """
    script_dir = Path(__file__).parent
    notes_manager = script_dir / "notes_manager.py"

    if not notes_manager.exists():
        return {"status": "error", "message": f"notes_manager.py not found at {notes_manager}"}

    # Format heading as "Category - Brief description"
    # Extract first ~50 chars as description, clean up newlines
    description = content[:50].replace('\n', ' ').replace('\r', '').strip()
    if len(content) > 50:
        description += "..."
    heading = f"{category} - {description}"

    cmd_input = json.dumps({
        "command": "add",
        "heading": heading,
        "content": content
    })

    try:
        result = subprocess.run(
            ["python", str(notes_manager)],
            input=cmd_input,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"status": "error", "message": f"Invalid JSON from notes_manager: {result.stdout}"}
        return {"status": "error", "message": result.stderr or "Unknown error from notes_manager"}

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "notes_manager.py timed out"}
    except FileNotFoundError:
        return {"status": "error", "message": "Python not found in PATH"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    """Main entry point for quick note capture."""

    # Validate input
    if len(sys.argv) < 2:
        print("Usage: quick_note.py <note content>", file=sys.stderr)
        print("\nExample: quick_note.py meeting with Jim about pricing", file=sys.stderr)
        sys.exit(1)

    note_text = " ".join(sys.argv[1:])

    if not note_text.strip():
        print("Error: Note content required", file=sys.stderr)
        sys.exit(1)

    if len(note_text) > MAX_INPUT_LENGTH:
        print(f"Error: Note too long ({len(note_text)} chars, max {MAX_INPUT_LENGTH})", file=sys.stderr)
        sys.exit(1)

    # Check dependencies
    if not ANTHROPIC_AVAILABLE:
        print("Error: anthropic package not installed", file=sys.stderr)
        print("Run: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        print("Get your key at https://console.anthropic.com", file=sys.stderr)
        print("\nSet it with:", file=sys.stderr)
        print("  Windows: $env:ANTHROPIC_API_KEY = 'sk-ant-...'", file=sys.stderr)
        print("  macOS/Linux: export ANTHROPIC_API_KEY='sk-ant-...'", file=sys.stderr)
        sys.exit(1)

    # Infer category
    category, api_success = infer_category(note_text)

    # Add note
    result = add_note(category, note_text)

    if result.get("status") == "success":
        print(f"Note saved to {result.get('file')} ({category})")
        if not api_success:
            print("(Category defaulted - API unavailable)", file=sys.stderr)
    else:
        print(f"Error: {result.get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
