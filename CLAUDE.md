# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Claude Skills marketplace plugin** that provides AI-native productivity skills for both Claude Code and Claude Desktop. The primary skill is **note-taking**, which transforms markdown notes into an AI-navigable "second brain" system.

**Key concept**: Skills make Claude an active partner in personal knowledge management rather than just a conversational assistant. They enable persistent memory, cross-project functionality, and natural interaction patterns.

## Project Architecture

### Directory Structure

```
productivity-skills/
├── .claude-plugin/
│   └── marketplace.json          # Plugin marketplace manifest
├── plugins/
│   └── productivity-suite/       # Self-contained plugin bundle
│       └── skills/               # Production-ready skills
│           └── note-taking/      # Primary skill implementation
│               ├── SKILL.md      # Skill definition with YAML frontmatter
│               ├── hooks/
│               │   └── notes_manager.py  # Python utility for note operations
│               └── templates/
│                   └── monthly-template.md
├── docs/                         # User documentation
├── examples/                     # Configuration examples
└── README.md                     # User-facing documentation
```

**Important:** This repository follows the Claude Code plugin marketplace pattern, NOT the simple skillDirectories approach. The root contains NO SKILL.md - individual skills are in `plugins/productivity-suite/skills/`.

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

1. Create a new directory in `plugins/productivity-suite/skills/`: `skill-name/`
2. Add `SKILL.md` with YAML frontmatter and clear documentation
3. Include `name` and `description` in frontmatter (REQUIRED)
4. Include trigger phrases and examples in the body
5. Add supporting scripts in `hooks/` (Python 3.7+)
6. Scripts should accept JSON via stdin, output JSON to stdout
7. Update `.claude-plugin/marketplace.json` to include new skill
8. Follow the note-taking skill as a template

**Critical**: SKILL.md must have YAML frontmatter. Required fields:
```yaml
---
name: skill-identifier
description: What the skill does AND when to use it (max 1024 chars)
---
```

Optional frontmatter fields:
- `allowed-tools`: Restrict which tools Claude can use
- `metadata.version`: Semantic versioning
- `metadata.category`: Skill category
- `metadata.status`: production, beta, experimental
- `metadata.documentation`: References to additional docs

**Body Content:**
- Clear and concise (under 500 lines recommended)
- Example-driven
- Include conversational trigger phrases
- Document edge cases and error handling
- Use progressive disclosure (move details to reference files)

## Distribution & Installation

**Plugin Marketplace Distribution (Recommended):**
```bash
# Install from Claude Code marketplace
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

**Manual Installation (Claude Code):**
```bash
git clone https://github.com/mcdow-webworks/productivity-skills.git
cp -r plugins/productivity-suite "$APPDATA/Claude/plugins/"
```

**Manual Installation (Claude Desktop - Web & App):**
```bash
# Create ZIP archive of individual skill
cd plugins/productivity-suite/skills/note-taking
zip -r note-taking-skill.zip . -x "*.gz"

# Then upload through UI:
# 1. Go to Settings > Capabilities (claude.ai/settings/capabilities)
# 2. Enable "Skills" toggle
# 3. Click "Upload skill" and select note-taking-skill.zip
# 4. Skill becomes available immediately (private to your account)
```

**Important:** Claude Desktop requires ZIP file upload with SKILL.md at root level. The ZIP must contain:
- SKILL.md (with YAML frontmatter at root)
- hooks/ folder (scripts)
- templates/ folder (resources)
- No nested directories before SKILL.md

**Custom notes directory**:
```bash
export NOTES_DIR="$HOME/my-custom-notes"
```

**Marketplace Configuration:**
- Marketplace manifest: `.claude-plugin/marketplace.json`
- Plugin name: `productivity-suite`
- Marketplace name: `productivity-skills`
- Current version: 1.0.0

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
