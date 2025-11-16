# Productivity Skills for Claude

A collection of AI-native productivity skills that work seamlessly with both Claude Code and Claude Desktop. These skills transform Claude into an active partner in your personal knowledge management, task tracking, and daily workflows.

## Available Skills

### 📝 Note-Taking
Transform your markdown notes into an AI-navigable second brain. Claude becomes your interface for capturing, organizing, and retrieving knowledge across all your projects.

**Key Features:**
- Conversational note capture from any project
- Intelligent search across all your notes
- Automatic updates to existing entries
- Pattern recognition and insight generation
- Maintains simple markdown format

[Read more about Note-Taking →](note-taking/README.md)

## Coming Soon

- **Task Management**: AI-assisted todo tracking with automatic prioritization
- **Time Tracking**: Conversational time logging with intelligent categorization
- **Meeting Notes**: Structured capture and retrieval of meeting information
- **Daily Logs**: Automated work journaling and reflection

## Philosophy

These skills follow key principles:

1. **Plain text first** - All data in markdown, portable forever
2. **AI-navigable** - Claude as your interface, not just storage
3. **Natural interaction** - Talk naturally, not commands
4. **Cross-project** - Available in every Claude session
5. **Incremental adoption** - Start simple, grow organically

## Installation

### For Claude Code

Add to your `~/.claude/settings.json`:

```json
{
  "projectDefaults": {
    "skillDirectories": [
      "~/productivity-skills"
    ]
  }
}
```

### For Claude Desktop

Add to your Claude Desktop settings:

```json
{
  "skillDirectories": [
    "~/productivity-skills"
  ]
}
```

Then clone this repo:

```bash
git clone https://github.com/YOUR-USERNAME/productivity-skills.git ~/productivity-skills
```

See [Installation Guide](docs/installation.md) for detailed setup.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/productivity-skills.git ~/productivity-skills
   ```

2. **Configure Claude**
   Add the skill directory to your settings (see Installation above)

3. **Set up your first skill**
   ```bash
   # For note-taking
   mkdir -p ~/notes/2025
   ```

4. **Start using it**
   Open any Claude session and say:
   ```
   "Note that I just had a great idea about..."
   ```

## Usage

Once installed, these skills are available in **every Claude session** - both Claude Code and Claude Desktop.

```
# In any project directory
cd ~/projects/my-app
claude

You: "Note that I solved the cache busting issue with a hash-based approach"
Claude: Added to your November notes. This is related to your earlier Reverb deployment work - should I link them?

You: "What have I been working on this week?"
Claude: Looking across your notes from Nov 10-17...
```

## Why Skills, Not Just Prompts?

Skills provide:
- **Persistent knowledge** - Claude learns your patterns across sessions
- **Structured operations** - Reliable file handling and search
- **Cross-project availability** - Works everywhere automatically  
- **Extensibility** - Easy to add new capabilities

## Contributing

Want to add a new productivity skill? See [Contributing Guide](docs/contributing.md).

## Structure

```
productivity-skills/
├── SKILL.md                 # This file
├── note-taking/             # Note-taking skill
│   ├── SKILL.md
│   ├── hooks/
│   └── templates/
├── task-management/         # Coming soon
├── time-tracking/           # Coming soon
├── docs/                    # Documentation
└── examples/                # Example configurations
```

## Requirements

- Claude Code 2.0+ or Claude Desktop
- Bash shell (for hooks)
- Python 3.7+ (for utility scripts)

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Examples**: See [examples/](examples/) directory

## License

MIT - See [LICENSE](LICENSE)

## Acknowledgments

Inspired by:
- ["Your Second Brain = AI's Interface"](https://jkudish.com/newsletter/003) by Joey Kudish
- The Building a Second Brain methodology
- Plain text enthusiasts everywhere

---

**Start simple. Build collaboratively with AI. Let the system grow.**

📝 Made with Claude
