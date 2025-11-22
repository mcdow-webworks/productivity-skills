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
├── .github/
│   └── research/                 # Development research and analysis
├── plugins/
│   └── productivity-suite/       # Self-contained plugin bundle
│       └── skills/               # Production-ready skills
│           └── note-taking/      # Primary skill implementation
│               ├── SKILL.md      # Lean implementation guide (145 lines)
│               ├── scripts/
│               │   └── notes_manager.py  # Python utility for note operations
│               ├── templates/
│               │   └── monthly-template.md
│               └── examples/
│                   └── sample-notes.md   # Example note file
├── docs/                         # User documentation
│   ├── note-taking-guide.md      # Comprehensive user guide (383 lines)
│   ├── installation.md           # Installation and troubleshooting
│   ├── development.md            # Developer workflow
│   ├── contributing.md           # Contributing guidelines
│   └── faq.md                    # FAQ and troubleshooting
└── README.md                     # Concise overview (271 lines)
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

## Development Resources

### Research and Analysis Documents

**Location:** `.github/research/`

All development research, analysis, and summary documents should be placed in `.github/research/`. This keeps the repository clean for end users while preserving valuable context for contributors.

**Convention:** When conducting research for features, bug fixes, or architectural decisions:

1. Create comprehensive research/analysis documents in `.github/research/`
2. Use descriptive filenames: `research-<topic>.md`, `analysis-<issue>.md`, `summary-<topic>.md`
3. Include findings, trade-offs, recommendations, and references
4. Link to these documents from GitHub issues for context

**Current Research Documents:**
- `research-cross-platform-paths.md` - Cross-platform file path handling best practices
- `research-hooks-vs-utility-scripts.md` - Claude Code hooks vs utility scripts distinction
- `research-tiered-trigger-systems.md` - Natural language trigger system design
- `analysis-notes-manager-issues.md` - notes_manager.py issue analysis
- `summary-path-best-practices.md` - Quick reference for path handling

**Note:** GitHub issue descriptions are stored in GitHub Issues (#1, #2, etc.), not as markdown files in the repository.

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
   # Use full path with tilde expansion (works from any directory)
   SCRIPT=~/.claude/plugins/marketplaces/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py

   # Search notes
   echo "{\"command\":\"search\",\"query\":\"test\"}" | python "$SCRIPT"

   # Add new note
   echo "{\"command\":\"add\",\"heading\":\"Test - Note\",\"content\":\"Test content\"}" | python "$SCRIPT"

   # Append to existing note (use search_term parameter)
   echo "{\"command\":\"append\",\"search_term\":\"Test\",\"content\":\"Update content\"}" | python "$SCRIPT"

   # Reindex notes
   echo "{\"command\":\"reindex\"}" | python "$SCRIPT"

   # Get statistics
   echo "{\"command\":\"stats\"}" | python "$SCRIPT"
   ```

   **Note:** Use `python` (not `python3`) and escaped double quotes for cross-platform compatibility.

## Adding New Skills

When creating additional skills (task-management, time-tracking, etc.):

1. Create a new directory in `plugins/productivity-suite/skills/`: `skill-name/`
2. Add `SKILL.md` with YAML frontmatter and clear documentation
3. Include `name` and `description` in frontmatter (REQUIRED)
4. Include trigger phrases and examples in the body
5. Add supporting scripts in `scripts/` (Python 3.7+)
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
- **Lean and focused** (under 200 lines strongly recommended)
- **Implementation-only** - no user-facing documentation
- Move user guides to `docs/` directory
- Example-driven with complete, working code
- Include conversational trigger phrases
- Document essential edge cases only
- Use progressive disclosure (move details to separate docs)

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

**Claude Desktop Support:**

⚠️ **Not Yet Available** - Claude Desktop support is currently in planning phase.

The current implementation uses the Skills system which is specific to Claude Code. To support Claude Desktop, an MCP (Model Context Protocol) server wrapper is needed.

**Research Available:**
- `.github/research/research-mcp-server-implementation.md` - Implementation research
- `.github/research/summary-mcp-server-best-practices.md` - Best practices summary

The MCP server would wrap `notes_manager.py` functionality and expose it through the Model Context Protocol, allowing Claude Desktop to interact with notes through the standard MCP interface rather than the Skills system.

**Planned Approach:**
1. Create MCP server that wraps notes_manager.py operations
2. Map skill commands to MCP tools/resources
3. Handle authentication and file permissions through MCP
4. Maintain feature parity with Claude Code implementation
5. Test on Claude Desktop (Web & App)

See research documents for detailed implementation plan.

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

**Current Support (Claude Code):**
- **OS**: macOS, Linux, Windows
- **Python**: 3.7+ required for utility scripts
- **Claude**: Claude Code 2.0+

**Future Support (Planned):**
- **Claude Desktop** - Requires MCP server implementation (see Distribution & Installation section)

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

### 2025-11-20: SKILL.md Should Be Lean Implementation Guide Only
The note-taking SKILL.md was refactored from 331 lines (verbose, mixed user/implementation content) to 145 lines (lean, implementation-only). Key learnings:
- **Separate concerns**: SKILL.md = implementation instructions for Claude; docs/note-taking-guide.md = user documentation
- **Essential only**: API commands with exact JSON formats, critical rules, brief workflow patterns
- **No user docs**: Philosophy, troubleshooting, extensive examples → move to docs/
- **Cross-platform**: Always use escaped double quotes `echo "{\"command\":\"...\"}"`; full paths with tilde `~/.claude/plugins/.../script.py`; `python` not `python3`

### 2025-11-20: Documentation Structure Should Be Streamlined
Consolidated documentation to eliminate duplication and establish clear hierarchy:
- **README.md**: Concise overview (271 lines) with quick start and links
- **docs/note-taking-guide.md**: Comprehensive user guide (383 lines)
- **docs/installation.md**: Full installation and troubleshooting
- **Single source of truth**: Each topic documented in one place only
- **Research archived**: All design docs in `.github/research/` (not user-facing)

### 2025-11-22: Entry Extraction Must Handle Leading Whitespace
Markdown headings with leading whitespace (e.g., ` # Heading`) were not recognized as entry boundaries, causing entries to be merged incorrectly. This resulted in wrong content being attached to entries and false positive search results. Solution: Strip leading whitespace with `line.lstrip()` before checking if a line is a heading (`stripped.startswith('# ')`). This ensures all headings are properly recognized regardless of indentation.

### 2025-11-22: Scoring Bonuses Should Only Apply to Actual Matches
Applying scoring bonuses (like recency) unconditionally to all entries creates false positives where recent unrelated entries appear in search results. Solution: Calculate base score from content/heading matches first, then only apply bonuses when `base_score > 0`. This ensures bonuses enhance relevant results rather than creating false positives.

## Git Workflow Notes

This repository follows standard GitHub workflow:
- Feature branches: `feature/`, `fix/`, `docs/`
- PRs should include documentation updates
- Test on both Claude Code and Claude Desktop before submitting
