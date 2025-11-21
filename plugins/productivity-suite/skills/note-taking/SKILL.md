---
name: note-taking
description: ALWAYS use this skill when user says "Note that", "Remember that", "Add a note about", or explicitly asks about their notes with phrases like "What did I note about", "Show me my notes on", "Search my notes for", "Find in my notes", or "What have I noted about". This searches the user's persistent note-taking system (their second brain), NOT conversation history or general knowledge. Only trigger when the user explicitly mentions "note/notes/noted" or clearly refers to their personal knowledge system.
allowed-tools: Bash
---

# Note-Taking Skill - Implementation Instructions

## CRITICAL RULES

**YOU MUST ALWAYS:**
- Use `scripts/notes_manager.py` for ALL note operations
- Pass JSON commands via stdin to the script
- Parse JSON responses and present them conversationally

**YOU MUST NEVER:**
- Use Read, Write, or Edit tools on note files in `~/Documents/notes/` or `~/OneDrive/Documents/notes/`
- Bypass the script to manipulate `.index.json` or markdown files directly

## Script Invocation

**CRITICAL Path Requirements:**
- Use tilde `~/.claude/plugins/...` (expands on all platforms)
- Use forward slashes `/` (works on Windows) - NEVER backslashes `\`
- This exact pattern works from any directory on Windows, macOS, Linux

```bash
echo "{\"command\":\"<cmd>\",\"param\":\"value\"}" | python ~/.claude/plugins/marketplaces/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py
```

**Cross-platform notes:**
- Use `python` (not `python3`) - works on Windows, macOS, Linux
- Use double quotes with escaped inner quotes: `echo "{\"command\":\"...\"}"` (works on all platforms)
- Script auto-detects notes directory (OneDrive on Windows, Documents otherwise, or `$NOTES_DIR` if set)

## API Commands

### add - Create new note

**Command:**
```bash
echo "{\"command\":\"add\",\"heading\":\"Category - Brief description\",\"content\":\"Note text\"}" | python ~/.claude/plugins/marketplaces/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py
```

**Response:**
```json
{"status":"success","file":"2025/11-November.md","heading":"Work - Title","path":"/full/path.md"}
```

**Heading:** Always "Category - Description". Never "Untitled". Infer category from keywords:
- Work: "fixed", "built", "implemented", "deployed"
- Learning: "learned", "discovered", "realized"
- Meeting: "meeting", "discussed", "decided in meeting"
- Idea: "what if", "consider", "idea"
- Decision: "decided", "will", "plan to"
- Question: "how", "why", "question about"
- Reference: "record", "bookmark", "found"
- Note: "note that", "remember"

### search - Find notes

**Command:**
```bash
echo "{\"command\":\"search\",\"query\":\"search terms\"}" | python ~/.claude/plugins/marketplaces/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py
```

**Response:**
```json
[
  {
    "heading":"Work - Title",
    "content":"Preview text...",
    "file":"2025/11-November.md",
    "date":"2025-11-17",
    "relevance":520
  }
]
```

Returns array of matches (max 10). Empty `[]` if none. Present high relevance (≥500) in full detail; multiple results by relevance with dates.

### append - Update existing note

**Command:**
```bash
echo "{\"command\":\"append\",\"search_term\":\"unique term\",\"content\":\"Update text\"}" | python ~/.claude/plugins/marketplaces/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py
```

**Response (success):**
```json
{"status":"success","heading":"Work - Original title","file":"2025/11-November.md","alternatives":[]}
```

**Response (no match):**
```json
{"status":"not_found","query":"term","suggestion":"No matching entry found. Create a new note?"}
```

**Response (weak match):**
```json
{"status":"ambiguous","query":"term","alternatives":[{"heading":"Work - Title","relevance":45}],"message":"No strong match found."}
```

Requires relevance ≥50. If weak match, suggest alternatives or create new note.

### Other Commands

All use same pattern: `echo "{\"command\":\"...\"}" | python ~/.claude/plugins/marketplaces/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py`

**reindex:** Rebuild search index → `{"status":"success","total_files":12,"total_entries":145}`

**stats:** Get statistics → `{"status":"success","total_entries":145,"categories":{...}}`

**migrate:** Import from `source_dir` → `{"status":"success","imported":23,"skipped":2}`

**info:** Get directory info → `{"status":"success","notes_dir":"/path","onedrive_detected":true}`

**validate:** Check files → `{"status":"success","files_checked":12,"issues":[...]}`

**clean-index:** Remove and rebuild → `{"status":"success","message":"Removed and rebuilt"}`

## Error Handling

All commands include `status` field. Check for errors:

```json
{"status":"error","message":"Description of error"}
```

When errors occur, inform user clearly and suggest corrective action.

## Workflows

**Add:** Infer category from keywords → extract topic → format "Category - Description" → execute add → confirm

**Search:** Extract terms → execute search → parse by relevance → present with dates → summarize

**Update:** Extract search term → execute append → check status → handle weak matches → confirm with timestamp

## Entry Format & Categories

Script automatically adds `**Created:** YYYY-MM-DD` to new notes and `**Update (YYYY-MM-DD):**` to updates.

Categories: Work, Learning, Meeting, Idea, Decision, Question, Reference, Note
