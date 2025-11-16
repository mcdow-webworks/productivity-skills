# Claude Skills Best Practices Research Report

**Research Date:** 2025-11-15
**Subject:** Claude Code/Desktop Skills Distribution, Directory Structure, and Marketplace Standards

---

## Executive Summary

After comprehensive research of official Anthropic documentation, community repositories, and marketplace examples, the **standard pattern for Claude Skills is NOT to use a root-level SKILL.md file**. Instead, Skills should be organized as individual, self-contained directories, each with their own SKILL.md file. This finding has significant implications for the current `productivity-skills` repository structure.

---

## 1. Official Claude Skills Architecture

### 1.1 Core Specifications

**Official Documentation Sources:**
- Primary: https://code.claude.com/docs/en/skills
- Best Practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- Plugins: https://code.claude.com/docs/en/plugins
- Anthropic Blog: https://www.anthropic.com/news/skills

**Key Requirements (as of January 2025):**

1. **YAML Frontmatter** (Required in every SKILL.md):
   ```yaml
   ---
   name: skill-name-here
   description: Brief description of what the skill does and when to use it
   ---
   ```

2. **Field Constraints:**
   - `name`: Max 64 characters, lowercase letters/numbers/hyphens only
   - `description`: Max 1024 characters, critical for discovery
   - Description must include BOTH "what it does" and "when to use it"
   - Must be written in third person (injected into system prompt)

3. **File Size Guidelines:**
   - Keep SKILL.md body under 500 lines for optimal performance
   - Under 5,000 words recommended
   - Use progressive disclosure pattern when approaching limits

### 1.2 Standard Directory Structure

**Single Skill Structure:**
```
my-skill/
├── SKILL.md              # Required: Core instructions with YAML frontmatter
├── scripts/              # Optional: Executable Python/Bash scripts
├── references/           # Optional: Documentation loaded on-demand
└── assets/               # Optional: Templates and binary files
```

**Progressive Disclosure Pattern:**
```
pdf/
├── SKILL.md              # Loaded when skill is triggered
├── FORMS.md              # Loaded only when form filling is needed
├── reference.md          # API reference loaded on-demand
├── examples.md           # Usage examples loaded as needed
└── scripts/
    ├── analyze_form.py
    ├── fill_form.py
    └── validate.py
```

**Key Principle:** Keep references "one level deep from SKILL.md" to prevent incomplete file reads.

---

## 2. Multi-Skill Repository Patterns

### 2.1 Official Anthropic Repository Structure

**Repository:** https://github.com/anthropics/skills

**Structure:** Flat, multi-skill organization with NO root SKILL.md

```
skills/
├── .claude-plugin/
│   └── marketplace.json
├── algorithmic-art/
│   └── SKILL.md
├── brand-guidelines/
│   └── SKILL.md
├── mcp-builder/
│   └── SKILL.md
├── skill-creator/
│   └── SKILL.md
├── webapp-testing/
│   └── SKILL.md
└── document-skills/
    ├── docx/
    │   └── SKILL.md
    ├── pdf/
    │   └── SKILL.md
    ├── pptx/
    │   └── SKILL.md
    └── xlsx/
        └── SKILL.md
```

**Key Finding:** No root-level SKILL.md exists. Each skill is completely self-contained.

### 2.2 Community Best Practice Examples

**obra/superpowers** (20+ skills): https://github.com/obra/superpowers

```
superpowers/
├── .claude-plugin/
├── skills/
│   ├── testing/
│   │   ├── test-driven-development/
│   │   │   └── SKILL.md
│   │   └── condition-based-waiting/
│   │       └── SKILL.md
│   ├── debugging/
│   │   ├── systematic-debugging/
│   │   │   └── SKILL.md
│   │   └── root-cause-tracing/
│   │       └── SKILL.md
│   └── collaboration/
│       ├── brainstorming/
│       │   └── SKILL.md
│       └── writing-plans/
│           └── SKILL.md
├── commands/
├── agents/
└── hooks/
```

**Pattern:** Categorized directories with individual skill folders, NO root SKILL.md

### 2.3 Marketplace Boilerplate Standard

**Repository:** https://github.com/halans/cc-marketplace-boilerplate

```
.
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── webapp-starter/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       ├── commands/
│       ├── skills/
│       │   └── skill-creator/
│       │       └── SKILL.md
│       ├── hooks/
│       │   └── hooks.json
│       └── .mcp.json
└── README.md
```

**Key Insight:** Skills are nested within plugins, but still maintain individual SKILL.md files

---

## 3. Distribution Mechanisms

### 3.1 Three Installation Methods

**1. Local Directory (Direct)**
```bash
# Personal skills
~/.claude/skills/my-skill/SKILL.md

# Project skills (team-shared via git)
.claude/skills/my-skill/SKILL.md
```

**2. Plugin Marketplace (Recommended for Distribution)**
```bash
# Add marketplace
/plugin marketplace add anthropics/skills

# Install specific plugin
/plugin install document-skills@anthropic-agent-skills
```

**3. Manual Copy**
```bash
git clone https://github.com/user/skill-repo.git
cp -r skill-repo/my-skill ~/.claude/skills/
```

### 3.2 Marketplace.json Format

**Location:** `.claude-plugin/marketplace.json`

**Structure (from Anthropic official repository):**
```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Owner Name",
    "email": "contact@example.com"
  },
  "metadata": {
    "description": "Marketplace description",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "document-skills",
      "description": "Document processing capabilities",
      "source": "./document-skills",
      "strict": false,
      "skills": [
        "./document-skills/xlsx",
        "./document-skills/docx",
        "./document-skills/pptx",
        "./document-skills/pdf"
      ]
    },
    {
      "name": "example-skills",
      "description": "Example skill collection",
      "source": ".",
      "skills": [
        "./algorithmic-art",
        "./artifacts-builder",
        "./brand-guidelines",
        "./canvas-design",
        "./frontend-design",
        "./internal-comms",
        "./mcp-builder",
        "./skill-creator",
        "./slack-gif-creator",
        "./theme-factory",
        "./webapp-testing"
      ]
    }
  ]
}
```

**Key Elements:**
- `plugins[]`: Array of skill collections
- `source`: Base directory for the plugin
- `skills[]`: Array of paths to individual skill directories
- Each path points to a directory containing SKILL.md

### 3.3 Plugin vs Skill Distinction

**Plugin:** A bundled package that can contain:
- Multiple skills (in `skills/` directory)
- Commands (slash commands)
- Agents (subagents)
- Hooks (event triggers)
- MCP servers (Model Context Protocol)

**Skill:** A single capability with:
- Required: SKILL.md with YAML frontmatter
- Optional: scripts/, references/, assets/

**Distribution Philosophy:**
- **Skills work everywhere:** Claude.ai, Claude Code, Claude Desktop, API
- **Plugins are Claude Code specific:** Enhanced packaging for professional distribution
- **Skills are model-invoked:** Claude decides when to use them
- **Commands are user-invoked:** User explicitly triggers them

---

## 4. Discovery and Loading Mechanism

### 4.1 How Claude Discovers Skills

**Three-tier search path:**
1. Personal: `~/.claude/skills/*/SKILL.md`
2. Project: `.claude/skills/*/SKILL.md`
3. Plugin: Installed plugins' skills directories

**Discovery Process:**
1. Claude scans all skill directories
2. Reads YAML frontmatter from each SKILL.md
3. Uses `description` field to determine relevance
4. Loads full SKILL.md content when skill is triggered
5. Progressive disclosure of references/scripts as needed

### 4.2 Progressive Disclosure (Core Design Pattern)

**Three levels of context loading:**

**Level 1 - Metadata Only (Always Loaded):**
```yaml
---
name: note-taking
description: Transform markdown notes into an AI-navigable second brain.
  Use when user wants to capture, search, or organize knowledge.
---
```

**Level 2 - SKILL.md Body (Loaded When Relevant):**
- Full instructions and capabilities
- Usage patterns and trigger phrases
- Core functionality documentation

**Level 3 - Supporting Files (Loaded On-Demand):**
- Reference documentation (when specific features needed)
- Scripts (when executed via Bash tool)
- Examples (when user asks for them)

**Why This Matters:**
- Enables "effectively unbounded" skill content
- Prevents context window overflow
- Allows detailed documentation without performance penalty

---

## 5. Best Practices Summary

### 5.1 File Organization

**DO:**
- ✅ Create separate directory for each skill
- ✅ Include YAML frontmatter in every SKILL.md
- ✅ Keep main SKILL.md under 500 lines
- ✅ Use references/ for detailed documentation
- ✅ Keep references one level deep from SKILL.md
- ✅ Use gerund form for skill names (e.g., "note-taking", "task-managing")

**DON'T:**
- ❌ Create root-level SKILL.md for multi-skill repositories
- ❌ Nest SKILL.md files deeper than intended structure
- ❌ Exceed 5,000 words in main SKILL.md
- ❌ Use XML tags or reserved words in metadata
- ❌ Write descriptions in first person

### 5.2 Writing Effective Descriptions

**Good Examples:**
```yaml
description: Transform markdown notes into an AI-navigable second brain.
  Use when user wants to capture, search, or organize knowledge across projects.
```

**Bad Examples:**
```yaml
description: A note-taking tool  # Too vague, missing "when to use"
description: I help you take notes  # First person, not "when to use"
description: This is the best note-taking system ever created...  # Marketing, not functional
```

**Formula:** [What it does] + [When to use it] = Effective Description

### 5.3 Multi-Skill Repository Organization

**Recommended Structure for Your Repository:**

**Option A - Flat Structure (Anthropic Pattern):**
```
productivity-skills/
├── .claude-plugin/
│   └── marketplace.json
├── note-taking/
│   ├── SKILL.md
│   ├── hooks/
│   └── templates/
├── task-management/
│   └── SKILL.md
├── time-tracking/
│   └── SKILL.md
├── meeting-notes/
│   └── SKILL.md
├── docs/
├── examples/
└── README.md
```

**Option B - Categorized Structure (Superpowers Pattern):**
```
productivity-skills/
├── .claude-plugin/
│   └── marketplace.json
├── skills/
│   ├── knowledge/
│   │   ├── note-taking/
│   │   │   └── SKILL.md
│   │   └── meeting-notes/
│   │       └── SKILL.md
│   ├── workflow/
│   │   ├── task-management/
│   │   │   └── SKILL.md
│   │   └── time-tracking/
│   │       └── SKILL.md
├── docs/
├── examples/
└── README.md
```

**Critical:** NO root-level SKILL.md in either pattern

### 5.4 Marketplace Distribution

**To enable one-command installation:**

1. Create `.claude-plugin/marketplace.json`:
```json
{
  "name": "productivity-skills",
  "owner": {
    "name": "Your Name",
    "email": "your@email.com"
  },
  "metadata": {
    "description": "AI-native productivity skills for Claude",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "productivity-skills",
      "description": "Note-taking, task management, and personal productivity",
      "source": ".",
      "skills": [
        "./note-taking",
        "./task-management",
        "./time-tracking",
        "./meeting-notes"
      ]
    }
  ]
}
```

2. Users install via:
```bash
/plugin marketplace add username/productivity-skills
/plugin install productivity-skills
```

---

## 6. Current Repository Analysis

### 6.1 Current Structure

```
productivity-skills/
├── SKILL.md                  # ⚠️ NON-STANDARD ROOT FILE
├── CLAUDE.md
├── note-taking/
│   ├── SKILL.md             # ✅ Correct
│   ├── hooks/
│   └── templates/
├── docs/
└── examples/
```

### 6.2 Issues Identified

**Issue #1: Root SKILL.md is Non-Standard**
- No examples found in official or community repositories
- May confuse Claude's discovery mechanism
- Not aligned with marketplace distribution patterns

**Issue #2: Root SKILL.md Content**
- Current root SKILL.md is actually a README-style overview
- Contains installation instructions and philosophy
- This content belongs in README.md, not SKILL.md

**Issue #3: Missing Marketplace Configuration**
- No `.claude-plugin/marketplace.json`
- Prevents one-command installation
- Not ready for marketplace distribution

### 6.3 Recommended Changes

**High Priority:**

1. **Remove or Rename Root SKILL.md**
   - Convert current SKILL.md → README.md (merge with existing README if present)
   - Keep skill-specific SKILL.md files only

2. **Add Marketplace Configuration**
   - Create `.claude-plugin/marketplace.json`
   - List all skills in the plugins array
   - Enable plugin-based installation

3. **Validate YAML Frontmatter**
   - Ensure all skill SKILL.md files have proper frontmatter
   - Verify descriptions follow best practices
   - Check name format compliance

**Medium Priority:**

4. **Consider Organizational Structure**
   - Decide: Flat vs. Categorized
   - Update marketplace.json paths accordingly

5. **Add Template Skill**
   - Create `template-skill/` as reference
   - Document your skill creation process

**Low Priority:**

6. **Documentation**
   - Add contributing guide for new skills
   - Document marketplace installation
   - Create skill authoring guide

---

## 7. Authoritative Sources

### 7.1 Official Documentation

1. **Agent Skills Overview**
   https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

2. **Skill Authoring Best Practices**
   https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

3. **Claude Code Skills**
   https://code.claude.com/docs/en/skills

4. **Claude Code Plugins**
   https://code.claude.com/docs/en/plugins

5. **Anthropic Skills Announcement**
   https://www.anthropic.com/news/skills

6. **Engineering Deep Dive**
   https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

### 7.2 Reference Implementations

1. **Official Anthropic Skills**
   https://github.com/anthropics/skills
   - Canonical example of multi-skill repository
   - Official marketplace.json structure

2. **Superpowers Core Library**
   https://github.com/obra/superpowers
   - 20+ battle-tested skills
   - Excellent categorization pattern

3. **Marketplace Boilerplate**
   https://github.com/halans/cc-marketplace-boilerplate
   - Complete plugin structure example
   - Demonstrates marketplace.json usage

4. **Claude Code Builder**
   https://github.com/alexanderop/claude-code-builder
   - Full plugin ecosystem example

### 7.3 Community Resources

1. **Awesome Claude Skills**
   https://github.com/travisvn/awesome-claude-skills
   - Curated list of 100+ skills
   - Examples and patterns

2. **Claude Skills Deep Dive**
   https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
   - Technical analysis of skills system

3. **Skills Marketplace Hub**
   https://skillsmp.com/
   - Unofficial browser for 10,000+ skills
   - Community patterns and trends

---

## 8. Key Takeaways

### 8.1 Critical Findings

1. **No Root SKILL.md Pattern Exists**
   - Zero examples in official repositories
   - Zero examples in major community projects
   - Not supported by marketplace.json structure

2. **Progressive Disclosure is Core**
   - Skills can be "effectively unbounded" in size
   - Context management handled through file structure
   - References loaded only when needed

3. **Marketplace Distribution is Standard**
   - `.claude-plugin/marketplace.json` is the expected format
   - Enables professional, versioned distribution
   - Required for one-command installation

4. **Skills vs Plugins Distinction**
   - Skills: Cross-platform capabilities (model-invoked)
   - Plugins: Claude Code-specific bundles (can include skills)
   - Skills are the portable unit, plugins are the distribution unit

### 8.2 Recommendations for Productivity-Skills

**Immediate Actions:**

1. Convert root SKILL.md to README.md
2. Create `.claude-plugin/marketplace.json`
3. Validate YAML frontmatter in all skill SKILL.md files

**Strategic Decisions Needed:**

1. Choose organizational pattern (flat vs. categorized)
2. Define version numbering strategy
3. Decide on skill naming conventions (for future skills)

**Future Planning:**

1. Template for creating new skills
2. Contributing guidelines
3. Skill discovery documentation
4. Testing methodology

---

## 9. References and Further Reading

### Official Documentation
- Claude Agent Skills Overview: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- Best Practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- Claude Code Skills: https://code.claude.com/docs/en/skills
- Plugin Documentation: https://code.claude.com/docs/en/plugins

### Example Repositories
- Anthropic Official Skills: https://github.com/anthropics/skills
- Superpowers Library: https://github.com/obra/superpowers
- Marketplace Boilerplate: https://github.com/halans/cc-marketplace-boilerplate

### Community Resources
- Awesome Claude Skills: https://github.com/travisvn/awesome-claude-skills
- Skills Marketplace Hub: https://skillsmp.com/
- Deep Dive Analysis: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/

### Articles and Guides
- "Claude Skills are awesome, maybe a bigger deal than MCP": https://simonwillison.net/2025/Oct/16/claude-skills/
- "Your First Claude Skill": https://build.ms/2025/10/17/your-first-claude-skill/
- Understanding Skills vs Commands vs Plugins: https://www.youngleaders.tech/p/claude-skills-commands-subagents-plugins

---

**Research compiled by:** Claude Code
**Date:** 2025-11-15
**Sources validated:** Official Anthropic docs, GitHub examples, community resources
**Confidence level:** High (multiple authoritative sources confirm findings)
