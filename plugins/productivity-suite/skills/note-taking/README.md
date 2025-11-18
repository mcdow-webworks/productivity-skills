# Note-Taking Skill

Transform markdown notes into an AI-navigable second brain. Claude becomes your interface for capturing, organizing, and retrieving information across all your work.

## Quick Start

Just start using it in any Claude session:

```
"Note that I just discovered a great caching solution"
"What did I note about Claude Code?"
"Add to my note about caching that it's now deployed"
```

The skill automatically creates your notes directory on first use with organized monthly files.

## Documentation

### For Users
- **[User Guide](docs/USER_GUIDE.md)** - Complete documentation with examples, best practices, and configuration
- **[Examples](examples/)** - Sample notes and usage patterns

### For Developers & Implementation
- **[SKILL.md](SKILL.md)** - Implementation instructions for Claude (how to use the script correctly)
- **[API Reference](docs/API.md)** - Complete `notes_manager.py` JSON command reference
- **[Search Algorithm](reference/ALGORITHM.md)** - Relevance scoring technical details
- **[Workflow Guide](reference/WORKFLOW.md)** - Decision trees and implementation patterns
- **[Troubleshooting](reference/TROUBLESHOOTING.md)** - Common issues and solutions

## Features

- **Natural Language Interface**: Talk naturally to Claude - no commands to memorize
- **Automatic Organization**: Monthly files organized by year
- **Smart Search**: Finds notes by heading priority, with relevance scoring
- **Context Preservation**: Updates maintain history with timestamps
- **Cross-Platform**: Works on Windows (with OneDrive support), macOS, and Linux
- **Plain Text**: All notes in portable markdown format
- **Local-First**: Your data never leaves your machine

## Installation

### Claude Code
```bash
# Install from marketplace
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

### Claude Desktop
Upload the skill ZIP file through Settings > Capabilities > Skills

## Architecture

The skill uses a Python script (`scripts/notes_manager.py`) as the backend for all note operations. Claude interacts with notes exclusively through this script using JSON commands via stdin/stdout.

**Critical Design Rule**: Claude MUST use the script for all operations - never directly reading or writing note files. This ensures:
- Consistent index management
- Proper relevance scoring for search
- Correct timestamp handling
- File format integrity

See [SKILL.md](SKILL.md) for complete implementation details.

## Support

- **Issues**: [GitHub Issues](https://github.com/mcdow-webworks/productivity-skills/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mcdow-webworks/productivity-skills/discussions)
- **Repository**: [mcdow-webworks/productivity-skills](https://github.com/mcdow-webworks/productivity-skills)

## License

MIT License - See repository root for full license text.

---

**Your second brain, AI-navigable.**
