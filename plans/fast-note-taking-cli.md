# feat: Fast Note-Taking CLI Tool

## Overview

Build a lightweight CLI wrapper (`qn`) that calls the Anthropic API directly to achieve **sub-3-second response times** for quick note capture, integrating with the existing note-taking skill's file storage patterns.

**Problem:** The existing note-taking skill works well in interactive Claude Code sessions, but invoking via `claude -p` has 10-30+ second overhead for quick capture workflows.

**Solution:** A dedicated Python script calling Claude Haiku 4.5 directly for category inference, with a PowerShell wrapper for CLI access.

## Technical Approach

### Architecture

```
┌────────────────┐     ┌────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PowerShell    │────▶│  quick_note.py │────▶│  Anthropic API  │────▶│ notes_manager.py│
│  qn function   │     │  (categorizer) │     │  Haiku 4.5      │     │  (file I/O)     │
└────────────────┘     └────────────────┘     └─────────────────┘     └─────────────────┘
         │                                                                     │
         │                                                                     ▼
         │                                                           ┌─────────────────┐
         └───────────────────────────────────────────────────────────│ notes/YYYY/MM.md│
                                                                     └─────────────────┘
```

**Key decisions:**
1. **Use Anthropic Python SDK** - provides connection pooling, retry logic, proper error handling
2. **Call notes_manager.py for file I/O** - reuses existing logic, maintains format consistency
3. **Haiku 4.5 for speed** - 300-800ms typical latency, $1/MTok input, $5/MTok output
4. **Minimal prompt** - under 100 tokens for category extraction only

### Latency Budget

| Component | Budget | Notes |
|-----------|--------|-------|
| PowerShell startup | 100ms | Function invocation overhead |
| Python startup | 200ms | Import anthropic SDK |
| API call (Haiku 4.5) | 800ms | Category inference |
| notes_manager.py | 300ms | Subprocess + file I/O |
| Buffer | 600ms | Network variance |
| **Total** | **2000ms** | Target: < 3 seconds |

### File Locations

```
plugins/productivity-suite/skills/note-taking/scripts/
├── notes_manager.py          # Existing - handles file I/O
└── quick_note.py             # NEW - API call + orchestration

PowerShell Profile:
~/.config/powershell/profile.ps1  # Add qn function
```

## Implementation Phases

### Phase 1: Core Python Script

Create `quick_note.py` with:

#### 1.1 API Configuration

```python
#!/usr/bin/env python3
"""Fast note capture using Claude Haiku 4.5 for category inference."""

import json
import os
import sys
import subprocess
from pathlib import Path
from anthropic import Anthropic
import anthropic

# Configuration
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 30
TIMEOUT = 2.0  # seconds
MAX_RETRIES = 1
MAX_INPUT_LENGTH = 1000

VALID_CATEGORIES = ["Work", "Learning", "Meeting", "Idea", "Decision", "Question", "Reference", "Note"]
DEFAULT_CATEGORY = "Note"
```

#### 1.2 Category Inference Prompt

```python
SYSTEM_PROMPT = """You are a note categorizer. Given a note, return ONLY the category name.

Categories: Work, Learning, Meeting, Idea, Decision, Question, Reference, Note

Rules:
- Work: tasks, bugs, implementations, deployments
- Meeting: calls, discussions, people mentioned by name
- Learning: discoveries, tutorials, TILs
- Idea: "what if", brainstorms, future possibilities
- Decision: "will", "decided", commitments
- Question: uncertainties, "how to", investigations
- Reference: bookmarks, links, documentation
- Note: general observations (default)

Return ONLY the category name, nothing else."""
```

#### 1.3 Core Functions

```python
def infer_category(note_text: str) -> tuple[str, bool]:
    """Infer category from note text. Returns (category, api_success)."""
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
        return DEFAULT_CATEGORY, True  # API worked but invalid category

    except (anthropic.APITimeoutError, anthropic.APIConnectionError):
        return DEFAULT_CATEGORY, False
    except anthropic.APIError as e:
        print(f"Warning: API error - {e}", file=sys.stderr)
        return DEFAULT_CATEGORY, False
```

#### 1.4 Integration with notes_manager.py

```python
def add_note(category: str, content: str) -> dict:
    """Add note using notes_manager.py."""
    script_dir = Path(__file__).parent
    notes_manager = script_dir / "notes_manager.py"

    # Format heading as "Category - Brief description"
    # Extract first ~50 chars as description
    description = content[:50].replace('\n', ' ').strip()
    if len(content) > 50:
        description += "..."
    heading = f"{category} - {description}"

    cmd_input = json.dumps({
        "command": "add",
        "heading": heading,
        "content": content
    })

    result = subprocess.run(
        ["python", str(notes_manager)],
        input=cmd_input,
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode == 0:
        return json.loads(result.stdout)
    return {"status": "error", "message": result.stderr}
```

#### 1.5 Main Entry Point

```python
def main():
    # Validate input
    if len(sys.argv) < 2:
        print("Usage: quick_note.py <note content>", file=sys.stderr)
        sys.exit(1)

    note_text = " ".join(sys.argv[1:])

    if not note_text.strip():
        print("Error: Note content required", file=sys.stderr)
        sys.exit(1)

    if len(note_text) > MAX_INPUT_LENGTH:
        print(f"Error: Note too long (max {MAX_INPUT_LENGTH} chars)", file=sys.stderr)
        sys.exit(1)

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        print("Get your key at https://console.anthropic.com", file=sys.stderr)
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
```

### Phase 2: PowerShell Wrapper

#### 2.1 Function Definition

Add to `~/.config/powershell/profile.ps1`:

```powershell
function qn {
    <#
    .SYNOPSIS
    Quick note capture using Claude Haiku 4.5

    .EXAMPLE
    qn meeting with Jim about AutoMap pricing
    qn "important: remember to follow up with client"
    #>

    if ($args.Count -eq 0) {
        Write-Error "Usage: qn <note content>"
        return
    }

    $noteContent = $args -join " "
    $scriptPath = "$env:USERPROFILE\.claude\plugins\marketplaces\productivity-skills\plugins\productivity-suite\skills\note-taking\scripts\quick_note.py"

    python $scriptPath $noteContent
}
```

#### 2.2 Alternative: Path-Based Setup

```powershell
# Add to PATH instead of function
# User can run: qn.py "my note"
# Requires quick_note.py to have shebang and be in PATH
```

### Phase 3: Setup & Documentation

#### 3.1 Installation Script

Create `scripts/install-qn.ps1`:

```powershell
#!/usr/bin/env pwsh
# Install quick note CLI

$profilePath = "$env:USERPROFILE\.config\powershell\profile.ps1"
$scriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$quickNotePath = Join-Path $scriptDir "plugins\productivity-suite\skills\note-taking\scripts\quick_note.py"

# Create profile directory if needed
$profileDir = Split-Path -Parent $profilePath
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force
}

# Add qn function to profile
$functionDef = @"

# Quick Note - Fast note capture
function qn {
    if (`$args.Count -eq 0) {
        Write-Error "Usage: qn <note content>"
        return
    }
    python "$quickNotePath" `$args
}
"@

if (Test-Path $profilePath) {
    $existing = Get-Content $profilePath -Raw
    if ($existing -notmatch "function qn") {
        Add-Content $profilePath $functionDef
        Write-Host "Added qn function to profile"
    } else {
        Write-Host "qn function already exists in profile"
    }
} else {
    Set-Content $profilePath $functionDef
    Write-Host "Created profile with qn function"
}

Write-Host ""
Write-Host "Setup complete! Restart PowerShell and run:"
Write-Host "  qn 'your first quick note'"
```

#### 3.2 Requirements

Add `requirements-qn.txt`:

```
anthropic>=0.40.0
```

## Acceptance Criteria

### Functional Requirements

- [ ] `qn "note text"` saves note in < 3 seconds
- [ ] Notes stored at `~/Documents/notes/YYYY/MM-Month.md` (or OneDrive equivalent)
- [ ] Category inferred automatically (Work, Learning, Meeting, etc.)
- [ ] Heading format: `# Category - Brief description`
- [ ] Automatic timestamp: `**Created:** YYYY-MM-DD`
- [ ] API failures fallback to "Note" category (data never lost)

### Error Handling

- [ ] Missing ANTHROPIC_API_KEY: clear error with setup instructions
- [ ] Empty input: usage error
- [ ] Input > 1000 chars: length error
- [ ] API timeout: fallback to default category, save note
- [ ] Invalid API key: authentication error
- [ ] File write failure: error with details

### Non-Functional Requirements

- [ ] Response time < 3 seconds (p95)
- [ ] API cost < $0.001 per note (estimate: ~50 input tokens + 5 output tokens = $0.000075)
- [ ] Works on Windows, macOS, Linux (PowerShell Core 7+)

## Cost Estimate

| Operation | Tokens | Cost |
|-----------|--------|------|
| System prompt | ~75 | $0.000075 |
| User input (avg) | ~50 | $0.000050 |
| Output (category) | ~5 | $0.000025 |
| **Per note** | ~130 | **~$0.00015** |
| **1000 notes** | ~130K | **~$0.15** |

## Dependencies & Prerequisites

- Python 3.7+
- PowerShell Core 7+ (cross-platform)
- `anthropic` Python package
- `ANTHROPIC_API_KEY` environment variable
- Existing note-taking skill structure

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API latency exceeds 2s | Medium | High | Fallback to default category, never block |
| Rate limiting | Low | Medium | Single-user CLI, unlikely to hit limits |
| File contention | Low | Low | Append-only writes, atomic on most FS |
| Invalid category from AI | Medium | Low | Validate against allowed list, fallback |

## Testing Plan

### Manual Testing

```powershell
# Basic functionality
qn "test note"
qn "meeting with Jim about pricing"
qn "learned about async Python"
qn "what if we added dark mode?"

# Edge cases
qn ""                              # Should error
qn "a"                             # Minimal input
qn "x" * 1000                      # Max length
qn "very long note..." * 100       # Over max length

# Error conditions
$env:ANTHROPIC_API_KEY = ""        # Missing key
qn "test"                          # Should error with instructions
```

### Verify File Output

```powershell
# Check note was saved
Get-Content ~/Documents/notes/2026/01-January.md | Select-Object -Last 20
```

## Files to Create

| File | Purpose |
|------|---------|
| `plugins/productivity-suite/skills/note-taking/scripts/quick_note.py` | Core Python script |
| `scripts/install-qn.ps1` | PowerShell installation script |
| `requirements-qn.txt` | Python dependencies |
| `docs/quick-notes.md` | User documentation |

## References

### Internal References
- Existing notes_manager.py: `plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py`
- SKILL.md: `plugins/productivity-suite/skills/note-taking/SKILL.md`
- Entry format conventions: CLAUDE.md lines 72-78

### External References
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Claude Haiku 4.5 Pricing](https://www.anthropic.com/claude/haiku) - $1/MTok input, $5/MTok output
- [Reducing Claude API Latency](https://docs.claude.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency)
