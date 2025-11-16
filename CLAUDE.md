# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Claude Skills marketplace plugin** that provides AI-native productivity skills for both Claude Code and Claude Desktop. The primary skill is **note-taking**, which transforms markdown notes into an AI-navigable "second brain" system.

**Key concept**: Skills make Claude an active partner in personal knowledge management rather than just a conversational assistant. They enable persistent memory, cross-project functionality, and natural interaction patterns.

## Project Architecture

### Directory Structure

```
productivity-skills/
├── SKILL.md                      # Main skill descriptor (read by Claude)
├── note-taking/                  # Primary skill implementation
│   ├── SKILL.md                  # Detailed skill documentation
│   ├── hooks/
│   │   └── notes_manager.py      # Python utility for note operations
│   └── templates/
│       └── monthly-template.md
├── docs/                         # User documentation
└── examples/                     # Configuration examples
```

### Note-Taking Skill Architecture

**Data Storage:**
- Notes stored in `~/notes/YYYY/MM-Month.md` by default
- Can be customized via `NOTES_DIR` environment variable
- All files are plain markdown for portability

**Core Components:**

1. **notes_manager.py**: Python utility that handles:
   - Adding new notes to monthly files
   - Searching across all notes with relevance scoring
   - Appending updates to existing entries
   - Index management (`.index.json`)
   - Statistics and analytics

2. **Relevance Scoring Algorithm** (in `calculate_relevance`):
   - Exact heading match: +100 points
   - All query terms in heading: +50 points
   - Individual terms in heading: +20 each
   - Terms in content: +5 per occurrence
   - Recency boost: +20 (< 30 days), +10 (< 90 days), +5 (< 180 days)

3. **Entry Format**:
   ```markdown
   # Category - Brief description
   Content with multiple lines, code blocks, links, etc.

   **Update (YYYY-MM-DD):** Additional information
   ```

**Interaction Patterns:**

The skill responds to natural phrases:
- Adding: "Note that...", "Add a note about...", "Remember that..."
- Searching: "What did I note about...", "Status of...", "Find my notes on..."
- Updating: "Add to the X note...", "Update X with...", "Append to X..."

## Development Commands

Since this is a skills plugin (not a traditional development project), there are no build/test commands. Testing is done through:

1. **Manual Testing in Claude**:
   ```bash
   # Configure Claude to use this skill directory
   # Then open any Claude session and use natural language
   "Note that I'm testing the skill"
   "What did I note about testing?"
   ```

2. **Python Script Testing**:
   ```bash
   # Test notes_manager.py directly
   echo '{"command":"search","query":"test"}' | python3 note-taking/hooks/notes_manager.py

   # Reindex notes
   echo '{"command":"reindex"}' | python3 note-taking/hooks/notes_manager.py

   # Get statistics
   echo '{"command":"stats"}' | python3 note-taking/hooks/notes_manager.py
   ```

## Adding New Skills

When creating additional skills (task-management, time-tracking, etc.):

1. Create a new directory: `skill-name/`
2. Add `SKILL.md` with clear documentation
3. Include trigger phrases and examples
4. Add supporting scripts in `hooks/` (Python 3.7+)
5. Scripts should accept JSON via stdin, output JSON to stdout
6. Follow the note-taking skill as a template

**Critical**: SKILL.md is what Claude reads to understand the skill. Make it:
- Clear and concise
- Example-driven
- Include conversational trigger phrases
- Document edge cases and error handling

## Configuration

**For Claude Code** - Add to `~/.claude/settings.json`:
```json
{
  "projectDefaults": {
    "skillDirectories": ["~/productivity-skills"]
  }
}
```

**For Claude Desktop** - Add to settings:
```json
{
  "skillDirectories": ["~/productivity-skills"]
}
```

**Custom notes directory**:
```bash
export NOTES_DIR="$HOME/my-custom-notes"
```

## Philosophy & Design Principles

1. **Plain text first**: All data in markdown, portable forever
2. **AI-navigable**: Claude as interface, not just storage
3. **Natural interaction**: Talk naturally, not commands
4. **Cross-project**: Available in every Claude session
5. **Local-first**: Data stays on user's machine
6. **Incremental adoption**: Start simple, grow organically

## Platform Compatibility

- **OS**: macOS, Linux, Windows (WSL)
- **Python**: 3.7+ required for utility scripts
- **Bash**: For optional hooks
- **Git**: For version control (recommended)

## Important Implementation Details

**Notes Manager (`notes_manager.py`)**:
- Uses `Path` objects for cross-platform compatibility
- Handles encoding with UTF-8 explicitly
- Gracefully handles missing files/directories
- Maintains `.index.json` for fast searching
- Supports `.connections.json` for relationship tracking (future use)

**Entry Extraction**:
- Top-level headings (`# `) mark new entries
- Second-level headings (`## `) are part of entry content
- Entries can span multiple lines
- Updates are appended with timestamps

**Search Implementation**:
- Searches newest files first (reverse chronological)
- Returns top 10 results by default (configurable)
- Truncates content preview to 300 characters
- Provides relevance scores for ranking

## Git Workflow Notes

This repository follows standard GitHub workflow:
- Feature branches: `feature/`, `fix/`, `docs/`
- PRs should include documentation updates
- Test on both Claude Code and Claude Desktop before submitting
