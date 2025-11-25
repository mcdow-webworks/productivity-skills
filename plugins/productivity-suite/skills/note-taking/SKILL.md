---
name: note-taking
description: ALWAYS use this skill when user says "Note that", "Remember that", "Add a note about", or explicitly asks about their notes with phrases like "What did I note about", "Show me my notes on", "Search my notes for", "Find in my notes", or "What have I noted about". This searches the user's persistent note-taking system (their second brain), NOT conversation history or general knowledge. Only trigger when the user explicitly mentions "note/notes/noted" or clearly refers to their personal knowledge system.
allowed-tools: Bash
---

<objective>
Manage user's persistent note-taking system ("second brain") stored in markdown files. All operations go through notes_manager.py script.
</objective>

<critical_rules>
**YOU MUST ALWAYS:**
- Use `scripts/notes_manager.py` for ALL note operations
- Pass JSON commands via stdin to the script
- Parse JSON responses and present them conversationally

**YOU MUST NEVER:**
- Use Read, Write, or Edit tools on note files in `~/Documents/notes/` or `~/OneDrive/Documents/notes/`
- Bypass the script to manipulate `.index.json` or markdown files directly
</critical_rules>

<script_invocation>
**Path Requirements:**
- Use tilde `~/.claude/plugins/...` (expands on all platforms)
- Use forward slashes `/` (works on Windows) - NEVER backslashes
- Use `python` (not `python3`)
- Use double quotes with escaped inner quotes

**Pattern:**
```bash
echo "{\"command\":\"<cmd>\",\"param\":\"value\"}" | python ~/.claude/plugins/marketplaces/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py
```

Script auto-detects notes directory (OneDrive on Windows, Documents otherwise, or `$NOTES_DIR` if set).
</script_invocation>

<api>
  <command name="add" purpose="Create new note">
    <request>{"command":"add","heading":"Category - Brief description","content":"Note text"}</request>
    <response>{"status":"success","file":"2025/11-November.md","heading":"Work - Title","path":"/full/path.md"}</response>
    <heading_format>
    Always "Category - Description". Never "Untitled". Infer category from keywords:
    - Work: "fixed", "built", "implemented", "deployed"
    - Learning: "learned", "discovered", "realized"
    - Meeting: "meeting", "discussed", "decided in meeting"
    - Idea: "what if", "consider", "idea"
    - Decision: "decided", "will", "plan to"
    - Question: "how", "why", "question about"
    - Reference: "record", "bookmark", "found"
    - Note: "note that", "remember"
    </heading_format>
  </command>

  <command name="search" purpose="Find notes">
    <request>{"command":"search","query":"search terms"}</request>
    <response>[{"heading":"Work - Title","content":"Preview...","file":"2025/11-November.md","date":"2025-11-17","relevance":520}]</response>
    <notes>Returns max 10 matches. Empty `[]` if none. Present high relevance (>=500) in full detail; multiple results by relevance with dates.</notes>
  </command>

  <command name="append" purpose="Update existing note">
    <request>{"command":"append","search_term":"unique term","content":"Update text"}</request>
    <response_success>{"status":"success","heading":"Work - Title","file":"2025/11-November.md","alternatives":[]}</response_success>
    <response_not_found>{"status":"not_found","query":"term","suggestion":"No matching entry found. Create a new note?"}</response_not_found>
    <response_ambiguous>{"status":"ambiguous","query":"term","alternatives":[{"heading":"Work - Title","relevance":45}],"message":"No strong match found."}</response_ambiguous>
    <notes>Requires relevance >=50. If weak match, suggest alternatives or create new note.</notes>
  </command>

  <command name="reindex" purpose="Rebuild search index">
    <request>{"command":"reindex"}</request>
    <response>{"status":"success","total_files":12,"total_entries":145}</response>
  </command>

  <command name="stats" purpose="Get statistics">
    <request>{"command":"stats"}</request>
    <response>{"status":"success","total_entries":145,"categories":{...}}</response>
  </command>

  <command name="info" purpose="Get directory info">
    <request>{"command":"info"}</request>
    <response>{"status":"success","notes_dir":"/path","onedrive_detected":true}</response>
  </command>

  <command name="validate" purpose="Check files for issues">
    <request>{"command":"validate"}</request>
    <response>{"status":"success","files_checked":12,"issues":[...]}</response>
  </command>

  <command name="clean-index" purpose="Remove and rebuild index">
    <request>{"command":"clean-index"}</request>
    <response>{"status":"success","message":"Removed and rebuilt"}</response>
  </command>

  <command name="migrate" purpose="Import from source directory">
    <request>{"command":"migrate","source_dir":"/path/to/source"}</request>
    <response>{"status":"success","imported":23,"skipped":2}</response>
  </command>
</api>

<workflows>
**Add:** Infer category from keywords -> extract topic -> format "Category - Description" -> execute add -> confirm

**Search:** Extract terms -> execute search -> parse by relevance -> present with dates -> summarize

**Update:** Extract search term -> execute append -> check status -> handle weak matches -> confirm with timestamp
</workflows>

<error_handling>
All commands include `status` field. Check for:
```json
{"status":"error","message":"Description of error"}
```
When errors occur, inform user clearly and suggest corrective action.
</error_handling>

<entry_format>
Script automatically adds `**Created:** YYYY-MM-DD` to new notes and `**Update (YYYY-MM-DD):**` to updates.

Categories: Work, Learning, Meeting, Idea, Decision, Question, Reference, Note
</entry_format>

<success_criteria>
- Note operations complete with "success" status
- User receives conversational confirmation
- Search returns relevant results sorted by relevance score
- Updates append to correct entry with timestamp
</success_criteria>
