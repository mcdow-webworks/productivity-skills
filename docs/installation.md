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

**File System Permissions:** Claude Desktop requires file system permissions to access your Documents folder for reading and writing notes. You'll need to configure these permissions in your Claude Desktop settings. See [Getting Started with Local MCP Servers](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop) for detailed instructions on granting file access.

**Note:** No additional setup required! The skill automatically creates the notes directory (`~/Documents/notes` or `~/OneDrive/Documents/notes` on Windows with OneDrive) when you add your first note.

### Custom Notes Location (Optional)

To use a custom location, set the `NOTES_DIR` environment variable:

```bash
# macOS/Linux
export NOTES_DIR="$HOME/my-custom-notes"

# Windows (System Environment Variables)
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
