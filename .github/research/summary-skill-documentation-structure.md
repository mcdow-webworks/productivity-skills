# Quick Reference: Claude Skills Documentation Structure

**Date:** 2025-11-17
**See also:** research-skill-documentation-best-practices.md (comprehensive findings)

---

## The Golden Rule: Progressive Disclosure

> "Rather than including everything in SKILL.md, adopt a 'table of contents' approach. Reference files are read only when needed (zero token cost until accessed)."
> — Anthropic Official Documentation

---

## SKILL.md Content Limits

**Target size**: Under 500 lines (under 200 lines ideal)

**Must include**:
- YAML frontmatter with `name` and `description`
- When to use (trigger phrases)
- Quick start examples (minimal)
- Links to reference documentation

**Must NOT include**:
- Comprehensive API specifications → `reference/API.md`
- Algorithm implementation details → `reference/ALGORITHM.md`
- Detailed examples → `examples/EXAMPLES.md`
- Step-by-step implementation → `reference/WORKFLOW.md`

---

## Directory Structure

```
skill-name/
├── SKILL.md              # Navigation hub (100-200 lines)
├── scripts/              # Executable tools
│   ├── tool.py           # Main utility
│   └── README.md         # Script architecture overview
├── references/           # Loaded only when needed
│   ├── API.md            # Complete command specification
│   ├── WORKFLOW.md       # Implementation decision logic
│   ├── ALGORITHM.md      # Technical details
│   └── TROUBLESHOOTING.md
├── examples/
│   └── EXAMPLES.md       # Comprehensive usage examples
└── assets/
    └── template.md       # Templates and resources
```

---

## What Goes Where: Quick Decision Tree

### SKILL.md
- Skill purpose (1-2 sentences)
- When Claude should use it (trigger phrases)
- Basic workflow (3-5 steps, high-level)
- Quick examples (1-2 simple cases)
- Links to references ("See API.md for details")

### reference/API.md
- Complete command specifications
- All parameters (required/optional)
- JSON input/output schemas
- Error responses and exit codes
- Parameter validation rules

### reference/WORKFLOW.md
- Detailed implementation logic
- Decision trees (when to add vs. update)
- Content extraction patterns
- Edge case handling
- When to load other references

### reference/ALGORITHM.md
- Technical implementation details
- Scoring formulas
- Data structure explanations
- Performance considerations
- Why specific approaches were chosen

### examples/EXAMPLES.md
- Comprehensive usage scenarios
- Edge cases
- Multi-step workflows
- Common patterns
- Real-world use cases

### scripts/README.md
- Script architecture overview
- Dependencies and requirements
- Testing instructions
- Development notes

---

## Three-Tier Token Architecture

### Tier 1: Metadata (Always Loaded)
```yaml
name: skill-name
description: What it does and when to use it
```
**Cost**: ~50 tokens
**Purpose**: Skill discovery

### Tier 2: SKILL.md (Loaded When Relevant)
- Overview and navigation
- Basic usage
- Links to references

**Cost**: 500-1000 tokens (if kept under 200 lines)
**Purpose**: Decide what to do next

### Tier 3: Reference Files (Loaded Only When Needed)
- API.md
- WORKFLOW.md
- ALGORITHM.md
- EXAMPLES.md

**Cost**: 0 tokens until accessed
**Purpose**: Detailed implementation

---

## CLI Tool API Documentation Pattern

### In SKILL.md (minimal)
```markdown
## Usage

Run commands via JSON stdin:
```bash
echo '{"command":"action","param":"value"}' | python scripts/tool.py
```

See reference/API.md for complete command specification.
```

### In reference/API.md (comprehensive)
```markdown
# Tool API Reference

## command_name

**Required parameters**:
- `param1` (string): Description
- `param2` (number): Description

**Optional parameters**:
- `param3` (boolean): Description, defaults to false

**Example**:
```bash
echo '{"command":"command_name","param1":"value"}' | python tool.py
```

**Success response**:
```json
{"success": true, "data": {...}}
```

**Error responses**:
- Missing param: `{"success": false, "error": "Missing param1"}`
- Invalid value: `{"success": false, "error": "Invalid param2"}`
```

---

## Writing Style

### SKILL.md
**Use**: Imperative/infinitive form (verb-first)
- ✅ "To add a note, run the add command"
- ✅ "Extract heading from user input"
- ❌ "You should add a note"
- ❌ "Claude will extract the heading"

**Tone**: Direct, instructional
**Perspective**: Second-person imperative or infinitive

### Reference Files
**Use**: Third-person technical
- ✅ "The search algorithm calculates relevance scores based on..."
- ✅ "Returns JSON object with success boolean"
- ❌ "You calculate relevance by..."

---

## Common Anti-Patterns to Avoid

### ❌ Everything in SKILL.md
- Results in 400+ line files
- High token cost every time skill activates
- Tempts Claude to implement inline instead of using scripts

### ❌ Nested references
- SKILL.md → reference/A.md → reference/B.md
- Claude may only preview B.md partially
- Keep all references one level deep from SKILL.md

### ❌ Duplicate information
- Same examples in SKILL.md and EXAMPLES.md
- Keep SKILL.md minimal, comprehensive examples in separate file

### ❌ Implementation details in SKILL.md
- Algorithm explanations
- Scoring formulas
- Data structure internals
- Move to reference/ALGORITHM.md

### ❌ No links to references
- Claude doesn't know references exist
- Must explicitly link: "See API.md for command details"

---

## Refactoring Checklist

When refactoring an existing skill:

- [ ] SKILL.md is under 200 lines
- [ ] API specifications moved to reference/API.md
- [ ] Algorithm details moved to reference/ALGORITHM.md
- [ ] Workflow logic moved to reference/WORKFLOW.md
- [ ] Comprehensive examples moved to examples/EXAMPLES.md
- [ ] SKILL.md links to all reference files
- [ ] Scripts have separate README.md (if needed)
- [ ] No nested references (all one level from SKILL.md)
- [ ] Frontmatter includes name and description
- [ ] Writing style is imperative/infinitive

---

## Testing the Structure

After refactoring, verify:

1. **SKILL.md is concise**: Can you read it in under 2 minutes?
2. **Navigation is clear**: Does SKILL.md point to where details live?
3. **References are accessible**: Can Claude find API.md when needed?
4. **No duplication**: Is each piece of information in exactly one place?
5. **Script usage clear**: Does SKILL.md make it obvious to use scripts vs. inline code?

---

## Real-World Example: Note-Taking Skill

### Before Refactoring
```
note-taking/
└── SKILL.md (400 lines)
    ├── Trigger phrases
    ├── Workflow logic
    ├── API specifications
    ├── Search algorithm details
    ├── Comprehensive examples
    └── Error handling
```
**Problem**: Claude has all details in context, bypasses scripts

### After Refactoring
```
note-taking/
├── SKILL.md (120 lines)
│   ├── When to use
│   ├── Basic workflow
│   ├── Quick examples
│   └── Links to references
├── reference/
│   ├── API.md (200 lines) - Complete command specs
│   ├── SEARCH.md (150 lines) - Algorithm details
│   ├── WORKFLOW.md (180 lines) - Implementation logic
│   └── TROUBLESHOOTING.md (100 lines)
└── examples/
    └── EXAMPLES.md (250 lines) - Comprehensive scenarios
```
**Result**: Clear architecture, references loaded only when needed

---

## Key Metrics for Success

**SKILL.md**:
- Lines: 100-200 (under 500 max)
- Token cost when loaded: 500-1000
- Links to references: 3-6

**Reference files**:
- Count: 3-6 typical
- Token cost until accessed: 0
- Load frequency: Only when specific details needed

**Overall**:
- Total skill size: Unlimited (but organized)
- Active token cost: Minimal (just SKILL.md when relevant)
- Maintenance: Easy (update references without touching SKILL.md)

---

## Quick Decision: "Does This Belong in SKILL.md?"

Ask yourself:

1. **Does Claude need this to decide whether to use the skill?** → YES, include
2. **Does Claude need this to decide what to do next?** → YES, include (high-level)
3. **Is this a specific parameter value or technical detail?** → NO, reference file
4. **Is this one example among many?** → NO, examples file
5. **Is this explaining how an algorithm works?** → NO, reference file
6. **Could I summarize this in one sentence with a link?** → YES, do that instead

**When in doubt**: Put it in a reference file and link to it from SKILL.md

---

## Resources

- **Full research**: research-skill-documentation-best-practices.md
- **Official docs**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- **CLI guidelines**: https://clig.dev/
- **Anthropic examples**: https://github.com/anthropics/skills
