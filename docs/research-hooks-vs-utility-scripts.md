# Research: Hooks vs Utility Scripts in Claude Code Skills

**Research Date:** 2025-11-17
**Context:** Clarifying the difference between Claude Code "hooks" and skill "utility scripts"
**Status:** Complete

---

## Executive Summary

**Key Finding:** "Hooks" and "utility scripts" are completely different concepts in the Claude Code ecosystem:

- **Hooks** = Event-driven automation callbacks in `.claude/settings.json`
- **Utility Scripts** = Helper functions called by skills, stored in `scripts/` directory

**Our Current Issue:** The `productivity-skills` repository incorrectly uses `hooks/` directory for utility scripts. According to official Anthropic conventions, these should be in `scripts/`.

---

## 1. What Are Hooks? (Event-Driven Automation)

### Definition
Hooks are **lifecycle event callbacks** configured in `.claude/settings.json` that trigger custom shell commands at specific points during Claude Code execution.

### Configuration Location
```
~/.claude/settings.json           # User-level (all projects)
.claude/settings.json             # Project-level (committed)
.claude/settings.local.json       # Local project-level (not committed)
```

### Available Hook Events

| Event | When It Fires | Use Cases |
|-------|--------------|-----------|
| `SessionStart` | When Claude session begins | Environment setup |
| `UserPromptSubmit` | Before Claude starts working | Prompt modification |
| `PreToolUse` | Before any tool execution | Block dangerous commands, validate |
| `PostToolUse` | After tool completes successfully | Auto-format, run tests |
| `Notification` | When Claude needs user input | Log notifications |
| `PreCompact` | Before context compression | Save state |
| `Stop` | When session completes | Auto-commit, save transcripts |
| `SubagentStop` | When subagent finishes | Track subagent results |

### Example Hook Configuration
```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "prompt",
        "prompt": "If anything significant was accomplished in this session, briefly suggest (in one sentence) what could be noted. If nothing notable, output nothing."
      }]
    }],
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "prettier --write {{file}}"
      }]
    }]
  }
}
```

### Hooks Receive
- Session IDs
- Working directories
- Transcript file paths
- Tool invocation details
- JSON data via stdin

### Purpose
Hooks provide **deterministic control** over Claude's lifecycle, turning suggestions ("please run tests") into guaranteed actions.

---

## 2. What Are Utility Scripts? (Helper Functions)

### Definition
Utility scripts are **executable helper programs** (Python, Bash, JavaScript, etc.) that skills invoke to perform deterministic operations like data processing, validation, or automation.

### Official Directory Structure (Anthropic Convention)

According to the official `anthropics/skills` repository:

```
skill-name/
├── SKILL.md              # Required: Skill instructions
├── scripts/              # Executable code (Python/Bash/etc.)
│   ├── helper.py
│   ├── validate.py
│   └── process.py
├── references/           # Documentation loaded into context
│   ├── api-reference.md
│   └── examples.md
└── assets/               # Templates and binary files
    └── template.txt
```

**Key Point:** Official Anthropic skills use `scripts/` NOT `hooks/`

### Examples from Anthropic Skills Repository

**skill-creator** (anthropics/skills):
```
skill-creator/
├── SKILL.md
├── scripts/
│   ├── init_skill.py
│   ├── package_skill.py
│   └── quick_validate.py
└── references/
    └── documentation.md
```

**document-skills/pdf** (anthropics/skills):
```
pdf/
├── SKILL.md
├── scripts/
│   ├── check_bounding_boxes.py
│   ├── convert_pdf_to_images.py
│   ├── extract_form_field_info.py
│   ├── fill_fillable_fields.py
│   └── fill_pdf_form_with_annotations.py
├── reference.md
└── forms.md
```

### How Skills Call Utility Scripts

Skills instruct Claude to use the **Bash tool** to execute scripts:

1. **SKILL.md provides instruction** about which script to run
2. **Claude invokes Bash tool** with the script command
3. **Bash tool executes** the Python/shell script
4. **Claude processes output** and continues workflow

**Important:** Skills do NOT directly execute scripts. They prompt Claude to use tools.

### Script Communication Pattern
- Scripts accept JSON via stdin
- Scripts output JSON to stdout
- Exit codes indicate success/failure
- Portable paths recommended (relative to skill directory)

---

## 3. Key Differences

| Aspect | Hooks | Utility Scripts |
|--------|-------|-----------------|
| **What** | Event callbacks | Helper functions |
| **Where** | `.claude/settings.json` | `scripts/` in skill directory |
| **When** | Automatic at lifecycle events | Manually invoked by skill instructions |
| **How** | Triggered by Claude events | Executed via Bash tool |
| **Purpose** | Workflow automation | Deterministic operations |
| **Scope** | Global or project-level | Skill-specific |
| **Examples** | Auto-format, auto-test, auto-commit | Data processing, validation, file manipulation |

---

## 4. Our Mistake: Using `hooks/` for Utility Scripts

### Current (Incorrect) Structure
```
note-taking/
├── SKILL.md
└── hooks/                    # WRONG: This is not a hook
    └── notes_manager.py      # This is a utility script
```

### Should Be
```
note-taking/
├── SKILL.md
└── scripts/                  # CORRECT: Follows Anthropic convention
    └── notes_manager.py
```

### Why This Matters

1. **Confusion:** Users expect `hooks/` to contain `.claude/settings.json` hook definitions
2. **Documentation:** Official docs use `scripts/` exclusively
3. **Discoverability:** Developers looking for utility scripts expect `scripts/`
4. **Consistency:** All Anthropic examples use `scripts/`
5. **Plugin marketplace:** May have expectations about directory naming

### Migration Required

**Files to update:**
- Move `hooks/notes_manager.py` → `scripts/notes_manager.py`
- Update SKILL.md references
- Update CLAUDE.md documentation
- Update any path references in code
- Update installation instructions

---

## 5. Best Practices for Skills Directory Organization

### Recommended Structure (from Anthropic docs)

```
my-skill/
├── SKILL.md                 # Core instructions (required)
│   ├── YAML frontmatter
│   │   ├── name (required)
│   │   ├── description (required)
│   │   └── allowed-tools (optional)
│   └── Markdown content
├── scripts/                 # Executable utilities
│   ├── process.py          # Data processing
│   ├── validate.sh         # Validation
│   └── utils/              # Sub-organization allowed
│       └── helpers.py
├── references/              # Loaded into context as needed
│   ├── api-reference.md
│   ├── examples.md
│   └── advanced.md
├── assets/                  # Binary files, templates
│   ├── template.txt
│   └── config.json
└── templates/               # Alternative to assets/
    └── monthly-template.md
```

### Progressive Disclosure Pattern

**Small skills:**
```
simple-skill/
└── SKILL.md (everything in one file)
```

**Medium skills:**
```
medium-skill/
├── SKILL.md (core instructions)
└── reference.md (additional details)
```

**Large skills:**
```
complex-skill/
├── SKILL.md (core)
├── scripts/ (executables)
├── references/ (documentation)
└── assets/ (resources)
```

### When to Use Scripts vs Inline Code

**Use scripts/ when:**
- Same code is rewritten repeatedly
- Deterministic reliability required
- Complex multi-step operations
- External dependencies needed
- Performance-critical operations

**Use inline code in SKILL.md when:**
- Simple, one-off operations
- Context-dependent logic
- Educational examples
- Demonstrating patterns

---

## 6. Script Invocation Patterns (Best Practices)

### Pattern 1: Direct Invocation
```markdown
When performing X, use the Bash tool to execute:

python3 {baseDir}/scripts/helper.py --option value
```

### Pattern 2: JSON Communication
```markdown
To search notes, pipe JSON to the script:

echo '{"command":"search","query":"term"}' | python3 {baseDir}/scripts/notes_manager.py
```

### Pattern 3: Environment Variables
```markdown
The script respects these environment variables:
- NOTES_DIR: Custom notes location (default: ~/Documents/notes)

Run:
python3 {baseDir}/scripts/notes_manager.py
```

### Note on `{baseDir}`
Based on research, skills can use `{baseDir}` or similar variables for portable paths. However, explicit documentation on this is limited. Alternative approaches:
- Use relative paths from skill directory
- Document installation-specific paths
- Use environment variables for configuration

---

## 7. Integration Examples

### Example 1: Skill Using Scripts (Correct Pattern)

**SKILL.md:**
```markdown
---
name: data-processor
description: Process and validate data files
---

# Data Processing Skill

## Usage

To validate a CSV file:

1. Use the Bash tool to execute the validator:
   ```bash
   python3 scripts/validate_csv.py input.csv
   ```

2. If validation passes, process the file:
   ```bash
   python3 scripts/process_csv.py input.csv output.json
   ```
```

**Directory:**
```
data-processor/
├── SKILL.md
└── scripts/
    ├── validate_csv.py
    └── process_csv.py
```

### Example 2: Hook Triggering Note Capture (Correct Pattern)

**~/.claude/settings.json:**
```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "prompt",
        "prompt": "If anything significant was accomplished, suggest what should be noted."
      }]
    }]
  }
}
```

This hook runs at session end and prompts Claude to suggest note-worthy items. It's completely separate from the note-taking skill's utility scripts.

---

## 8. Documentation Sources

### Primary Sources
1. **Anthropic Skills Repository**: https://github.com/anthropics/skills
   - Official skill examples
   - `scripts/` directory convention
   - Skill structure best practices

2. **Skill Creator Documentation**: https://github.com/anthropics/skills/tree/main/skill-creator
   - Recommended directory structure
   - `scripts/`, `references/`, `assets/` directories
   - No mention of `hooks/` for utility scripts

3. **Claude Code Hooks Documentation**: https://docs.claude.com/en/docs/claude-code/hooks
   - Hook events and configuration
   - `.claude/settings.json` structure
   - Hook use cases

### Secondary Sources
4. **Inside Claude Code Skills** (Mikhail Shilkov): https://mikhail.io/2025/10/claude-code-skills/
   - Skill directory structure
   - Script integration patterns

5. **Claude Skills Deep Dive** (Lee-Han Chung): https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
   - Helper scripts in `scripts/` directory
   - Bash tool execution pattern

6. **GitButler Hooks Blog**: https://blog.gitbutler.com/automate-your-ai-workflows-with-claude-code-hooks
   - Hook lifecycle events
   - Real-world hook examples

---

## 9. Recommendations for productivity-skills

### Immediate Actions Required

1. **Rename directory:** `hooks/` → `scripts/`
   ```bash
   mv plugins/productivity-suite/skills/note-taking/hooks \
      plugins/productivity-suite/skills/note-taking/scripts
   ```

2. **Update SKILL.md references:**
   - Change `hooks/notes_manager.py` to `scripts/notes_manager.py`
   - Update example commands

3. **Update CLAUDE.md:**
   - Document `scripts/` convention
   - Explain hooks vs utility scripts distinction
   - Update architecture documentation

4. **Update README.md:**
   - Fix installation paths
   - Correct example commands

5. **Add migration note:**
   - Document the rename in changelog
   - Add note about backward compatibility (if needed)

### Optional Enhancements

1. **Add .claude/settings.json example:**
   Show users how to set up actual hooks for auto-capture

2. **Create references/ directory:**
   Move detailed docs from SKILL.md to references/

3. **Add assets/ or templates/ directory:**
   Organize monthly-template.md properly

4. **Document baseDir usage:**
   Research and document portable path strategies

---

## 10. Key Learnings

### 2025-11-17: Hooks vs Scripts Distinction Critical

**Problem:** Used `hooks/` directory name for utility scripts, causing confusion about what "hooks" means in Claude Code ecosystem.

**Root Cause:** Misunderstanding of Claude Code terminology. "Hooks" specifically refers to lifecycle event callbacks in `.claude/settings.json`, NOT helper scripts in skill directories.

**Solution:** Follow official Anthropic convention:
- Use `scripts/` for executable helper programs in skills
- Use `.claude/settings.json` hooks for event-driven automation
- Keep these concepts completely separate in documentation

**Impact:**
- Clearer documentation for users
- Consistency with official examples
- Better discoverability of utility scripts
- Proper use of hooks for workflow automation

---

## Appendix: Glossary

**Hook:** Event-driven callback configured in `.claude/settings.json` that runs at specific points in Claude's lifecycle.

**Utility Script:** Executable helper program (Python, Bash, etc.) stored in a skill's `scripts/` directory and invoked via Bash tool.

**Skill:** Modular capability with SKILL.md descriptor that Claude loads when relevant, optionally including scripts and resources.

**Tool:** Claude's built-in capabilities (Read, Write, Edit, Bash, Grep, etc.) that skills can use.

**baseDir:** Variable (documented in some sources) that may provide skill's installation directory for portable path references.

**Progressive Disclosure:** Design pattern where simple skills use single SKILL.md, complex skills add references/ and scripts/ as needed.

---

## References

1. Anthropic Skills Repository: https://github.com/anthropics/skills
2. Skill Creator: https://github.com/anthropics/skills/tree/main/skill-creator
3. PDF Skill Example: https://github.com/anthropics/skills/tree/main/document-skills/pdf
4. Claude Code Hooks Docs: https://docs.claude.com/en/docs/claude-code/hooks
5. Mikhail Shilkov - Inside Claude Code Skills: https://mikhail.io/2025/10/claude-code-skills/
6. Lee-Han Chung - Skills Deep Dive: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
7. GitButler - Claude Code Hooks: https://blog.gitbutler.com/automate-your-ai-workflows-with-claude-code-hooks
8. Playwright Skill: https://github.com/lackeyjb/playwright-skill
