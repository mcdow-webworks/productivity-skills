# Prompt: Refactor note-taking SKILL.md for Simplicity and Reliability

## Context

The `productivity-skills` plugin contains a `note-taking` skill located at:
`/c/Projects/productivity-skills/plugins/productivity-suite/skills/note-taking/`

The current `SKILL.md` file is intended to provide implementation instructions for Claude on how to use the `notes_manager.py` script, but it contains too much user-facing documentation mixed with implementation details, making it verbose and potentially confusing.

## Goal

Refactor `SKILL.md` to be **lean, focused, and implementation-only** with clear, unambiguous instructions for Claude to follow.

## Requirements

1. **Remove all user-facing documentation** from SKILL.md
   - Move user documentation to a separate `docs/USER_GUIDE.md`
   - SKILL.md should be for Claude's implementation only

2. **Keep only essential implementation instructions:**
   - Script location and how to invoke it
   - Complete API specification with exact parameter names
   - Required vs optional parameters
   - Expected JSON response formats
   - Error handling patterns
   - Workflow examples showing correct usage

3. **Make instructions crystal clear:**
   - Use explicit parameter names that match the Python script exactly
   - Show complete JSON command examples for each operation
   - Don't explain WHY things work, just HOW to use them
   - Remove unnecessary explanations and philosophy

4. **Focus on preventing common mistakes:**
   - Clearly specify which parameters are required
   - Show the exact JSON structure expected
   - Provide minimal but complete working examples
   - Don't add defensive documentation for non-issues (like "Untitled" warnings)

## Current Structure Issues

- SKILL.md is ~466 lines, mostly user-facing content
- Implementation instructions are buried in user documentation
- Contains extensive "how it works" explanations not needed for implementation
- Includes troubleshooting, philosophy, and support sections irrelevant to Claude

## Desired Outcome

A lean SKILL.md (~100-150 lines) that contains:

1. **Frontmatter** - Name and description trigger
2. **Critical Rules** - What Claude MUST always do
3. **Script API Reference** - Complete command specification
4. **Workflow Examples** - 2-3 concrete usage patterns
5. **Error Handling** - How to handle script errors

That's it. Nothing more.

## Files to Review

- Current SKILL.md: `/c/Projects/productivity-skills/plugins/productivity-suite/skills/note-taking/SKILL.md`
- Python script: `/c/Projects/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py`

## Task

1. Analyze the current SKILL.md and `notes_manager.py` to understand the actual API
2. Extract only the essential implementation instructions
3. Create a new lean SKILL.md focused on correct usage
4. Move all user-facing content to `docs/USER_GUIDE.md`
5. Ensure all JSON parameter names exactly match what `notes_manager.py` expects

## Success Criteria

- SKILL.md is under 200 lines
- Every JSON command example is complete and correct
- No user-facing documentation remains in SKILL.md
- Instructions are unambiguous and follow the script's actual API
- Claude can follow the instructions without guessing parameter names
