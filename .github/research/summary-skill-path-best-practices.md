# Quick Reference: Skill Path Best Practices

**Last Updated:** 2025-11-18

---

## The One Critical Rule

**Always use `${CLAUDE_SKILL_ROOT}` to reference skill resources from SKILL.md**

```bash
# CORRECT
python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py

# WRONG - Only works if cwd happens to be skill directory
python3 scripts/notes_manager.py
```

---

## Why This Matters

**Skills execute in the USER'S working directory, not the skill directory.**

**Example:**
- User runs Claude Code in: `/c/Projects/my-app`
- Skill installed at: `~/.claude/plugins/marketplaces/foo/plugins/bar/skills/baz/`
- When skill executes: `pwd` returns `/c/Projects/my-app`

**Result:** Relative paths resolve from `/c/Projects/my-app`, NOT from the skill directory.

---

## Installation Locations

### Personal Skills
```
~/.claude/skills/<skill-name>/
```

### Project Skills
```
<project>/.claude/skills/<skill-name>/
```

### Plugin Skills
```
~/.claude/plugins/marketplaces/<marketplace>/plugins/<plugin>/skills/<skill>/
```

---

## Common Patterns

### Calling Python Scripts

```bash
# Basic execution
python3 ${CLAUDE_SKILL_ROOT}/scripts/script_name.py

# With JSON stdin
echo '{"command":"search"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/manager.py

# With arguments
python3 ${CLAUDE_SKILL_ROOT}/scripts/process.py input.txt output.txt
```

### Reading Reference Files

```bash
# Read documentation into context
cat ${CLAUDE_SKILL_ROOT}/references/api-docs.md

# Copy template
cp ${CLAUDE_SKILL_ROOT}/templates/template.md ./output.md
```

### Directory Structure

```
skill-name/
├── SKILL.md               # Skill definition with frontmatter
├── scripts/               # Executable scripts
│   └── manager.py
├── references/            # Docs loaded on-demand
│   └── advanced.md
├── templates/             # User-facing templates
│   └── template.md
└── assets/               # Binary resources
    └── icon.png
```

---

## Environment Variables

### Provided by Claude Code

**${CLAUDE_SKILL_ROOT}:**
- Absolute path to skill directory
- Set automatically when skill executes
- Cross-platform compatible

**CLAUDECODE:**
- Set to `1` when running inside Claude Code (v0.2.47+)
- Useful for conditional logic

### User-Defined

Skills can access user environment variables:

```python
import os
custom_dir = os.getenv('NOTES_DIR', os.path.expanduser('~/Documents/notes'))
```

---

## Path Style Rules

**Always Use:**
- Forward slashes: `scripts/helper.py` ✓
- Unix-style paths: `/path/to/file` ✓

**Never Use:**
- Backslashes: `scripts\helper.py` ✗
- Windows-style: `C:\path\to\file` ✗

**Reason:** Unix-style paths work on all platforms (including Windows via WSL)

---

## Cross-Platform Python Paths

```python
import os
from pathlib import Path

# Get skill root (always use Path objects)
skill_root = Path(os.getenv('CLAUDE_SKILL_ROOT'))

# Build paths using / operator
script_path = skill_root / 'scripts' / 'helper.py'
data_path = skill_root / 'data' / 'config.json'

# Expand user paths
notes_dir = Path.home() / 'Documents' / 'notes'

# Check if path exists
if script_path.exists():
    # Do something
```

---

## Testing Skills Locally

### Install and Test

```bash
# Install skill locally
cp -r skill-name ~/.claude/skills/

# Test from different directory
cd ~/Projects/test-project

# Trigger skill in Claude Code
"Use the skill..."
```

### Direct Script Testing

```bash
# Set environment variable
export CLAUDE_SKILL_ROOT="$HOME/.claude/skills/skill-name"

# Test script
echo '{"command":"test"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/manager.py
```

### Debug Output

```python
import sys

def debug_log(message):
    """Log to stderr (won't pollute stdout)"""
    print(f"DEBUG: {message}", file=sys.stderr)

debug_log(f"Skill root: {os.getenv('CLAUDE_SKILL_ROOT')}")
debug_log(f"Working dir: {os.getcwd()}")
```

---

## Common Mistakes to Avoid

### 1. Assuming cwd is Skill Directory

```bash
# BAD - Only works if cwd happens to be skill directory
python3 scripts/manager.py

# GOOD - Works from any directory
python3 ${CLAUDE_SKILL_ROOT}/scripts/manager.py
```

### 2. Hardcoded Paths

```bash
# BAD - Breaks on other systems
python3 ~/.claude/skills/note-taking/scripts/manager.py

# GOOD - Portable across installations
python3 ${CLAUDE_SKILL_ROOT}/scripts/manager.py
```

### 3. Windows-Style Paths

```bash
# BAD - Breaks on Unix systems
type ${CLAUDE_SKILL_ROOT}\references\docs.md

# GOOD - Works everywhere
cat ${CLAUDE_SKILL_ROOT}/references/docs.md
```

### 4. Direct File Manipulation

```bash
# BAD - Bypasses script logic, breaks encapsulation
cat ~/Documents/notes/2025/11-November.md

# GOOD - Uses skill's interface
echo '{"command":"search"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/manager.py
```

---

## Security Considerations

**Skills have full filesystem access (within user permissions):**

1. Validate all inputs in scripts
2. Sanitize file paths to prevent traversal
3. Fail safely with clear error messages
4. Document permission requirements
5. Don't expose sensitive data in error messages

---

## Quick Checklist

Before publishing a skill:

- [ ] All script references use `${CLAUDE_SKILL_ROOT}/`
- [ ] All paths use forward slashes (`/`)
- [ ] Python scripts use `pathlib.Path` objects
- [ ] Tested from different working directories
- [ ] Tested as personal skill (`~/.claude/skills/`)
- [ ] Tested as plugin skill (`.claude/plugins/...`)
- [ ] Scripts handle missing environment variables gracefully
- [ ] Error messages are helpful and don't expose sensitive data
- [ ] Documentation includes setup instructions
- [ ] Examples work copy-paste

---

## References

**Full Research:** See `research-skill-execution-environment.md`

**Official Docs:**
- https://code.claude.com/docs/en/skills
- https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- https://github.com/anthropics/skills

---

**Version:** 1.0
