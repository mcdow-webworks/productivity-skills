# notes_manager.py API Reference

This document provides a complete reference for the `notes_manager.py` JSON command interface used by the note-taking skill.

## Overview

The `notes_manager.py` script accepts JSON commands via stdin and outputs JSON responses to stdout. All note operations should go through this script interface.

**Script Location:**
```bash
${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Usage Pattern:**
```bash
echo '{"command":"<command_name>","param1":"value1","param2":"value2"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

## Commands

### 1. add - Add New Note

Adds a new note entry to the appropriate monthly file.

**Request:**
```json
{
  "command": "add",
  "heading": "Category - Brief description",
  "content": "Full note content with markdown support",
  "category": "Optional category (inferred from heading if omitted)"
}
```

**Parameters:**
- `heading` (required): The note title in format "Category - Description"
- `content` (required): The note body content (supports markdown)
- `category` (optional): Category for the note (Work, Learning, Meeting, etc.)

**Response (Success):**
```json
{
  "success": true,
  "message": "Note added to 2025/11-November.md",
  "file": "/path/to/notes/2025/11-November.md",
  "heading": "Work - Testing note-taking skill"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional context if available"
}
```

**Example:**
```bash
echo '{"command":"add","heading":"Work - Implemented feature X","content":"Successfully completed the implementation with tests"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 2. search - Search Notes

Searches all notes for matching entries based on query terms.

**Request:**
```json
{
  "command": "search",
  "query": "search terms",
  "max_results": 10
}
```

**Parameters:**
- `query` (required): Search terms to find in headings and content
- `max_results` (optional): Maximum number of results to return (default: 10)

**Response (Success):**
```json
{
  "success": true,
  "results": [
    {
      "heading": "Work - Note title",
      "content": "Preview of note content (truncated to 300 chars)...",
      "file": "2025/11-November.md",
      "date": "2025-11-17",
      "relevance_score": 520
    }
  ],
  "count": 1,
  "query": "search terms"
}
```

**Response (No Results):**
```json
{
  "success": true,
  "results": [],
  "count": 0,
  "query": "search terms"
}
```

**Relevance Scoring:**
- Exact phrase match in heading: +500 points
- All query terms in heading: +100 points
- Individual query term in heading: +20 points each
- Query terms in content: capped at +50 total
- Recency bonus: +10 (<30 days), +5 (<90 days), +2 (<180 days)

**Example:**
```bash
echo '{"command":"search","query":"Claude Code"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 3. append - Update Existing Note

Appends new content to an existing note entry with a timestamp.

**Request:**
```json
{
  "command": "append",
  "search_term": "unique term to find the note",
  "content": "Additional content to append"
}
```

**Parameters:**
- `search_term` (required): Term to search for the target note (must match with relevance ≥50)
- `content` (required): Content to append with automatic timestamp

**Response (Success):**
```json
{
  "success": true,
  "message": "Appended to note in 2025/11-November.md",
  "file": "/path/to/notes/2025/11-November.md",
  "matched_heading": "Work - Original note title",
  "relevance_score": 520
}
```

**Response (No Strong Match):**
```json
{
  "success": false,
  "error": "No note found matching 'search term' with sufficient relevance (minimum: 50)",
  "alternatives": [
    "Work - Similar note (score: 45)",
    "Learning - Another note (score: 30)"
  ]
}
```

**Important:**
- Requires minimum relevance score of 50 to prevent incorrect updates
- Automatically adds `**Update (YYYY-MM-DD):**` timestamp
- Returns alternatives if no strong match found

**Example:**
```bash
echo '{"command":"append","search_term":"feature X","content":"Deployed to production successfully"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 4. reindex - Rebuild Search Index

Rebuilds the `.index.json` file by scanning all note files.

**Request:**
```json
{
  "command": "reindex"
}
```

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "Reindexed 145 notes from 12 files",
  "stats": {
    "files": 12,
    "entries": 145
  }
}
```

**When to Use:**
- After manual edits to note files
- After migration
- When search results seem outdated
- After resolving file permission issues

**Example:**
```bash
echo '{"command":"reindex"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 5. stats - Get Statistics

Returns statistics about the notes collection.

**Request:**
```json
{
  "command": "stats"
}
```

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "total_entries": 145,
  "total_files": 12,
  "categories": {
    "Work": 45,
    "Learning": 32,
    "Meeting": 28,
    "Idea": 20,
    "Decision": 12,
    "Question": 8
  },
  "date_range": {
    "earliest": "2025-01-15",
    "latest": "2025-11-17"
  },
  "notes_directory": "/path/to/notes"
}
```

**Example:**
```bash
echo '{"command":"stats"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 6. info - Get System Information

Returns information about the notes directory and configuration.

**Request:**
```json
{
  "command": "info"
}
```

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "notes_directory": "/path/to/notes",
  "index_file": "/path/to/notes/.index.json",
  "index_exists": true,
  "config": {
    "NOTES_DIR": "/path/to/notes",
    "ONEDRIVE_DETECTED": true
  }
}
```

**Example:**
```bash
echo '{"command":"info"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 7. clean-index - Clean Index File

Removes the `.index.json` file. Use before `reindex` if index is corrupted.

**Request:**
```json
{
  "command": "clean-index"
}
```

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "Index file removed successfully"
}
```

**Example:**
```bash
echo '{"command":"clean-index"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 8. validate - Validate Note Files

Validates all note files for proper formatting and encoding.

**Request:**
```json
{
  "command": "validate"
}
```

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "validated_files": 12,
  "issues": [
    {
      "file": "2025/08-August.md",
      "issue": "Encoding issue detected",
      "line": 42
    }
  ]
}
```

**Example:**
```bash
echo '{"command":"validate"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 9. migrate - Import Existing Notes

Migrates notes from an external directory into the organized structure.

**Request:**
```json
{
  "command": "migrate",
  "source_dir": "/path/to/old-notes"
}
```

**Parameters:**
- `source_dir` (required): Path to directory containing markdown files to migrate

**Response:**
```json
{
  "success": true,
  "message": "Migrated 23 notes from 15 files",
  "stats": {
    "files_processed": 15,
    "entries_migrated": 23,
    "categories_inferred": 18
  }
}
```

**Migration Process:**
- Reads all `.md` files from source directory
- Infers categories from content (Work, Learning, etc.)
- Organizes by file modification date into monthly files
- Adds `**Created:** YYYY-MM-DD` timestamps
- Rebuilds index automatically

**Example:**
```bash
echo '{"command":"migrate","source_dir":"~/old-notes"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

## Error Handling

All commands follow a consistent error response format:

**Standard Error Response:**
```json
{
  "success": false,
  "error": "Human-readable error message",
  "details": "Additional technical details (optional)",
  "command": "command_name"
}
```

**Common Error Codes:**
- File permission errors
- Invalid JSON input
- Missing required parameters
- Notes directory not found
- Encoding issues

## Testing

### Direct Testing

Test commands directly from the command line:

```bash
cd /path/to/skill/directory

# Test add
echo '{"command":"add","heading":"Test - Note","content":"Test content"}' | python3 scripts/notes_manager.py

# Test search
echo '{"command":"search","query":"test"}' | python3 scripts/notes_manager.py

# Test append
echo '{"command":"append","search_term":"Test","content":"Update"}' | python3 scripts/notes_manager.py

# Test reindex
echo '{"command":"reindex"}' | python3 scripts/notes_manager.py

# Test stats
echo '{"command":"stats"}' | python3 scripts/notes_manager.py
```

### Automated Testing

```bash
# Run all commands sequentially
for cmd in '{"command":"stats"}' '{"command":"info"}' '{"command":"reindex"}'; do
  echo "$cmd" | python3 scripts/notes_manager.py | python3 -m json.tool
done
```

## Environment Variables

**NOTES_DIR:**
- Custom notes directory location
- Default: `~/Documents/notes` (or `~/OneDrive/Documents/notes` if OneDrive detected)
- Example: `export NOTES_DIR="$HOME/my-notes"`

**CLAUDE_SKILL_ROOT:**
- Set automatically by Claude Code
- Points to skill directory root
- Use in script paths: `${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py`

## Best Practices

1. **Always use JSON interface:** Don't directly edit note files
2. **Handle errors gracefully:** Check `success` field in responses
3. **Validate input:** Ensure required parameters are present
4. **Parse responses:** Extract data from JSON responses
5. **Use append for updates:** Don't re-add existing notes
6. **Reindex after manual changes:** Keep index synchronized

## Cross-Platform Notes

**Windows:**
- Use forward slashes in paths: `~/Documents/notes/`
- Script handles OneDrive detection automatically
- Git Bash and WSL both supported

**macOS/Linux:**
- Standard POSIX paths work
- Tilde expansion supported: `~/Documents/notes/`

**All Platforms:**
- UTF-8 encoding enforced
- Path objects used for compatibility
- Environment variables work consistently

## Version History

**1.0.0** - Initial release
- Core commands: add, search, append
- Index management
- OneDrive detection

## Support

For issues or questions:
- [GitHub Issues](https://github.com/mcdow-webworks/productivity-skills/issues)
- [Documentation](../docs/USER_GUIDE.md)
- [SKILL.md](../SKILL.md) - Implementation instructions
