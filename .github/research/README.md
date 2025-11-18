# Research Documentation

This directory contains development research, analysis, and technical documentation for the productivity-skills plugin.

## Purpose

These documents capture:
- Technical research and findings
- Platform compatibility investigations
- Design decision analysis
- Framework documentation research
- Best practices and recommendations

## Documents

### Cross-Platform Development

- **[research-cross-platform-paths.md](./research-cross-platform-paths.md)**
  - Cross-platform file path handling best practices
  - Windows vs Unix path conventions
  - Python Path object usage

- **[summary-path-best-practices.md](./summary-path-best-practices.md)**
  - Quick reference for path handling
  - Actionable recommendations

### Claude Skills Framework

- **[research-claude-skills-execution.md](./research-claude-skills-execution.md)**
  - Comprehensive research on Claude Code skills execution model
  - How Claude executes commands from SKILL.md
  - Working directory behavior and environment variables
  - Python version requirements and executable naming
  - Base directory message and resource location
  - **Status:** Based on official docs, community research, and reverse engineering

- **[summary-skills-execution-best-practices.md](./summary-skills-execution-best-practices.md)**
  - Quick reference for skill authors
  - Path handling patterns
  - Script design recommendations
  - Common mistakes to avoid

### Architecture and Design

- **[research-hooks-vs-utility-scripts.md](./research-hooks-vs-utility-scripts.md)**
  - Distinction between Claude Code hooks and utility scripts
  - When to use each approach

- **[research-tiered-trigger-systems.md](./research-tiered-trigger-systems.md)**
  - Natural language trigger system design
  - Tiered trigger architecture

### Issue Analysis

- **[analysis-notes-manager-issues.md](./analysis-notes-manager-issues.md)**
  - Analysis of notes_manager.py issues
  - Relevance scoring algorithm improvements
  - Entry matching and update logic

## Organization

Documents follow these naming conventions:

- `research-<topic>.md` - In-depth research and findings
- `summary-<topic>.md` - Quick reference and actionable guidance
- `analysis-<topic>.md` - Deep dive into specific issues or problems

## Contributing

When adding new research:

1. Create comprehensive research document: `research-<topic>.md`
2. Create actionable summary: `summary-<topic>.md`
3. Update this README with document descriptions
4. Link from GitHub issues for context

## Integration with Development

These documents inform:
- CLAUDE.md guidance for AI assistants
- Implementation decisions
- Testing strategies
- Documentation for end users

**Important:** Keep user-facing docs (README.md, CLAUDE.md) concise. Store detailed research here.

## Latest Research (2025-11-18)

### Claude Skills Execution Model

**Key Findings:**
- Skills execute via prompt expansion and Bash tool invocation
- No environment variables for skill location (use `Path(__file__).parent.parent`)
- Working directory is unpredictable - always use absolute paths
- Python executable hardcoded to `python3` (breaks on Windows Anaconda)
- Base directory provided at invocation but not as environment variable
- Forward slashes required in all paths (even on Windows)

**Impact on productivity-skills:**
- Remove `${CLAUDE_SKILL_ROOT}` references (doesn't exist)
- Update SKILL.md to use relative paths
- Update scripts to compute skill root from `__file__`
- Document Windows Anaconda limitation
- Test working directory assumptions

See: [research-claude-skills-execution.md](./research-claude-skills-execution.md)
