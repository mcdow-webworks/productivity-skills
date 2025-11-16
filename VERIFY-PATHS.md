# Verify Notes Directory Location

This guide helps verify that Claude Desktop and Claude Code use the same notes directory location.

## Current Default Behavior

The notes_manager.py script uses:
```python
NOTES_DIR = Path(os.environ.get('NOTES_DIR', Path.home() / 'notes'))
```

**Expected default:**
- Windows: `C:\Users\username\Documents\notes`
- macOS/Linux: `~/Documents/notes`

**Can be overridden with environment variable:**
```bash
export NOTES_DIR="$HOME/Documents/notes"
```

## Testing in Claude Code

In Claude Code terminal:

```bash
cd C:\Projects\productivity-skills
echo '{"command":"info"}' | python plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py
```

**Look for:**
- `notes_dir`: The actual path being used
- `home_dir`: User's home directory
- `notes_dir_exists`: Whether directory already exists

## Testing in Claude Desktop

In Claude Desktop conversation, ask:

```
Can you run the info command on the notes manager to show me where notes are being stored?
```

Claude should execute the notes_manager.py script and show you the path information.

**Alternative test:**
```
Note that I'm testing the notes directory location
```

Then check where the note was actually saved on your filesystem.

## Comparison

After testing both platforms, compare:

| Platform | notes_dir | home_dir |
|----------|-----------|----------|
| Claude Code | ___ | ___ |
| Claude Desktop | ___ | ___ |

## Common Scenarios

### Scenario 1: Different Paths (Problem)

**Claude Code:** `C:\Users\username\Documents\notes`
**Claude Desktop:** `C:\Users\username\CustomLocation\notes`

**Cause:** Different HOME environment variables or NOTES_DIR override

**Solution:** Set explicit NOTES_DIR environment variable for consistency:
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export NOTES_DIR="$HOME/Documents/notes"

# Or on Windows (System Environment Variables)
NOTES_DIR=C:\Users\username\Documents\notes
```

### Scenario 2: Same Path (Good)

Both platforms use `C:\Users\username\Documents\notes`

**No action needed** - they're already consistent! ✅

### Scenario 3: Prefer Documents Folder

If you prefer all notes in Documents folder:

1. **Option A: Environment Variable** (recommended)
   ```bash
   export NOTES_DIR="$HOME/Documents/notes"
   ```

2. **Option B: Already Using Documents Folder**

   The default has been updated to use `~/Documents/notes`. If you need
   a different location, use the environment variable method above.

## Why Documents Folder Might Be Better

**Advantages:**
- ✅ Standard Windows location for user documents
- ✅ Included in Windows backup by default
- ✅ Synced by OneDrive/Dropbox if configured
- ✅ Easier to find in File Explorer
- ✅ More discoverable for non-technical users

**Previous default (`~/notes`):**
- ✅ Simpler path
- ✅ Unix-like convention
- ❌ Less discoverable on Windows
- ❌ Not in default backup/sync locations

**Current default (`~/Documents/notes`):**
- ✅ Standard location across all platforms
- ✅ Included in Windows backup by default
- ✅ Synced by OneDrive/Dropbox if configured
- ✅ More discoverable
- ✅ Consistent with Claude Desktop behavior

## Recommendation

Based on your testing results, we can:

1. **Keep current default** if both platforms use the same path
2. **Change default to Documents** if that's more intuitive
3. **Document both options** and let users choose

Please run the tests above and share your results!

---

**Created:** 2025-11-16
**Purpose:** Verify cross-platform notes directory consistency
