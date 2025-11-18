# Summary: Path Best Practices for Claude Skills

**Quick Reference Guide** | Research Date: 2025-11-17

---

## TL;DR

1. **Use `scripts/` not `hooks/`** - Official Anthropic convention
2. **Always use `pathlib.Path`** - Modern Python standard (2025)
3. **Order matters:** `expanduser()` then `resolve()`
4. **OneDrive: Simple exists() check** - Works for 95% of cases
5. **Security: Use `is_relative_to()`** - Prevents path traversal

---

## Directory Naming: scripts/ vs hooks/

### Why scripts/ is the Standard

**Official Anthropic Skills Use `scripts/`:**
- ✅ webapp-testing skill: `scripts/`
- ✅ mcp-builder skill: `scripts/`
- ✅ All official examples: `scripts/`

**Semantic Clarity:**
- `scripts/` = General-purpose utilities, standalone executables
- `hooks/` = Git hooks, event-driven callbacks, framework lifecycle

**Industry Alignment:**
- Django, Flask, FastAPI: `scripts/`
- npm, many CLI tools: `bin/`
- Git hooks (version-controlled): `.githooks/` or `.git-hooks/`

**Recommendation:** Use `scripts/` for Claude Skills utilities.

---

## Python Pathlib Essentials

### Core Pattern

```python
from pathlib import Path
import os

# 1. Define default with OneDrive detection
def get_default_notes_dir() -> Path:
    onedrive_docs = Path.home() / 'OneDrive' / 'Documents' / 'notes'
    local_docs = Path.home() / 'Documents' / 'notes'

    if (Path.home() / 'OneDrive' / 'Documents').exists():
        return onedrive_docs
    return local_docs

# 2. Allow environment override
DEFAULT_NOTES_DIR = get_default_notes_dir()
NOTES_DIR = Path(os.environ.get('NOTES_DIR', DEFAULT_NOTES_DIR))

# 3. Normalize to absolute path
NOTES_DIR = NOTES_DIR.expanduser().resolve()

# 4. Create if needed
NOTES_DIR.mkdir(parents=True, exist_ok=True)
```

### Key Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `Path.home()` | User home directory | `/home/user` or `C:\Users\user` |
| `.expanduser()` | Expand `~` to home | `~/docs` → `/home/user/docs` |
| `.resolve()` | Make absolute, resolve symlinks | `../file` → `/abs/path/file` |
| `/` operator | Join paths | `base / 'sub' / 'file.txt'` |
| `.exists()` | Check if path exists | `True` or `False` |
| `.mkdir(parents=True)` | Create directory tree | Creates all intermediate dirs |
| `.glob('*.md')` | Pattern matching | Returns iterator of Path objects |
| `.relative_to(base)` | Make relative to base | `/a/b/c` relative to `/a` = `b/c` |
| `.read_text(encoding='utf-8')` | Read file content | Returns string |
| `.write_text(content, encoding='utf-8')` | Write file content | Writes string |

### Critical Order

```python
# ✅ CORRECT
path = Path('~/Documents/notes').expanduser().resolve()

# ❌ WRONG - resolve() fails on '~'
path = Path('~/Documents/notes').resolve().expanduser()

# ❌ INCOMPLETE - not absolute
path = Path('~/Documents/notes').expanduser()
```

**Rule:** Always `expanduser()` FIRST, then `resolve()`.

---

## OneDrive Path Detection

### The Challenge

Windows with OneDrive creates TWO Documents folders:
- Local: `C:\Users\username\Documents`
- OneDrive: `C:\Users\username\OneDrive\Documents`

Different Claude environments may use different defaults.

### Simple Solution (Recommended)

```python
def get_default_notes_dir() -> Path:
    """Prefer OneDrive Documents if it exists"""
    onedrive_docs = Path.home() / 'OneDrive' / 'Documents' / 'notes'
    local_docs = Path.home() / 'Documents' / 'notes'

    if (Path.home() / 'OneDrive' / 'Documents').exists():
        return onedrive_docs
    return local_docs
```

**Why This Works:**
- ✅ Simple and reliable
- ✅ No dependencies
- ✅ Works on Windows, macOS, Linux
- ✅ Handles 95% of OneDrive setups

### Advanced Solution (If Needed)

```python
import os

def get_default_notes_dir() -> Path:
    """Use environment variables for OneDrive detection"""
    # Check OneDrive environment variables (Windows)
    onedrive_root = os.getenv('OneDrive') or os.getenv('OneDriveConsumer')

    if onedrive_root:
        onedrive_docs = Path(onedrive_root) / 'Documents' / 'notes'
        if onedrive_docs.parent.exists():
            return onedrive_docs

    # Fall back to standard detection
    return get_default_notes_dir_simple()
```

**When to Use:**
- Enterprise/commercial skills
- Multiple OneDrive account support
- Advanced sync scenarios

**When NOT to Use:**
- Simple note-taking skills
- Most personal productivity tools
- Adds complexity with minimal benefit

---

## Security Best Practices

### Path Traversal Prevention

```python
def safe_path_join(base_dir: Path, user_input: str) -> Path:
    """Safely join user input to base directory"""
    base = base_dir.resolve()
    target = (base / user_input).resolve()

    # Ensure target is inside base_dir
    if not target.is_relative_to(base):
        raise ValueError(f"Path traversal detected: {user_input}")

    return target

# Usage
notes_dir = Path.home() / 'Documents' / 'notes'
safe_file = safe_path_join(notes_dir, user_filename)
```

### Input Validation

```python
def validate_heading(heading: str) -> bool:
    """Validate heading doesn't contain path separators"""
    if not heading or not heading.strip():
        return False

    # Reject path separators and traversal attempts
    if any(char in heading for char in ['/', '\\', '..', '\0']):
        return False

    return True
```

---

## Cross-Platform Gotchas

### Always Specify Encoding

```python
# ❌ BAD - Platform-dependent (Windows: cp1252, Linux: utf-8)
with open(file_path, 'r') as f:
    content = f.read()

# ✅ GOOD - Explicit UTF-8
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ✅ BETTER - Use pathlib methods
content = file_path.read_text(encoding='utf-8')
```

### Never Hardcode Separators

```python
# ❌ BAD - Platform-specific
path = base_dir + '\\subdir\\file.txt'  # Windows only

# ❌ BAD - Platform-specific
path = base_dir + '/subdir/file.txt'   # Unix only

# ✅ GOOD - Platform-independent
path = base_dir / 'subdir' / 'file.txt'
```

### Use pathlib for Globbing

```python
# ✅ GOOD - Clean and cross-platform
for year_dir in sorted(NOTES_DIR.glob('*/'), reverse=True):
    if year_dir.is_dir():
        for md_file in sorted(year_dir.glob('*.md'), reverse=True):
            process_file(md_file)

# ❌ BAD - Less readable, more error-prone
for root, dirs, files in os.walk(NOTES_DIR):
    for filename in files:
        if filename.endswith('.md'):
            process_file(os.path.join(root, filename))
```

---

## Common Patterns

### Pattern 1: Environment Variable Override

```python
DEFAULT_DIR = Path.home() / 'Documents' / 'notes'
NOTES_DIR = Path(os.environ.get('NOTES_DIR', DEFAULT_DIR)).expanduser().resolve()
NOTES_DIR.mkdir(parents=True, exist_ok=True)
```

### Pattern 2: Relative Path Display

```python
def get_display_path(file_path: Path, base_dir: Path) -> str:
    """Get user-friendly relative path for display"""
    try:
        return str(file_path.resolve().relative_to(base_dir.resolve()))
    except ValueError:
        return str(file_path.resolve())

# Shows: "2025/11-November.md" instead of full absolute path
```

### Pattern 3: Defensive File Operations

```python
def safe_read_file(file_path: Path) -> Optional[str]:
    """Safely read file with comprehensive error handling"""
    try:
        file_path = file_path.expanduser().resolve()

        if not file_path.exists():
            return None

        if file_path.is_dir():
            raise ValueError(f"{file_path} is a directory, not a file")

        return file_path.read_text(encoding='utf-8')

    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None
```

---

## Migration Checklist: hooks/ → scripts/

For notes_manager.py and note-taking skill:

**File Operations:**
- [ ] Rename directory: `mv hooks/ scripts/`
- [ ] Update SKILL.md: Change `hooks/notes_manager.py` → `scripts/notes_manager.py`
- [ ] Update CLAUDE.md documentation
- [ ] Update README.md examples

**Code Quality:**
- [ ] Verify all paths use `.resolve()`
- [ ] Check UTF-8 encoding is explicit everywhere
- [ ] Add input validation to user-facing functions
- [ ] Test OneDrive detection on Windows
- [ ] Test standard paths on macOS/Linux

**Documentation:**
- [ ] Update references from `hooks/` to `scripts/`
- [ ] Document OneDrive behavior in SKILL.md
- [ ] Update command examples in testing docs

---

## Quick Reference: Do's and Don'ts

### DO ✅

- Use `pathlib.Path` for all path operations
- Use `/` operator for joining paths
- Call `expanduser()` before `resolve()`
- Specify `encoding='utf-8'` explicitly
- Validate user input before using in paths
- Use `is_relative_to()` for security checks
- Create directories with `mkdir(parents=True, exist_ok=True)`
- Use `scripts/` directory for utilities
- Test on multiple operating systems
- Document OneDrive behavior

### DON'T ❌

- Use `os.path` for new code
- Hardcode path separators (`/` or `\\`)
- Trust platform default encoding
- Use user input directly in paths
- Forget to check if paths exist
- Use `hooks/` for utility scripts
- Assume case-insensitive filesystem
- Ignore path length limits (Windows)
- Skip error handling on file operations
- Use `relative_to()` without `resolve()`

---

## Testing Recommendations

### Local Testing

```bash
# Test on current platform
cd plugins/productivity-suite/skills/note-taking

# Test search
echo '{"command":"search","query":"test"}' | python scripts/notes_manager.py

# Test add
echo '{"command":"add","heading":"Test","content":"Content"}' | python scripts/notes_manager.py

# Test info (shows paths being used)
echo '{"command":"info"}' | python scripts/notes_manager.py
```

### Cross-Platform Testing

**Windows (PowerShell):**
```powershell
# Test OneDrive detection
$env:NOTES_DIR = "$HOME\OneDrive\Documents\notes"
python scripts/notes_manager.py info
```

**macOS/Linux:**
```bash
# Test custom directory
export NOTES_DIR="$HOME/custom-notes"
python scripts/notes_manager.py info
```

**Docker (Linux testing from Windows):**
```bash
docker run -it -v "$(pwd):/app" python:3.9 bash
cd /app/plugins/productivity-suite/skills/note-taking
python scripts/notes_manager.py info
```

---

## Additional Resources

- **Full Research:** See `research-cross-platform-paths.md`
- **Anthropic Skills Repo:** https://github.com/anthropics/skills
- **Python pathlib Docs:** https://docs.python.org/3/library/pathlib.html
- **Real Python Tutorial:** https://realpython.com/python-pathlib/
