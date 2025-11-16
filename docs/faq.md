# Frequently Asked Questions

## General Questions

### What are Productivity Skills?

Productivity Skills are AI-native extensions that teach Claude how to help you manage knowledge, tasks, time, and workflows. Instead of just answering questions, Claude becomes an active partner in your productivity system.

### How is this different from just prompting Claude?

**Regular prompting:**
- Claude forgets everything between sessions
- You repeat yourself constantly
- No persistent knowledge base
- Limited to what's in the conversation

**With Productivity Skills:**
- Knowledge persists across all sessions
- Claude actively manages your systems
- Searchable, queryable information
- Works from any Claude session (Code or Desktop)

### Do my notes/data leave my computer?

No! All your data stays local in markdown files on your machine. The skills just teach Claude how to interact with your local files. Your notes, tasks, and other data never leave your computer unless you explicitly share them.

### Can I use this with both Claude Code and Claude Desktop?

Yes! Once configured, skills work in both environments seamlessly.

## Installation & Setup

### Where should I install this?

The recommended location is `~/productivity-skills`, but you can install anywhere:

```bash
cd ~/Documents
git clone https://github.com/mcdow-webworks/productivity-skills.git
```

Just update your settings.json with the actual path.

### How do I know if skills are loaded?

Ask Claude:
```
"What skills do you have access to?"
```

Or try using a skill:
```
"Note that installation is working"
```

If Claude responds appropriately, skills are loaded!

### Do I need to restart Claude after installing?

**Claude Code**: Yes, restart your terminal session
**Claude Desktop**: Yes, quit and reopen the app

### Can I use this in a project subdirectory?

Yes! Skills configured globally work in any directory. You can also add project-specific skills by creating `.claude/skills/` in your project.

## Usage Questions

### How do I add a note?

Just talk naturally:
- "Note that..."
- "Remember that..."
- "Add a note about..."
- "Capture this..."

Claude understands variations and will create the note.

### Can I search old notes?

Yes! Ask Claude:
- "What did I note about X?"
- "Find my notes on Y"
- "Status of project Z?"

Claude searches across all your markdown files.

### How do I update an existing note?

Just ask:
- "Add to the X note that..."
- "Update the Y entry with..."
- "Append to Z..."

Claude finds the most relevant entry and updates it.

### Can I use this for work and personal notes separately?

Yes! Use different directories:

```bash
# Work notes
export NOTES_DIR="$HOME/work-notes"

# Personal notes  
export NOTES_DIR="$HOME/personal-notes"
```

Or organize with subdirectories in a single notes folder.

### What if I want to note something for a specific project?

From any directory, just ask:
```
"Note in project X that..."
```

Or navigate to the project directory first. Claude is context-aware.

## Technical Questions

### What file format are notes stored in?

Plain markdown (.md files). This means:
- Readable in any text editor
- Version controllable with git
- Portable forever
- No vendor lock-in

### Can I edit notes manually?

Absolutely! Your notes are just markdown files. Edit them however you want - vim, VS Code, Obsidian, etc. Claude will pick up changes.

### Will manual edits break anything?

No! As long as you keep the basic heading format (`# Category - Description`), everything works. The index rebuilds automatically.

### Can I version control my notes with Git?

Highly recommended! Your notes directory is perfect for git:

```bash
cd ~/Documents/notes
git init
git add .
git commit -m "Initial notes"
```

The `.index.json` file is gitignored by default (regenerated automatically).

### What if I have thousands of notes?

The search is designed to handle large collections. The index makes searches fast even with many files. If you notice slowdowns, open an issue!

### Can I migrate from Obsidian/Notion/etc?

Yes! If your existing notes are in markdown:

```bash
cp -r ~/path/to/old-notes/*.md ~/Documents/notes/2025/
```

Then ask Claude to reindex. If they're not in markdown, you'll need to export/convert first.

## Customization

### Can I change the notes directory location?

Yes! Set the environment variable:

```bash
# Add to ~/.bashrc or ~/.zshrc
export NOTES_DIR="$HOME/Documents/my-notes"
```

### Can I customize categories?

Categories are flexible - just use whatever makes sense:
```
"Note as Customer-Feedback: ..."
```

Claude learns your categories over time.

### Can I add custom templates?

Yes! Create templates in `~/productivity-skills/note-taking/templates/` and tell Claude about them.

### Can I use this with other note-taking apps?

If they use markdown and can watch file changes (like Obsidian), yes! Point both tools at the same directory.

## Troubleshooting

### "Command not found: claude"

This means Claude Code isn't installed or not in PATH. See [Claude Code installation](https://docs.claude.com/en/docs/claude-code).

### "Claude doesn't respond to note commands"

**Checklist:**
1. Are skills configured in settings.json?
2. Does the directory exist? `ls ~/productivity-skills/`
3. Did you restart Claude after configuration?
4. Try: `"What skills do you have access to?"`

### "Notes aren't saving"

**Check:**
1. Does notes directory exist? `mkdir -p ~/Documents/notes/$(date +%Y)`
2. Do you have write permissions? `touch ~/Documents/notes/test.txt`
3. Try reindexing: `"Reindex my notes"`

### "Search not finding my notes"

**Solutions:**
1. Rebuild index: `"Reindex all my notes"`
2. Check file format - should be `# Heading` style
3. Verify files are in `~/Documents/notes/YYYY/*.md`

### "Python errors"

**Check Python version:**
```bash
python3 --version  # Should be 3.7+
```

**Make script executable:**
```bash
chmod +x ~/productivity-skills/note-taking/hooks/notes_manager.py
```

### "Works in Claude Code but not Claude Desktop"

Make sure you configured settings for both. They use separate config files:
- Claude Code: `~/.claude/settings.json`
- Claude Desktop: OS-specific (see installation guide)

## Platform-Specific

### macOS: Permission denied errors

```bash
# Make scripts executable
chmod +x ~/productivity-skills/note-taking/hooks/*.py
```

### Windows: Path not working

Use forward slashes or double backslashes:
```json
{
  "skillDirectories": ["C:/Users/YourName/productivity-skills"]
}
```

### WSL: Can't find files

Make sure you're using Linux paths (`~`) inside WSL, not Windows paths (`C:\`).

## Advanced Usage

### Can I add hooks for automatic capture?

Yes! See [examples/claude-code-settings.json](../examples/claude-code-settings.json) for hook examples.

### Can I integrate with other tools?

Yes! Since notes are markdown, you can:
- Sync with Dropbox/iCloud
- Use with static site generators
- Process with custom scripts
- Import into other tools

### Can I search by date range?

Ask Claude:
```
"Show me notes from October"
"What did I work on last week?"
"Find entries from Q3"
```

### Can I export notes in different formats?

Ask Claude to convert:
```
"Export all my November notes as a single document"
"Create a PDF of my project notes"
```

### Can I share specific notes with team members?

Since they're markdown files:
```bash
# Share via git
cd ~/Documents/notes
git remote add origin https://github.com/you/notes.git
git push

# Or export specific files
cp ~/Documents/notes/2025/11-November.md ~/shared/
```

## Feature Requests

### Will there be mobile support?

We're exploring options. For now, you can access notes through any text editor on mobile that syncs with your desktop.

### Will there be a GUI?

The power is in the conversational interface with Claude. A GUI might come as a separate project, but the core will remain CLI/conversation-based.

### Can I build my own skill?

Yes! See [Contributing Guide](contributing.md) for how to create and share new skills.

### Will there be integration with [tool X]?

Maybe! Open a feature request issue. Better yet, build it yourself and contribute!

## Community

### How do I get help?

1. Check this FAQ
2. Read [Installation Guide](installation.md)
3. Search [existing issues](https://github.com/mcdow-webworks/productivity-skills/issues)
4. Open a [new issue](https://github.com/mcdow-webworks/productivity-skills/issues/new)
5. Ask in [Discussions](https://github.com/mcdow-webworks/productivity-skills/discussions)

### How can I contribute?

See [Contributing Guide](contributing.md)! We welcome:
- New skills
- Bug fixes
- Documentation improvements
- Usage examples
- Feature ideas

### Where can I share my setup?

Share in [Discussions](https://github.com/mcdow-webworks/productivity-skills/discussions) under "Show and Tell"!

### Is there a community chat?

Currently using GitHub Discussions. If there's enough interest, we might add Discord/Slack.

## Privacy & Security

### Who can see my notes?

Only you. Everything is local. We never collect or transmit your notes.

### Are skills tracking my usage?

No tracking. Skills are just instructions for Claude. No analytics, no telemetry.

### Can I audit the code?

Yes! Everything is open source. Review any file:
```bash
cat ~/productivity-skills/note-taking/hooks/notes_manager.py
```

### Should I add sensitive data to notes?

That's your choice. Notes are local markdown files with standard file permissions. Use the same judgment you would for any local files.

## Still Have Questions?

Open an issue or discussion on GitHub:
- [Issues](https://github.com/mcdow-webworks/productivity-skills/issues)
- [Discussions](https://github.com/mcdow-webworks/productivity-skills/discussions)

We're here to help!
