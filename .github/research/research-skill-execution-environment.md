# Research: Claude Code Skill Execution Environment

**Research Date:** 2025-11-18
**Researcher:** Claude (Sonnet 4.5)
**Purpose:** Understand how Claude Code executes skills, manages file paths, and accesses plugin resources

---

## Executive Summary

**Key Finding:** Claude Code provides the environment variable `${CLAUDE_SKILL_ROOT}` that points to the absolute path of the skill directory when a skill executes. This enables skills to reference their bundled scripts and resources using a reliable, cross-platform path.

**Critical Discovery:** Skills execute with the USER'S working directory as cwd (e.g., `/c/Projects/productivity-skills`), NOT the skill's directory. Therefore, relative paths like `scripts/notes_manager.py` will NOT work unless prefixed with `${CLAUDE_SKILL_ROOT}`.

**Best Practice:** Always use `${CLAUDE_SKILL_ROOT}/scripts/script_name.py` to reference skill resources from SKILL.md.

---

## 1. Plugin Installation Locations

### Personal Skills
```
~/.claude/skills/<skill-name>/
```
- Available across all projects
- User-specific

### Project Skills
```
<project-root>/.claude/skills/<skill-name>/
```
- Checked into git
- Shared with team

### Plugin Skills
```
~/.claude/plugins/marketplaces/<marketplace-name>/plugins/<plugin-name>/skills/<skill-name>/
```
- Installed via marketplace
- Example: `~/.claude/plugins/marketplaces/claude-code-plugins/plugins/frontend-design/skills/frontend-design/`

**Windows Example:**
```
C:\Users\username\.claude\plugins\marketplaces\productivity-skills\plugins\productivity-suite\skills\note-taking\
```

**Structure After Installation:**
```
plugins/productivity-suite/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── note-taking/
        ├── SKILL.md
        ├── scripts/
        │   └── notes_manager.py
        ├── templates/
        └── examples/
```

---

## 2. Skill Execution Environment

### Working Directory Behavior

**Critical Finding:** When a skill executes, the working directory is **NOT** the skill directory - it's the user's current working directory.

**Example:**
- User runs Claude Code in: `/c/Projects/my-app`
- Skill installed at: `~/.claude/plugins/marketplaces/foo/plugins/bar/skills/baz/`
- When skill executes: `pwd` returns `/c/Projects/my-app`

**Implication:** Relative paths in SKILL.md resolve relative to the user's working directory, NOT the skill directory.

### How Claude Accesses Skills

According to research from [mikhail.io](https://mikhail.io/2025/10/claude-code-skills/):

> When a skill is invoked, the system response includes "the base path and SKILL.md body" enabling Claude to locate resources. The base path (e.g., `/Users/username/.claude/skills/pdf/`) is provided in the tool response.

**What This Means:**
1. Claude receives the skill's absolute path as context
2. This path is exposed via `${CLAUDE_SKILL_ROOT}` environment variable
3. Skills can use this variable to reference their resources

---

## 3. The ${CLAUDE_SKILL_ROOT} Environment Variable

### Discovery

The `${CLAUDE_SKILL_ROOT}` variable is the **officially supported** way to reference skill resources. It's automatically set by Claude Code when a skill executes.

### Usage Examples

**Calling a Python script:**
```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/helper.py
```

**With JSON stdin:**
```bash
echo '{"command":"search","query":"test"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Reading a reference file:**
```bash
cat ${CLAUDE_SKILL_ROOT}/references/api-docs.md
```

### Cross-Platform Compatibility

The variable works across all platforms:
- **macOS/Linux:** Expands to `/Users/username/.claude/skills/skill-name`
- **Windows (WSL):** Expands to `/c/Users/username/.claude/plugins/.../skill-name`
- **Windows (Native):** Expands to `C:\Users\username\.claude\plugins\...\skill-name`

---

## 4. Alternative Patterns Observed

### Pattern 1: Direct Script Name (Anthropic's xlsx skill)

**Location:** [anthropics/skills/document-skills/xlsx](https://github.com/anthropics/skills/tree/main/document-skills/xlsx)

**Directory Structure:**
```
xlsx/
├── SKILL.md
├── recalc.py          # Script at root level
└── LICENSE.txt
```

**SKILL.md Reference:**
```bash
python recalc.py <excel_file> [timeout_seconds]
```

**Why This Works:**
- The script is at the ROOT of the skill directory (not in `scripts/`)
- Claude's base path points to the skill root
- Simple filename resolution works

**Limitation:** Doesn't scale well for skills with multiple scripts or organized subdirectories.

### Pattern 2: scripts/ Prefix (Anthropic's skill-creator)

**Location:** [anthropics/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator)

**Directory Structure:**
```
skill-creator/
├── SKILL.md
├── scripts/
│   ├── init_skill.py
│   └── package_skill.py
├── references/
└── LICENSE.txt
```

**SKILL.md Reference:**
```bash
scripts/init_skill.py <skill-name> --path <output-directory>
scripts/package_skill.py <path/to/skill-folder>
```

**Why This Works:**
- Assumes execution from skill root directory
- Uses relative paths from skill root

**Question:** Is Claude automatically `cd`ing to the skill directory? Or is this relying on `${CLAUDE_SKILL_ROOT}` being prepended?

---

## 5. Best Practices for Path Handling

### Recommended Approach

**Use `${CLAUDE_SKILL_ROOT}` for all skill resources:**

```bash
# Python scripts
python3 ${CLAUDE_SKILL_ROOT}/scripts/script_name.py

# Reading reference files
cat ${CLAUDE_SKILL_ROOT}/references/docs.md

# Templates
cp ${CLAUDE_SKILL_ROOT}/templates/template.md ./output.md
```

### Path Style Requirements

**Official Documentation States:**
> Use Unix-style paths (like `scripts/helper.py`) which work across all platforms, while Windows-style paths cause errors on Unix systems.

**Always Use:**
- Forward slashes: `scripts/helper.py` ✓
- Unix-style paths: `${CLAUDE_SKILL_ROOT}/scripts/helper.py` ✓

**Never Use:**
- Backslashes: `scripts\helper.py` ✗
- Windows-style: `C:\path\to\script.py` ✗

### Directory Organization

**Recommended Structure:**
```
skill-name/
├── SKILL.md               # Main skill definition
├── scripts/               # Executable scripts
│   ├── main.py
│   └── utils.py
├── references/            # Documentation loaded on-demand
│   └── advanced.md
├── templates/             # User-facing templates
│   └── template.md
└── assets/               # Binary resources
    └── icon.png
```

**Rationale:**
- `scripts/` - Clear separation of executable code
- `references/` - Progressive disclosure (loaded only when needed)
- `templates/` - Resources users will copy/modify
- `assets/` - Supporting files (images, fonts, etc.)

---

## 6. Script Execution Patterns

### Stdin/Stdout Pattern (Recommended for Complex Operations)

**Benefits:**
- Clean separation between Claude and script logic
- Structured data exchange (JSON)
- Error handling via exit codes + JSON responses
- No context pollution (script code never enters Claude's context)

**Example:**
```bash
echo '{"command":"search","query":"test"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Script Response:**
```json
{
  "success": true,
  "results": [
    {"heading": "Work - Feature X", "content": "...", "file": "2025/11-November.md"}
  ]
}
```

### Direct Output Pattern (Simple Operations)

**Benefits:**
- Straightforward for simple scripts
- Direct text output

**Example:**
```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/count_lines.py file.txt
```

**Output:**
```
42 lines
```

---

## 7. Sandbox and Security Considerations

### Execution Sandbox

**Finding:** Skills do NOT run in a restricted sandbox. They execute in Claude Code's VM environment with:
- Full filesystem access (subject to user permissions)
- Ability to execute any shell commands
- Network access
- Process spawning capabilities

**From Official Docs:**
> Skills leverage Claude's VM environment to provide capabilities beyond what's possible with prompts alone. Claude operates in a virtual machine with filesystem access, allowing Skills to exist as directories containing instructions, executable code, and reference materials.

### Security Implications

**Script Permissions:**
- Scripts need execute permissions: `chmod +x scripts/*.py`
- Scripts can access any file the user can access
- Scripts can make network requests
- Scripts can modify user data

**Best Practices:**
1. **Validate all inputs** in scripts
2. **Use explicit paths** to prevent path traversal
3. **Sanitize user input** before file operations
4. **Fail safely** with clear error messages
5. **Document permission requirements** in SKILL.md

---

## 8. Environment Variables Available

### Confirmed Environment Variables

**${CLAUDE_SKILL_ROOT}:**
- Points to skill's installation directory
- Set automatically by Claude Code
- Works across all platforms

**CLAUDECODE:**
- Added in Claude Code v0.2.47
- Set to `1` when running inside Claude Code
- Useful for conditional logic in scripts
- Source: [GitHub Issue #531](https://github.com/anthropics/claude-code/issues/531)

### User-Defined Environment Variables

Skills can access user-defined environment variables:

**Example (from note-taking skill):**
```bash
# Optional: Custom notes directory
export NOTES_DIR="$HOME/my-custom-notes"
```

**In Python Script:**
```python
import os
notes_dir = os.getenv('NOTES_DIR', os.path.expanduser('~/Documents/notes'))
```

---

## 9. Cross-Platform Path Resolution

### Windows Considerations

**Claude Code on Windows:**
- Requires WSL (Windows Subsystem for Linux)
- Paths in WSL use Unix format: `/c/Users/username/...`
- Windows paths (`C:\Users\...`) are converted to WSL format
- `${CLAUDE_SKILL_ROOT}` expands to Unix-style paths even on Windows

**OneDrive Detection (Specific to Our Use Case):**
```python
import os
from pathlib import Path

# Prefer OneDrive Documents if it exists (Windows with OneDrive)
onedrive_docs = Path.home() / "OneDrive" / "Documents" / "notes"
default_docs = Path.home() / "Documents" / "notes"

notes_dir = onedrive_docs if onedrive_docs.parent.exists() else default_docs
```

**Why:** Windows with OneDrive creates two `Documents` folders. Claude Desktop and Claude Code may use different defaults.

### Path Object Best Practices (Python)

**Always use `pathlib.Path` for cross-platform compatibility:**

```python
from pathlib import Path

# Good
skill_root = Path(os.getenv('CLAUDE_SKILL_ROOT'))
script_path = skill_root / 'scripts' / 'helper.py'

# Bad
script_path = os.getenv('CLAUDE_SKILL_ROOT') + '/scripts/helper.py'  # Breaks on Windows
```

---

## 10. Testing Skills Locally

### Manual Testing in Claude Code

```bash
# 1. Install skill locally
cp -r skill-name ~/.claude/skills/

# 2. Open Claude Code in any directory
cd ~/Projects/test-project

# 3. Trigger skill with natural language
"Note that testing the skill"
```

### Direct Script Testing

```bash
# Navigate to skill directory
cd ~/.claude/skills/note-taking

# Test script directly
echo '{"command":"search","query":"test"}' | python3 scripts/notes_manager.py

# Or simulate CLAUDE_SKILL_ROOT
export CLAUDE_SKILL_ROOT="$HOME/.claude/skills/note-taking"
echo '{"command":"add","heading":"Test","content":"Content"}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

### Debugging Tips

**Enable debug output in scripts:**
```python
import sys
import json

def debug_log(message):
    """Log to stderr (won't pollute JSON stdout)"""
    print(f"DEBUG: {message}", file=sys.stderr)

debug_log(f"CLAUDE_SKILL_ROOT: {os.getenv('CLAUDE_SKILL_ROOT')}")
debug_log(f"Current working directory: {os.getcwd()}")
```

**Check Claude's environment:**
```bash
# In Claude Code, run:
echo "Skill root: ${CLAUDE_SKILL_ROOT}"
env | grep CLAUDE
pwd
```

---

## 11. Migration Path for Existing Skills

### Issue with Current Implementation

**Our current SKILL.md uses:**
```bash
python3 scripts/notes_manager.py
```

**Problem:**
- Assumes skill directory is the working directory
- Fails when user runs Claude Code from a different directory
- Non-portable across different installation methods

### Recommended Fix

**Update all script references to:**
```bash
python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Changes Required:**
1. Update SKILL.md (all script references)
2. Test with plugin installation
3. Test with personal skill installation
4. Verify on Windows (WSL) and macOS

---

## 12. Official Documentation References

### Primary Sources

1. **Agent Skills Overview**
   https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

2. **Claude Code Skills**
   https://code.claude.com/docs/en/skills

3. **Plugins**
   https://code.claude.com/docs/en/plugins

4. **Skill Authoring Best Practices**
   https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

### Community Resources

1. **Anthropic Skills Repository**
   https://github.com/anthropics/skills

2. **Inside Claude Code Skills: Structure, Prompts, Invocation**
   https://mikhail.io/2025/10/claude-code-skills/

3. **Awesome Claude Skills**
   https://github.com/travisvn/awesome-claude-skills

---

## 13. Key Learnings

### 2025-11-18: ${CLAUDE_SKILL_ROOT} is Essential for Portable Skills

**Problem:** Skills using relative paths like `scripts/notes_manager.py` only work if executed from the skill directory.

**Solution:** Always use `${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py` to ensure skills work regardless of user's working directory.

**Impact:** Critical for plugin-based skills that are installed in `.claude/plugins/marketplaces/...` and executed from arbitrary project directories.

### Skills Execute in User's Working Directory

**Discovery:** When a skill is triggered, `pwd` returns the user's current working directory, NOT the skill's installation directory.

**Example:**
- User in: `/c/Projects/my-app`
- Skill at: `~/.claude/plugins/.../note-taking`
- When skill executes: `pwd` = `/c/Projects/my-app`

**Implication:** Never assume the current directory contains skill resources.

### Directory Structure Matters for Maintainability

**Observation:** Anthropic's skills vary in organization:
- Simple skills (xlsx): Scripts at root level
- Complex skills (skill-creator): Organized with `scripts/` subdirectory

**Recommendation:** For skills with multiple scripts or resources, use organized subdirectories:
- `scripts/` for executable code
- `references/` for documentation
- `templates/` for user-facing resources

### Path Style is Critical for Cross-Platform Support

**Rule:** Always use forward slashes (`/`), never backslashes (`\`).

**Rationale:** Unix-style paths work on Windows (via WSL) but Windows-style paths break on Unix systems.

### Security is User's Responsibility

**Finding:** Skills have full access to filesystem and system resources (within user permissions).

**Implication:** Script authors must:
- Validate all inputs
- Sanitize file paths
- Handle errors gracefully
- Document security considerations

---

## 14. Recommendations for productivity-skills

### Immediate Actions

1. **Update SKILL.md:**
   - Replace all instances of `scripts/notes_manager.py` with `${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py`
   - Test thoroughly with plugin installation

2. **Add Documentation:**
   - Document `${CLAUDE_SKILL_ROOT}` in CLAUDE.md
   - Include examples for future skill development

3. **Test Scenarios:**
   - Test from different working directories
   - Test with plugin installation
   - Test with personal skill installation
   - Test on Windows (WSL) if possible

### Future Considerations

1. **Add Debug Mode:**
   - Environment variable: `DEBUG_NOTES=1`
   - Log to stderr for troubleshooting

2. **Improve Error Messages:**
   - Include skill root path in errors
   - Help users diagnose path issues

3. **Consider Additional Scripts:**
   - Migration script for legacy notes
   - Backup script for notes directory
   - Analytics script for note statistics

---

## 15. Open Questions

1. **Does Claude automatically cd to skill directory for some skills?**
   - The skill-creator examples use `scripts/init_skill.py` without `${CLAUDE_SKILL_ROOT}`
   - Need to verify if Claude changes directory before execution or if examples are incomplete

2. **Is there a difference between Claude Code and Claude Desktop behavior?**
   - Desktop uses ZIP upload with SKILL.md at root
   - Does this affect path resolution?

3. **Are there performance implications of using environment variables?**
   - Does `${CLAUDE_SKILL_ROOT}` expansion have any overhead?
   - Should we cache the path in scripts?

4. **What happens if a skill tries to write to its own directory?**
   - Permissions on plugin directories?
   - Should skills be read-only after installation?

---

## Conclusion

The `${CLAUDE_SKILL_ROOT}` environment variable is the cornerstone of portable, reliable skill development in Claude Code. By using this variable for all resource references, skills can work correctly regardless of:
- Installation method (personal, project, plugin)
- User's working directory
- Operating system (macOS, Linux, Windows/WSL)

**Critical Fix Required:** Update all script references in SKILL.md from `scripts/notes_manager.py` to `${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py`.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-18
**Next Review:** When testing reveals edge cases or official documentation updates
