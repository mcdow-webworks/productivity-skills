# Installation Guide

Complete installation instructions for Productivity Skills on Claude Code and Claude Desktop.

## Quick Install (Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/productivity-skills.git ~/productivity-skills
```

### 2. Configure Claude

Choose your platform:

#### Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "projectDefaults": {
    "skillDirectories": ["~/productivity-skills"]
  }
}
```

#### Claude Desktop

1. Open Claude Desktop
2. Go to **Settings** (or **Preferences** on macOS)
3. Navigate to **Advanced** tab
4. Add skill directory:

```json
{
  "skillDirectories": ["~/productivity-skills"]
}
```

Or edit the config file directly:
- **macOS**: `~/Library/Application Support/Claude/settings.json`
- **Windows**: `%APPDATA%\Claude\settings.json`
- **Linux**: `~/.config/Claude/settings.json`

### 3. Set Up Individual Skills

#### Note-Taking

```bash
# Create notes directory
mkdir -p ~/notes/$(date +%Y)

# Optional: Custom location
export NOTES_DIR="$HOME/Documents/notes"
mkdir -p "$NOTES_DIR/$(date +%Y)"
```

### 4. Verify Installation

Open a new Claude session:

```bash
# For Claude Code
claude

# For Claude Desktop
# Open a new conversation
```

Test it:
```
"Note that productivity skills are now installed"
```

If Claude responds by adding the note, you're all set! 🎉

## Detailed Installation

### Prerequisites

Before installing, ensure you have:

- ✅ **Claude Code 2.0+** or **Claude Desktop**
- ✅ **Bash** shell (macOS/Linux/WSL)
- ✅ **Python 3.7+** (for utility scripts)
- ✅ **Git** (for cloning the repository)

Check your versions:

```bash
# Check Python
python3 --version

# Check Git  
git --version

# Check Bash
bash --version
```

### Step-by-Step Setup

#### 1. Choose Installation Location

**Default** (recommended):
```bash
cd ~
git clone https://github.com/YOUR-USERNAME/productivity-skills.git productivity-skills
```

**Custom location**:
```bash
cd /path/to/your/location
git clone https://github.com/YOUR-USERNAME/productivity-skills.git productivity-skills
```

If using a custom location, update paths in configuration accordingly.

#### 2. Configure Claude Settings

##### Claude Code

Create or edit `~/.claude/settings.json`:

```bash
# Create if doesn't exist
touch ~/.claude/settings.json

# Edit with your preferred editor
nano ~/.claude/settings.json
```

Add configuration:

```json
{
  "projectDefaults": {
    "skillDirectories": [
      "~/productivity-skills"
    ],
    "memoryEnabled": true
  }
}
```

**Full configuration** with optional features:

```json
{
  "projectDefaults": {
    "skillDirectories": [
      "~/productivity-skills"
    ],
    "memoryEnabled": true
  },
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "If this session accomplished anything notable, suggest in one sentence what could be noted. If nothing notable, output nothing."
          }
        ]
      }
    ]
  }
}
```

##### Claude Desktop

**Option A: Through UI**

1. Open Claude Desktop
2. Click **Settings** (⚙️ icon)
3. Go to **Advanced** tab
4. Under "Custom Settings", add:
   ```json
   {
     "skillDirectories": ["~/productivity-skills"]
   }
   ```
5. Click **Save**
6. Restart Claude Desktop

**Option B: Edit Config File**

Find your config file:

```bash
# macOS
nano ~/Library/Application\ Support/Claude/settings.json

# Linux
nano ~/.config/Claude/settings.json

# Windows (Git Bash)
notepad "$APPDATA/Claude/settings.json"
```

Add:

```json
{
  "skillDirectories": [
    "~/productivity-skills"
  ]
}
```

Save and restart Claude Desktop.

#### 3. Set Up Individual Skills

##### Note-Taking Setup

Create your notes directory:

```bash
# Default location
mkdir -p ~/notes/$(date +%Y)

# Add to shell config for custom location (optional)
echo 'export NOTES_DIR="$HOME/Documents/notes"' >> ~/.bashrc
source ~/.bashrc
mkdir -p "$NOTES_DIR/$(date +%Y)"
```

Create initial structure:

```bash
cd ~/notes
cat > 2025/$(date +%m-%B).md << 'EOF'
# Notes - $(date +%B %Y)

<!-- Your notes will appear below -->

EOF
```

Make utility script executable:

```bash
chmod +x ~/productivity-skills/note-taking/hooks/notes_manager.py
```

#### 4. Verify Installation

##### Check Directory Structure

```bash
# Verify skills installed
ls -la ~/productivity-skills/

# Should see:
# SKILL.md
# README.md
# note-taking/
# docs/
# examples/
```

##### Check Configuration

```bash
# Claude Code
cat ~/.claude/settings.json | grep -A2 skillDirectories

# Claude Desktop (macOS)
cat ~/Library/Application\ Support/Claude/settings.json | grep -A2 skillDirectories
```

##### Test Skills

Open Claude and try:

```
"Reindex my notes and tell me what you found"
```

Expected response:
```
I've indexed your notes. Found:
- 0 files (you just set up, nothing added yet)
- 0 entries
Ready to start capturing knowledge!
```

Then test adding a note:

```
"Note that productivity skills installation is complete"
```

Claude should confirm the note was added.

## Platform-Specific Notes

### macOS

Everything should work out of the box. If you get permission errors:

```bash
# Make scripts executable
chmod +x ~/productivity-skills/note-taking/hooks/*.py
```

### Linux

Same as macOS. Ensure Python 3 is installed:

```bash
# Ubuntu/Debian
sudo apt-get install python3

# Fedora
sudo dnf install python3
```

### Windows (WSL2)

Recommended approach: Use WSL2 with Ubuntu.

1. **Install WSL2** (if not already):
   ```powershell
   wsl --install
   ```

2. **Inside WSL**, follow Linux instructions:
   ```bash
   cd ~
   git clone https://github.com/YOUR-USERNAME/productivity-skills.git productivity-skills
   ```

3. **Configure paths** in `~/.claude/settings.json` (inside WSL):
   ```json
   {
     "projectDefaults": {
       "skillDirectories": [
         "~/productivity-skills"
       ]
     }
   }
   ```

**Note**: If using Claude Code in Windows (not WSL), use Windows paths:
```json
{
  "projectDefaults": {
    "skillDirectories": [
      "C:\\Users\\YourUsername\\productivity-skills"
    ]
  }
}
```

### Windows (Native)

1. **Clone with Git Bash**:
   ```bash
   cd ~
   git clone https://github.com/YOUR-USERNAME/productivity-skills.git productivity-skills
   ```

2. **Configure** `%USERPROFILE%\.claude\settings.json`:
   ```json
   {
     "projectDefaults": {
       "skillDirectories": [
         "C:\\Users\\YourUsername\\productivity-skills"
       ]
     }
   }
   ```

3. **Ensure Python** in PATH:
   ```bash
   python --version
   ```

## Configuration Options

### Custom Notes Directory

To use a different location for notes:

**Environment variable** (recommended):
```bash
# Add to ~/.bashrc or ~/.zshrc
export NOTES_DIR="$HOME/Documents/notes"
```

**Or specify when asking**:
```
"Note in ~/Documents/work-notes that..."
```

### Multiple Skill Directories

You can load skills from multiple locations:

```json
{
  "projectDefaults": {
    "skillDirectories": [
      "~/productivity-skills",
      "~/custom-skills",
      "~/work/team-skills"
    ]
  }
}
```

### Project-Specific Override

Override skills per project in `.claude/settings.json`:

```json
{
  "skillDirectories": [
    "~/productivity-skills",
    "./.claude/skills"
  ]
}
```

## Updating Skills

To update to the latest version:

```bash
cd ~/productivity-skills
git pull origin main
```

Then restart Claude (Code or Desktop).

## Uninstalling

To remove productivity skills:

1. **Remove from configuration**:
   Edit `~/.claude/settings.json` and remove the skill directory.

2. **Delete repository** (optional):
   ```bash
   rm -rf ~/productivity-skills
   ```

3. **Keep your notes** (they're separate):
   Your notes in `~/notes/` are independent and remain intact.

## Troubleshooting

### Skills Not Loading

**Problem**: Claude doesn't recognize skills.

**Solutions**:

1. **Verify path** in settings:
   ```bash
   cat ~/.claude/settings.json
   ```

2. **Check directory exists**:
   ```bash
   ls -la ~/productivity-skills/
   ```

3. **Restart Claude completely**:
   - Claude Code: Exit terminal and restart
   - Claude Desktop: Quit app and reopen

4. **Check for typos** in JSON:
   ```bash
   cat ~/.claude/settings.json | python3 -m json.tool
   ```

### Python Script Errors

**Problem**: `notes_manager.py` not working.

**Solutions**:

1. **Make executable**:
   ```bash
   chmod +x ~/productivity-skills/note-taking/hooks/notes_manager.py
   ```

2. **Test directly**:
   ```bash
   python3 ~/productivity-skills/note-taking/hooks/notes_manager.py stats
   ```

3. **Check Python version**:
   ```bash
   python3 --version  # Should be 3.7+
   ```

### Notes Not Saving

**Problem**: Notes aren't being saved.

**Solutions**:

1. **Verify notes directory exists**:
   ```bash
   mkdir -p ~/notes/$(date +%Y)
   ```

2. **Check permissions**:
   ```bash
   ls -la ~/notes/
   touch ~/notes/test.txt  # Should work
   rm ~/notes/test.txt
   ```

3. **Try manual index rebuild**:
   ```
   In Claude: "Reindex all my notes"
   ```

### Windows Path Issues

**Problem**: Paths not working on Windows.

**Solution**: Use forward slashes or double backslashes:

```json
{
  "skillDirectories": [
    "C:/Users/YourName/productivity-skills"
  ]
}
```

Or:

```json
{
  "skillDirectories": [
    "C:\\Users\\YourName\\productivity-skills"
  ]
}
```

## Getting Help

Still having issues?

1. **Check FAQ**: [docs/faq.md](faq.md)
2. **Search issues**: [GitHub Issues](https://github.com/YOUR-USERNAME/productivity-skills/issues)
3. **Open new issue**: Include:
   - Your platform (OS, Claude version)
   - Configuration file content
   - Error messages
   - Steps to reproduce

## Next Steps

After installation:

1. ✅ Read [Note-Taking Guide](note-taking-guide.md)
2. ✅ Try [Example Workflows](../README.md#-example-workflows)
3. ✅ Explore [Examples](../examples/)
4. ✅ Join [Discussions](https://github.com/YOUR-USERNAME/productivity-skills/discussions)

---

**Questions?** Open an issue or discussion on GitHub!
