# Summary: Python Executable Naming Best Practices for Claude Skills

**Date:** 2025-11-18
**Status:** ACTIONABLE RECOMMENDATIONS
**Related:** `research-python-executable-naming.md` (full research)

---

## TL;DR - What to Do

**Change all `python3` to `python` in SKILL.md examples.**

This makes the skill work on Windows where `python3.exe` doesn't exist.

---

## Quick Facts

### The Problem
```bash
# Current (in SKILL.md)
echo '{"command":"search","query":"test"}' | python3 scripts/notes_manager.py
```

**Fails on Windows** because:
- Windows Python installer creates `python.exe` only
- No `python3.exe` by default
- Users get "command not found" errors

### The Solution
```bash
# Recommended
echo '{"command":"search","query":"test"}' | python scripts/notes_manager.py
```

**Works everywhere** because:
- Windows has `python.exe` ✓
- Modern Python 3.x installations alias `python` → Python 3 ✓
- Virtual environments always provide `python` ✓
- Anthropic's official skills use `python` ✓

---

## Evidence-Based Decision

### Authority Sources (HIGHEST to HIGH)

1. **PEP 394 (Official Python Standard):** Recommends `python` in virtual environments
2. **Anthropic's Own Skills:** Use `python` in examples (webapp-testing skill)
3. **Python Windows Documentation:** Only `python.exe` installed by default
4. **Claude Code Documentation:** No requirement for `python3`

### Platform Reality Check

| Platform | `python` | `python3` | Recommendation |
|----------|----------|-----------|----------------|
| Windows  | ✓ Always | ✗ Never   | Use `python`   |
| macOS    | ✓ Usually| ✓ Yes     | Use `python`   |
| Linux    | ⚠ Varies | ✓ Yes     | Use `python`   |
| Virtual Env | ✓ Always | ⚠ Maybe | Use `python`   |

**Winner:** `python` works in more scenarios

---

## What Needs to Change

### File: `SKILL.md`

**Lines with `python3` (15 occurrences):**
- Line 37: Add note example
- Line 52: Add note example
- Line 69: Search example
- Line 94: Search example
- Line 108: Append example
- Line 133: Append example
- Line 141: Reindex example
- Line 156: Stats example
- Line 175: Migrate example
- All other examples in the file

**Change:** Replace `python3` with `python`

### File: `notes_manager.py`

**Current shebang (line 1):**
```python
#!/usr/bin/env python3
```

**Status:** ✓ CORRECT - Keep as is

**Rationale:**
- Shebangs are for direct script execution (e.g., `./notes_manager.py`)
- Windows ignores shebangs (treats as comments)
- Unix systems use shebang to find Python 3
- This is the correct cross-platform pattern per PEP 394

---

## Why This Works

### 1. Windows Compatibility
- Only `python.exe` exists (official installer)
- Python launcher (`py`) optional but common
- `python` command always works

### 2. Virtual Environments
- All platforms: `python` → Python 3.x in venv
- Recommended way to run Python projects
- Most users run Claude Code with activated venv

### 3. Modern Python Installations
- Python 2 EOL since January 2020
- New installations: `python` → Python 3.x
- Legacy systems: Users can create alias if needed

### 4. Anthropic Precedent
- Official `webapp-testing` skill uses `python`
- No documentation requiring `python3`
- Following the standard set by Anthropic

---

## What Doesn't Need to Change

### 1. Shebang in `notes_manager.py`
Keep `#!/usr/bin/env python3` because:
- Correct for Unix direct execution
- Ignored on Windows (harmless comment)
- Follows PEP 394 guidance

### 2. Script Paths
Keep relative paths like `scripts/notes_manager.py`:
- Claude Code docs confirm this pattern
- Skills execute from skill base directory
- Works on all platforms

### 3. JSON Interface
No changes to stdin/stdout protocol:
- Cross-platform by design
- Not affected by executable name

---

## Testing Checklist

After making changes, verify on:

**Minimum Testing:**
- [ ] Windows 10/11 (PowerShell and Git Bash)
- [ ] macOS (Terminal)
- [ ] Linux Ubuntu/Debian

**Extended Testing:**
- [ ] Windows with Python from python.org
- [ ] Windows with Python from Microsoft Store
- [ ] macOS with Homebrew Python
- [ ] Linux with apt/dnf installed Python
- [ ] Virtual environments (venv, conda)

**Test Commands:**
```bash
# Add note test
echo '{"command":"add","heading":"Test - Note","content":"Test"}' | python scripts/notes_manager.py

# Search test
echo '{"command":"search","query":"test"}' | python scripts/notes_manager.py

# Stats test
echo '{"command":"stats"}' | python scripts/notes_manager.py
```

---

## Migration Steps

### Step 1: Update SKILL.md
```bash
# Find all occurrences
grep -n "python3" plugins/productivity-suite/skills/note-taking/SKILL.md

# Replace (careful review!)
# Use editor find-and-replace:
# Find: | python3 scripts/notes_manager.py
# Replace: | python scripts/notes_manager.py
```

### Step 2: Update Documentation (if needed)
Check these files for `python3` references:
- `README.md`
- `docs/*.md`
- Other research docs

### Step 3: Test on Multiple Platforms
Run test commands above on Windows, macOS, Linux

### Step 4: Update Research Docs
Add findings to:
- This summary document
- `research-python-executable-naming.md`

---

## Common Questions

### Q: Won't this break Linux systems where `python` → Python 2?

**A:** Unlikely in 2025:
- Python 2 EOL was January 2020
- Most distributions removed Python 2 or point `python` to Python 3
- Users with legacy systems can create alias: `alias python=python3`
- Virtual environments (recommended) always provide `python` → Python 3

### Q: What about the shebang? Shouldn't that match?

**A:** No - different use cases:
- **Shebang (`#!/usr/bin/env python3`)**: For direct script execution (`./script.py`)
- **Command invocation (`python`)**: For calling via interpreter (`python script.py`)
- Both can coexist and have different requirements

### Q: What if user doesn't have Python at all?

**A:** Skill prerequisites already require Python:
- User must have Python installed to use skill
- Documentation should mention Python 3.7+ requirement
- This is not a change - just clarifying which command to use

### Q: Should we use `py` launcher on Windows instead?

**A:** No:
- Not guaranteed to be installed (though common)
- `python` is more universal
- `py` is for version-specific execution (e.g., `py -3.12`)
- Keep it simple

---

## Risk Assessment

### Risk Level: LOW

**Breaking Changes:** None
- Users invoke via natural language (unchanged)
- JSON protocol unchanged
- Script functionality unchanged
- Only affects command examples in SKILL.md

**Compatibility Impact:** POSITIVE
- Currently broken on Windows
- Will work on Windows after fix
- No negative impact on macOS/Linux

**Testing Required:** MEDIUM
- Should test on 3+ platforms
- Simple smoke tests sufficient
- No complex integration scenarios

---

## Rollout Plan

### Phase 1: Update SKILL.md (Immediate)
- Replace all `python3` with `python` in examples
- Update in-repository version
- No user impact (documentation change only)

### Phase 2: Test Multi-Platform (Before Release)
- Windows testing (critical - currently broken)
- macOS testing (verify no regression)
- Linux testing (verify no regression)

### Phase 3: Update ZIP Distribution
- Regenerate `note-taking-skill.zip` with updated SKILL.md
- Test upload to Claude Desktop
- Verify skill works on Windows

### Phase 4: Documentation
- Update README if needed
- Update FAQ if needed
- Add to CLAUDE.md learnings

---

## Success Criteria

Skill is considered fixed when:

1. ✅ Windows users can invoke skill without errors
2. ✅ macOS users experience no regression
3. ✅ Linux users experience no regression
4. ✅ Virtual environment users experience no regression
5. ✅ All test commands return valid JSON responses

---

## References

**Full Research:** `.github/research/research-python-executable-naming.md`

**Key Sources:**
- [PEP 394](https://peps.python.org/pep-0394/) - Official Python naming conventions
- [Anthropic Skills Repo](https://github.com/anthropics/skills) - Official examples
- [Claude Code Docs](https://code.claude.com/docs/en/skills) - Skill execution
- [Python Windows Docs](https://docs.python.org/3/using/windows.html) - Windows specifics

**Related Research:**
- `.github/research/research-cross-platform-paths.md` - Path handling
- `.github/research/research-skill-execution-environment.md` - Execution context

---

## Approval Status

**Recommended Action:** APPROVED for implementation

**Rationale:**
- Fixes real Windows incompatibility
- Aligned with Anthropic standards
- Low risk, high benefit
- Follows Python official guidance
- Simple to implement and test

**Next Steps:** Implement changes in SKILL.md and test on Windows
