# Note-Taking Skill - User Guide

## Overview

The note-taking skill transforms Claude into an active partner in your personal knowledge management. Instead of just conversing, Claude can remember and retrieve information across all your sessions, creating an AI-navigable "second brain."

## Quick Start

Talk to Claude naturally:

- **Add notes:** "Note that I fixed the authentication bug today"
- **Search notes:** "What did I note about authentication?"
- **Update notes:** "Add to my authentication note that I deployed it to production"

That's it. No commands to memorize, no special syntax.

## How It Works

### Storage

Notes are stored in plain markdown files organized by year and month:

```
~/Documents/notes/  (or ~/OneDrive/Documents/notes/ on Windows)
├── 2025/
│   ├── 01-January.md
│   ├── 11-November.md
│   └── 12-December.md
├── .index.json          # Search index (managed automatically)
└── .gitignore
```

### Entry Format

Each note has a category and brief description:

```markdown
# Work - Fixed authentication bug
Resolved the issue where users couldn't log in after password reset. The problem was in the token validation logic.

**Created:** 2025-11-17

**Update (2025-11-18):** Deployed to production successfully
```

Claude automatically adds timestamps when creating and updating notes.

### Categories

Claude infers categories from what you say:

- **Work** - "I implemented...", "Fixed...", "Deployed..."
- **Learning** - "I learned...", "Discovered...", "Realized..."
- **Meeting** - "In the meeting we discussed...", "Team decided..."
- **Idea** - "What if we...", "Consider...", "Maybe we could..."
- **Decision** - "I decided...", "We will...", "Plan to..."
- **Question** - "How does...", "Why is...", "Wondering about..."
- **Reference** - "Bookmark this...", "Save for later...", "Found this resource..."
- **Note** - General notes that don't fit other categories

You can also specify categories explicitly: "Note that in the Work category, I completed the API integration."

## Common Use Cases

### Daily Work Log

"Note that I completed the user dashboard feature with full test coverage"

Claude creates:
```markdown
# Work - Completed user dashboard feature
Full test coverage included with unit and integration tests.

**Created:** 2025-11-17
```

### Learning Journal

"I learned that Python's GIL prevents true parallel execution of threads"

Claude creates:
```markdown
# Learning - Python GIL prevents parallel thread execution
The Global Interpreter Lock (GIL) ensures only one thread executes Python bytecode at a time, preventing race conditions but limiting parallelism.

**Created:** 2025-11-17
```

### Meeting Notes

"In today's meeting we decided to use PostgreSQL instead of MongoDB"

Claude creates:
```markdown
# Meeting - Decision to use PostgreSQL over MongoDB
Team discussed database options. Chose PostgreSQL for better transaction support and mature ecosystem.

**Created:** 2025-11-17
```

### Ideas and Questions

"What if we used WebSockets for real-time updates instead of polling?"

Claude creates:
```markdown
# Idea - Use WebSockets for real-time updates
Consider replacing polling mechanism with WebSockets to reduce server load and improve responsiveness.

**Created:** 2025-11-17
```

### Progress Updates

First note:
"Note that I started working on the payment integration"

Later:
"Add to my payment integration note that I completed the Stripe setup"

Claude updates:
```markdown
# Work - Payment integration
Started working on integrating payment processing.

**Created:** 2025-11-15

**Update (2025-11-17):** Completed Stripe setup with webhook handlers
```

## Searching Your Notes

### Simple Searches

"What did I note about authentication?"

Claude searches across all your notes and shows the most relevant results with dates and files.

### Finding Progress

"Show me my notes about the API project"

Claude will find all related notes, sorted by relevance, showing you the full timeline.

### Recent Activity

"What have I noted this week?"

Combine with date context to find recent notes on any topic.

## Tips for Better Notes

### Be Specific in Headings

Claude infers headings from your message. More specific information = better headings.

**Less effective:**
- "Note that I did some work" → Vague heading

**More effective:**
- "Note that I implemented OAuth login" → Clear heading: "Work - Implemented OAuth login"

### Use Natural Language

Don't worry about categories or formatting. Just talk naturally:

- "I figured out how to fix the memory leak" → "Learning - Fixed memory leak"
- "Record this article about Rust async" → "Reference - Article about Rust async"
- "We agreed to ship by Friday" → "Decision - Ship by Friday"

### Update Existing Notes

When adding to an existing topic, reference it clearly:

- "Add to my OAuth note that I finished testing"
- "Update the memory leak note with the final solution"

Claude will find the right note and append your update with a timestamp.

## Advanced Features

### Statistics

"How many notes do I have?"

Claude shows total notes, category breakdown, and date range.

### Reindexing

"Reindex my notes"

Rebuilds the search index. Useful if you manually edit note files.

### Migration

"Migrate my notes from ~/old-notes"

Import existing markdown files into the notes system. Claude will organize them by modification date and rebuild the index.

### Validation

"Validate my notes"

Check all note files for issues like empty files or encoding problems.

## Directory Structure (Read-Only Knowledge)

You never need to access files directly, but here's what's happening behind the scenes:

```
~/Documents/notes/
├── 2025/
│   ├── 01-January.md       # All notes from January 2025
│   ├── 02-February.md
│   └── 11-November.md
├── .index.json              # Search index (auto-managed)
└── .gitignore
```

Each monthly file contains multiple note entries, all searchable through Claude.

## Data Integrity and Backup

### Recommended Backup Strategy

Your notes are plain markdown files. Back them up like any important data:

```bash
# Option 1: Git (recommended)
cd ~/Documents/notes
git init
git add .
git commit -m "Initial backup"

# Option 2: Sync service
# Move notes to Dropbox, OneDrive, or iCloud folder

# Option 3: Manual backup
# Periodically copy ~/Documents/notes to external drive
```

### Concurrent Access

Avoid running multiple Claude sessions simultaneously that modify notes. The system doesn't have file locking, so concurrent writes could cause issues.

### Manual Edits

You can manually edit note files in any text editor. After manual edits, tell Claude to "Reindex my notes" to update the search index.

## Privacy and Security

### Where Your Data Lives

Notes are stored **only on your local machine** in `~/Documents/notes/` (or `~/OneDrive/Documents/notes/` on Windows with OneDrive).

- Claude reads and writes to these files when you ask
- No notes are sent to Anthropic's servers for storage
- Notes are part of your conversation context when searching/adding

### Migration Security

When migrating notes from other directories, only use trusted source folders within your home directory. The migration command has limited path validation.

### Environment Variables

You can customize the notes directory:

```bash
# On macOS/Linux
export NOTES_DIR="$HOME/my-custom-notes"

# On Windows (System Environment Variables)
NOTES_DIR=C:\Users\username\my-custom-notes
```

Most users should use the default location and avoid custom paths.

## Troubleshooting

### "No notes found"

- The notes directory might not exist yet. Claude will create it when you add your first note.
- Check the directory path with: "Show me my notes directory info"

### "Weak match" when updating

The search term didn't strongly match any existing note heading. Claude will suggest alternatives. Either:
- Be more specific with the search term
- Use exact words from the heading you want to update
- Create a new note instead

### Search results seem wrong

The search prioritizes heading matches over content matches. If you're searching for content-specific terms, you might need to be more specific or browse by category.

### Wrong notes directory on Windows

If you have OneDrive, Claude automatically uses `~/OneDrive/Documents/notes` for consistency between Claude Desktop and Claude Code. This is intentional behavior.

## Philosophy

### Plain Text First

All notes are markdown. You can read them, edit them, grep them, version them - without Claude. The skill just makes Claude a better interface.

### AI-Navigable

Instead of organizing by folders or tags, let Claude navigate by content. You remember what you noted, Claude finds it.

### Natural Interaction

Talk to Claude naturally. The skill interprets your intent and handles the mechanics.

### Cross-Project

The notes system is available in every Claude session, creating persistent memory across all your work.

### Local-First

Your data stays on your machine. You control it, back it up, and own it forever.

### Incremental Adoption

Start with simple notes. Add complexity as needed. No upfront setup required.

## Limitations (Personal Use)

The note-taking skill is designed for **personal use**. Some current limitations:

### Security Considerations

- **Path traversal risk** in migration - only migrate from trusted directories
- **Command injection possible** if JSON escaping fails - script uses stdin to mitigate
- **NOTES_DIR environment variable** trusted without validation - use default location
- **Error messages** may leak system paths - acceptable for personal use

### Data Integrity Risks

- **No atomic writes** - system crash during append can corrupt files (backup recommended)
- **No file locking** - avoid running multiple Claude sessions simultaneously
- **Index deletion** in clean-index command has no backup
- **Migration appends** without validation - validate source files manually first

### Mitigation for Personal Use

- Keep regular backups (git recommended)
- Avoid migration from untrusted directories
- Don't run multiple Claude sessions simultaneously on same notes
- Use default NOTES_DIR location
- After manual file edits, run reindex command

### Future Improvements

For production/multi-user use, the following improvements are tracked:
- Atomic write pattern (temp file + rename)
- File locking for concurrent access
- Input validation (length limits, sanitization)
- Automatic backup before destructive operations
- Type hints and improved error handling

See `.github/research/code-review-2025-11-17.md` for comprehensive security analysis.

## Getting Help

### In Claude

"How does the note-taking skill work?"

Claude can answer questions about the skill based on this guide.

### Support

For issues, questions, or feature requests:
- GitHub: [productivity-skills repository](https://github.com/mcdow-webworks/productivity-skills)
- File an issue with details about the problem

### Example Workflows

Check `plugins/productivity-suite/skills/note-taking/examples/` for sample notes and workflows.

## Version

This guide is for note-taking skill v1.0.0, part of the productivity-suite plugin.
