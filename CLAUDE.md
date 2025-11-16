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
│               ├── templates/
│               │   └── monthly-template.md
│               └── examples/
│                   └── sample-notes.md   # Example note file
├── docs/                         # User documentation
└── README.md                     # User-facing documentation
```

**Important:** This repository follows the Claude Code plugin marketplace pattern, NOT the simple skillDirectories approach. The root contains NO SKILL.md - individual skills are in `plugins/productivity-suite/skills/`.

### Note-Taking Skill Architecture

**Data Storage:**
- Notes stored in `~/Documents/notes/YYYY/MM-Month.md` by default
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
   - File headers filtered out (e.g., "Notes - November 2025" not searchable)
   - Exact phrase match in heading: +500 points (overwhelming bonus)
   - All query terms in heading: +100 points
   - Individual terms in heading: +20 each
   - Terms in content: capped at +50 total (prevents content from overwhelming heading matches)
   - Recency boost: +10 (< 30 days), +5 (< 90 days), +2 (< 180 days)
   - Minimum relevance threshold: ≥50 required for updates (prevents weak matches)

3. **Entry Format**:
   ```markdown
   # Category - Brief description
   Content with multiple lines, code blocks, links, etc.

   **Created:** YYYY-MM-DD

   **Update (YYYY-MM-DD):** Additional information
   ```

   - New entries automatically get `**Created:** YYYY-MM-DD` timestamp
   - Updates automatically get `**Update (YYYY-MM-DD):**` timestamp

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
   cd plugins/productivity-suite/skills/note-taking

   # Search notes
   echo '{"command":"search","query":"test"}' | python hooks/notes_manager.py

   # Add new note
   echo '{"command":"add","heading":"Test - Note","content":"Test content"}' | python hooks/notes_manager.py

   # Append to existing note (use search_term parameter)
   echo '{"command":"append","search_term":"Test","content":"Update content"}' | python hooks/notes_manager.py

   # Reindex notes
   echo '{"command":"reindex"}' | python hooks/notes_manager.py

   # Get statistics
   echo '{"command":"stats"}' | python hooks/notes_manager.py
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
# Create ZIP archive with proper path separators
# Use the provided Python script (ensures forward slashes)
python scripts/create-skill-zip.py

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

**Custom notes directory** (optional - default is ~/Documents/notes):
```bash
export NOTES_DIR="$HOME/my-custom-notes"

# Or on Windows (System Environment Variables):
# NOTES_DIR=C:\Users\username\my-custom-notes
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
- **OneDrive Detection**: Automatically uses `~/OneDrive/Documents/notes` if OneDrive folder exists, ensuring consistency between Claude Desktop and Claude Code on Windows

**Entry Extraction**:
- Top-level headings (`# `) mark new entries
- File headers (e.g., "Notes - November 2025") are automatically filtered out
- Second-level headings (`## `) are part of entry content
- Entries can span multiple lines
- New entries get automatic `**Created:** YYYY-MM-DD` timestamp
- Updates are appended with `**Update (YYYY-MM-DD):**` timestamps

**Search Implementation**:
- Searches newest files first (reverse chronological)
- Returns top 10 results by default (configurable)
- Truncates content preview to 300 characters
- Provides relevance scores for ranking
- File headers automatically excluded from search results
- Exact phrase matches in headings heavily prioritized (+500 bonus)
- Content scoring capped at +50 to prevent overwhelming heading matches

**Update Implementation**:
- Requires minimum relevance score of ≥50 to prevent weak matches
- Returns alternatives when no strong match found
- Ensures entries don't get "fouled up" with incorrect updates
- Uses `search_term` parameter (not `search`) in JSON interface

## Key Learnings

### 2025-11-16: OneDrive Path Detection Critical for Windows Users
Windows with OneDrive creates two `Documents` folders (local and synced). Claude Desktop and Claude Code may use different paths by default. Solution: Implement automatic detection that prefers `~/OneDrive/Documents/notes` when OneDrive folder exists. This ensures consistency across both platforms.

### 2025-11-16: Entry Matching Requires Aggressive Heading Prioritization
Initial relevance scoring allowed content matches to overwhelm heading matches, causing updates to target wrong entries. Solution: Exact phrase match in heading gets +500 points (vs +5 per content term), content scoring capped at +50 total, minimum threshold of ≥50 required for updates. This prevents "fouled up" entries.

### 2025-11-16: File Headers Must Be Filtered from Search
File headers like "Notes - November 2025" were appearing in search results and could be matched for updates. Solution: Filter them during entry extraction using regex pattern `^Notes - \w+ \d{4}$`. This prevents accidental updates to file headers.

### 2025-11-16: Automatic Timestamps Essential for Context
Without creation timestamps, users couldn't determine when notes were added, reducing usefulness for time-based queries. Solution: Automatically append `**Created:** YYYY-MM-DD` to all new entries and `**Update (YYYY-MM-DD):**` to appends.

### 2025-11-16: Category Inference Enables Better Migration
Legacy notes without categories are harder to scan and organize. Solution: Keyword-based category inference during migration (Work, Learning, Health, etc.) transforms simple headings into categorized entries automatically.

### 2025-11-16: Stick to Official YAML Frontmatter Specification
When adding skills, use only documented frontmatter fields (`name`, `description`, `allowed-tools`, `metadata.*`). Custom fields may confuse users or break compatibility with future Claude versions. Document any optional fields clearly with their purpose.

## Git Workflow Notes

This repository follows standard GitHub workflow:
- Feature branches: `feature/`, `fix/`, `docs/`
- PRs should include documentation updates
- Test on both Claude Code and Claude Desktop before submitting
