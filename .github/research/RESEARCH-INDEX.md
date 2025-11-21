# Research Index - Best Practices for Claude Skills Development

**Last Updated:** 2025-11-20
**Status:** Active research collection for productivity-skills plugin

---

## Overview

This directory contains comprehensive research on best practices for developing cross-platform, portable Claude Skills. All research is evidence-based, citing official Anthropic documentation, Python standards (PEPs), and industry best practices.

---

## Quick Reference Guide

### Python Executable Naming

**Question:** Should I use `python` or `python3` in SKILL.md?

**Answer:** Use `python` (not `python3`)

**Source:** `summary-python-executable-recommendations.md`

**Rationale:**
- Windows only has `python.exe` (no `python3.exe`)
- Anthropic's official skills use `python`
- Works in virtual environments on all platforms
- Follows PEP 394 recommendations for venv usage

---

### Script Paths

**Question:** How should I reference scripts in SKILL.md?

**Answer:** Use relative paths with forward slashes: `scripts/helper.py`

**Source:** `research-skill-script-invocation-patterns.md`

**Rationale:**
- Skills execute from skill base directory
- Forward slashes work in bash on all platforms (including Windows Git Bash)
- Official Claude Code documentation requires forward slashes
- Portable across all installation methods

---

### Working Directory

**Question:** What is the working directory when my script runs?

**Answer:** The skill's base directory (where SKILL.md is located)

**Source:** `research-skill-script-invocation-patterns.md`

**Evidence:** Claude Code documentation: "The base path enables Claude Code to locate and execute scripts bundled with the skill relative to that folder."

---

### Cross-Platform Paths

**Question:** How do I handle file paths in Python scripts for skills?

**Answer:** Use `pathlib.Path` and forward slashes

**Source:** `research-cross-platform-paths.md`

**Example:**
```python
from pathlib import Path

# Correct - works everywhere
notes_dir = Path.home() / "Documents" / "notes"

# Wrong - platform-specific separators
notes_dir = os.path.join(os.path.expanduser("~"), "Documents", "notes")
```

---

### Shebang Lines

**Question:** What shebang should I use in Python scripts?

**Answer:** `#!/usr/bin/env python3`

**Source:** `summary-python-executable-recommendations.md`

**Rationale:**
- Ignored on Windows (treated as comment)
- Ensures Python 3 on Unix systems
- Follows PEP 394 recommendations
- Different from command invocation (which should use `python`)

---

### Data Passing

**Question:** How should I pass data to scripts?

**Answer:** JSON via stdin (not command-line arguments)

**Source:** `research-skill-script-invocation-patterns.md`

**Example:**
```bash
# Correct - secure
echo '{"command":"search","query":"user input"}' | python scripts/helper.py

# Wrong - injection risk
python scripts/helper.py "user input"
```

---

### MCP Servers for Claude Desktop

**Question:** How do I make my skill work in Claude Desktop (remote environment)?

**Answer:** Create an MCP server wrapper using FastMCP

**Source:** `research-mcp-server-implementation.md`

**Rationale:**
- Claude Desktop runs remotely, can't directly execute local scripts
- MCP servers bridge the remote environment to local machine
- Stdio transport provides secure, local communication
- FastMCP minimizes boilerplate for Python scripts

**Quick Start:**
```python
from fastmcp import FastMCP
from my_script import MyLogic

mcp = FastMCP(name="my-tool")

@mcp.tool()
def my_operation(param: str) -> dict:
    """Tool description for Claude."""
    logic = MyLogic()
    return logic.operation(param)

if __name__ == "__main__":
    mcp.run()  # stdio transport by default
```

---

## Research Documents

### Core Best Practices

#### 1. Python Executable Naming

**Files:**
- `research-python-executable-naming.md` - Full research with citations
- `summary-python-executable-recommendations.md` - Quick actionable summary

**Key Findings:**
- Use `python` not `python3` in SKILL.md examples
- Shebang should still use `#!/usr/bin/env python3`
- Windows compatibility is the driving factor
- Anthropic's official skills use `python`

**Authority Sources:**
- PEP 394 (Official Python standard)
- Anthropic skills repository (webapp-testing)
- Python Windows documentation
- Claude Code documentation

**Status:** Research complete, ready for implementation

---

#### 2. Script Invocation Patterns

**File:** `research-skill-script-invocation-patterns.md`

**Key Findings:**
- Working directory is skill base (where SKILL.md lives)
- Use relative paths with forward slashes
- stdin/stdout for data exchange is best practice
- Skills must work across marketplace, manual, and ZIP installation

**Authority Sources:**
- Claude Code official documentation
- Anthropic skills repository examples
- Cross-platform bash best practices

**Status:** Research complete, patterns validated

---

#### 3. Cross-Platform Path Handling

**Files:**
- `research-cross-platform-paths.md` - Best practices for file paths
- `summary-path-best-practices.md` - Quick reference

**Key Findings:**
- Use `pathlib.Path` for all file operations
- Always use forward slashes in path literals
- Use `Path.home()` for user directory
- Handle OneDrive on Windows (special case)

**Authority Sources:**
- Python pathlib documentation
- Cross-platform development guides
- Windows OneDrive behavior analysis

**Status:** Research complete, implemented in notes_manager.py

---

### Implementation Analysis

#### 4. Notes Manager Issues Analysis

**File:** `analysis-notes-manager-issues.md`

**Key Findings:**
- Entry matching requires heading prioritization
- Relevance scoring prevents wrong updates
- File headers must be filtered from search
- Timestamps essential for context

**Status:** Analysis complete, fixes implemented

---

#### 5. Code Review (Security & Data Integrity)

**File:** `code-review-2025-11-17.md`

**Key Findings:**
- Path traversal risk in migration (personal use acceptable)
- Command injection mitigated by stdin usage
- No atomic writes (backup recommended)
- No file locking (single session recommended)

**Status:** Reviewed - Future improvements tracked, acceptable for personal use

---

### Architecture Decisions

#### 6. Hooks vs Utility Scripts

**File:** `research-hooks-vs-utility-scripts.md`

**Key Findings:**
- notes_manager.py is utility script (not a hook)
- Hooks integrate with Claude Code workflow
- Utility scripts are general-purpose tools
- Different use cases, different patterns

**Status:** Distinction clarified

---

#### 7. Tiered Trigger Systems

**File:** `research-tiered-trigger-systems.md`

**Key Findings:**
- Three-tier trigger system for natural language
- Must-trigger phrases in description
- Secondary triggers in body
- Prevents false positives

**Status:** Research complete, implemented in SKILL.md

---

### Issue Investigation

#### 8. Skill Path Resolution Fix

**Files:**
- `path-resolution-issue-analysis.md` - Problem analysis
- `action-required-path-fix.md` - Action plan
- `summary-skill-path-resolution-fix.md` - Implementation summary
- `summary-skill-path-best-practices.md` - Best practices

**Key Findings:**
- `${CLAUDE_SKILL_ROOT}` doesn't exist
- Use relative paths instead
- Skills execute from base directory
- Simple paths more portable

**Status:** Fixed in commit 4b84168

---

### Environment & Execution

#### 9. Skill Execution Environment

**File:** `research-skill-execution-environment.md`

**Key Findings:**
- Skills run in user's local environment (not containerized)
- Uses user's Python installation
- Environment variables available
- No special Claude-provided variables

**Status:** Research complete

---

#### 10. MCP Server Implementation

**File:** `research-mcp-server-implementation.md`

**Key Findings:**
- MCP servers bridge Claude Desktop to local machine resources
- Use FastMCP for rapid development with minimal boilerplate
- Stdio transport is most secure for local execution (no authentication needed)
- Tools expose actions, resources expose data, prompts guide users
- Dual-mode pattern enables skills to work in both Claude Code and Claude Desktop

**Recommendations:**
- Expose Python scripts as MCP tools (one tool per operation)
- Use environment variables for detection (MCP_SERVER_MODE)
- Configure via claude_desktop_config.json for automatic server launching
- Follow error handling best practices (stdout for JSON-RPC, stderr for logs)

**Authority Sources:**
- Official MCP specification (modelcontextprotocol.io)
- Anthropic MCP documentation and blog posts
- FastMCP documentation and examples
- Real-world MCP server implementations

**Status:** Research complete - Ready for implementation

---

## Research Methodology

### Sources by Authority Level

**HIGHEST (Official Standards):**
- Python Enhancement Proposals (PEPs)
- Official Python documentation
- POSIX/ISO standards

**HIGH (Official Anthropic):**
- Anthropic skills repository
- Claude Code documentation
- Claude API documentation

**MEDIUM-HIGH (Industry Standards):**
- Well-established cross-platform guides
- Security best practices (OWASP, etc.)
- Multiple corroborating sources

**MEDIUM (Community Consensus):**
- Stack Overflow discussions
- Third-party tutorials (when validated)
- Common patterns in open source

**LOW (Anecdotal):**
- Single blog posts
- Unverified claims
- Personal experience without validation

### Research Process

1. **Question Identification:** Specific, answerable question
2. **Official Source Check:** Anthropic docs first
3. **Standard Check:** Relevant PEPs, RFCs, ISO standards
4. **Community Validation:** Cross-reference multiple sources
5. **Testing:** Validate findings on multiple platforms
6. **Documentation:** Record sources, authority level, findings
7. **Recommendation:** Actionable guidance with confidence level

---

## Best Practices Summary

### For SKILL.md Authors

1. Use `python` not `python3` in examples
2. Use forward slashes for all paths
3. Use relative paths from skill root
4. Pass data via stdin (JSON recommended)
5. Document Python version requirements
6. Include clear trigger phrases in description
7. Test on Windows, macOS, Linux

### For Python Script Authors

1. Use `#!/usr/bin/env python3` shebang
2. Use `pathlib.Path` for all file operations
3. Read input from stdin, write to stdout
4. Use JSON for structured data
5. Handle errors gracefully with JSON responses
6. Validate user inputs (paths, commands)
7. Support Python 3.7+ (no modern-only syntax)
8. Use forward slashes in path literals

### For Cross-Platform Compatibility

1. Test on Windows (most restrictive)
2. Test with Git Bash and PowerShell
3. Test with system Python and venv
4. Handle OneDrive paths on Windows
5. Use `Path.home()` not hardcoded paths
6. Document platform-specific requirements
7. Provide clear error messages for missing deps

---

## Contributing to Research

### Adding New Research

1. **Create file:** `.github/research/research-<topic>.md`
2. **Follow template:** Include Executive Summary, Sources, Findings, Recommendations
3. **Cite sources:** Include URLs and authority levels
4. **Update index:** Add to this file
5. **Cross-reference:** Link related research

### Research Template

```markdown
# Research: <Topic>

**Date:** YYYY-MM-DD
**Focus:** Specific question or problem
**Authority:** Primary sources used

## Executive Summary
[TL;DR of findings and recommendations]

## 1. Problem Statement
[What we're investigating]

## 2. Sources
[List of authoritative sources with links]

## 3. Findings
[What we learned with evidence]

## 4. Recommendations
[Actionable guidance]

## 5. References
[Full citations]
```

---

## License

Research documents are part of the productivity-skills project.
See repository LICENSE for details.

---

**Remember:** Good research saves debugging time. Document findings, cite sources, test assumptions.
