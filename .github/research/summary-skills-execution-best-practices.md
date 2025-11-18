# Summary: Claude Skills Execution Best Practices

**Quick Reference for Skill Authors**
**Last Updated:** 2025-11-18

---

## TL;DR

- Use **relative paths** in SKILL.md (`scripts/run.py`, not absolute paths)
- Scripts should use `Path(__file__).parent.parent` to find skill root
- Always use **forward slashes** (`/`), even on Windows
- Document as `python3`, warn Windows Anaconda users
- Working directory is **unreliable** - pass absolute paths to scripts
- No environment variables for skill location - compute from `__file__`

---

## Path Handling

### In SKILL.md (Relative Paths)

```markdown
✓ CORRECT
Run the analyzer: python scripts/analyze.py input.txt
See reference documentation: `reference/api-docs.md`
Use template: templates/default.md

✗ WRONG
Run: python /Users/username/.claude/skills/my-skill/scripts/analyze.py
Run: python scripts\analyze.py  (Windows-style backslash)
```

**Why:** Claude automatically converts relative paths to absolute using the base directory provided at skill invocation.

### In Python Scripts (Compute Skill Root)

```python
from pathlib import Path

# Assumes script is in scripts/ subfolder
SKILL_ROOT = Path(__file__).parent.parent

# Access resources
template_path = SKILL_ROOT / "templates" / "default.md"
reference_path = SKILL_ROOT / "reference" / "api-docs.md"

# Read files
with open(template_path, 'r', encoding='utf-8') as f:
    template = f.read()
```

**Why:** No environment variables like `$SKILL_ROOT` are available. Scripts must compute their location.

### Cross-Platform Compatibility

```python
✓ CORRECT - Path objects (Python 3.4+)
from pathlib import Path
path = Path("templates") / "default.md"

✓ CORRECT - Forward slashes in strings
path = "templates/default.md"

✗ WRONG - os.path.join (platform-specific)
import os
path = os.path.join("templates", "default.md")  # Creates "templates\\default.md" on Windows

✗ WRONG - Backslashes
path = "templates\\default.md"  # Fails on macOS/Linux
```

---

## Python Executable

### In Documentation

```markdown
# SKILL.md
Run the script: python3 scripts/process.py

**Requirements:** Python 3.7+ with packages: requests, pathlib

**Windows Anaconda Users:** Claude Code requires python3 executable.
Create symlink: mklink python3.exe python.exe in Scripts folder.
```

### In Scripts

```python
#!/usr/bin/env python3
# ^ Shebang for clarity (not always used by Claude)

import sys

# Check version if needed
if sys.version_info < (3, 7):
    print("Error: Python 3.7+ required", file=sys.stderr)
    sys.exit(1)
```

### Known Issue

**Windows Anaconda users cannot run Claude Code** due to hardcoded `python3` requirement:
- Anaconda uses `python.exe`, not `python3.exe`
- Workaround: Create symlink or use WSL
- GitHub Issue: [#7364](https://github.com/anthropics/claude-code/issues/7364)

---

## Working Directory

### Do NOT Rely on Current Working Directory

```python
✗ WRONG - Assumes cwd is skill directory
with open("templates/default.md", 'r') as f:  # May fail!
    template = f.read()

✓ CORRECT - Compute from script location
from pathlib import Path
SKILL_ROOT = Path(__file__).parent.parent
template_path = SKILL_ROOT / "templates" / "default.md"
with open(template_path, 'r') as f:
    template = f.read()
```

**Why:** Working directory behavior is unpredictable and varies by:
- How Claude Code was launched
- Project vs user-level skill
- Security restrictions on `cd` command

### Script Arguments Should Be Absolute Paths

```markdown
# SKILL.md
Run: python scripts/process.py /full/path/to/input.txt /full/path/to/output.txt
```

Claude constructs absolute paths before invoking. Scripts can trust these are valid.

---

## Environment Variables

### No Skill-Specific Variables

```bash
# These DO NOT EXIST:
$SKILL_ROOT
$SKILL_BASE_DIR
$CLAUDE_SKILL_PATH
{baseDir}  # Undocumented, use with caution
```

### User Variables Are Available

```python
import os

# User-defined variables work
notes_dir = os.getenv("NOTES_DIR", os.path.expanduser("~/Documents/notes"))

# Standard environment variables
home = os.getenv("HOME")  # Unix
appdata = os.getenv("APPDATA")  # Windows
```

---

## Script Design Patterns

### Accept Absolute Paths as Arguments

```python
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=Path, help="Input file (absolute path)")
parser.add_argument("--output", type=Path, help="Output file (absolute path)")
args = parser.parse_args()

# Verify paths are absolute (optional but recommended)
if not args.input_file.is_absolute():
    print(f"Warning: Expected absolute path, got {args.input_file}", file=sys.stderr)
```

### Use JSON for Structured Input/Output

```python
import json
import sys

# Read JSON from stdin
try:
    data = json.load(sys.stdin)
    command = data["command"]
    params = data.get("params", {})
except json.JSONDecodeError as e:
    print(json.dumps({"error": f"Invalid JSON: {e}"}), file=sys.stderr)
    sys.exit(1)

# Process...

# Output JSON to stdout
result = {
    "status": "success",
    "entries": 42,
    "categories": ["Work", "Personal"]
}
print(json.dumps(result, indent=2))
```

### Handle Errors Gracefully

```python
import sys
import json

try:
    # Your processing logic
    process_file(input_path)
except FileNotFoundError as e:
    print(json.dumps({"error": f"File not found: {e}"}), file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(json.dumps({"error": f"Unexpected error: {e}"}), file=sys.stderr)
    sys.exit(1)
```

---

## Directory Structure

### Recommended Layout

```
skill-name/
├── SKILL.md                    # Required - entry point (concise!)
├── scripts/                    # Executable code
│   ├── main_task.py           # Primary operations
│   ├── utilities.py           # Helper functions
│   └── __init__.py            # Optional (makes it a package)
├── reference/                  # Detailed documentation (loaded on demand)
│   ├── api-reference.md
│   ├── examples.md
│   └── troubleshooting.md
└── templates/                  # Static resources
    ├── default.md
    └── advanced.md
```

### Progressive Disclosure

**SKILL.md should be concise** (under 500 lines):

```markdown
# My Skill

Brief overview and common operations.

## Quick Start

python scripts/run.py <input_file>

## Advanced Usage

For detailed API reference, see `reference/api-reference.md`
For examples, see `reference/examples.md`
For troubleshooting, see `reference/troubleshooting.md`
```

**Why:** Claude loads reference files **only when needed**, preserving context window.

---

## SKILL.md Best Practices

### Be Explicit About Execution

```markdown
✓ CLEAR - Action to take
Run the analyzer: python scripts/analyze.py input.pdf

✗ AMBIGUOUS - Read or run?
The analyze.py script can help with PDF analysis
```

### Distinguish Run vs Read

```markdown
# For Execution
Run `scripts/extract.py` to extract form fields

# For Reference
See `scripts/extract.py` for the extraction algorithm
Read `reference/api-docs.md` for available functions
```

### Include Expected Output

```markdown
Run: python scripts/stats.py notes.md

Expected output (JSON):
{
  "entries": 42,
  "categories": ["Work", "Personal", "Learning"],
  "date_range": ["2025-01-01", "2025-11-18"]
}
```

---

## Testing Checklist

Before releasing a skill, test:

- [ ] **Multiple platforms:** macOS, Linux, Windows WSL
- [ ] **Different Python installations:** system Python, Anaconda, pyenv
- [ ] **Different working directories:** Launch Claude Code from various locations
- [ ] **Relative and absolute input paths:** Both should work
- [ ] **Missing files:** Scripts handle FileNotFoundError gracefully
- [ ] **Missing dependencies:** Clear error message if packages not installed
- [ ] **Edge cases:** Empty inputs, large files, special characters in paths

---

## Common Mistakes to Avoid

### 1. Hardcoded Absolute Paths

```markdown
✗ WRONG
python /Users/myuser/.claude/skills/my-skill/scripts/run.py

✓ CORRECT
python scripts/run.py
```

### 2. Windows-Style Backslashes

```markdown
✗ WRONG
See reference\api-docs.md

✓ CORRECT
See reference/api-docs.md
```

### 3. Relying on Current Working Directory

```python
✗ WRONG
with open("templates/default.md") as f:  # Assumes cwd

✓ CORRECT
from pathlib import Path
SKILL_ROOT = Path(__file__).parent.parent
with open(SKILL_ROOT / "templates" / "default.md") as f:
```

### 4. Assuming Environment Variables

```python
✗ WRONG
skill_root = os.getenv("SKILL_ROOT")  # Does not exist!

✓ CORRECT
skill_root = Path(__file__).parent.parent
```

### 5. Using `python` Instead of `python3` in Docs

```markdown
✗ INCONSISTENT (may work but non-standard)
python scripts/run.py

✓ CORRECT (Unix convention, matches most platforms)
python3 scripts/run.py
```

**Note:** Some Anthropic examples use `python`, but `python3` is safer for documentation.

---

## Quick Reference: File Paths Checklist

| Context | Use | Example |
|---------|-----|---------|
| SKILL.md → scripts | Relative, forward slashes | `python scripts/run.py` |
| SKILL.md → reference | Relative, forward slashes | `reference/api-docs.md` |
| SKILL.md → templates | Relative, forward slashes | `templates/default.md` |
| Python → skill root | Compute from `__file__` | `Path(__file__).parent.parent` |
| Python → resources | `SKILL_ROOT / "path"` | `SKILL_ROOT / "templates" / "file.md"` |
| Script arguments | Accept absolute paths | `parser.add_argument("file", type=Path)` |
| Environment vars | User-defined only | `os.getenv("NOTES_DIR", default)` |

---

## Resources

- **Full Research:** [research-claude-skills-execution.md](./research-claude-skills-execution.md)
- **Official Spec:** [agent_skills_spec.md](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)
- **Best Practices:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- **Example Skills:** [Anthropic Skills Repository](https://github.com/anthropics/skills)

---

## Contributing

Found new information about skill execution? Please update:
1. [research-claude-skills-execution.md](./research-claude-skills-execution.md) with detailed findings
2. This summary with actionable guidance
3. Include sources (docs, GitHub issues, community posts)

**Areas needing clarification:**
- Exact working directory behavior on skill invocation
- Official environment variables (if any exist)
- Security/sandboxing model for script execution
- Dependency management best practices
