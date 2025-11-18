# Productivity Skills for Claude

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-purple)](https://claude.ai/code)
[![Claude Desktop](https://img.shields.io/badge/Claude-Desktop-purple)](https://claude.ai)

Transform Claude into your AI-powered productivity partner. A collection of skills that make Claude an active participant in your personal knowledge management, task tracking, and daily workflows.

## 🎯 What is This?

Instead of just asking Claude questions, these skills make Claude an **active partner** in managing your work:

- 📝 **Capture knowledge** conversationally across any project
- 🔍 **Search your notes** naturally with AI understanding  
- 🔗 **Surface connections** between ideas you've forgotten
- 📊 **Recognize patterns** in your work over time
- 💡 **Get insights** from your accumulated knowledge

All while keeping your data local in simple markdown files.

![Claude Desktop showing automatic note connections](docs/images/note-taking-demo.png)
*Claude automatically finds and connects related notes across sessions, showing the progression from idea to implementation*

## ✨ Quick Start (2 Minutes)

### Installation

**Claude Code:**

```bash
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

Restart Claude Code to load the plugin.

**Claude Desktop:**

1. Download [note-taking-skill.zip](https://github.com/mcdow-webworks/productivity-skills/raw/main/note-taking-skill.zip)
2. Go to [claude.ai/settings/capabilities](https://claude.ai/settings/capabilities)
3. Enable "Skills" toggle → Click "Upload skill" → Select the ZIP file

**Important:** Claude Desktop requires file system permissions to access your Documents folder. See [Getting Started with Local MCP Servers](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop) for details on configuring file read/write/create permissions.

### Start Using It!

**No setup required!** The skill automatically creates your notes directory when you add your first note:
- Default location: `~/Documents/notes/` (or `~/OneDrive/Documents/notes/` on Windows with OneDrive)
- Organized by year: `~/Documents/notes/2025/`
- Monthly files: `11-November.md`, `12-December.md`, etc.

Open any Claude session and say:

```
"Note that I just discovered a great caching solution for the deployment"
```

That's it! You're now building an AI-navigable second brain.

### Updating

**Claude Code:**
```bash
/plugin marketplace remove productivity-skills
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

**Claude Desktop:**
Download the latest [note-taking-skill.zip](https://github.com/mcdow-webworks/productivity-skills/raw/main/note-taking-skill.zip) and re-upload via Settings > Capabilities → Click skill name → Replace.

## 🚀 Available Skills

### 📝 Note-Taking (Available Now)

Transform markdown notes into an AI-navigable knowledge system. Claude becomes your interface for capturing, organizing, and retrieving information.

**Key Features:**
- Conversational note capture from any project
- Intelligent search across all your notes  
- Automatic updates to existing entries
- Pattern recognition and insight generation
- Maintains simple markdown format

[Full Note-Taking Documentation →](plugins/productivity-suite/skills/note-taking/SKILL.md)

**Example Usage:**
```
You: "Note that the German partner loved the llms.txt idea"
Claude: Added to November notes! I also found your earlier llms.txt
        entry from Nov 15.

You: "What's the status of llms.txt?"
Claude: You have 3 entries showing progression from concept to
        validated to implementation. Ready to move forward?
```

## 💡 Why Skills?

### Traditional Approach
```
You: "Can you remember that I prefer TypeScript?"
Claude: "I'll try to remember that..."
[Next session: Claude has forgotten]
```

### With Productivity Skills
```
You: "Note that our team prefers TypeScript for new projects"
Claude: Added to your November notes!

[Days later, different session]
You: "What language should I use for this new API?"
Claude: Based on your Nov 12 note, your team prefers TypeScript.
        Should I use that?
```

**Skills provide:**
- ✅ Persistent memory across sessions
- ✅ Searchable knowledge base
- ✅ Pattern recognition over time
- ✅ Cross-project availability
- ✅ Plain text portability

## 📖 Philosophy

These skills follow core principles:

1. **Plain text first** - All data in markdown, portable forever
2. **AI-navigable** - Claude as interface, not just storage
3. **Natural interaction** - Talk naturally, not commands
4. **Cross-project** - Available in every Claude session
5. **Local-first** - Your data stays on your machine
6. **Incremental adoption** - Start simple, grow organically

Inspired by:
- ["Your Second Brain = AI's Interface"](https://jkudish.com/newsletter/003) by Joey Kudish
- Building a Second Brain methodology
- Plain text productivity systems

## 🎮 Example Workflows

### Knowledge Worker

```bash
# Morning
cd ~/projects/api-service
claude

You: "What did I note about the authentication refactor?"
Claude: Shows 3 entries from last week with evolution of thinking

# During work
You: "Note that we decided to use JWT with refresh tokens"
Claude: Added! I also found your earlier auth discussion from last week.

# Evening  
You: "What should I remember from today?"
Claude: You made progress on auth, fixed caching bug, and had
        the partner demo. Worth noting any insights?
```

### Developer

```bash
cd ~/projects/web-app
claude

You: "I just solved that React rendering issue"
Claude: Great! Want me to note the solution so you remember
        this approach for future projects?

You: "Yes - it was the useEffect dependency array"
Claude: Added technical note with code example

[Weeks later, different project]
You: "I'm seeing weird React renders again"
Claude: I found your note from Nov 17 about useEffect dependencies.
        Is this the same issue?
```

### Product Manager

```bash
You: "Note that the Q4 roadmap was approved with 3 major features"
Claude: Added to November notes

You: "Connect this to our earlier product vision discussion"  
Claude: Linked! The approved features align well with your 
        October vision note about AI integration

You: "What themes emerged in my product notes this month?"
Claude: Analyzing 23 entries... Three main themes:
        1. AI/ML integration (8 entries)
        2. User feedback incorporation (6 entries)  
        3. Performance optimization (5 entries)
```

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup for Claude Code & Desktop
- **[Development Guide](docs/development.md)** - Modifying skills and development workflow
- **[Note-Taking Guide](docs/note-taking-guide.md)** - Comprehensive note-taking usage
- **[Contributing](docs/contributing.md)** - How to add new skills
- **[FAQ](docs/faq.md)** - Common questions

## 🔧 Requirements

**Required:**
- **Claude Code** 2.0+ or **Claude Desktop**
- **Python** 3.7+ (for notes_manager.py utility)
- **Bash** shell (for script execution)

**Optional:**
- **Git** (for version controlling your notes)

## 📂 Repository Structure

```
productivity-skills/
├── .claude-plugin/
│   └── marketplace.json         # Marketplace manifest
├── plugins/
│   └── productivity-suite/      # Main plugin (self-contained)
│       └── skills/              # Production skills
│           └── note-taking/     # Note-taking skill
│               ├── SKILL.md     # Skill definition
│               ├── scripts/     # Utility scripts
│               │   └── notes_manager.py
│               ├── templates/   # Note templates
│               │   └── monthly-template.md
│               └── examples/    # Example notes
│                   └── sample-notes.md
├── docs/                        # Documentation
│   ├── installation.md          # Installation guide
│   ├── development.md           # Development workflow
│   ├── contributing.md          # Contributing guidelines
│   └── faq.md                   # Frequently asked questions
├── README.md                    # This file
├── CLAUDE.md                    # Repository context for Claude
├── LICENSE                      # MIT License
└── .gitignore                   # Git ignore patterns
```

## 🤝 Contributing

Want to add a new productivity skill? We'd love your help!

See [Contributing Guide](docs/contributing.md) for:
- How to create a new skill
- Skill structure guidelines
- Testing and documentation
- Pull request process

**Potential Skills to Add:**
- Task management with priorities
- Time tracking and reporting
- Meeting notes with action items
- Daily logs and journaling
- Project documentation
- Reference management
- Habit tracking

## 🐛 Troubleshooting

### Skills not loading?

```bash
# Verify skill directory exists
ls -la ~/productivity-skills/

# Check Claude settings
cat ~/.claude/settings.json | grep skillDirectories

# Restart Claude session
```

### Notes not found?

```bash
# Check notes directory
ls -la ~/Documents/notes/

# Verify structure
ls ~/Documents/notes/$(date +%Y)/

# Rebuild index
cd ~/Documents/notes
claude
# Then: "Reindex my notes"
```

See [FAQ](docs/faq.md) for more solutions.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

Free to use, modify, and distribute. Attribution appreciated but not required.

## 🌟 Star History

If you find these skills useful, please ⭐ star the repo! It helps others discover it.

## 💬 Community

- **Issues**: [GitHub Issues](https://github.com/mcdow-webworks/productivity-skills/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mcdow-webworks/productivity-skills/discussions)
- **Twitter**: [@tonymcdow](https://twitter.com/tonymcdow)

## 🙏 Acknowledgments

- [Joey Kudish](https://jkudish.com/) for the "Second Brain = AI's Interface" article
- The Building a Second Brain community
- All contributors and early adopters

## 📬 Support

Need help?

1. Check the [FAQ](docs/faq.md)
2. Search [existing issues](https://github.com/mcdow-webworks/productivity-skills/issues)
3. Open a [new issue](https://github.com/mcdow-webworks/productivity-skills/issues/new)
4. Join the [discussion](https://github.com/mcdow-webworks/productivity-skills/discussions)

---

**Start simple. Build collaboratively with AI. Let the system grow.**

📝 Made with Claude | 🚀 Powered by Anthropic
