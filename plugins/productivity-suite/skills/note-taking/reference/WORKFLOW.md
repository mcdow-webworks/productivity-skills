# Implementation Workflow

This document provides decision trees and workflow guidance for implementing the note-taking skill correctly.

## Command Selection Decision Tree

```
User Input
    │
    ├─> Contains "Note that", "Remember that", "Add a note"
    │   └─> ADD command
    │
    ├─> Contains "What did I note", "Show me my notes", "Find in my notes"
    │   └─> SEARCH command
    │
    ├─> Contains "Add to the X note", "Update my note about X"
    │   └─> APPEND command (search first, then append)
    │
    ├─> Contains "Reindex", "Rebuild index"
    │   └─> REINDEX command
    │
    ├─> Contains "How many notes", "Statistics", "Stats"
    │   └─> STATS command
    │
    └─> Contains "Import notes", "Migrate notes from"
        └─> MIGRATE command
```

## ADD Workflow

**Trigger Phrases:**
- "Note that..."
- "Add a note about..."
- "Remember that..."
- "Capture this..."

**Decision Process:**

1. **Extract Information**
   ```
   User says: "Note that I fixed the cache bug by updating headers"

   Extract:
   - Topic: "cache bug fix"
   - Details: "by updating headers"
   - Context: Current work session
   ```

2. **Infer Category**
   ```
   Keywords → Category
   - "fixed", "bug", "implemented" → Work
   - "learned", "discovered", "realized" → Learning
   - "discussed", "meeting", "talked" → Meeting
   - "idea", "what if", "could we" → Idea
   - "decided", "will", "going to" → Decision
   - "question", "how", "why" → Question
   ```

3. **Construct Heading**
   ```
   Format: "Category - Brief description"

   Example: "Work - Fixed cache bug"
   ```

4. **Construct Content**
   ```
   Include:
   - Full context from user message
   - Technical details
   - Relevant code snippets
   - Links if mentioned
   ```

5. **Execute Command**
   ```bash
   echo '{"command":"add","heading":"Work - Fixed cache bug","content":"Updated cache headers to fix bug. Changed max-age from 0 to 3600."}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
   ```

6. **Confirm to User**
   ```
   "Added to your November notes! I categorized it as 'Work' since it's a bug fix."
   ```

## SEARCH Workflow

**Trigger Phrases:**
- "What did I note about..."
- "Show me my notes on..."
- "Find in my notes..."
- "Search my notes for..."
- "What have I noted about..."

**Decision Process:**

1. **Extract Query Terms**
   ```
   User says: "What did I note about Claude Code skills?"

   Extract: "Claude Code skills"
   ```

2. **Execute Search**
   ```bash
   echo '{"command":"search","query":"Claude Code skills"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
   ```

3. **Parse Results**
   ```json
   {
     "success": true,
     "results": [
       {
         "heading": "Learning - Claude Code skills",
         "content": "...",
         "date": "2025-11-15",
         "relevance_score": 520
       }
     ],
     "count": 1
   }
   ```

4. **Format Response**
   ```
   High relevance (≥500):
   "You have a note from Nov 15 about Claude Code skills:

   Learning - Claude Code skills
   [Content preview...]

   This was created 2 days ago."

   Multiple results:
   "You have 3 notes about Claude Code skills:

   1. Nov 15 - Learning - Claude Code skills (score: 520)
   2. Nov 10 - Work - Implementing skills (score: 125)
   3. Nov 5 - Idea - New skill ideas (score: 75)

   The most relevant is from Nov 15."
   ```

5. **No Results**
   ```
   "I couldn't find any notes about Claude Code skills in your notes.

   Would you like to create one?"
   ```

## APPEND Workflow

**Trigger Phrases:**
- "Add to my note about..."
- "Update my X note with..."
- "Append to the X note..."

**Decision Process:**

1. **Extract Search Term**
   ```
   User says: "Add to my note about cache bug that it's now deployed"

   Extract:
   - Search term: "cache bug"
   - Update content: "now deployed"
   ```

2. **Search for Target Note**
   ```bash
   echo '{"command":"search","query":"cache bug"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
   ```

3. **Check Relevance Score**
   ```
   If top result score ≥ 50:
     → Proceed with append

   If top result score < 50:
     → Suggest alternatives
     → Ask user to clarify
   ```

4. **Execute Append (if strong match)**
   ```bash
   echo '{"command":"append","search_term":"cache bug","content":"Deployed to production successfully"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
   ```

5. **Confirm Update**
   ```
   "Updated your 'Work - Fixed cache bug' note from Nov 17:

   **Update (2025-11-17):** Deployed to production successfully

   This is your 2nd update to this note."
   ```

6. **Handle Weak Match**
   ```
   "I found these notes that might match 'cache bug':

   1. Work - Fixed cache bug (score: 45) - Nov 17
   2. Work - Cache optimization (score: 30) - Nov 10

   Which one would you like to update?"
   ```

## Category Inference

### Keyword-Based Inference

```python
category_keywords = {
    'Work': ['fixed', 'implemented', 'built', 'deployed', 'shipped', 'completed'],
    'Learning': ['learned', 'discovered', 'realized', 'understood', 'figured out'],
    'Meeting': ['discussed', 'meeting', 'talked about', 'agreed', 'decided in'],
    'Idea': ['idea', 'what if', 'could we', 'proposal', 'concept'],
    'Decision': ['decided', 'will', 'going to', 'chose', 'selected'],
    'Question': ['how', 'why', 'what if', 'wondering', 'question'],
    'Update': ['status', 'progress', 'update on', 'now', 'currently']
}
```

### Default Category

```
If no keywords match:
  → Use 'Update' as default
  → Mention to user: "I categorized this as 'Update' - let me know if you'd prefer a different category"
```

## Timestamp Management

### Automatic Timestamps

**New Entries:**
```markdown
# Work - Fixed cache bug
Updated cache headers to fix bug.

**Created:** 2025-11-17
```

**Updates/Appends:**
```markdown
# Work - Fixed cache bug
Updated cache headers to fix bug.

**Created:** 2025-11-17

**Update (2025-11-18):** Deployed to production
```

### Multiple Updates

```markdown
# Work - Fixed cache bug
Updated cache headers to fix bug.

**Created:** 2025-11-17

**Update (2025-11-18):** Deployed to production

**Update (2025-11-20):** Monitoring shows 50% reduction in cache misses
```

## Error Handling Workflow

### File Permission Errors

```
1. Catch error from script
2. Check if notes directory is writable
3. Suggest:
   "I couldn't write to your notes directory. Please check permissions:

   ls -la ~/Documents/notes/

   The directory should be writable by your user."
```

### Invalid JSON Errors

```
1. Validate input before sending to script
2. If validation fails:
   "I encountered an issue constructing the command. Let me try again..."
3. Log error for debugging
```

### Index Corruption

```
1. If search returns unexpected results
2. Suggest reindex:
   "Your search index might be out of sync. Would you like me to reindex your notes?"
3. If user agrees:
   echo '{"command":"reindex"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### Encoding Issues

```
1. If script reports encoding error
2. Suggest:
   "There's an encoding issue with one of your note files. Run:

   echo '{\"command\":\"validate\"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py

   This will identify which file needs fixing."
```

## Monthly File Management

### Automatic Monthly File Creation

```
User adds note in December:
  → Script checks if 2025/12-December.md exists
  → If not, creates it with header:
     # Notes - December 2025
  → Adds entry below header
```

### Year Rollover

```
User adds note in January 2026:
  → Script checks if 2026/ directory exists
  → If not, creates it
  → Creates 2026/01-January.md
  → Adds entry
```

## Content Formatting

### Code Blocks

```
User mentions code:
"Note that I fixed it with this function: def fix_cache()..."

Format as:
```markdown
# Work - Cache fix
Fixed cache issue with new function:

```python
def fix_cache():
    # implementation
```
```

### Lists

```
User mentions multiple items:
"Note that we decided: use PostgreSQL, deploy to AWS, start next week"

Format as:
```markdown
# Decision - Database and deployment
We decided on the following:
- Use PostgreSQL for database
- Deploy to AWS infrastructure
- Start implementation next week
```

### Links

```
User mentions URLs:
"Note that I found this great article: https://example.com/article"

Format as:
```markdown
# Learning - Great article on topic
Found excellent resource: [Article Title](https://example.com/article)

[Summary of key points...]
```

## Cross-Platform Considerations

### Path Handling

```
All paths use forward slashes:
  ~/Documents/notes/2025/11-November.md

Never use backslashes:
  ~\Documents\notes\2025\11-November.md
```

### OneDrive Detection

```
Script automatically detects OneDrive:
  1. Check if ~/OneDrive exists
  2. If yes, use ~/OneDrive/Documents/notes/
  3. If no, use ~/Documents/notes/

No manual configuration needed.
```

### Environment Variables

```
Check for custom directory:
  1. Check $NOTES_DIR environment variable
  2. If set, use that path
  3. If not set, use OneDrive detection logic
```

## Testing Workflow

### Before Deploying Changes

```
1. Test add command:
   echo '{"command":"add","heading":"Test - Note","content":"Test"}' | python3 scripts/notes_manager.py

2. Test search command:
   echo '{"command":"search","query":"test"}' | python3 scripts/notes_manager.py

3. Test append command:
   echo '{"command":"append","search_term":"Test","content":"Update"}' | python3 scripts/notes_manager.py

4. Verify files created:
   ls -la ~/Documents/notes/2025/

5. Check content:
   cat ~/Documents/notes/2025/11-November.md
```

### Integration Testing

```
1. Open Claude session
2. Test natural language:
   "Note that I'm testing the skill"
3. Verify Claude uses script (not Read/Write tools)
4. Test search:
   "What did I note about testing?"
5. Verify results formatted correctly
6. Test update:
   "Add to my testing note that it works"
7. Verify update appended with timestamp
```

## Success Indicators

You're implementing correctly when:
- ✅ All note operations use `notes_manager.py`
- ✅ Categories are inferred correctly
- ✅ Timestamps are added automatically
- ✅ Search results are ranked properly
- ✅ Updates go to correct notes (score ≥ 50)
- ✅ Errors are handled gracefully
- ✅ User receives conversational feedback

## Failure Indicators

You're NOT implementing correctly if:
- ❌ Using Read tool on note files
- ❌ Using Write/Edit tools on notes
- ❌ Bypassing script for any operation
- ❌ Not parsing JSON responses
- ❌ Not checking success field
- ❌ Not handling errors

## References

- [SKILL.md](../SKILL.md) - Implementation instructions
- [API.md](../docs/API.md) - Command reference
- [ALGORITHM.md](./ALGORITHM.md) - Search relevance scoring
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Error handling
