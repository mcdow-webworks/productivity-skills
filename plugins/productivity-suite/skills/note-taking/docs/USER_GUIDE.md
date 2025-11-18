# Note-Taking - AI-Navigable Second Brain

Transform your markdown notes into an AI-navigable knowledge system. Claude becomes your interface for capturing, organizing, and retrieving information across all your work.

## Quick Start

**No setup required!** Just start using it in any Claude session:

```
"Note that I just discovered a great caching solution"
```

The skill automatically creates your notes directory on first use:
- Default location: `~/Documents/notes/`
- **Windows with OneDrive:** Automatically uses `~/OneDrive/Documents/notes/` if OneDrive is installed, ensuring sync across devices and consistency between Claude Desktop and Claude Code
- Organized by year: `2025/`, `2026/`, etc.
- Monthly files: `11-November.md`, `12-December.md`, etc.

**Custom location** (optional):
```bash
export NOTES_DIR="$HOME/my-custom-notes"
```

That's it! Claude now manages your notes across all sessions.

## Your Note Format

### Monthly Files
- Files are organized by year and month: `~/Documents/notes/2025/11-November.md`
- Current month is automatically used unless specified
- Plain markdown - portable, searchable, version-controllable

### Entry Format
```markdown
# Category - Brief description
Details about the entry. Can include:
- Multiple lines
- Code blocks
- Links
- Lists

**Update (2025-11-16):** Additional information added later
```

### Common Categories
- `Idea` - New concepts or features
- `Meeting` - Discussion notes
- `Update` - Status changes
- `Question` - Things to explore
- `Decision` - Conclusions reached
- `Work` - Daily accomplishments
- `Learning` - Insights from reading/research

Claude can suggest appropriate categories if you're not sure.

## Core Capabilities

### 1. Adding Notes Conversationally

Just talk naturally to Claude:

```
You: "Note that the German partner loved the llms.txt idea"

Claude: I'll add that to your November notes.

# Meeting - llms.txt discussion with German partner
They're very interested in the automatic generation approach for their AI training pipeline.

Added! I noticed you had an earlier entry about llms.txt from Nov 15. Want me to link them?
```

**Trigger phrases:**
- "Note that..."
- "Add a note about..."
- "Remember that..."
- "Capture this..."

### 2. Finding Notes

Ask Claude to search your knowledge:

```
You: "What's the status of the llms.txt idea?"

Claude: You have 3 entries about llms.txt:

**Nov 15** - Idea - Generate llms.txt automatically from Reverb format
Initial concept about creating a build step.

**Nov 16** - Meeting - German partner discussion
They validated the approach and see value for their pipeline.

**Nov 17** - Update
Decision to start with proof-of-concept.

The idea has progressed from concept to validated to implementation in 3 days!
```

**Alternative query showing progression:**

```
You: "What did I note about Claude Code?"

Claude: You have 40+ entries across 7 months showing your learning progression:

**March** - Moving to Claude for Dev (discovery)
**July** - Claude Code basics, SubAgents (learning fundamentals)
**August** - 15 entries on MCP, Studio, Philosophy (deep dive)
**September** - Sub-agents, Search agent (advanced topics)
**October** - Plugins, Rules, Workflows, Skills (building expertise)
**November** - Skills, Router Tips, Agentic Library (mastery)

Your progression from beginner to expert over 7 months is impressive!
```

**Trigger phrases (must explicitly mention notes):**
- "What did I **note** about..."
- "What have I **noted** about..."
- "Show me my **notes** on..."
- "Search my **notes** for..."
- "Find in my **notes**..."
- "What's in my **notes** about..."
- "Status of [topic] in my **notes**"

**Note:** Generic phrases like "What have I learned about..." or "What do I know about..." won't reliably trigger because they're ambiguous. Always use "note/notes/noted" in your query.

### 3. Updating Existing Entries

Claude automatically finds and appends to the right note:

```
You: "Add to the llms.txt note that we're starting the POC next week"

Claude: Updated your llms.txt entry:

# Idea - Generate llms.txt automatically from Reverb format
...original content...

**Update (2025-11-17):** Starting proof-of-concept next week. Will test with small subset of Reverb docs first.

This is your 4th update to this idea - great momentum!
```

**Trigger phrases:**
- "Add to the X note..."
- "Update X with..."
- "Append to X..."

### 4. Pattern Recognition

Ask Claude to analyze your thinking:

```
You: "What themes emerged in my November notes?"

Claude: Looking across 47 entries in November, I see three main themes:

1. **Documentation Automation** (12 entries)
   - llms.txt generation
   - API doc automation
   - Making content AI-friendly

2. **Partner Engagement** (8 entries)
   - German partner discussions
   - Customer feedback sessions
   - Feature validation

3. **Infrastructure** (6 entries)
   - WSL2 optimization
   - Development environments
   - Build automation

Documentation automation is your hottest topic - you've touched on it weekly. Might warrant dedicated focus time?
```

### 5. Daily Capture

End-of-day knowledge capture:

```
You: "What's worth noting from today?"

Claude: Looking at today's activity:
- You fixed that Reverb cache busting issue (3 commits)
- Had meeting about ePublisher Designer
- Helped customer with ePUB table rendering

Should we capture:
1. The technical solution for cache busting?
2. Any decisions from the Designer meeting?
3. The ePUB workaround for future reference?
```

## How It Works

### Behind the Scenes

1. **Automatic Indexing**: Claude maintains a search index (`.index.json`) of all your entries
2. **Smart Search**: Searches headings first, then content, weighted by recency
3. **Context Preservation**: Updates maintain history with timestamps

### File Structure

```
~/Documents/notes/
├── 2025/
│   ├── 01-January.md
│   ├── 02-February.md
│   └── 11-November.md          # Current month
├── .index.json                 # Auto-generated search index
└── .gitignore                  # Ignore index files
```

## Integration with Your Workflow

### Works Everywhere

Because this is configured globally, it works in **every Claude session**:

```bash
# Working on a code project
cd ~/projects/ePublisher
claude

You: "Note that I found the VBA field type bug - it was the filter logic"
Claude: Added to your notes with technical details!

# Different project
cd ~/projects/boat-business
claude

You: "What did I note about GetMyBoat bookings?"
Claude: Found 2 entries showing 20% increase this month...
```

### Automatic Context

Claude understands context from your work:

```
# You're debugging an issue
You: "I finally figured it out - the cache headers were wrong"
Claude: "Great! Want me to note the solution so you remember this approach?"

# Reviewing past work
You: "What solutions have I noted for caching issues?"
Claude: Searches and shows relevant past solutions
```

### Cross-Reference with Code

```
You: "Link this commit to my note about the cache fix"
Claude: I'll add the commit hash to your Nov 17 note about cache headers.
```

## Advanced Usage

### Custom Categories

Define your own categories:

```
You: "Note this as a 'Customer-Request' - they want bulk export"
Claude: Added new category to your schema:

# Customer-Request - Bulk export feature
[Details...]
```

### Timeline Queries

```
You: "What was I working on in October?"
You: "Show me all Reverb-related notes from Q3"
You: "What decisions did I make last week?"
```

### Batch Operations

```
You: "Find all entries tagged with 'urgent' and show their status"
You: "What ideas have I captured but not acted on?"
You: "Show me all meetings from this month"
```

### Export and Reporting

```
You: "Create a summary of all my November work"
You: "Export all llms.txt entries as a single document"
You: "Generate a timeline of the Reverb project"
```

## Best Practices

### 1. Capture Immediately
Don't wait - note ideas as they happen. Claude makes it frictionless.

### 2. Trust the Search
Don't stress about organization. Claude can find it later.

### 3. Update, Don't Delete
Add updates with timestamps. Shows evolution of thinking.

### 4. Review Patterns
Weekly: "What did I focus on this week?"
Monthly: "What themes emerged?"

### 5. Be Conversational
Claude understands natural language. Don't worry about exact syntax.

## Migrating Existing Notes

If you already have markdown notes, ask Claude to help migrate them:

```
You: "I have old notes in ~/old-notes - can you import them?"

Claude: I'll migrate your existing notes into the organized structure.
```

This will:
- Import all markdown files with UTF-8 encoding
- Organize by modification date into appropriate monthly files
- Rebuild the search index automatically
- Validate files and report any issues

## Configuration Options

### Custom Notes Directory

```bash
# In your shell config (~/.bashrc or ~/.zshrc)
export NOTES_DIR="$HOME/Documents/notes"
```

### Auto-Capture Hook (Optional)

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "prompt",
        "prompt": "If anything significant was accomplished in this session, briefly suggest (in one sentence) what could be noted. If nothing notable, output nothing."
      }]
    }]
  }
}
```

### Custom Categories

Define in `~/Documents/notes/.config.json`:

```json
{
  "categories": [
    "Idea",
    "Meeting",
    "Decision",
    "Work",
    "Learning",
    "Customer-Request",
    "Bug",
    "Feature"
  ]
}
```

## Troubleshooting

### "Claude can't find my notes"

Check your directory structure:
```bash
ls -la ~/Documents/notes/
# Should see year directories and .index.json
```

Manually reindex:
```
In Claude: "Reindex all my notes"
```

### "Entries aren't updating"

Verify file permissions:
```bash
ls -la ~/Documents/notes/2025/
# Files should be writable by your user
```

### "Search not working"

Ask Claude: "Reindex all my notes"

This rebuilds the search index safely.

## Privacy & Data

- **All data stays local** - Notes never leave your machine
- **Plain text** - No proprietary formats, portable forever
- **Version control friendly** - Git works perfectly with markdown
- **No external services** - Everything runs locally

## Tips from Users

> "I keep one terminal always in ~/Documents/notes with Claude running. Quick access for capture, but I can still search from any other session." - *Tony W.*

> "I ask Claude 'what should I note from today?' at the end of each workday. Helps ensure I don't lose insights." - *Developer*

> "The pattern recognition is amazing. Claude found connections between ideas I'd completely forgotten about." - *Product Manager*

## Philosophy

This skill embodies the "Second Brain = AI's Interface" philosophy:

1. **Not just storage** - Claude actively helps you think
2. **Queryable history** - Ask questions your notes can answer
3. **Pattern recognition** - Surface connections you'd miss
4. **Reflection tool** - Review your thinking over time
5. **Minimal friction** - Capture should be effortless

Your notes aren't just for you anymore - they're for you and your AI partner.

## Support

- **Issues**: [GitHub Issues](https://github.com/mcdow-webworks/productivity-skills/issues)
- **Examples**: See [examples/](../examples/)
- **Discussions**: [GitHub Discussions](https://github.com/mcdow-webworks/productivity-skills/discussions)

---

**Remember**: Start simple. Capture consistently. Let Claude surface the insights.

Your second brain, AI-navigable.
