---
name: note-taking
description: ALWAYS use this skill when user says "Note that", "Remember that", "Add a note about", or explicitly asks about their notes with phrases like "What did I note about", "Show me my notes on", "Search my notes for", "Find in my notes", or "What have I noted about". This searches the user's persistent note-taking system (their second brain), NOT conversation history or general knowledge. Only trigger when the user explicitly mentions "note/notes/noted" or clearly refers to their personal knowledge system.
allowed-tools: Bash
---

# Note-Taking Skill - Implementation Instructions

## CRITICAL RULES

**YOU MUST ALWAYS:**
- Use `${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py` for ALL note operations
- Pass JSON commands via stdin to the script
- Parse JSON responses from the script and present them conversationally

**YOU MUST NEVER:**
- Use Read, Write, or Edit tools directly on note files in `~/Documents/notes/` or `~/OneDrive/Documents/notes/`
- Bypass the script to manipulate markdown files or `.index.json`
- Access note files directly with any tool other than the notes_manager.py script

## Script Location

```bash
${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

The script automatically detects the notes directory (OneDrive on Windows, Documents otherwise, or `$NOTES_DIR` if set).

## Available Commands

### 1. Add Note

**When:** User says "Note that...", "Remember that...", "Add a note about..."

**Command:**
```bash
echo '{"command":"add","heading":"Category - Brief description","content":"Full note content"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Parameters:**
- `heading` (required): Format "Category - Description" (e.g., "Work - Fixed cache bug")
- `content` (required): Full note text with markdown support

**Response:**
```json
{"success": true, "message": "Note added to 2025/11-November.md", "file": "/path/to/file.md"}
```

**Example:**
```bash
echo '{"command":"add","heading":"Work - Implemented feature X","content":"Successfully completed with tests and documentation"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Category Inference:**
Use keywords to infer category:
- "fixed", "built", "implemented" → Work
- "learned", "discovered" → Learning
- "discussed", "meeting" → Meeting
- "idea", "what if" → Idea
- "decided", "will" → Decision
- "how", "why" → Question

### 2. Search Notes

**When:** User asks "What did I note about...", "Show me my notes on...", "Find in my notes..."

**Command:**
```bash
echo '{"command":"search","query":"search terms"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Parameters:**
- `query` (required): Search terms to find in headings and content

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "heading": "Work - Note title",
      "content": "Preview...",
      "file": "2025/11-November.md",
      "date": "2025-11-17",
      "relevance_score": 520
    }
  ],
  "count": 1
}
```

**Example:**
```bash
echo '{"command":"search","query":"Claude Code"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Presenting Results:**
- High relevance (≥500): Show full detail
- Multiple results: List by relevance with dates
- No results: Offer to create new note

### 3. Update Note (Append)

**When:** User says "Add to my note about...", "Update my X note with..."

**Command:**
```bash
echo '{"command":"append","search_term":"unique term to find note","content":"Additional content"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Parameters:**
- `search_term` (required): Term to find the target note (must match with relevance ≥50)
- `content` (required): Content to append (script adds timestamp automatically)

**Response (Success):**
```json
{"success": true, "message": "Appended to note", "matched_heading": "Work - Original title"}
```

**Response (Weak Match):**
```json
{
  "success": false,
  "error": "No note found matching 'term' with sufficient relevance (minimum: 50)",
  "alternatives": ["Work - Similar note (score: 45)"]
}
```

**Important:** Minimum relevance threshold of 50 prevents incorrect updates. If search term doesn't strongly match, suggest alternatives or create new note.

**Example:**
```bash
echo '{"command":"append","search_term":"feature X","content":"Deployed to production successfully"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 4. Reindex

**When:** User says "Reindex my notes" or after manual file edits

**Command:**
```bash
echo '{"command":"reindex"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Response:**
```json
{"success": true, "message": "Reindexed 145 notes from 12 files", "stats": {"files": 12, "entries": 145}}
```

### 5. Get Statistics

**When:** User asks "How many notes", "Show my note statistics"

**Command:**
```bash
echo '{"command":"stats"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Response:**
```json
{
  "success": true,
  "total_entries": 145,
  "categories": {"Work": 45, "Learning": 32},
  "date_range": {"earliest": "2025-01-15", "latest": "2025-11-17"}
}
```

### 6. Migrate Notes

**When:** User wants to import existing markdown notes

**Command:**
```bash
echo '{"command":"migrate","source_dir":"/path/to/old-notes"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Parameters:**
- `source_dir` (required): Path to directory with markdown files

**Response:**
```json
{"success": true, "message": "Migrated 23 notes from 15 files"}
```

**⚠️ Security Note:** Only migrate from trusted directories within your home directory (Documents, Desktop). Path validation is limited.

## Error Handling

All commands return JSON with `success` field. Always check it:

```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional context"
}
```

When errors occur, inform the user clearly and suggest corrective action.

## Workflow Guidelines

**Adding Notes:**
1. Extract key information from user's message
2. Infer appropriate category from keywords
3. Construct heading as "Category - Brief description"
4. Include full context in content
5. Execute add command
6. Confirm to user with category used

**Searching Notes:**
1. Extract search terms from user's query
2. Execute search command
3. Parse results and sort by relevance
4. Present conversationally with dates and categories
5. Summarize findings (e.g., "You have 3 notes across 2 months")

**Updating Notes:**
1. Extract search term and update content
2. Execute search first to find target note
3. Check relevance score (must be ≥50)
4. If strong match, execute append
5. If weak match, suggest alternatives or create new
6. Confirm update with timestamp

## Entry Format

Notes are stored as markdown entries with automatic timestamps:

```markdown
# Category - Brief description
Content with multiple lines, code blocks, links, etc.

**Created:** 2025-11-17

**Update (2025-11-18):** Additional information
```

Script handles all timestamp management automatically.

## Common Categories

Suggest these categories when adding notes:
- **Work** - Implementations, fixes, deployments
- **Learning** - Discoveries, insights, realizations
- **Meeting** - Discussions, decisions from meetings
- **Idea** - New concepts, proposals
- **Decision** - Conclusions, commitments
- **Question** - Things to explore, uncertainties

## Notes Directory Structure

Understanding the structure (read-only knowledge - never manipulate directly):

```
~/Documents/notes/  (or ~/OneDrive/Documents/notes/ on Windows)
├── 2025/
│   ├── 01-January.md
│   ├── 11-November.md
│   └── 12-December.md
├── .index.json          # Managed by script
└── .gitignore
```

## Success Indicators

You're using the skill correctly when:
- ✅ All operations use `notes_manager.py`
- ✅ You never directly access note files with Read/Write/Edit
- ✅ You parse JSON responses and present conversationally
- ✅ You handle errors gracefully
- ✅ Updates go to correct notes (relevance ≥50)

## Failure Indicators

You're NOT using the skill correctly if:
- ❌ You use Read tool on `~/Documents/notes/**/*.md`
- ❌ You use Write/Edit tools to modify note files
- ❌ You bypass the script for any operation
- ❌ You directly access `.index.json`

## Known Limitations & Risks (Personal Use)

**⚠️ Security Considerations:**
- **Path traversal risk** in migration command - only migrate from trusted directories
- **Command injection possible** if JSON escaping fails in bash - script uses stdin to mitigate
- **Environment variable NOTES_DIR** trusted without validation - use default location
- **Error messages** may leak system paths - acceptable for personal use

**⚠️ Data Integrity Risks:**
- **No atomic write operations** - system crash during append can corrupt files (backup recommended)
- **No file locking** - avoid running multiple Claude sessions simultaneously
- **Index deletion without backup** in clean-index command
- **Migration appends without validation** - validate source files manually first

**✅ Mitigation for Personal Use:**
- Keep regular backups (git recommended: `cd ~/Documents/notes && git init && git add . && git commit -m "backup"`)
- Avoid migration from untrusted/unknown directories
- Don't run multiple Claude sessions simultaneously on same notes
- Use default NOTES_DIR location (don't override with environment variable)
- Manual file edits: run reindex command after making changes

**Future Improvements Tracked:**
See `.github/research/code-review-2025-11-17.md` for comprehensive security and data integrity analysis from code review. Future versions should address:
- Atomic write pattern (temp file + rename)
- File locking for concurrent access
- Input validation (length limits, sanitization)
- Backup before destructive operations
- Type hints and improved error handling

**For Production Use:** Address critical findings in code review before deploying to multi-user environments.
