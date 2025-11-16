# Development Guide

Complete guide for developing and modifying Productivity Skills for Claude Code and Claude Desktop.

## Quick Reference

### Modifying Skills for Claude Desktop

```bash
# 1. Edit skill files
# 2. Regenerate ZIP
python scripts/create-skill-zip.py

# 3. Re-upload: Settings > Capabilities > Click skill name > Replace
```

### Modifying Skills for Claude Code

```bash
# 1. Edit skill files
# 2. Commit and push to GitHub
# 3. Update in Claude Code:
/plugin marketplace remove productivity-skills
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

---

## Development Setup

### Prerequisites

- **Python 3.7+** (for ZIP creation script)
- **Git** (for version control)
- **Claude Code** or **Claude Desktop** installed
- **Text editor** (VS Code, vim, nano, etc.)

### Clone for Development

```bash
# Clone the repository
git clone https://github.com/mcdow-webworks/productivity-skills.git
cd productivity-skills

# Create a development branch
git checkout -b feature/your-feature-name
```

### Directory Structure

```
productivity-skills/
├── plugins/
│   └── productivity-suite/
│       └── skills/
│           └── note-taking/
│               ├── SKILL.md              # Skill definition
│               ├── hooks/
│               │   └── notes_manager.py  # Python utilities
│               └── templates/
│                   └── monthly-template.md
├── scripts/
│   └── create-skill-zip.py              # ZIP creation utility
└── docs/
    └── development.md                    # This file
```

---

## Claude Desktop Development Workflow

Claude Desktop uses **ZIP file upload** for custom skills. Here's the complete workflow:

### 1. Edit Skill Files

Make your changes to any of these files:

```bash
# Edit the skill definition
nano plugins/productivity-suite/skills/note-taking/SKILL.md

# Edit Python utilities
nano plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py

# Edit templates
nano plugins/productivity-suite/skills/note-taking/templates/monthly-template.md
```

**Important:** SKILL.md must have valid YAML frontmatter:

```yaml
---
name: note-taking
description: Brief description of what the skill does
---
```

Claude Desktop only supports `name` and `description` fields. Do not add other fields.

### 2. Regenerate ZIP File

```bash
# From project root
python scripts/create-skill-zip.py
```

This creates `note-taking-skill.zip` with:
- SKILL.md at root
- hooks/ directory with all scripts
- templates/ directory with all templates
- Proper forward-slash (/) path separators (required by ZIP spec)

**Verify the ZIP:**

```bash
# On Windows (Git Bash)
unzip -l note-taking-skill.zip

# On macOS/Linux
unzip -l note-taking-skill.zip
```

### 3. Replace Skill in Claude Desktop

**Via Web (claude.ai):**

1. Go to [claude.ai/settings/capabilities](https://claude.ai/settings/capabilities)
2. Find your uploaded skill in the list
3. Click the skill name
4. Click **"Replace"** button
5. Select the new `note-taking-skill.zip` file
6. Claude validates and updates the skill

**Via Desktop App:**

1. Open Claude Desktop
2. Go to **Settings** (⚙️ icon)
3. Click **Capabilities** tab
4. Find your skill in the list
5. Click the skill name
6. Click **"Replace"** button
7. Select the new `note-taking-skill.zip` file
8. Restart Claude Desktop for changes to take effect

### 4. Test the Updated Skill

Open a new conversation and test:

```
"Note that I'm testing the updated skill"
```

If the skill doesn't respond correctly:
- Check the YAML frontmatter syntax
- Verify ZIP contents with `unzip -l`
- Check for errors in Settings > Capabilities
- Try removing and re-uploading (instead of replacing)

---

## Claude Code Development Workflow

### 1. Edit Skill Files

```bash
# Edit files in your local repository
nano plugins/productivity-suite/skills/note-taking/SKILL.md
nano plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py
```

### 2. Commit and Push

```bash
git add -A
git commit -m "Description of changes"
git push origin main
```

### 3. Update Plugin

```bash
/plugin marketplace remove productivity-skills
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

Restart Claude Code to load the updated plugin.

### 4. Test Changes

```
"Note that I'm testing my changes"
```

---

## Testing Changes

### Local Testing

Before committing changes, test thoroughly:

**1. Test Basic Functionality**

```
"Note that I'm testing basic note capture"
"What did I note about testing?"
"Update the testing note with additional details"
```

**2. Test Edge Cases**

```
"Note with special characters: @#$%"
"Note with code: \`console.log('test')\`"
"Very long note content..." (test truncation)
```

**3. Test Python Scripts Directly**

```bash
# Test notes_manager.py directly
cd plugins/productivity-suite/skills/note-taking/hooks

# Add a note
echo '{"command":"add","heading":"Test","content":"Testing direct script"}' | python notes_manager.py

# Search notes
echo '{"command":"search","query":"testing"}' | python notes_manager.py

# Get stats
echo '{"command":"stats"}' | python notes_manager.py

# Get info (shows configuration)
echo '{"command":"info"}' | python notes_manager.py
```

**4. Test Cross-Platform**

If possible, test on:
- Windows (Git Bash or WSL)
- macOS
- Linux

Pay attention to:
- Path separators (/ vs \\)
- Line endings (LF vs CRLF)
- Home directory expansion (~)
- Environment variables

### Debugging

**Check Python Script Output:**

```bash
# Run with verbose error output
python -u plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py <<< '{"command":"info"}'
```

**Check Skill Loading:**

```
# Ask Claude directly
"What skills do you have access to?"
"Show me details about the note-taking skill"
```

**Check Notes Directory:**

```bash
# Verify structure
ls -la ~/Documents/notes/
ls -la ~/Documents/notes/$(date +%Y)/

# Check recent files
ls -lt ~/Documents/notes/$(date +%Y)/ | head

# View index
cat ~/Documents/notes/.index.json | python -m json.tool
```

---

## Creating New Skills

### Skill Structure

Every skill needs at minimum:

```
skill-name/
├── SKILL.md           # Required: Skill definition with YAML frontmatter
├── hooks/             # Optional: Utility scripts
│   └── script.py
└── templates/         # Optional: Template files
    └── template.md
```

### SKILL.md Requirements

```yaml
---
name: skill-name
description: Brief description (1-2 sentences) of what the skill does
---

# Skill Name

Detailed instructions for Claude on how to use this skill.

## When to Use

Describe trigger phrases and use cases.

## Examples

Provide clear examples of user interactions.
```

### Adding to Plugin

1. Create skill directory:
   ```bash
   mkdir -p plugins/productivity-suite/skills/your-skill
   ```

2. Add SKILL.md with YAML frontmatter

3. Add supporting files (hooks, templates)

4. Update marketplace.json:
   ```json
   {
     "plugins": [{
       "skills": [
         "./skills/note-taking",
         "./skills/your-skill"
       ]
     }]
   }
   ```

5. Test locally

6. Create ZIP for Claude Desktop (if needed)

---

## ZIP Creation Script

### Usage

```bash
# Run from project root
python scripts/create-skill-zip.py
```

### Customization

To create ZIPs for other skills, modify the script or use the function:

```python
from pathlib import Path
from scripts.create_skill_zip import create_skill_zip

create_skill_zip(
    skill_dir='plugins/productivity-suite/skills/your-skill',
    output_zip='your-skill.zip'
)
```

### What Gets Included

- ✅ SKILL.md (required, at root)
- ✅ hooks/*.py (all Python scripts)
- ✅ templates/*.md (all templates)
- ❌ .gz files (excluded)
- ❌ __pycache__ directories (excluded)
- ❌ .pyc files (excluded)

### Path Requirements

The script ensures:
- Forward slashes (/) in all paths (ZIP spec requirement)
- No backslashes (\\) which Claude Desktop rejects
- Relative paths from ZIP root

---

## Version Management

### Updating Version Numbers

When releasing a new version, update:

1. **`.claude-plugin/marketplace.json`:**
   ```json
   {
     "version": "1.1.0",
     "plugins": [{
       "version": "1.1.0"
     }]
   }
   ```

2. **Document changes** in commit message or CHANGELOG

### Semantic Versioning

Follow [semver](https://semver.org/):

- **Major (1.0.0 → 2.0.0):** Breaking changes
- **Minor (1.0.0 → 1.1.0):** New features, backwards compatible
- **Patch (1.0.0 → 1.0.1):** Bug fixes

---

## Publishing Changes

### Marketplace Plugin Updates

Users can update via:

```bash
# Check for updates
/plugin update productivity-suite

# Or reinstall
/plugin install productivity-suite@productivity-skills
```

### Git Workflow

```bash
# Commit changes
git add .
git commit -m "Add new feature: ..."
git push origin feature/your-feature

# Create pull request on GitHub
gh pr create --base main --head feature/your-feature
```

### Release Process

1. Update version numbers
2. Test on both Claude Code and Claude Desktop
3. Update documentation
4. Commit changes
5. Create GitHub release with ZIP file attached
6. Update marketplace listing (if applicable)

---

## Common Development Tasks

### Add a New Note Template

```bash
# Create template
nano plugins/productivity-suite/skills/note-taking/templates/weekly-template.md

# Document in SKILL.md
nano plugins/productivity-suite/skills/note-taking/SKILL.md

# Regenerate ZIP for Claude Desktop
python scripts/create-skill-zip.py
```

### Modify Search Algorithm

```bash
# Edit notes_manager.py
nano plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py

# Test directly
echo '{"command":"search","query":"test"}' | python plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py

# Regenerate ZIP
python scripts/create-skill-zip.py
```

### Add New Python Dependency

If adding a Python package dependency:

1. Document in README or requirements.txt
2. Ensure it's Python 3.7+ compatible
3. Consider: Does the user need to install this?
4. Update installation docs if needed

**Note:** Avoid dependencies when possible. Skills should be self-contained.

---

## Troubleshooting Development

### "YAML frontmatter malformed"

**Cause:** Invalid YAML syntax or unsupported fields

**Fix:** Ensure only `name` and `description` fields:

```yaml
---
name: note-taking
description: Your description here
---
```

### "Zip file contains path with invalid characters"

**Cause:** Backslashes (\\) in ZIP paths

**Fix:** Use `scripts/create-skill-zip.py` which ensures forward slashes

### "Skill not loading in Claude Code"

**Causes:**
1. Plugin not copied to correct directory
2. YAML syntax error
3. Claude Code not restarted

**Fix:**

```bash
# Verify plugin directory
ls -la "$APPDATA/Claude/plugins/productivity-suite/skills/"

# Check YAML
head -10 plugins/productivity-suite/skills/note-taking/SKILL.md

# Restart Claude Code
exit
claude
```

### "Python script errors"

**Causes:**
1. Python version < 3.7
2. Script not executable
3. Missing dependencies
4. Path issues

**Fix:**

```bash
# Check Python version
python --version

# Make executable (macOS/Linux)
chmod +x plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py

# Test directly
python plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py <<< '{"command":"info"}'
```

---

## Best Practices

### Code Quality

- ✅ Use Python 3.7+ compatible syntax
- ✅ Handle errors gracefully
- ✅ Validate input JSON
- ✅ Use pathlib for cross-platform paths
- ✅ Write clear documentation strings
- ✅ Test on multiple platforms

### Documentation

- ✅ Update SKILL.md with new features
- ✅ Provide clear examples
- ✅ Document edge cases
- ✅ Keep README.md in sync
- ✅ Update version numbers

### Testing

- ✅ Test both Claude Code and Claude Desktop
- ✅ Test on Windows, macOS, Linux (if possible)
- ✅ Test edge cases and error conditions
- ✅ Verify ZIP contents before distribution
- ✅ Test with fresh installation

### Git Commits

- ✅ Use clear, descriptive commit messages
- ✅ One logical change per commit
- ✅ Test before committing
- ✅ Update docs in same commit as code changes

---

## Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Claude Skills Guide](https://docs.claude.com/en/docs/skills)
- [Plugin Marketplace Spec](https://anthropic.com/claude-code/marketplace.schema.json)
- [Contributing Guide](contributing.md)
- [Installation Guide](installation.md)

---

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/mcdow-webworks/productivity-skills/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mcdow-webworks/productivity-skills/discussions)
- **FAQ:** [docs/faq.md](faq.md)

---

**Happy developing! 🚀**
