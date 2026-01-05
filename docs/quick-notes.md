# Quick Notes CLI

Fast note capture from the command line using Claude Haiku 4.5 for automatic categorization.

## Overview

The `qn` command provides sub-3-second note capture that integrates with your existing notes system. It uses Claude Haiku 4.5 to automatically categorize notes.

**Cost:** ~$0.00015 per note (~$0.15 per 1000 notes)

## Install

### Prerequisites

- Python 3.7+
- PowerShell Core 7+ (or Windows PowerShell)
- Anthropic API key

### Step 1: Install Python Package

```bash
pip install anthropic
```

### Step 2: Set API Key

Get your API key at [console.anthropic.com](https://console.anthropic.com)

```powershell
# Add to your PowerShell profile for persistence
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

### Step 3: Install the qn Function

```powershell
# From the productivity-skills directory
.\scripts\install-qn.ps1
```

### Step 4: Restart PowerShell

```powershell
. $PROFILE
```

## Usage

```powershell
qn meeting with Jim about AutoMap pricing
# Saves as: # Meeting - meeting with Jim about AutoMap pricing

qn learned how async Python works
# Saves as: # Learning - learned how async Python works

qn what if we added dark mode?
# Saves as: # Idea - what if we added dark mode?
```

## Categories

The AI automatically infers one of these categories:

| Category | Triggers |
|----------|----------|
| Work | tasks, bugs, implementations, fixing things |
| Meeting | calls, discussions, people mentioned by name |
| Learning | discoveries, tutorials, "learned", "realized" |
| Idea | "what if", brainstorms, future possibilities |
| Decision | "will", "decided", commitments, plans |
| Question | uncertainties, "how to", investigations |
| Reference | bookmarks, links, documentation, records |
| Note | general observations (default) |

## Notes Storage

Notes are saved to the same location as the main note-taking skill:

- **Default:** `~/Documents/notes/YYYY/MM-Month.md`
- **Windows with OneDrive:** `~/OneDrive/Documents/notes/YYYY/MM-Month.md`
- **Custom:** Set `NOTES_DIR` environment variable

## Error Handling

- **No API key:** Clear error with setup instructions
- **API timeout:** Falls back to "Note" category (data never lost)
- **Invalid API key:** Authentication error with link to console

## Troubleshooting

### "anthropic package not installed"

```bash
pip install anthropic
```

### "ANTHROPIC_API_KEY not set"

1. Get your key at [console.anthropic.com](https://console.anthropic.com)
2. Add to your environment:
   ```powershell
   $env:ANTHROPIC_API_KEY = "sk-ant-..."
   ```

### qn command not found

1. Re-run the installation: `.\scripts\install-qn.ps1`
2. Restart PowerShell: `. $PROFILE`

### Notes not appearing in search

The quick notes CLI doesn't update the search index for speed. Run a reindex:

```powershell
echo '{"command":"reindex"}' | python path/to/notes_manager.py
```

Or use the note-taking skill: "Reindex my notes"

## Performance

| Component | Time |
|-----------|------|
| PowerShell startup | ~100ms |
| Python + API call | ~800ms |
| File I/O | ~300ms |
| **Total** | **~1.2-2s** |

## See Also

- [Note-Taking Guide](note-taking-guide.md) - Full note-taking skill documentation
- [Installation](installation.md) - Main plugin installation
