# Testing the Marketplace Plugin

This guide explains how to test the productivity-skills marketplace plugin after the conversion.

## Current Status

✅ **Converted to Marketplace Plugin Structure**
- Plugin marketplace manifest created at `.claude-plugin/marketplace.json`
- Skills moved to `plugins/productivity-suite/skills/`
- YAML frontmatter added to all SKILL.md files
- Documentation updated for marketplace distribution
- All changes committed and pushed to GitHub

## Plugin Information

- **Marketplace Name:** `productivity-skills`
- **Plugin Name:** `productivity-suite`
- **Repository:** `https://github.com/mcdow-webworks/productivity-skills`
- **Version:** 1.0.0
- **Available Skills:** note-taking

## Installation Testing

### Method 1: Plugin Marketplace (Recommended)

Test the marketplace installation flow:

```bash
# In Claude Code, run these commands:
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

**Expected Result:**
- Plugin should download from GitHub
- Skills should be available immediately
- No additional configuration needed

**Verify Installation:**
```bash
# List installed plugins
/plugin list

# Check if note-taking skill is available
# Try using it in any Claude session:
"Note that the marketplace plugin installation worked!"
```

### Method 2: Manual Installation (Claude Code)

For development testing or if marketplace isn't working:

```bash
cd C:\Projects\productivity-skills

# Copy plugin to Claude Code plugins directory
mkdir -p "$APPDATA/Claude/plugins"
cp -r plugins/productivity-suite "$APPDATA/Claude/plugins/"

# Restart Claude Code
```

**Verify Installation:**
- Skills should auto-load when working in any project
- Test with: "Note that manual installation is working"

### Method 3: Claude Desktop ZIP Upload (Web & App)

Claude Desktop requires uploading skills as ZIP files through the UI:

```bash
cd C:\Projects\productivity-skills

# Create ZIP archive with proper path separators (forward slashes)
# IMPORTANT: Use Python script to ensure Claude Desktop compatibility
python scripts/create-skill-zip.py

# Note: PowerShell Compress-Archive creates backslashes which Claude Desktop rejects
# The Python script ensures paths use forward slashes (/) as required by ZIP spec
```

**Upload Steps:**
1. Go to [claude.ai/settings/capabilities](https://claude.ai/settings/capabilities) (web) or Settings > Capabilities (desktop app)
2. Enable "Skills" toggle if not already enabled
3. Click "Upload skill" button
4. Select `note-taking-skill.zip`
5. Claude validates the ZIP (must have SKILL.md at root with YAML frontmatter)
6. Skill becomes available immediately

**ZIP Requirements:**
- SKILL.md must be at root level (not in subdirectory)
- SKILL.md must have YAML frontmatter with `name` and `description`
- Can include hooks/, templates/, and other resource folders
- Custom skills are private to your account

## Skill Testing

Once installed, test the note-taking skill:

### Setup
```bash
# Create notes directory
mkdir -p ~/Documents/notes/2025
```

### Basic Tests

1. **Add a Note:**
   ```
   "Note that I'm testing the marketplace plugin installation"
   ```
   - Should create/append to `~/Documents/notes/2025/11-November.md`
   - Entry should be properly formatted

2. **Search Notes:**
   ```
   "What did I note about marketplace?"
   ```
   - Should find the note you just created
   - Should show relevance score

3. **Update Existing Note:**
   ```
   "Add to the marketplace note that the installation was successful"
   ```
   - Should append update with timestamp to existing entry

4. **Pattern Recognition:**
   ```
   "What have I been working on this month?"
   ```
   - Should analyze all November notes
   - Should surface themes and patterns

## Troubleshooting

### Plugin Not Found

**Problem:** `/plugin install` says plugin not found

**Solutions:**
1. Verify marketplace was added:
   ```bash
   /plugin marketplace list
   ```
   Should show `productivity-skills` marketplace

2. Check repository is public and accessible:
   ```bash
   # Visit in browser:
   https://github.com/mcdow-webworks/productivity-skills
   ```

3. Verify `.claude-plugin/marketplace.json` exists in repo

### Skill Not Loading

**Problem:** Skill doesn't activate when you try to use it

**Check:**
1. YAML frontmatter is present in SKILL.md:
   ```bash
   head -15 plugins/productivity-suite/skills/note-taking/SKILL.md
   ```
   Should show `---` delimiters and `name:` and `description:` fields

2. Skill path in marketplace.json is correct:
   ```bash
   # Should be relative to plugin source directory
   "skills": ["./skills/note-taking"]
   ```

3. Restart Claude Code/Desktop

### Notes Not Saving

**Problem:** Notes aren't being created or updated

**Check:**
1. Notes directory exists:
   ```bash
   ls -la ~/Documents/notes/2025/
   ```

2. Python script is executable:
   ```bash
   ls -la plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py
   ```

3. Test script directly:
   ```bash
   echo '{"command":"add","heading":"Test","content":"Testing"}' | \
     python3 plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py
   ```

## Comparison with webworks-agent-skills

This plugin follows the same pattern as your webworks-agent-skills:

| Feature | webworks-agent-skills | productivity-skills |
|---------|----------------------|---------------------|
| Marketplace manifest | ✅ `.claude-plugin/marketplace.json` | ✅ `.claude-plugin/marketplace.json` |
| Plugin directory | `plugins/epublisher-automation` | `plugins/productivity-suite` |
| Skills location | `plugins/*/skills/` | `plugins/*/skills/` |
| YAML frontmatter | ✅ All SKILL.md files | ✅ All SKILL.md files |
| Self-contained | ✅ Includes shared resources | ✅ Skills are self-contained |
| Distribution | Marketplace + manual | Marketplace + manual |

## Next Steps

After successful testing:

1. **Add More Skills:**
   - Create `plugins/productivity-suite/skills/task-management/`
   - Add SKILL.md with YAML frontmatter
   - Update marketplace.json `skills` array

2. **Version Updates:**
   - Update version in marketplace.json
   - Update version in SKILL.md metadata
   - Commit and push changes
   - Users can update with `/plugin update`

3. **Share with Community:**
   - Add to awesome-claude-skills list
   - Share on GitHub Discussions
   - Blog about your second-brain workflow

## Support

If you encounter issues:

1. Check SKILL.md has proper YAML frontmatter
2. Verify marketplace.json paths are correct
3. Look at webworks-agent-skills for reference
4. Review docs/RESEARCH-claude-skills-best-practices.md

---

**Current Version:** 1.0.0
**Last Updated:** 2025-11-15
**Status:** Ready for Testing
