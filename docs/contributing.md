# Contributing to Productivity Skills

Thank you for your interest in contributing! This guide will help you add new skills or improve existing ones.

## 🎯 What Can You Contribute?

### New Skills
- Task management
- Time tracking
- Meeting notes
- Daily journaling
- Project documentation
- Reference management
- Habit tracking

### Improvements
- Bug fixes
- Documentation
- Examples
- Performance optimizations
- Platform compatibility

### Community
- Use cases and workflows
- Templates
- Integration guides

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR-USERNAME/productivity-skills.git
cd productivity-skills
git remote add upstream https://github.com/mcdow-webworks/productivity-skills.git
```

### 2. Create a Branch

```bash
git checkout -b feature/my-new-skill
# or
git checkout -b fix/bug-description
```

### 3. Make Your Changes

See sections below for guidelines.

### 4. Test Thoroughly

- Test on both Claude Code and Claude Desktop
- Test on multiple platforms (macOS, Linux, Windows)
- Ensure backward compatibility

### 5. Submit Pull Request

- Write clear commit messages
- Reference related issues
- Include examples and documentation

## 📝 Creating a New Skill

### Directory Structure

```
productivity-skills/
└── your-skill-name/
    ├── SKILL.md              # Main documentation (required)
    ├── README.md             # User-facing guide (optional)
    ├── hooks/                # Utility scripts (optional)
    │   └── your_script.py
    ├── templates/            # File templates (optional)
    │   └── template.md
    └── examples/             # Usage examples (optional)
        └── example.md
```

### SKILL.md Format

Your `SKILL.md` is what Claude reads to understand your skill. Follow this structure:

```markdown
# Skill Name - Brief Description

One-paragraph overview of what this skill does.

## Quick Start

Minimal steps to get started (2-5 minutes max).

## Core Capabilities

### 1. Primary Feature
Description and examples

### 2. Secondary Feature
Description and examples

## How It Works

Behind-the-scenes explanation.

## Best Practices

Tips for effective use.

## Configuration Options

Optional customizations.

## Troubleshooting

Common issues and solutions.
```

**Key principles for SKILL.md:**

1. **Clear and concise** - Claude reads this, so be direct
2. **Example-driven** - Show don't tell
3. **Conversational triggers** - Explain what phrases activate features
4. **Error handling** - Document edge cases
5. **Integration patterns** - How it works with other skills

### Example SKILL.md Snippet

```markdown
# Task Management - AI-Assisted Todo Tracking

Track tasks conversationally with automatic prioritization and context awareness.

## Quick Start

1. Create tasks directory:
   ```bash
   mkdir -p ~/tasks
   ```

2. Start using:
   ```
   "Add task: Review pull requests"
   ```

## Core Capabilities

### 1. Adding Tasks

**Trigger phrases:**
- "Add task..."
- "Todo: ..."
- "Remember to..."

**Example:**
```
You: "Add task: Review the API documentation by Friday"
Claude: Added high-priority task with deadline Nov 22.
```

### 2. Listing Tasks

**Trigger phrases:**
- "What's on my todo list?"
- "Show my tasks"
- "What should I work on?"

**Example:**
```
You: "What should I work on today?"
Claude: You have 3 high-priority tasks:
        1. Review API docs (due Friday)
        2. Fix caching bug (no deadline)
        3. Customer demo prep (due tomorrow)
```
```

### Supporting Scripts

If your skill needs Python/Bash scripts:

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.
Part of productivity-skills/your-skill-name
"""

import json
import sys
from pathlib import Path

# Configuration
SKILL_DIR = Path.home() / ".your-skill"

def main():
    """Main entry point"""
    # Read input from stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}
    
    # Process command
    command = data.get('command', 'help')
    
    # Execute and return JSON
    result = {'status': 'success'}
    print(json.dumps(result, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

**Script guidelines:**
- Use Python 3.7+ (widely available)
- Accept JSON via stdin
- Output JSON to stdout
- Use stderr for errors
- Include helpful error messages
- Make scripts executable (`chmod +x`)

## 📚 Documentation Standards

### README.md

User-facing documentation should:
- Start with clear value proposition
- Include quick start (< 5 minutes)
- Provide usage examples
- Show common workflows
- Link to related resources

### Comments and Docstrings

```python
def search_tasks(query: str, max_results: int = 10) -> List[Dict]:
    """
    Search for tasks matching query.
    
    Args:
        query: Search terms
        max_results: Maximum number of results to return
    
    Returns:
        List of matching tasks with relevance scores
        
    Example:
        >>> search_tasks("review api")
        [{"title": "Review API docs", "priority": "high"}]
    """
    pass
```

### Inline Documentation

```markdown
## Advanced Configuration

You can customize the task directory:

```bash
# Add to ~/.bashrc
export TASKS_DIR="$HOME/Documents/tasks"
```

This is useful when:
- You want tasks in a synced folder
- Multiple users share a system
- You're organizing by project
```
```

## 🧪 Testing Your Skill

### Manual Testing Checklist

- [ ] Basic functionality works
- [ ] Edge cases handled gracefully
- [ ] Error messages are helpful
- [ ] Works on Claude Code
- [ ] Works on Claude Desktop
- [ ] Works on macOS
- [ ] Works on Linux
- [ ] Works on Windows/WSL
- [ ] Scripts are executable
- [ ] Paths are configurable
- [ ] Documentation is clear

### Test Commands

```bash
# Test Python script directly
echo '{"command":"test"}' | python3 your-skill/hooks/script.py

# Test in Claude
cd ~/productivity-skills
claude
# Then: "Test your skill by..."
```

### Example Testing Session

```
You: "Add task: Test the new skill"
Claude: Added task successfully!

You: "Show my tasks"
Claude: 1. Test the new skill (added just now)

You: "Complete the test task"
Claude: Marked as complete!

You: "Show completed tasks"
Claude: 1. Test the new skill (completed 2025-11-17)
```

## 🎨 Code Style

### Python

Follow PEP 8 with these specifics:
- 4 spaces for indentation
- Max line length: 100 characters
- Type hints where helpful
- Docstrings for public functions

```python
def add_task(title: str, priority: str = "medium") -> Dict:
    """Add a new task with optional priority."""
    pass
```

### Markdown

- Use ATX-style headers (`#`)
- Code blocks with language specifiers
- Lists with consistent style
- One sentence per line (for diffs)

### JSON

```json
{
  "key": "value",
  "nested": {
    "property": "formatted"
  }
}
```

2-space indentation, trailing commas allowed.

## 📋 Pull Request Guidelines

### PR Title Format

```
[Type] Brief description

Types:
- feat: New skill or feature
- fix: Bug fix
- docs: Documentation only
- refactor: Code restructuring
- test: Testing improvements
- chore: Maintenance tasks
```

Examples:
- `feat: Add task management skill`
- `fix: Handle empty notes directory gracefully`
- `docs: Improve installation guide for Windows`

### PR Description Template

```markdown
## Description
Brief overview of changes.

## Type of Change
- [ ] New skill
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Tested on Claude Code
- [ ] Tested on Claude Desktop
- [ ] Tested on macOS/Linux/Windows

## Screenshots (if applicable)
Add screenshots or example output.

## Related Issues
Fixes #123
Related to #456

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Examples included
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** run on PR
2. **Maintainer review** (1-2 days typically)
3. **Address feedback** if needed
4. **Merge** when approved

## 🐛 Reporting Bugs

### Before Opening an Issue

1. Check existing issues
2. Try latest version
3. Verify it's not a configuration issue

### Issue Template

```markdown
**Skill**: note-taking / task-management / etc.

**Platform**:
- OS: macOS 14.0 / Ubuntu 22.04 / Windows 11
- Claude: Code 2.1 / Desktop 1.5
- Python: 3.9.0

**Description**:
Clear description of the bug.

**Steps to Reproduce**:
1. Do this
2. Then that
3. See error

**Expected Behavior**:
What should happen.

**Actual Behavior**:
What actually happens.

**Logs/Screenshots**:
Include relevant output or screenshots.

**Configuration**:
```json
{
  "relevant": "config"
}
```
```

## 💡 Suggesting Features

We love feature suggestions! Open an issue with:

**Title**: `[Feature Request] Brief description`

**Content**:
- **Problem**: What problem does this solve?
- **Solution**: Proposed implementation
- **Alternatives**: Other approaches considered
- **Examples**: Usage examples

## 🌟 Recognition

Contributors get:
- Credit in CONTRIBUTORS.md
- Mention in release notes
- Our eternal gratitude! 🙏

## 📬 Questions?

- **General questions**: [Discussions](https://github.com/mcdow-webworks/productivity-skills/discussions)
- **Bug reports**: [Issues](https://github.com/mcdow-webworks/productivity-skills/issues)
- **Feature requests**: [Issues](https://github.com/mcdow-webworks/productivity-skills/issues)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making Productivity Skills better!** 🚀
