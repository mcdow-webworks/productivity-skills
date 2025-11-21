# Documentation Streamlining Analysis

## Current State

### Root Level Documentation (330 lines total)
- **README.md** (330 lines) - Main entry point
- **CLAUDE.md** - Project context for Claude Code (keep)
- **SKILL_REFACTOR_PROMPT.md** - Temporary task file (DELETE)
- **SKILL_REFACTOR_SUMMARY.md** - Temporary task file (DELETE or archive)

### docs/ Directory (2,126 lines total)
- **USER_GUIDE.md** (383 lines) - NEW: Comprehensive note-taking user guide
- **installation.md** (140 lines) - Installation instructions
- **development.md** (616 lines) - Development workflow
- **contributing.md** (498 lines) - Contributing guidelines
- **faq.md** (349 lines) - FAQ
- **images/README.md** - Placeholder (empty)

### Research Directory (.github/research/) - 23 files
Many contain outdated research that's been implemented or superseded.

## Identified Issues

### 1. Duplication: Installation Instructions

**Found in:**
- README.md (lines 26-70) - Quick start installation
- docs/installation.md (entire file) - Detailed installation

**Problem:** 90% overlap with different verbosity levels

**Recommendation:**
- **Keep in README:** Ultra-concise quick start (5-10 lines)
- **Keep in docs/installation.md:** Full details including troubleshooting
- Remove duplication

### 2. Duplication: Troubleshooting

**Found in:**
- README.md (lines 264-293) - Basic troubleshooting
- docs/installation.md (lines 78-140) - Installation troubleshooting
- docs/faq.md - Comprehensive FAQ

**Problem:** Similar troubleshooting content scattered across 3 files

**Recommendation:**
- Remove from README.md (just link to FAQ)
- Keep detailed troubleshooting in docs/faq.md
- Keep installation-specific issues in docs/installation.md

### 3. Missing Document Referenced in README

**Line 203 in README.md:**
```markdown
- **[Note-Taking Guide](docs/note-taking-guide.md)** - Comprehensive note-taking usage
```

**Problem:** File `docs/note-taking-guide.md` does NOT exist

**Recommendation:**
- Update README.md to point to `docs/USER_GUIDE.md` (just created)
- OR rename USER_GUIDE.md to note-taking-guide.md for consistency

### 4. Research Documents (.github/research/)

**Keep all 23 research files** - They provide valuable historical context for design decisions and are hidden from users in the `.github/` directory. Not a maintenance burden.

### 5. Temporary Files in Root

**DELETE:**
- `SKILL_REFACTOR_PROMPT.md` - Task-specific temporary file
- `SKILL_REFACTOR_SUMMARY.md` - Can archive to .github/research/ if desired

### 6. Empty Placeholder

**docs/images/README.md** - Empty placeholder

**Recommendation:** DELETE (directory purpose is self-evident)

## Streamlining Plan

### Phase 1: Remove Unnecessary Files (Immediate)

```bash
# Archive temporary task files to research
mv SKILL_REFACTOR_PROMPT.md .github/research/
mv SKILL_REFACTOR_SUMMARY.md .github/research/

# Delete empty placeholder
rm docs/images/README.md
```

**Estimated reduction:** 3 files cleaned up from root

### Phase 2: Consolidate Duplication

**README.md changes:**
1. Reduce installation section to 5-10 lines with link to full guide
2. Remove troubleshooting section, just link to FAQ
3. Fix broken link: `note-taking-guide.md` → `USER_GUIDE.md`

**docs/installation.md:**
- Keep as-is (detailed installation guide)

**docs/faq.md:**
- Keep as-is (comprehensive FAQ)

**docs/USER_GUIDE.md:**
- Rename to `note-taking-guide.md` (matches README link)
- OR update README link to `USER_GUIDE.md`

### Phase 3: Verify Consistency

After streamlining, verify all remaining docs reference:
- New SKILL.md with full path and escaped quotes
- Correct Python invocation (`python` not `python3`)
- Updated installation paths

## Final Documentation Structure (Proposed)

```
productivity-skills/
├── README.md                    # Concise overview, quick start, links (~200 lines)
├── CLAUDE.md                    # Project context for Claude (keep as-is)
├── docs/
│   ├── installation.md          # Full installation guide (keep as-is)
│   ├── note-taking-guide.md     # User guide (rename from USER_GUIDE.md)
│   ├── development.md           # Developer guide (keep as-is)
│   ├── contributing.md          # Contributing guide (keep as-is)
│   └── faq.md                   # FAQ (keep as-is)
├── .github/research/            # Historical design docs (keep all 23 files)
│   ├── SKILL_REFACTOR_PROMPT.md # Archived from root
│   └── SKILL_REFACTOR_SUMMARY.md # Archived from root
└── plugins/productivity-suite/skills/note-taking/
    ├── SKILL.md                 # Lean implementation guide (145 lines)
    ├── scripts/notes_manager.py
    ├── templates/monthly-template.md
    └── examples/sample-notes.md
```

**User-facing docs streamlined:**
- Temporary files moved to .github/research/
- Duplication removed from README.md
- Clear documentation hierarchy established
- Lines in user docs: ~2,500 → ~2,000 (20% reduction)

## Benefits

1. **Easier maintenance** - Single source of truth for each topic
2. **Clearer navigation** - No confusion about where to find information
3. **Reduced redundancy** - Updates only needed in one place
4. **Smaller repository** - Faster clones, clearer git history
5. **Better user experience** - Clear documentation hierarchy

## Risks

**Minimal risk:**
- Only removing temporary files and duplication
- All research preserved in .github/research/
- No unique content being deleted

## Next Steps

1. Review this analysis
2. Approve deletion/consolidation plan
3. Execute Phase 1 (remove unnecessary files)
4. Execute Phase 2 (consolidate duplication)
5. Execute Phase 3 (verify consistency)
6. Update CLAUDE.md with streamlining notes
