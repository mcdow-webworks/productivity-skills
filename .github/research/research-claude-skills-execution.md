# Research: Claude Code Skills Framework Execution Model

**Date:** 2025-11-18
**Purpose:** Document official and community-discovered behavior of Claude Code skills execution
**Status:** Based on official docs, community research, and reverse engineering

## Executive Summary

Claude Code skills operate through **prompt expansion and context modification**, not separate processes. When a skill is invoked, Claude receives the skill's base directory path and SKILL.md contents, enabling it to locate and execute bundled scripts using the Bash tool. However, **official documentation is sparse** on execution mechanics, working directory behavior, and environment setup.

**Key Findings:**
1. No official environment variables for resource location (use relative paths from skill directory)
2. Working directory behavior is **unpredictable** - scripts should use absolute paths
3. Python executable naming is **hardcoded to `python3`** on some platforms (Windows Anaconda issue)
4. Base directory path is provided at skill invocation but not exposed as environment variable
5. Scripts execute via the Bash tool with standard shell semantics

---

## 1. How Claude Code Executes Commands from SKILL.md

### Execution Model

**Source:** [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

Skills are **NOT** separate processes, sub-agents, or external tools. Instead:

1. **Prompt Expansion:** When triggered, SKILL.md is loaded and expanded into detailed instructions
2. **Context Injection:** Instructions are injected as messages with `isMeta: true` flags (hidden from UI)
3. **Tool Pre-approval:** `allowed-tools` in frontmatter modifies execution context to pre-approve tools (e.g., Bash)
4. **Script Execution:** Claude uses the **Bash tool** to run scripts, following expanded instructions

**Example Flow:**
```
User: "Extract text from document.pdf"
  ↓
Skill Triggered → SKILL.md loaded
  ↓
Claude receives: "Base Path: /Users/username/.claude/skills/pdf/"
  ↓
Instruction: "Run python3 extract_text.py <file>"
  ↓
Claude executes via Bash tool: python3 /Users/username/.claude/skills/pdf/scripts/extract_text.py document.pdf
```

### Command Invocation Patterns

**Source:** [Anthropic Skills Repository - PPTX Skill](https://github.com/anthropics/skills/blob/main/document-skills/pptx/SKILL.md)

Skills demonstrate these patterns:

```bash
# Relative path from skill root
python scripts/thumbnail.py template.pptx output_prefix

# With arguments and options
python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52

# Nested scripts folder
python ooxml/scripts/unpack.py <office_file> <output_dir>
```

**Critical:** Commands in SKILL.md are **templates** that Claude interprets. They are NOT shell scripts executed directly.

---

## 2. Working Directory Behavior

### Current State: Unpredictable

**Source:** GitHub Issues [#5038](https://github.com/anthropics/claude-code/issues/5038), [#852](https://github.com/anthropics/claude-code/issues/852), [#1628](https://github.com/anthropics/claude-code/issues/1628)

**Known Issues:**
- "Wrong working directory" - shell resets to unexpected directory even after cd
- "Unable to Change Working Directory" - security restrictions limit cd to child directories
- Skills may start with different cwd depending on how Claude Code was launched

**User-facing Message:**
```
For security, Claude Code may only change directories to child directories
of the original working directory for this session.
```

### Recommended Practice

**Source:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

**Do NOT rely on working directory.** Instead:

1. **Use absolute paths** constructed from base directory
2. **Use `{baseDir}` variable** in SKILL.md (resolved at invocation)
3. **Scripts should accept absolute paths** as arguments

**Example (from community research):**
```bash
# Template in SKILL.md uses {baseDir} variable
python {baseDir}/scripts/analyzer.py --path "$USER_PATH" --output report.json

# Claude resolves this to:
python /home/user/.claude/skills/my-skill/scripts/analyzer.py --path "/project/data" --output report.json
```

**Note:** `{baseDir}` is mentioned in community research but **not documented** in official specs.

---

## 3. Environment Variables and Resource Location

### No Official Environment Variables

**Source:** [Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)

The official spec does **NOT** define any environment variables for:
- Skill root directory (`CLAUDE_SKILL_ROOT` does NOT exist)
- Base directory path
- Resource location
- Temporary files

### Base Directory Provided at Invocation

**Source:** [Inside Claude Code Skills](https://mikhail.io/2025/10/claude-code-skills/)

When a skill loads, Claude receives:
```
Base Path: /Users/username/.claude/skills/skill-name/
```

This path is **NOT** exposed as an environment variable. Scripts cannot access it via `$SKILL_ROOT` or similar.

### Recommended Resource Location Strategy

**Source:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

1. **Relative paths in SKILL.md:** Reference resources relative to skill root
   ```markdown
   See `references/api-docs.md` for details
   Run `scripts/process.py` to execute
   ```

2. **Scripts receive absolute paths:** Claude constructs full paths before invoking
   ```bash
   # Claude translates:
   python scripts/process.py input.txt

   # To:
   python /full/path/to/skill/scripts/process.py /full/path/to/input.txt
   ```

3. **Scripts compute relative paths internally:** Use `__file__` in Python
   ```python
   import os
   from pathlib import Path

   SKILL_ROOT = Path(__file__).parent.parent  # Assumes scripts/ subfolder
   TEMPLATE_PATH = SKILL_ROOT / "templates" / "default.md"
   ```

### User Environment Variables Still Available

Scripts executed via Bash tool have access to standard environment variables:
- `$HOME`, `$USER`, `$PATH`
- Custom variables like `$NOTES_DIR` (if user sets them)
- Platform variables (`$APPDATA` on Windows via Git Bash)

---

## 4. Python Version Requirements and Executable Naming

### Official Requirements: Unspecified

**Source:** [Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)

The spec does **NOT** specify:
- Required Python version
- Executable naming conventions (`python` vs `python3`)
- Package manager requirements

### Community Observations: Python 3.7+

**Source:** [Skills Repository Examples](https://github.com/anthropics/skills)

- PDF skill requires: `pypdf`, `pdfplumber`, `reportlab`
- PPTX skill uses: `python-pptx`, `Pillow`
- All examples compatible with Python 3.7+

### Critical Issue: Hardcoded `python3` on Windows

**Source:** [GitHub Issue #7364](https://github.com/anthropics/claude-code/issues/7364)

**Problem:** Claude Code has hardcoded dependency on `python3` executable

**Impact:**
- **Anaconda Python on Windows** uses `python.exe`, NOT `python3.exe`
- Causes "blocking startup issue for Windows users with Anaconda Python"
- Common in data science/ML environments

**Workarounds:**
1. Create symlink: `mklink python3.exe python.exe` (in Anaconda Scripts folder)
2. Use WSL instead of native Windows
3. Use Git for Windows bash with Python 3.x installed

**Proposed Solutions (not yet implemented):**
- Auto-detect available executables (`python3`, `python`, `py`)
- Allow configuration in CLAUDE.md
- Use platform-specific defaults

### Executable Naming in Examples

**Source:** [Anthropic Skills Repository](https://github.com/anthropics/skills)

Examples are **inconsistent:**

- **PPTX skill:** Uses `python` (not `python3`)
  ```bash
  python scripts/thumbnail.py template.pptx
  ```

- **PDF skill:** Uses direct library imports (no executable)
  ```python
  from pypdf import PdfReader
  ```

- **Community guides:** Use `python3`
  ```bash
  python3 {baseDir}/scripts/analyzer.py
  ```

### Recommended Approach

**For Cross-Platform Compatibility:**

1. **Use `python3` in documentation** (matches Unix conventions)
2. **Warn Windows users** about Anaconda incompatibility
3. **Scripts use shebang** for clarity:
   ```python
   #!/usr/bin/env python3
   ```
4. **Document Python version requirement** in SKILL.md:
   ```yaml
   ---
   name: my-skill
   description: Requires Python 3.7+ with packages: requests, pathlib
   ---
   ```

---

## 5. Calling Scripts from SKILL.md

### Official Guidance: Minimal

**Source:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

**Key Principles:**

1. **Be explicit about execution:**
   ```markdown
   Run `analyze_form.py` to extract fields  ← Execute this
   See `analyze_form.py` for algorithm      ← Read this (reference)
   ```

2. **Provide clear commands:**
   ```markdown
   # Good - Actionable
   Extract fields with: python scripts/analyze.py input.pdf

   # Bad - Ambiguous
   The analyze script can help with field extraction
   ```

3. **Include expected output:**
   ```markdown
   Run: python scripts/stats.py notes.md
   Expected output: JSON with {entries: N, categories: [list]}
   ```

### Directory Structure Conventions

**Source:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

```
skill-name/
├── SKILL.md                    # Required - entry point
├── scripts/                    # Executable code (Python/Bash)
│   ├── primary_task.py        # Main operations
│   └── utilities.py           # Helper functions
├── reference/                  # Documentation (loaded on demand)
│   ├── api-reference.md
│   └── examples.md
└── templates/                  # Static resources
    └── default-template.md
```

**Critical:** Use **forward slashes** in all paths (even on Windows):
```markdown
✓ Correct: scripts/helper.py
✗ Wrong:   scripts\helper.py
```

### Progressive Disclosure Pattern

**Source:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

**SKILL.md should be concise** (under 500 lines recommended):

```markdown
# My Skill

Quick overview and common operations.

For detailed API reference, see `reference/api-docs.md`
For advanced examples, see `reference/advanced-usage.md`
```

Claude loads reference files **only when needed**, preserving context window.

### Script Design Patterns

**From Anthropic Skills Examples:**

1. **Accept JSON via stdin** (for complex inputs):
   ```python
   import json
   import sys

   data = json.load(sys.stdin)
   command = data["command"]
   ```

2. **Use argparse** (for simple CLI):
   ```python
   import argparse

   parser = argparse.ArgumentParser()
   parser.add_argument("input_file")
   parser.add_argument("--output", default="result.json")
   ```

3. **Output JSON to stdout** (for structured results):
   ```python
   import json

   result = {"status": "success", "entries": 42}
   print(json.dumps(result, indent=2))
   ```

4. **Handle errors gracefully:**
   ```python
   try:
       # Process
   except Exception as e:
       print(json.dumps({"error": str(e)}), file=sys.stderr)
       sys.exit(1)
   ```

---

## 6. The "Base Directory" Message

### What It Is

**Source:** [Inside Claude Code Skills](https://mikhail.io/2025/10/claude-code-skills/)

When a skill is invoked, Claude receives a message like:
```
Base Path: /Users/username/.claude/skills/pdf/

# PDF Processing Skill
[... SKILL.md contents ...]
```

This message is **hidden from the user** (marked `isMeta: true`) but visible to Claude.

### Purpose

**Source:** [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

The base path enables Claude to:

1. **Locate bundled scripts:** Convert relative paths to absolute
   ```
   SKILL.md says: "Run scripts/extract.py"
   Base path: /Users/username/.claude/skills/pdf/
   Claude executes: python3 /Users/username/.claude/skills/pdf/scripts/extract.py
   ```

2. **Read reference files:** Access documentation without loading everything upfront
   ```
   SKILL.md says: "See reference/api-docs.md"
   Claude reads: /Users/username/.claude/skills/pdf/reference/api-docs.md
   ```

3. **Access templates and resources:**
   ```
   SKILL.md says: "Use templates/default.md"
   Claude reads: /Users/username/.claude/skills/pdf/templates/default.md
   ```

### How to Use It (Skill Authors)

**In SKILL.md, use relative paths:**
```markdown
Run the analyzer: python scripts/analyze.py <file>
For more details, see `reference/advanced.md`
Use template from `templates/report.md`
```

**Claude translates these automatically** using the base path.

**Do NOT hardcode paths:**
```markdown
✗ Wrong: python /Users/username/.claude/skills/my-skill/scripts/run.py
✓ Correct: python scripts/run.py
```

### Variable Substitution (`{baseDir}`)

**Source:** [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

Some community examples show `{baseDir}` variable:
```bash
python {baseDir}/scripts/analyzer.py --path "$USER_PATH"
```

**Status:** **Not officially documented** in agent_skills_spec.md

**Appears to work** based on community reports, but may be:
- Implemented in Claude Code but undocumented
- Community convention that Claude infers
- Platform-specific behavior

**Recommendation:** Use relative paths instead of `{baseDir}` for portability.

---

## Platform Compatibility Notes

### Skill Installation Locations

**Source:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

Skills are discovered in:

1. **User-level (global):**
   - macOS/Linux: `~/.claude/skills/`
   - Windows: `%APPDATA%\Claude\skills\`

2. **Project-level (local):**
   - All platforms: `.claude/skills/` (in project root)

3. **Plugin-level:**
   - All platforms: `plugins/<plugin-name>/skills/`

### Path Handling: Always Unix-Style

**Source:** [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

**Critical Rule:** Use forward slashes in all file references:

```markdown
✓ Correct: scripts/helper.py
✓ Correct: reference/api-docs.md
✗ Wrong:   scripts\helper.py  (breaks on macOS/Linux)
```

This applies to:
- Paths in SKILL.md
- Paths in reference documentation
- Paths in script arguments (when passed by skill)

**Reason:** Unix-style paths work on all platforms (Windows handles `/` correctly), but Windows-style paths (`\`) fail on Unix systems.

### Python Scripts: Use `Path` Objects

**Source:** Community best practices + existing skills

```python
from pathlib import Path

# Works on all platforms
SKILL_ROOT = Path(__file__).parent.parent
template_path = SKILL_ROOT / "templates" / "default.md"

# Avoid os.path.join (platform-specific separators)
# Avoid hardcoded "C:\\..." or "/home/..." paths
```

---

## Unanswered Questions

These remain **undocumented** in official sources:

1. **Exact working directory on skill invocation**
   - Is it the project root, skill directory, or user's cwd?
   - How does it change between skill types (user/project/plugin)?

2. **Environment variable availability**
   - Can skills define custom environment variables?
   - Are there hidden variables like `CLAUDE_SKILL_ROOT`?

3. **Script execution security model**
   - Are there sandboxing restrictions?
   - What permissions do scripts have?

4. **Error handling conventions**
   - Should scripts exit with non-zero codes?
   - How should errors be communicated to Claude?

5. **Dependency management**
   - How should skills handle missing Python packages?
   - Should SKILL.md check for dependencies before running?

6. **Multi-platform script execution**
   - How to handle platform-specific tools (e.g., `qpdf` availability)?
   - Should skills detect platform and adjust behavior?

---

## Recommendations for Skill Authors

Based on this research:

### 1. Path Handling
- Use **relative paths** in SKILL.md (e.g., `scripts/run.py`)
- Scripts should use `Path(__file__).parent.parent` to find skill root
- Always use **forward slashes** in documentation
- Pass **absolute paths** to scripts as arguments

### 2. Python Executable
- Document as `python3` (Unix convention)
- Include Windows Anaconda warning in README
- Use shebang `#!/usr/bin/env python3` in scripts
- Specify minimum Python version in SKILL.md description

### 3. Script Design
- Accept **absolute paths** as arguments
- Output **JSON** for structured data
- Use **stderr** for errors
- Exit with **non-zero code** on failure
- Handle **missing dependencies** gracefully

### 4. Documentation
- Keep SKILL.md **under 500 lines**
- Use **progressive disclosure** (reference files for details)
- Provide **clear commands** (not vague descriptions)
- Include **expected output** examples
- Distinguish **"run this"** from **"read this"**

### 5. Testing
- Test on **multiple platforms** (macOS, Linux, Windows WSL)
- Test with **different Python installations** (system, Anaconda, pyenv)
- Test from **different working directories**
- Test with **relative and absolute input paths**

---

## Key Learnings Summary

### 2025-11-18: Claude Skills Execution Model

**What We Know (Official):**
- Skills expand prompts via `isMeta: true` messages
- Scripts execute via Bash tool (pre-approved with `allowed-tools`)
- Base path provided at invocation (but not as environment variable)
- Forward slashes required in all paths

**What We Know (Community):**
- Working directory is unreliable - use absolute paths
- `{baseDir}` variable works but is undocumented
- `python3` hardcoded on some platforms (Windows Anaconda breaks)
- Scripts should compute skill root from `__file__`

**What We Don't Know (Undocumented):**
- Exact working directory behavior
- Official environment variables
- Security/sandboxing model
- Dependency management best practices

**Critical Bug:**
- Windows Anaconda users cannot run Claude Code (python3 vs python executable mismatch)

---

## References

### Official Documentation
- [Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md) - Minimal spec, no execution details
- [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) - Path conventions, progressive disclosure
- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official skill examples

### Community Research
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) - `{baseDir}` variable, execution model
- [Inside Claude Code Skills](https://mikhail.io/2025/10/claude-code-skills/) - Base path message, script invocation
- [Mikhail Shilkov's Reverse Engineering](https://mikhail.io/2025/10/claude-code-skills/) - `isMeta: true` messages

### GitHub Issues
- [#7364: Windows Anaconda python3 Issue](https://github.com/anthropics/claude-code/issues/7364)
- [#5038: Wrong Working Directory](https://github.com/anthropics/claude-code/issues/5038)
- [#10443: Skills Not Loading from Project Root](https://github.com/anthropics/claude-code/issues/10443)

### Example Skills Analyzed
- [PDF Skill](https://github.com/anthropics/skills/blob/main/document-skills/pdf/SKILL.md) - Library imports, no external scripts
- [PPTX Skill](https://github.com/anthropics/skills/blob/main/document-skills/pptx/SKILL.md) - Script invocation patterns, uses `python` not `python3`
- [Skill Creator Skill](https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md) - Meta-skill for creating skills

---

## Appendix: Working Directory Testing Recommendations

To determine actual working directory behavior, test:

1. **Create test skill:**
   ```bash
   mkdir -p ~/.claude/skills/cwd-test/scripts
   ```

2. **Add script that reports cwd:**
   ```python
   # scripts/report_cwd.py
   import os
   import sys
   from pathlib import Path

   print(f"Current working directory: {os.getcwd()}")
   print(f"Script location: {Path(__file__).resolve()}")
   print(f"Script parent: {Path(__file__).parent.resolve()}")
   print(f"Script parent parent: {Path(__file__).parent.parent.resolve()}")
   print(f"sys.argv: {sys.argv}")
   ```

3. **Add SKILL.md:**
   ```yaml
   ---
   name: cwd-test
   description: Reports current working directory when invoked
   ---

   # Working Directory Test

   Run this command to see the working directory:

   python scripts/report_cwd.py
   ```

4. **Test from different locations:**
   - Open Claude Code in project A
   - Invoke skill: "Run the cwd-test skill"
   - Note output
   - Open Claude Code in project B
   - Invoke skill again
   - Compare outputs

This will reveal:
- Is cwd the project directory, skill directory, or something else?
- Does cwd change between invocations?
- How does Claude construct the full path to the script?

**Please contribute findings to this document!**
