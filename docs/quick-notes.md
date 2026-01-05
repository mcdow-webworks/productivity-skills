# Quick Notes CLI

Fast note capture from the command line using Claude Haiku 4.5 for automatic categorization and intelligent enrichment.

## Overview

The `qn` command provides sub-2-second note capture that integrates with your existing notes system. It uses Claude Haiku 4.5 to:

1. **Categorize** your note instantly (sync)
2. **Enrich** the note with context in the background (async)

**Cost:** ~$0.0022 per enriched note (~$2.20 per 1000 notes)

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

# Skip enrichment for quick captures
qn --no-enrich quick reminder to call mom
```

## Enrichment

After your note is saved (~1.5s), the CLI enriches it in the background with:

- **Definition:** Clarifies key concepts
- **Implications:** Captures significance and relevance
- **Next Steps:** Anticipates follow-up actions
- **Related:** Connects to common concepts

### Example

**Input:**
```powershell
qn link https://arxiv.org/paper123 study on Compression is Intelligence
```

**After enrichment (~10s later):**
```markdown
# Reference - link https://arxiv.org/paper123 study on Compression...
Recent study link: https://arxiv.org/paper123 exploring "Compression is Intelligence"
theory and its impact on software engineering.

**Definition:** Compression as intelligence refers to distilling complex information
into simpler representations that preserve essential meaning while reducing redundancy.

**Implications:** This has profound relevance for software engineering:
- Code abstraction is a form of compression (patterns, functions, libraries)
- Good architecture compresses complexity into navigable structures
- AI/ML models compress training data into generalizable rules

**Next Steps:** Consider how this applies to current projects - are there
opportunities to better compress complexity?

**Created:** 2026-01-04
```

### Skipping Enrichment

Use `--no-enrich` for quick captures that don't need expansion:

```powershell
qn --no-enrich buy milk
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
- **Enrichment fails:** Original note preserved, enrichment silently skipped

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
| Category inference | ~800ms |
| File I/O | ~300ms |
| **User sees "Note saved"** | **~1.2-2s** |
| Enrichment (background) | ~5-10s |

## See Also

- [Note-Taking Guide](note-taking-guide.md) - Full note-taking skill documentation
- [Installation](installation.md) - Main plugin installation
