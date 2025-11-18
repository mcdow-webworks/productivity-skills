# Troubleshooting Guide

This document provides solutions to common issues when implementing the note-taking skill.

## Common Issues

### 1. "Claude Can't Find My Notes"

**Symptoms:**
- Search returns no results
- User reports notes exist but Claude can't see them

**Diagnosis:**
```bash
# Check if notes directory exists
ls -la ~/Documents/notes/

# Check if index exists
ls -la ~/Documents/notes/.index.json

# Check for year directories
ls -la ~/Documents/notes/2025/
```

**Solutions:**

**A. Missing Index File**
```bash
# Reindex all notes
echo '{"command":"reindex"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**B. Wrong Directory Location**
```bash
# Check OneDrive location if on Windows
ls -la ~/OneDrive/Documents/notes/

# Check custom directory
echo $NOTES_DIR
```

**C. Permission Issues**
```bash
# Check permissions
ls -la ~/Documents/notes/

# Should see: drwxr-xr-x (or similar)
# If not, fix permissions:
chmod 755 ~/Documents/notes/
chmod 644 ~/Documents/notes/2025/*.md
```

### 2. "Entries Aren't Updating"

**Symptoms:**
- Append command completes but note isn't updated
- Updates go to wrong entries

**Diagnosis:**
```bash
# Check relevance scores
echo '{"command":"search","query":"your search term"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py

# Look for relevance_score in results
# Should be ≥ 50 for updates
```

**Solutions:**

**A. Low Relevance Score (< 50)**
```
Problem: Search term doesn't strongly match any note

Solution:
1. Use more specific search terms
2. Include exact phrase from note heading
3. Create new note instead of updating

Example:
Instead of: "update testing"
Use: "update testing note-taking skill"
```

**B. Multiple Strong Matches**
```
Problem: Multiple notes match with score ≥ 50

Solution:
1. Be more specific in search term
2. Include category in search
3. Review search results first, then append to specific note

Example:
"Show me my notes about testing"
[Review results]
"Update my 'Testing note-taking skill' note with..."
```

**C. File Write Permissions**
```bash
# Check if files are writable
ls -la ~/Documents/notes/2025/11-November.md

# Should see: -rw-r--r-- (or similar)
# If not, fix:
chmod 644 ~/Documents/notes/2025/11-November.md
```

### 3. "Search Not Working"

**Symptoms:**
- Search returns unexpected results
- Old notes don't appear in search
- Recently added notes not found

**Diagnosis:**
```bash
# Check index file
cat ~/Documents/notes/.index.json | python3 -m json.tool | head -50

# Check if index is outdated
stat ~/Documents/notes/.index.json
stat ~/Documents/notes/2025/11-November.md

# Index should be newer than or equal to note files
```

**Solutions:**

**A. Outdated Index**
```bash
# Rebuild index
echo '{"command":"reindex"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**B. Corrupted Index**
```bash
# Clean and rebuild
echo '{"command":"clean-index"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
echo '{"command":"reindex"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**C. File Headers in Results**
```
Problem: Search returns "Notes - November 2025" entries

Solution: Update notes_manager.py to filter file headers
(This should be automatic - if seeing this, check script version)
```

### 4. "Script Errors"

**Symptoms:**
- JSON error messages
- Python exceptions
- Command fails to execute

**Diagnosis:**
```bash
# Test script directly
echo '{"command":"info"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py

# Check for errors in output
```

**Solutions:**

**A. Invalid JSON**
```
Error: "JSONDecodeError: Expecting property name"

Problem: Malformed JSON input

Solution: Ensure JSON is properly formatted:
- Use double quotes for strings
- Escape special characters
- No trailing commas

Example:
Wrong: {"command":"add","heading":'Test'}
Right: {"command":"add","heading":"Test"}
```

**B. Missing Required Parameters**
```
Error: "Missing required parameter: heading"

Problem: Command missing required fields

Solution: Check API reference for required parameters:
- add: requires "heading" and "content"
- search: requires "query"
- append: requires "search_term" and "content"
```

**C. Python Path Issues**
```
Error: "python3: command not found"

Problem: Python not in PATH or wrong Python version

Solution:
# Check Python version
python --version  # Should be 3.7+

# Try alternative command:
python ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py

# Or use full path:
/usr/bin/python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### 5. "Encoding Issues"

**Symptoms:**
- Special characters display incorrectly
- Unicode errors
- "UnicodeDecodeError" messages

**Diagnosis:**
```bash
# Check file encoding
file ~/Documents/notes/2025/11-November.md

# Should show: "UTF-8 Unicode text"
```

**Solutions:**

**A. Wrong Encoding**
```bash
# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 ~/Documents/notes/2025/11-November.md > temp.md
mv temp.md ~/Documents/notes/2025/11-November.md

# Reindex after conversion
echo '{"command":"reindex"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**B. Mixed Encodings**
```bash
# Validate all files
echo '{"command":"validate"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py

# Fix reported issues individually
```

### 6. "OneDrive Sync Issues"

**Symptoms:**
- Notes appear in one session but not another
- Conflicts between Claude Desktop and Claude Code
- Duplicate entries

**Diagnosis:**
```bash
# Check OneDrive status
ls -la ~/OneDrive/Documents/notes/

# Check if OneDrive is syncing
# Look for .tmp or conflict files
ls -la ~/OneDrive/Documents/notes/**/*.tmp
```

**Solutions:**

**A. Sync Conflicts**
```
Problem: OneDrive created conflict files

Solution:
1. Resolve conflicts manually
2. Delete conflict files after merging
3. Reindex notes
```

**B. Directory Mismatch**
```
Problem: Claude Desktop uses OneDrive, Claude Code uses local Documents

Solution: Set NOTES_DIR to consistent location:
export NOTES_DIR="$HOME/OneDrive/Documents/notes"

Add to ~/.bashrc or ~/.zshrc for persistence
```

### 7. "Claude Uses Read/Write Tools Instead of Script"

**Symptoms:**
- Claude reads note files directly with Read tool
- Claude writes to files with Write/Edit tools
- Script is bypassed

**Diagnosis:**
```
Review Claude's tool usage in session
Look for: "Using Read tool on ~/Documents/notes/..."
Expected: "Using Bash tool with notes_manager.py"
```

**Solutions:**

**A. SKILL.md Not Updated**
```
Problem: Old SKILL.md doesn't have implementation instructions

Solution:
1. Ensure SKILL.md has CRITICAL RULES section
2. Verify allowed-tools: Bash in frontmatter (Claude Code only)
3. Check SKILL.md clearly states MUST use script
```

**B. Skill Not Loaded**
```
Problem: Skill not properly installed or enabled

Solution:
# Check skill installation
ls -la ${CLAUDE_SKILL_ROOT}/

# Should see SKILL.md and scripts/ directory
# Reinstall if missing files
```

## Error Messages Reference

### "File not found"

**Full Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/notes/...'
```

**Meaning:** Script trying to access file/directory that doesn't exist

**Solution:**
```bash
# Create notes directory
mkdir -p ~/Documents/notes/2025/

# Or run migration to set up structure
echo '{"command":"migrate","source_dir":"/tmp/empty"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### "Permission denied"

**Full Error:**
```
PermissionError: [Errno 13] Permission denied: '/path/to/notes/...'
```

**Meaning:** Script can't write to notes directory

**Solution:**
```bash
# Fix directory permissions
chmod 755 ~/Documents/notes/
chmod 755 ~/Documents/notes/2025/
chmod 644 ~/Documents/notes/2025/*.md
```

### "JSONDecodeError"

**Full Error:**
```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
```

**Meaning:** Invalid JSON input to script

**Solution:**
```
Ensure JSON uses double quotes:
Wrong: {'command':'add'}
Right: {"command":"add"}
```

### "No note found matching"

**Full Error:**
```
No note found matching 'search term' with sufficient relevance (minimum: 50)
```

**Meaning:** Search term didn't match any notes strongly enough for update

**Solution:**
1. Review alternative matches in error message
2. Use more specific search term
3. Create new note instead of updating

## Preventive Measures

### Regular Maintenance

```bash
# Weekly: Reindex notes
echo '{"command":"reindex"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py

# Monthly: Validate files
echo '{"command":"validate"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py

# Check stats
echo '{"command":"stats"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### Backup Strategy

```bash
# Backup notes (recommended weekly)
cp -r ~/Documents/notes ~/Documents/notes-backup-$(date +%Y%m%d)

# Or use git
cd ~/Documents/notes
git init
git add .
git commit -m "Backup $(date +%Y-%m-%d)"
```

### Version Control

```bash
# Initialize git in notes directory
cd ~/Documents/notes
git init
echo '.index.json' > .gitignore
git add .
git commit -m "Initial commit"

# Commit after major changes
git add -A
git commit -m "Added notes about X"
```

## Getting Help

### Information to Include

When reporting issues, include:

1. **Error message** (exact text)
2. **Command used**
3. **System info**:
   ```bash
   python3 --version
   echo $NOTES_DIR
   ls -la ~/Documents/notes/
   ```
4. **Script output**:
   ```bash
   echo '{"command":"info"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
   ```

### Where to Report

- **GitHub Issues**: https://github.com/mcdow-webworks/productivity-skills/issues
- **Discussions**: https://github.com/mcdow-webworks/productivity-skills/discussions

### Debug Mode

```bash
# Run script with error details
echo '{"command":"search","query":"test"}' | python3 -u ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py 2>&1
```

## Advanced Troubleshooting

### Inspect Index Manually

```bash
# View index structure
cat ~/Documents/notes/.index.json | python3 -m json.tool | less

# Count entries
cat ~/Documents/notes/.index.json | python3 -c "import json, sys; print(len(json.load(sys.stdin).get('entries', [])))"

# Find specific entry
cat ~/Documents/notes/.index.json | python3 -m json.tool | grep -A 5 "search term"
```

### Test Relevance Scoring

```bash
# Search and view scores
echo '{"command":"search","query":"your term"}' | \
  python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py | \
  python3 -m json.tool | \
  grep -E "(heading|relevance_score)"
```

### Verify Script Execution

```bash
# Test each command
for cmd in add search append reindex stats info; do
  echo "Testing $cmd..."
  # Add appropriate parameters for each command
done
```

## Related Documentation

- [SKILL.md](../SKILL.md) - Implementation instructions
- [API.md](../docs/API.md) - Command reference
- [WORKFLOW.md](./WORKFLOW.md) - Decision trees
- [ALGORITHM.md](./ALGORITHM.md) - Search scoring
- [USER_GUIDE.md](../docs/USER_GUIDE.md) - User documentation
