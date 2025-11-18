# Research: Claude Skills Documentation Best Practices

**Research Date:** 2025-11-17
**Context:** Refactoring note-taking skill to properly separate user documentation from implementation instructions
**Problem:** Current SKILL.md mixes user documentation with implementation details, causing Claude to bypass intended Python script architecture

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [SKILL.md Structure and Content](#skillmd-structure-and-content)
3. [Progressive Disclosure Pattern](#progressive-disclosure-pattern)
4. [Directory Organization](#directory-organization)
5. [What Belongs in SKILL.md vs. References](#what-belongs-in-skillmd-vs-references)
6. [CLI Tool API Documentation Standards](#cli-tool-api-documentation-standards)
7. [Documentation Separation of Concerns](#documentation-separation-of-concerns)
8. [Real-World Examples](#real-world-examples)
9. [Recommendations for Note-Taking Skill](#recommendations-for-note-taking-skill)
10. [References](#references)

---

## Executive Summary

### Key Findings

1. **SKILL.md should be concise** (under 500 lines recommended) and serve as a "table of contents" that points to detailed references, not a comprehensive implementation guide.

2. **Progressive disclosure is critical**: Show only essential information to help Claude decide what to do next, then reveal details as needed through reference files.

3. **Three-tier architecture**:
   - **Metadata** (name + description): Always loaded for skill discovery
   - **SKILL.md**: Loaded when skill becomes relevant
   - **Reference files**: Loaded only as needed (zero token cost until accessed)

4. **Clear separation**: User-facing instructions vs. implementation details vs. API documentation should live in different files.

5. **Scripts are tools, not documentation**: Python scripts should be executable utilities with their own API documentation, not embedded inline code examples in SKILL.md.

### Critical Insight

The official Anthropic documentation explicitly states:

> "Rather than including everything in SKILL.md, adopt a 'table of contents' approach. Reference files are read only when needed (zero token cost until accessed). Scripts execute without loading full contents into context."

This means implementation details, detailed API specifications, and comprehensive examples should NOT be in SKILL.md—they belong in separate reference files.

---

## SKILL.md Structure and Content

### Required Components

**YAML Frontmatter** (required):
```yaml
---
name: skill-name  # Max 64 chars, lowercase/numbers/hyphens only
description: What the skill does and when to use it  # Max 1024 chars, third-person
---
```

**Additional frontmatter fields** (optional):
```yaml
---
name: skill-name
description: Detailed description including when to use this skill
allowed-tools:
  - Bash
  - Read
  - Write
metadata:
  version: 1.0.0
  category: productivity
  status: production
  documentation: reference/API.md
---
```

### Body Content Guidelines

**Length**: Keep under 500 lines for optimal performance (Source: Anthropic official docs)

**Writing style**: Use imperative/infinitive form (verb-first instructions), not second person
- Good: "To add a note, use the add command"
- Bad: "You should add a note by using..."

**What to include in SKILL.md**:
- Quick overview of skill purpose
- Natural language trigger phrases users will say
- Basic usage examples (minimal, essential only)
- Links to detailed references ("See API.md for complete command reference")
- Workflow checklists for multi-step processes
- Template patterns showing expected output format
- Error handling guidance

**What to EXCLUDE from SKILL.md**:
- Explanations Claude already knows (e.g., "JSON is a data format...")
- Deep implementation details (algorithm explanations, code internals)
- Comprehensive API documentation (belongs in reference files)
- Time-sensitive information (use separate changelog files)
- Multiple equivalent approaches without default recommendation
- "Voodoo constants" without justification

---

## Progressive Disclosure Pattern

### Concept

Progressive disclosure is an interaction design pattern that structures information to show high-level overviews first, with expandable details for those who need depth. This directly supports information architecture by reducing cognitive load and maintaining visual hierarchy.

### Application to Claude Skills

**Three levels of detail**:

1. **Metadata** (name + description in frontmatter)
   - Always loaded into context
   - Used for skill discovery
   - Must be concise but descriptive

2. **SKILL.md body**
   - Loaded when skill becomes relevant
   - Provides overview and navigation
   - Points to reference files

3. **Reference files** (scripts/, references/, assets/)
   - Loaded only when explicitly needed
   - Zero token cost until accessed
   - Contains detailed specifications

### Implementation Strategy

**Table of Contents Approach**:
```markdown
# Note-Taking Skill

Use this skill when users say phrases like "Note that...", "Remember that...", or "What did I note about...".

## Quick Start

To add a note: "Note that [your content here]"
To search notes: "What did I note about [topic]?"

## Detailed Documentation

- [Complete API Reference](reference/API.md) - Full command specifications
- [Search Algorithm](reference/SEARCH.md) - Relevance scoring details
- [Entry Format Guide](reference/FORMAT.md) - Markdown structure and conventions
- [Examples](examples/) - Common usage patterns

## Error Handling

If commands fail, check [Troubleshooting Guide](reference/TROUBLESHOOTING.md)
```

**One level deep rule**: All reference files should link directly from SKILL.md. Avoid nested references (file A → file B → file C) since Claude may only preview nested content partially.

---

## Directory Organization

### Standard Structure

```
skill-name/
├── SKILL.md              # Core prompt and instructions (required)
├── scripts/              # Executable Python/Bash scripts
│   ├── tool_name.py      # Primary utility script
│   └── helper.sh         # Supporting scripts
├── references/           # Documentation loaded into context
│   ├── API.md            # Detailed API specifications
│   ├── EXAMPLES.md       # Comprehensive usage examples
│   └── TROUBLESHOOTING.md
└── assets/               # Templates and binary files
    └── template.md       # File templates
```

### Directory Purposes

**scripts/**:
- Contains executable code that Claude runs via Bash tool
- Automation scripts, data processors, validators, code generators
- Perform deterministic operations
- Should have their own API documentation (in references/)
- NOT loaded into context—only executed

**references/**:
- Documentation, API references, guides
- Loaded into context only when needed
- Can be comprehensive (detailed examples, specifications)
- Organized by domain or topic

**assets/**:
- Binary files, templates, configuration files
- Resources that support the skill
- Not documentation

### Evolution Pattern

**Simple skill**: Single SKILL.md file with embedded instructions

**Growing skill**: Add separate reference files
```
skill-name/
├── SKILL.md          # Overview and navigation
├── REFERENCE.md      # API details
└── EXAMPLES.md       # Usage patterns
```

**Complex skill**: Organize by domain
```
bigquery-skill/
├── SKILL.md          # Navigation hub
└── reference/
    ├── finance.md    # Domain-specific references
    ├── sales.md
    └── product.md
```

---

## What Belongs in SKILL.md vs. References

### SKILL.md Should Contain

**1. Skill activation context**
```markdown
Use this skill when users say:
- "Note that..."
- "Remember that..."
- "What did I note about...?"
```

**2. Quick start guide** (minimal examples)
```markdown
## Quick Start

Add a note: "Note that Python 3.12 was released in October 2023"
Search notes: "What did I note about Python?"
```

**3. Navigation to detailed docs**
```markdown
See [API Reference](reference/API.md) for complete command specifications.
See [Search Algorithm](reference/SEARCH.md) for relevance scoring details.
```

**4. High-level workflow**
```markdown
## Workflow

1. User says "Note that [content]"
2. Extract heading and content from user input
3. Run: `echo '{"command":"add","heading":"...","content":"..."}' | python scripts/notes_manager.py`
4. Confirm success to user
```

**5. Error handling strategy**
```markdown
If script returns error status:
1. Read error message from stderr
2. Check [Troubleshooting Guide](reference/TROUBLESHOOTING.md)
3. Provide user-friendly explanation
```

### Reference Files Should Contain

**reference/API.md** - Complete API specification:
```markdown
# Notes Manager API Reference

## Commands

### add
Adds a new note entry to the monthly file.

**Input (JSON via stdin)**:
```json
{
  "command": "add",
  "heading": "Category - Brief description",
  "content": "Detailed content with multiple lines..."
}
```

**Output (JSON to stdout)**:
```json
{
  "success": true,
  "file": "/path/to/2025/11-November.md",
  "message": "Note added successfully"
}
```

**Error cases**:
- Missing heading: Returns error with status code 1
- File write failure: Returns error with details
```

**reference/SEARCH.md** - Implementation details:
```markdown
# Search Algorithm

## Relevance Scoring

The search algorithm calculates relevance scores based on:

1. **Exact phrase match in heading**: +500 points
2. **All query terms in heading**: +100 points
3. **Individual terms in heading**: +20 each
4. **Terms in content**: Capped at +50 total
5. **Recency boost**:
   - < 30 days: +10
   - < 90 days: +5
   - < 180 days: +2

## Minimum Threshold

Updates require minimum relevance score ≥50 to prevent weak matches.
```

**reference/FORMAT.md** - Conventions and standards:
```markdown
# Note Entry Format

## Standard Structure

```markdown
# Category - Brief description
Content with multiple lines, code blocks, links, etc.

**Created:** YYYY-MM-DD

**Update (YYYY-MM-DD):** Additional information
```

## Categories

Inferred from keywords:
- Work: project, meeting, deadline, client
- Learning: learned, tutorial, course, documentation
- Health: exercise, sleep, diet, medication
```

**reference/EXAMPLES.md** - Comprehensive usage examples:
```markdown
# Usage Examples

## Adding Notes

**Simple note**:
User: "Note that I learned about Python decorators today"
Result: Creates entry "Learning - Python decorators" with content and timestamp

**Multi-line note**:
User: "Note that our project uses these dependencies: Django 4.2, PostgreSQL 15, Redis 7"
Result: Preserves line breaks and formatting

## Searching Notes

**Exact phrase match**:
User: "What did I note about Python decorators?"
Result: Returns entry with "Python decorators" in heading (high relevance score)

**Partial match**:
User: "Status of the project?"
Result: Returns entries mentioning "project" sorted by relevance
```

---

## CLI Tool API Documentation Standards

### Industry Best Practices

Based on research from Command Line Interface Guidelines (clig.dev) and Heroku CLI Style Guide:

**1. Standard streams usage**:
- **stdout**: All primary output (JSON results, success messages)
- **stderr**: Warnings, errors, out-of-band information
- **stdin**: Input data (JSON commands)

**2. Support `-` for stdin/stdout**:
```bash
# Read from stdin
cat data.json | python tool.py -

# Write to stdout (default)
python tool.py input.json > output.json
```

**3. JSON output flag**:
- Offer `--json` flag for structured output
- Makes scripting and parsing easier
- Human-readable by default, JSON on request

**4. Error handling**:
- Use appropriate exit codes (0 = success, non-zero = error)
- stderr for error messages (doesn't interfere with stdout piping)
- Provide clear, actionable error messages

### Python CLI Tool Documentation Structure

**API Reference format** (similar to notes_manager.py):

```markdown
# Tool Name API

## Usage

```bash
echo '{"command":"action","param":"value"}' | python tool.py
```

## Input Format

JSON via stdin with required fields:
- `command`: Action to perform (required)
- Additional fields vary by command

## Output Format

JSON to stdout with standard structure:
```json
{
  "success": true,
  "data": {...},
  "message": "Human-readable status"
}
```

## Commands

### command_name

**Description**: What this command does

**Required parameters**:
- `param1` (string): Description
- `param2` (number): Description

**Optional parameters**:
- `param3` (boolean): Description, defaults to false

**Example**:
```bash
echo '{"command":"command_name","param1":"value","param2":42}' | python tool.py
```

**Success response**:
```json
{
  "success": true,
  "data": {"result": "..."},
  "message": "Operation completed"
}
```

**Error responses**:
- Missing required parameter: `{"success": false, "error": "Missing param1"}`
- Invalid value: `{"success": false, "error": "param2 must be positive"}`

**Exit codes**:
- 0: Success
- 1: Invalid input
- 2: File operation failed
```

### Location of API Documentation

**NOT in SKILL.md** - Instead in `reference/API.md` or `scripts/README.md`

This keeps SKILL.md focused on when/how to use the skill, while technical specifications live in reference documentation that Claude loads only when needed.

---

## Documentation Separation of Concerns

### Three Types of Documentation

Research from "Documentation as Code" and API documentation best practices identifies three distinct documentation types:

**1. User Documentation** (End-user guides)
- How to use the skill from user perspective
- Natural language interaction patterns
- What users can accomplish
- Example: "Say 'Note that...' to add a note"

**2. Implementation Documentation** (Developer/Claude guides)
- How Claude should interact with the system
- Workflow and decision-making logic
- When to use scripts vs. direct implementation
- Example: "When user says 'Note that', extract heading and content, then run add command"

**3. API Documentation** (Technical reference)
- Complete specification of tools/scripts
- Input/output formats
- Error cases and edge cases
- Example: "add command requires heading and content fields, returns JSON with success boolean"

### Recommended File Organization

```
note-taking/
├── SKILL.md                    # User docs + Implementation docs (high-level)
├── reference/
│   ├── API.md                  # Complete API specification
│   ├── SEARCH.md               # Algorithm implementation details
│   ├── FORMAT.md               # Data format conventions
│   └── TROUBLESHOOTING.md      # Error handling reference
├── scripts/
│   ├── notes_manager.py        # Executable tool (self-documenting with docstrings)
│   └── README.md               # Script architecture overview
└── examples/
    └── EXAMPLES.md             # Comprehensive usage examples
```

### What Goes Where

**SKILL.md** (50-200 lines):
```markdown
# Note-Taking Skill

## When to Use
User says: "Note that...", "Remember that...", "What did I note about...?"

## How It Works
1. Extract user intent and content
2. Run appropriate notes_manager.py command
3. Report results to user

## Basic Usage
Add: "Note that [content]"
Search: "What did I note about [topic]?"
Update: "Add to my note about [topic]: [new content]"

## Implementation
Use scripts/notes_manager.py for all operations.
See reference/API.md for complete command specifications.
See reference/SEARCH.md for search algorithm details.
```

**reference/API.md** (200-500 lines):
```markdown
# Notes Manager API Reference

Complete specification of all commands, parameters, responses, and error cases.
[Comprehensive details from earlier example]
```

**scripts/README.md** (100-200 lines):
```markdown
# Notes Manager Script Architecture

## Overview
Python utility for managing markdown notes in monthly files.

## Dependencies
- Python 3.7+
- Standard library only (json, pathlib, datetime, re)

## File Structure
- Notes stored in ~/Documents/notes/YYYY/MM-Month.md
- Index maintained in .index.json for fast searching

## Testing
```bash
# Manual testing examples
echo '{"command":"search","query":"test"}' | python notes_manager.py
```
```

### Benefits of Separation

1. **Token efficiency**: SKILL.md stays small, detailed docs loaded only when needed
2. **Maintainability**: Update API details without changing skill logic
3. **Clarity**: Each file has single, clear purpose
4. **Scalability**: Easy to add new reference documents without bloating SKILL.md
5. **Prevents bypassing**: Clear architecture reduces Claude's temptation to implement inline

---

## Real-World Examples

### Example 1: PDF Skill (Anthropic Official)

**Structure observed**:
```
pdf/
├── SKILL.md           # Overview and basic usage
├── forms.md           # Detailed forms handling reference
└── scripts/
    └── extract_text.py
```

**SKILL.md pattern**:
- Concise overview of when to use skill
- Basic example: "To extract text from PDF, run extract_text.py"
- Link to forms.md for complex form handling
- Does NOT include full PDF parsing algorithm

**forms.md** (reference file):
- Comprehensive guide to PDF form field extraction
- Detailed examples and edge cases
- Loaded only when dealing with PDF forms

### Example 2: Skill Creator (Anthropic Official)

**Observed pattern**:
- SKILL.md provides interactive workflow
- Points to scripts/init_skill.py for actual execution
- Does NOT embed script logic in SKILL.md
- Clear separation: "Ask user questions, then run script with collected data"

### Example 3: Document Skills (PPTX)

**Structure**:
```
pptx/
├── SKILL.md
├── scripts/
│   └── create_presentation.py
└── templates/
    └── default_template.pptx
```

**SKILL.md approach**:
- Focuses on when to create presentations
- Shows basic command structure
- References template in assets/
- Script handles complex PPTX manipulation

### Common Patterns Across Examples

1. **SKILL.md is navigation hub**: Points to resources, doesn't contain them
2. **Scripts are tools**: Executed by Claude, not explained in detail in SKILL.md
3. **Reference files hold details**: Algorithm specifics, format documentation
4. **Examples are separate**: Comprehensive examples in dedicated files
5. **Progressive disclosure**: Start simple, link to complexity

---

## Recommendations for Note-Taking Skill

### Current Problem

The note-taking skill's SKILL.md currently contains:
- User-facing trigger phrases (good)
- Detailed implementation instructions (should be high-level only)
- Inline code examples (belongs in reference/EXAMPLES.md)
- API specifications (belongs in reference/API.md)
- Search algorithm details (belongs in reference/SEARCH.md)

This causes Claude to have all implementation details in context, leading to bypassing the intended Python script architecture.

### Recommended Refactoring

**1. Slim down SKILL.md** (target: 100-150 lines)

```markdown
---
name: note-taking
description: Transform markdown notes into an AI-navigable second brain. Use when users say "Note that", "Remember that", "What did I note about", or explicitly reference their notes.
allowed-tools:
  - Bash
  - Read
metadata:
  version: 2.0.0
  category: productivity
  status: production
---

# Note-Taking Skill

## When to Use

Trigger when user explicitly mentions notes:
- Adding: "Note that...", "Add a note about...", "Remember that..."
- Searching: "What did I note about...", "Find my notes on...", "Status of..."
- Updating: "Add to the X note...", "Update X with..."

## How It Works

1. Identify user intent (add/search/update)
2. Extract relevant content from user message
3. Execute appropriate notes_manager.py command
4. Report results conversationally

All operations use scripts/notes_manager.py via JSON stdin/stdout.

## Basic Usage

**Add a note**:
User: "Note that Python 3.12 was released in October 2023"
Action: Run add command with extracted heading and content

**Search notes**:
User: "What did I note about Python?"
Action: Run search command, present top results

**Update existing note**:
User: "Add to my Python note: now includes match-case statements"
Action: Search for best match, run append command

## Implementation Guide

See reference/WORKFLOW.md for detailed decision logic.
See reference/API.md for complete command specifications.
See reference/SEARCH.md for search and matching algorithm.
See examples/EXAMPLES.md for comprehensive usage patterns.

## Error Handling

If script returns error:
1. Read stderr message
2. Provide user-friendly explanation
3. Suggest corrective action

Common issues documented in reference/TROUBLESHOOTING.md.
```

**2. Create reference/API.md** (comprehensive specification)

Move all command specifications, JSON formats, parameters, and error cases here. Include:
- Complete command reference (add, search, append, reindex, stats)
- Input/output JSON schemas
- Error responses and exit codes
- Parameter validation rules

**3. Create reference/SEARCH.md** (algorithm details)

Move search algorithm explanation here:
- Relevance scoring formula
- File header filtering logic
- Minimum threshold for updates
- Recency boost calculation
- Why content scoring is capped

**4. Create reference/WORKFLOW.md** (Claude implementation guide)

Move detailed workflow logic here:
- How to extract heading from user input
- How to determine if it's add vs. update
- When to search before adding
- How to handle ambiguous requests

**5. Create examples/EXAMPLES.md** (comprehensive examples)

Move all detailed examples here:
- Simple notes, multi-line notes, code snippets
- Various search patterns
- Update scenarios
- Edge cases

**6. Create reference/FORMAT.md** (data conventions)

Document note entry format:
- Markdown structure
- Timestamp format
- Category inference keywords
- File organization (YYYY/MM-Month.md)

**7. Create reference/TROUBLESHOOTING.md** (error reference)

Common errors and solutions:
- Script not found
- Permission errors
- Invalid JSON
- OneDrive path issues

### Expected Benefits

1. **Reduced token usage**: SKILL.md drops from ~400 lines to ~100 lines
2. **Clearer architecture**: Explicit separation between "when to use" and "how it works"
3. **Better script adherence**: Without inline examples, Claude more likely to use script
4. **Easier maintenance**: Update API details without touching core skill logic
5. **Scalability**: Easy to add new reference docs (migration guide, best practices, etc.)

### Migration Path

1. Create reference/ directory
2. Extract API.md from current SKILL.md
3. Extract SEARCH.md from current SKILL.md
4. Extract WORKFLOW.md from current SKILL.md
5. Extract EXAMPLES.md to examples/ directory
6. Rewrite SKILL.md to be concise with links to references
7. Test skill to ensure Claude loads references when needed
8. Update CLAUDE.md to reflect new structure

---

## References

### Official Anthropic Documentation

1. **Skill Authoring Best Practices**
   https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
   - Progressive disclosure pattern
   - SKILL.md content guidelines
   - File organization recommendations
   - Token optimization strategies

2. **Agent Skills Overview**
   https://docs.claude.com/en/docs/claude-code/skills
   - Basic skill structure
   - YAML frontmatter requirements
   - Directory conventions

3. **Anthropic Skills Repository**
   https://github.com/anthropics/skills
   - Real-world skill examples
   - PDF skill structure
   - Skill creator pattern

### Industry Standards

4. **Command Line Interface Guidelines**
   https://clig.dev/
   - stdin/stdout/stderr conventions
   - JSON output standards
   - Exit code best practices

5. **Heroku CLI Style Guide**
   https://devcenter.heroku.com/articles/cli-style-guide
   - --json flag recommendations
   - Human-readable vs. parseable output
   - Error handling patterns

6. **API Documentation Best Practices (Kong)**
   https://konghq.com/blog/learning-center/guide-to-api-documentation
   - Reference vs. user guide separation
   - Example-driven documentation
   - Progressive learning paths

### Documentation Architecture

7. **Progressive Disclosure (I'd Rather Be Writing)**
   https://idratherbewriting.com/ucd-progressive-disclosure/
   - Information architecture principles
   - Hypertext implementation
   - Content hierarchy strategies

8. **IBM Progressive Disclosure Best Practices**
   https://www.ibm.com/docs/en/technical-content?topic=practices-progressive-disclosure
   - Technical content organization
   - Detail level management

9. **Documentation as Code (Write the Docs)**
   https://www.writethedocs.org/guide/docs-as-code/
   - Separation of concerns
   - Documentation workflows
   - Collaborative documentation

### Technical References

10. **Python argparse Documentation**
    https://docs.python.org/3/library/argparse.html
    - CLI tool argument parsing
    - API reference structure
    - Tutorial vs. reference separation

---

## Appendix: Research Methodology

### Search Strategy

1. **Official sources first**: Anthropic documentation and GitHub repositories
2. **Industry standards**: CLI guidelines, API documentation best practices
3. **Architecture patterns**: Progressive disclosure, separation of concerns
4. **Real examples**: Official Anthropic skills, popular open source projects

### Authority Levels

- **Official**: Anthropic documentation (docs.claude.com, github.com/anthropics)
- **Industry Standard**: CLIG, Heroku, Kong, Write the Docs
- **Best Practice**: IBM, Nielsen Norman Group, established technical writers
- **Community**: Blog posts, Stack Overflow (used for context only)

### Validation Approach

Cross-referenced multiple sources to ensure consistency:
- Progressive disclosure mentioned in both Anthropic docs AND UX/documentation sources
- CLI standards confirmed across multiple authoritative guides (CLIG, Heroku)
- Separation of concerns validated in both docs-as-code AND API documentation literature

---

## Conclusion

The research clearly indicates that Claude Skills should follow a progressive disclosure architecture:

1. **SKILL.md**: Concise overview and navigation (under 500 lines)
2. **Reference files**: Detailed specifications loaded only when needed
3. **Scripts**: Executable tools with separate API documentation
4. **Examples**: Comprehensive examples in dedicated files

For the note-taking skill specifically, the recommendation is to extract:
- API specifications → reference/API.md
- Search algorithm → reference/SEARCH.md
- Workflow logic → reference/WORKFLOW.md
- Comprehensive examples → examples/EXAMPLES.md
- Data formats → reference/FORMAT.md
- Troubleshooting → reference/TROUBLESHOOTING.md

This refactoring will align with industry best practices, reduce token usage, improve maintainability, and encourage Claude to use the intended Python script architecture rather than bypassing it with inline implementations.
