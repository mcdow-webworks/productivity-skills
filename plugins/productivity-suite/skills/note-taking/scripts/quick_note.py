#!/usr/bin/env python3
"""
Fast note capture using Claude Haiku 4.5 for category inference.
Part of productivity-skills/note-taking

Phase 1: Sync save (< 2s) - User sees "Note saved"
Phase 2: Async enrichment (background) - Expands note with context

Usage: python quick_note.py "your note content"
       python quick_note.py --no-enrich "quick note without enrichment"
"""

import json
import os
import sys
import subprocess
import threading
import atexit
from pathlib import Path

try:
    from anthropic import Anthropic
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Configuration - Category Inference (Phase 1)
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 30
TIMEOUT = 2.0  # seconds
MAX_RETRIES = 1
MAX_INPUT_LENGTH = 1000

# Configuration - Enrichment (Phase 2)
ENRICHMENT_MAX_TOKENS = 600
ENRICHMENT_TIMEOUT = 15.0  # Longer timeout for background processing
ENRICHMENT_TEMPERATURE = 0.3  # Slight creativity for enrichment

# Thread tracking for graceful shutdown
_enrichment_thread = None

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

ENRICHMENT_SYSTEM_PROMPT = """You are enhancing a quick note for future reference.
Your goal is to make the note MORE USEFUL when the user revisits it later.

Transform the note by:
1. PRESERVE the original content and any URLs/links verbatim at the start
2. ADD a concise **Definition:** if key concepts could use clarification
3. ADD **Implications:** if the note has significance worth capturing
4. ADD **Next Steps:** if there are obvious follow-up actions
5. ADD **Related:** only if there are clear connections to common concepts

Format rules:
- Start with the original content, cleaned up for clarity
- Add sections ONLY if they add real value (don't force all sections)
- Keep total output under 400 words
- Use markdown formatting (**bold** for section headers)
- Never add a Created timestamp (added automatically)
- If the note is already clear and complete, just clean it up slightly

Example input:
"link https://example.com study on Compression is Intelligence and its impact on software"

Example output:
Recent study link: https://example.com exploring "Compression is Intelligence" theory and its impact on software engineering.

**Definition:** Compression as intelligence refers to the principle that effective learning and reasoning can be understood as compression - distilling complex information into simpler, more efficient representations that preserve essential meaning.

**Implications:** This has profound relevance for software engineering:
- Code abstraction is a form of compression (patterns, functions, libraries)
- Good architecture compresses complexity into navigable structures
- AI/ML models compress training data into generalizable rules

**Next Steps:** Consider how this applies to current projects - are there opportunities to better compress complexity?"""


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


def call_enrichment_api(category: str, content: str) -> str:
    """
    Call API to enrich note content with context.

    Args:
        category: The note category
        content: Original note content

    Returns:
        Enriched content string, or None on failure
    """
    if not ANTHROPIC_AVAILABLE or not os.environ.get("ANTHROPIC_API_KEY"):
        return None

    try:
        client = Anthropic(timeout=ENRICHMENT_TIMEOUT, max_retries=1)
        response = client.messages.create(
            model=MODEL,
            max_tokens=ENRICHMENT_MAX_TOKENS,
            temperature=ENRICHMENT_TEMPERATURE,
            system=ENRICHMENT_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Category: {category}\nOriginal note: {content}\n\nEnrich this note for future reference."
            }]
        )
        return response.content[0].text.strip()

    except Exception as e:
        # Log error but don't crash - original note is already saved
        print(f"Enrichment API error: {e}", file=sys.stderr)
        return None


def replace_note(heading: str, content: str) -> dict:
    """
    Replace note content using notes_manager.py replace command.

    Args:
        heading: The note heading to find
        content: New content to replace with

    Returns:
        dict: Result from notes_manager.py
    """
    script_dir = Path(__file__).parent
    notes_manager = script_dir / "notes_manager.py"

    cmd_input = json.dumps({
        "command": "replace",
        "search_term": heading,
        "content": content,
        "preserve_timestamp": True
    })

    try:
        result = subprocess.run(
            ["python", str(notes_manager)],
            input=cmd_input,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"status": "error", "message": result.stderr}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def enrich_note_async(heading: str, category: str, original_content: str):
    """
    Background thread for note enrichment.
    Called after sync save completes - user already saw "Note saved".
    """
    def _enrich():
        try:
            enriched = call_enrichment_api(category, original_content)
            if enriched:
                result = replace_note(heading, enriched)
                if result.get("status") == "success":
                    # Optional feedback (goes to stderr, user may not see)
                    print(f"(Enriched: {heading[:40]}...)", file=sys.stderr)
                else:
                    print(f"Replace failed: {result.get('message')}", file=sys.stderr)
        except Exception as e:
            # Never crash - note is already saved with original content
            print(f"Enrichment error: {e}", file=sys.stderr)

    global _enrichment_thread
    _enrichment_thread = threading.Thread(target=_enrich, daemon=True)
    _enrichment_thread.start()


def _wait_for_enrichment():
    """Wait for background enrichment on graceful exit (max 5s)."""
    global _enrichment_thread
    if _enrichment_thread and _enrichment_thread.is_alive():
        _enrichment_thread.join(timeout=5.0)

# Register atexit handler to wait for enrichment before exit
atexit.register(_wait_for_enrichment)


def main():
    """Main entry point for quick note capture."""

    # Check for --no-enrich flag
    skip_enrichment = "--no-enrich" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--no-enrich"]

    # Validate input
    if len(args) < 1:
        print("Usage: quick_note.py [--no-enrich] <note content>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  quick_note.py meeting with Jim about pricing", file=sys.stderr)
        print("  quick_note.py --no-enrich quick reminder", file=sys.stderr)
        sys.exit(1)

    note_text = " ".join(args)

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

    # Phase 1: Sync save with category inference
    category, api_success = infer_category(note_text)
    result = add_note(category, note_text)

    if result.get("status") == "success":
        heading = result.get("heading")
        print(f"Note saved to {result.get('file')} ({category})")

        if not api_success:
            print("(Category defaulted - API unavailable)", file=sys.stderr)

        # Phase 2: Async enrichment (non-blocking)
        if not skip_enrichment and api_success:
            enrich_note_async(heading, category, note_text)
    else:
        print(f"Error: {result.get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
