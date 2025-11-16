# Installation Guide

Simple installation for Productivity Skills on Claude Code and Claude Desktop.

## Install

### Claude Code

```bash
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

Restart Claude Code to load the plugin.

### Claude Desktop

1. Download `note-taking-skill.zip` from [releases](https://github.com/mcdow-webworks/productivity-skills/releases)
2. Go to [claude.ai/settings/capabilities](https://claude.ai/settings/capabilities)
3. Enable "Skills" toggle
4. Click "Upload skill" → Select ZIP file

## Setup

### Note-Taking Skill

Create your notes directory:

```bash
# Default location (works on all platforms)
mkdir -p ~/Documents/notes/$(date +%Y)

# Windows with OneDrive
mkdir -p ~/OneDrive/Documents/notes/$(date +%Y)
```

**Note:** The skill automatically detects OneDrive on Windows and uses `~/OneDrive/Documents/notes` if available.

### Custom Notes Location (Optional)

```bash
# Set environment variable
export NOTES_DIR="$HOME/my-custom-notes"

# Create directory
mkdir -p "$NOTES_DIR/$(date +%Y)"
```

On Windows, set via System Environment Variables:
```
NOTES_DIR=C:\Users\username\my-custom-notes
```

## Verify Installation

Open a Claude session and test:

```
"Note that productivity skills are now installed"
```

If Claude responds by adding the note, you're all set! 🎉

Check the note was created:

```bash
# View your notes directory
ls -la ~/Documents/notes/$(date +%Y)/

# Or on Windows with OneDrive
ls -la ~/OneDrive/Documents/notes/$(date +%Y)/
```

## Updating

### Claude Code

```bash
/plugin marketplace remove productivity-skills
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

Restart Claude Code after updating.

### Claude Desktop

1. Download latest ZIP from [releases](https://github.com/mcdow-webworks/productivity-skills/releases)
2. Go to Settings > Capabilities
3. Click your skill name → **Replace**
4. Select new ZIP file

## Troubleshooting

### "Skill not loading" (Claude Code)

```bash
# Verify plugin is installed
/plugin list

# If not shown, reinstall:
/plugin install productivity-suite@productivity-skills
```

Restart Claude Code after installation.

### "Can't find notes" (Both platforms)

Check notes directory exists:

```bash
# Check default location
ls ~/Documents/notes/

# Windows with OneDrive
ls ~/OneDrive/Documents/notes/

# Check what path the skill is using
echo '{"command":"info"}' | python ~/path/to/notes_manager.py
```

### "Notes going to wrong folder" (Windows OneDrive)

The skill automatically prefers OneDrive Documents if it exists. To use local Documents instead:

```bash
export NOTES_DIR="$HOME/Documents/notes"
```

### "ZIP upload fails" (Claude Desktop)

Common causes:
- ZIP created with wrong tool (use provided Python script)
- YAML frontmatter syntax error

Create ZIP correctly:

```bash
# Clone repo if needed
git clone https://github.com/mcdow-webworks/productivity-skills.git
cd productivity-skills

# Use the script
python scripts/create-skill-zip.py
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/mcdow-webworks/productivity-skills/issues)
- **Documentation**: [Full documentation](../README.md)
- **Development**: [Development Guide](development.md)

---

**That's it!** Simple installation, powerful productivity. 🚀
