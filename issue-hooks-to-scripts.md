## Overview

Fix the note-taking skill to properly use `notes_manager.py` for all file operations and rename the misleading `hooks/` directory to `scripts/` to align with official Anthropic conventions. This addresses cross-platform compatibility issues and removes confusion about Claude Code's hook system.

## Problem Statement

### Issue 1: Misleading Directory Name

**Current state:**
- Directory: `plugins/productivity-suite/skills/note-taking/hooks/`
- Contains only `notes_manager.py` (a utility script, not hooks)
- Name implies Git hooks or Claude Code event callbacks
- Conflicts with official Anthropic convention using `scripts/`

**Problems:**
- Users confuse utility scripts with Claude Code's `.claude/settings.json` hooks
- Inconsistent with official Anthropic skills (all use `scripts/`)
- Semantic mismatch: "hooks" = event callbacks, not helper utilities

**Evidence:**
- skill-creator skill: Uses `scripts/` directory
- document-skills/pdf skill: Uses `scripts/` directory
- All examined official Anthropic skills: Use `scripts/` NOT `hooks/`

### Issue 2: Direct File Operations Bypass notes_manager.py

**SKILL.md Line 338:**
```bash
cp ~/old-notes/*.md ~/Documents/notes/2025/
```

**Problems:**
- Bypasses OneDrive detection (Windows users get wrong path)
- No index updates after copy
- No UTF-8 encoding guarantee
- Skips validation

**SKILL.md Line 422:**
```bash
rm ~/Documents/notes/.index.json
```

**Problems:**
- Direct file deletion without cleanup
- No error handling
- Index rebuilds should be through script

### Issue 3: Incorrect Script Paths in Documentation

**SKILL.md Lines 226, 230:**
```bash
python3 ~/productivity-skills/note-taking/hooks/notes_manager.py reindex
```

**Problems:**
- Path doesn't match actual installation location
- Should reference skill-local path: `scripts/notes_manager.py`
- Non-existent directory structure

### Issue 4: Missing Cross-Platform Path Normalization

**notes_manager.py Line 31:**
```python
NOTES_DIR = Path(os.environ.get('NOTES_DIR', DEFAULT_NOTES_DIR))
```

**Problem:** Missing `.expanduser().resolve()` call

**Impact:**
- Relative paths not resolved to absolute
- `~` expansion depends on shell state
- Path inconsistencies across sessions

### Issue 5: Confusing Terminology

**SKILL.md Line 222:**
```markdown
The `notes_manager.py` script provides programmatic access for advanced hooks:
```

**Problem:** "advanced hooks" is misleading terminology

**Correct:** "advanced operations" or "direct invocation"

## Proposed Solution

### Phase 1: Directory Rename

**Rename directory:**
```bash
git mv plugins/productivity-suite/skills/note-taking/hooks \
      plugins/productivity-suite/skills/note-taking/scripts
```

**Update all references:**
- `SKILL.md`: 13 occurrences (lines 19, 20, 34, 222, 224-231, 338, 401-402, 414-415, 422)
- `CLAUDE.md`: 3 occurrences (lines 24, 122, 179)
- Any other documentation files

### Phase 2: Add Missing Commands to notes_manager.py

**Add three new commands:**

#### 1. `clean-index` Command
```python
def clean_index():
    """Safely remove and rebuild search index."""
    index_path = NOTES_DIR / '.index.json'
    if index_path.exists():
        index_path.unlink()
    return reindex()
```

**Usage:**
```bash
echo '{"command":"clean-index"}' | python scripts/notes_manager.py
```

#### 2. `validate` Command
```python
def validate():
    """Check all note files for issues."""
    issues = []
    for year_dir in sorted(NOTES_DIR.glob('[0-9]*')):
        for note_file in sorted(year_dir.glob('*.md')):
            try:
                content = note_file.read_text(encoding='utf-8')
                # Check for common issues
                if not content.strip():
                    issues.append(f"{note_file.name}: Empty file")
                # Add more validation checks
            except Exception as e:
                issues.append(f"{note_file.name}: {str(e)}")

    return {
        'status': 'success',
        'issues': issues,
        'files_checked': len(list(NOTES_DIR.glob('[0-9]*/*.md')))
    }
```

**Usage:**
```bash
echo '{"command":"validate"}' | python scripts/notes_manager.py
```

#### 3. `migrate` Command
```python
def migrate(source_dir: str):
    """Import existing markdown files with validation."""
    source = Path(source_dir).expanduser().resolve()

    if not source.exists():
        return {'status': 'error', 'message': f'Source directory not found: {source}'}

    imported = []
    errors = []

    for md_file in source.glob('**/*.md'):
        try:
            # Read with UTF-8
            content = md_file.read_text(encoding='utf-8')

            # Determine target year/month (use modification time)
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            year_dir = NOTES_DIR / str(mtime.year)
            year_dir.mkdir(parents=True, exist_ok=True)

            # Copy to appropriate monthly file
            month_file = year_dir / f"{mtime.month:02d}-{mtime.strftime('%B')}.md"

            # Append content
            with open(month_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{content}")

            imported.append(str(md_file))

        except Exception as e:
            errors.append(f"{md_file.name}: {str(e)}")

    # Rebuild index
    reindex()

    return {
        'status': 'success',
        'imported': len(imported),
        'errors': errors
    }
```

**Usage:**
```bash
echo '{"command":"migrate","source_dir":"~/old-notes"}' | python scripts/notes_manager.py
```

### Phase 3: Enhance Path Normalization

**Update notes_manager.py line 31:**

**Before:**
```python
NOTES_DIR = Path(os.environ.get('NOTES_DIR', DEFAULT_NOTES_DIR))
```

**After:**
```python
NOTES_DIR = Path(os.environ.get('NOTES_DIR', DEFAULT_NOTES_DIR)).expanduser().resolve()
```

**Add to get_info() (after line 291):**
```python
def get_info() -> Dict:
    onedrive_path = Path.home() / 'OneDrive' / 'Documents'

    return {
        'status': 'success',
        'notes_dir': str(NOTES_DIR.resolve()),
        'notes_dir_exists': NOTES_DIR.exists(),
        'notes_dir_is_writable': os.access(NOTES_DIR, os.W_OK),  # NEW
        'onedrive_detected': onedrive_path.exists(),              # NEW
        'using_onedrive': str(NOTES_DIR).startswith(str(onedrive_path)),  # NEW
        # ... rest of existing fields
    }
```

### Phase 4: Update Documentation

**Replace direct file operations in SKILL.md:**

**Line 338 - Before:**
```bash
# Move existing files to new structure
cp ~/old-notes/*.md ~/Documents/notes/2025/
```

**Line 338 - After:**
```bash
# Import existing notes with validation
echo '{"command":"migrate","source_dir":"~/old-notes"}' | \
  python scripts/notes_manager.py
```

**Line 422 - Before:**
```bash
rm ~/Documents/notes/.index.json
# Then in Claude: "Reindex my notes"
```

**Line 422 - After:**
```bash
# Rebuild the index safely
echo '{"command":"clean-index"}' | python scripts/notes_manager.py
```

**Lines 226, 230 - Before:**
```bash
python3 ~/productivity-skills/note-taking/hooks/notes_manager.py reindex
```

**Lines 226, 230 - After:**
```bash
# From skill directory
python3 scripts/notes_manager.py reindex

# Or with full path
python3 $APPDATA/Claude/plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py
```

**Line 222 - Before:**
```markdown
The `notes_manager.py` script provides programmatic access for advanced hooks:
```

**Line 222 - After:**
```markdown
The `notes_manager.py` utility script provides direct access for advanced operations:
```

## Acceptance Criteria

### Directory Structure
- [ ] Directory renamed: `hooks/` → `scripts/`
- [ ] All file references updated in SKILL.md
- [ ] All file references updated in CLAUDE.md
- [ ] All file references updated in README.md
- [ ] Git history preserved with `git mv`

### New Commands
- [ ] `clean-index` command implemented and tested
- [ ] `validate` command implemented and tested
- [ ] `migrate` command implemented and tested
- [ ] All commands have JSON input/output
- [ ] Error handling for each command
- [ ] Documentation for each command in SKILL.md

### Path Normalization
- [ ] `NOTES_DIR` uses `.expanduser().resolve()`
- [ ] `get_info()` includes OneDrive detection fields
- [ ] All file operations use `encoding='utf-8'`
- [ ] Tested on Windows (with/without OneDrive)
- [ ] Tested on macOS
- [ ] Tested on Linux

### Documentation
- [ ] No direct `cp` commands in docs
- [ ] No direct `rm` commands in docs
- [ ] Correct script paths throughout
- [ ] "hooks" terminology replaced with "scripts" or "operations"
- [ ] Migration example uses new `migrate` command
- [ ] Index rebuild uses new `clean-index` command

### Testing
- [ ] Existing functionality unaffected
- [ ] New commands work on all platforms
- [ ] OneDrive detection works correctly
- [ ] Custom `NOTES_DIR` still supported
- [ ] Index rebuilds properly after migration

## Implementation Plan

### Step 1: Rename Directory (5 minutes)

```bash
cd C:/Projects/productivity-skills

# Rename using git mv (preserves history)
git mv plugins/productivity-suite/skills/note-taking/hooks \
      plugins/productivity-suite/skills/note-taking/scripts

# Verify
ls -la plugins/productivity-suite/skills/note-taking/scripts/
```

### Step 2: Update SKILL.md (15 minutes)

**Files to edit:**
- `plugins/productivity-suite/skills/note-taking/SKILL.md`

**Changes:**
1. Line 19-20: Update directory references
2. Line 34: Fix OneDrive path examples
3. Line 222: Change "hooks" → "operations"
4. Lines 224-231: Update script paths
5. Line 338: Replace `cp` with `migrate` command
6. Lines 401-402: Update troubleshooting commands
7. Lines 414-415: Update reindex commands
8. Line 422: Replace `rm` with `clean-index` command

### Step 3: Update CLAUDE.md (5 minutes)

**File:** `CLAUDE.md`

**Changes:**
1. Line 24: Update directory structure diagram
2. Line 122: Update "Key File Paths Reference"
3. Line 179: Update development command examples

### Step 4: Update README.md (5 minutes)

**File:** `README.md`

**Search and replace:**
- `hooks/notes_manager.py` → `scripts/notes_manager.py`
- Verify all command examples use correct path

### Step 5: Enhance notes_manager.py (30 minutes)

**File:** `plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py`

**Changes:**

1. **Line 31 - Add path normalization:**
```python
NOTES_DIR = Path(os.environ.get('NOTES_DIR', DEFAULT_NOTES_DIR)).expanduser().resolve()
```

2. **After line 115 - Add clean_index command:**
```python
def clean_index() -> Dict:
    """Safely remove and rebuild search index."""
    index_path = NOTES_DIR / '.index.json'

    try:
        if index_path.exists():
            index_path.unlink()
            return reindex()
        else:
            return {
                'status': 'success',
                'message': 'No index to clean. Building fresh index.',
                **reindex()
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to clean index: {str(e)}'
        }
```

3. **After line 240 - Add validate command:**
```python
def validate() -> Dict:
    """Check all note files for issues."""
    issues = []
    files_checked = 0

    try:
        for year_dir in sorted(NOTES_DIR.glob('[0-9]*')):
            if not year_dir.is_dir():
                continue

            for note_file in sorted(year_dir.glob('*.md')):
                files_checked += 1

                try:
                    content = note_file.read_text(encoding='utf-8')

                    # Check for empty files
                    if not content.strip():
                        issues.append({
                            'file': note_file.name,
                            'issue': 'Empty file',
                            'severity': 'warning'
                        })

                    # Check for proper heading format
                    if not content.startswith('#'):
                        issues.append({
                            'file': note_file.name,
                            'issue': 'No top-level heading',
                            'severity': 'info'
                        })

                except UnicodeDecodeError:
                    issues.append({
                        'file': note_file.name,
                        'issue': 'Not valid UTF-8',
                        'severity': 'error'
                    })
                except Exception as e:
                    issues.append({
                        'file': note_file.name,
                        'issue': str(e),
                        'severity': 'error'
                    })

        return {
            'status': 'success',
            'files_checked': files_checked,
            'issues_found': len(issues),
            'issues': issues
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Validation failed: {str(e)}'
        }
```

4. **After line 290 - Add migrate command:**
```python
def migrate(source_dir: str) -> Dict:
    """Import existing markdown files with validation and indexing."""
    try:
        source = Path(source_dir).expanduser().resolve()

        if not source.exists():
            return {
                'status': 'error',
                'message': f'Source directory not found: {source}'
            }

        if not source.is_dir():
            return {
                'status': 'error',
                'message': f'Source path is not a directory: {source}'
            }

        imported = []
        skipped = []
        errors = []

        for md_file in source.glob('**/*.md'):
            try:
                # Skip hidden files and index
                if md_file.name.startswith('.') or md_file.name == '.index.json':
                    skipped.append(str(md_file.name))
                    continue

                # Read with UTF-8
                content = md_file.read_text(encoding='utf-8')

                if not content.strip():
                    skipped.append(f"{md_file.name} (empty)")
                    continue

                # Use file modification time to determine target year/month
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                year_dir = NOTES_DIR / str(mtime.year)
                year_dir.mkdir(parents=True, exist_ok=True)

                month_name = mtime.strftime('%B')
                month_file = year_dir / f"{mtime.month:02d}-{month_name}.md"

                # Append with separator if file exists
                mode = 'a' if month_file.exists() else 'w'
                with open(month_file, mode, encoding='utf-8') as f:
                    if mode == 'a':
                        f.write('\n\n')
                    f.write(content)
                    if not content.endswith('\n'):
                        f.write('\n')

                imported.append({
                    'source': md_file.name,
                    'destination': f"{mtime.year}/{month_file.name}"
                })

            except Exception as e:
                errors.append({
                    'file': md_file.name,
                    'error': str(e)
                })

        # Rebuild index after migration
        reindex_result = reindex()

        return {
            'status': 'success' if not errors else 'partial',
            'imported': len(imported),
            'skipped': len(skipped),
            'errors': len(errors),
            'details': {
                'imported_files': imported,
                'skipped_files': skipped,
                'errors': errors
            },
            'index_rebuilt': reindex_result.get('status') == 'success'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Migration failed: {str(e)}'
        }
```

5. **Update get_info() - Add OneDrive detection:**
```python
def get_info() -> Dict:
    """Return information about notes directory and setup."""
    onedrive_path = Path.home() / 'OneDrive' / 'Documents'

    return {
        'status': 'success',
        'notes_dir': str(NOTES_DIR.resolve()),
        'notes_dir_exists': NOTES_DIR.exists(),
        'notes_dir_is_writable': os.access(NOTES_DIR, os.W_OK),
        'onedrive_detected': onedrive_path.exists(),
        'using_onedrive': str(NOTES_DIR).startswith(str(onedrive_path)),
        'platform': sys.platform,
        'python_version': sys.version
    }
```

6. **Update main() to handle new commands:**
```python
def main():
    try:
        input_data = json.loads(sys.stdin.read())
        command = input_data.get('command')

        if command == 'add':
            result = add_note(input_data['heading'], input_data['content'])
        elif command == 'search':
            result = search_notes(input_data['query'], input_data.get('limit', 10))
        elif command == 'append':
            result = append_to_note(input_data['search_term'], input_data['content'])
        elif command == 'reindex':
            result = reindex()
        elif command == 'stats':
            result = get_stats()
        elif command == 'info':
            result = get_info()
        elif command == 'clean-index':  # NEW
            result = clean_index()
        elif command == 'validate':     # NEW
            result = validate()
        elif command == 'migrate':      # NEW
            result = migrate(input_data['source_dir'])
        else:
            result = {
                'status': 'error',
                'message': f'Unknown command: {command}'
            }

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': str(e)
        }, indent=2))
        sys.exit(1)
```

### Step 6: Testing (30 minutes)

**Create test script:** `tests/test-scripts-migration.sh`

```bash
#!/bin/bash

echo "Testing notes_manager.py after migration..."

SCRIPT="plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py"

# Test 1: Info command
echo "Test 1: Info command"
echo '{"command":"info"}' | python "$SCRIPT"

# Test 2: Validate command
echo "Test 2: Validate command"
echo '{"command":"validate"}' | python "$SCRIPT"

# Test 3: Clean-index command
echo "Test 3: Clean-index command"
echo '{"command":"clean-index"}' | python "$SCRIPT"

# Test 4: Stats command
echo "Test 4: Stats command (should work as before)"
echo '{"command":"stats"}' | python "$SCRIPT"

# Test 5: Custom NOTES_DIR
echo "Test 5: Custom NOTES_DIR with tilde expansion"
NOTES_DIR="~/test-notes" python "$SCRIPT" <<< '{"command":"info"}'

echo "All tests completed!"
```

**Run tests:**
```bash
chmod +x tests/test-scripts-migration.sh
./tests/test-scripts-migration.sh
```

### Step 7: Update Distribution ZIP (5 minutes)

```bash
# Regenerate ZIP with new structure
python scripts/create-skill-zip.py

# Verify contents
unzip -l note-taking-skill.zip | grep scripts
```

### Step 8: Commit Changes (5 minutes)

```bash
git add .
git commit -m "Rename hooks/ to scripts/ and enhance notes_manager.py

- Rename hooks/ to scripts/ to align with Anthropic conventions
- Add clean-index, validate, and migrate commands
- Enhance path normalization with expanduser().resolve()
- Update all documentation references
- Replace direct file operations with script commands
- Add OneDrive detection to get_info()
- Update distribution ZIP

Fixes #[issue_number]"
```

## Success Metrics

### Code Quality
- ✅ All file operations use `notes_manager.py`
- ✅ No direct `cp`, `rm`, or file manipulation in docs
- ✅ Cross-platform path normalization in place
- ✅ UTF-8 encoding explicit everywhere

### User Experience
- ✅ Clear distinction between utility scripts and hooks
- ✅ Consistent with official Anthropic skills
- ✅ Better error messages for path issues
- ✅ OneDrive detection transparent to users

### Testing
- ✅ All existing functionality preserved
- ✅ New commands tested on Windows/macOS/Linux
- ✅ Migration handles edge cases gracefully
- ✅ Validation catches common issues

## Dependencies & Risks

### Dependencies
- None (pure Python standard library)
- No external packages required

### Risks

**Risk 1: Breaking existing user installations**
- **Likelihood:** Low
- **Impact:** Medium
- **Mitigation:**
  - Users install via marketplace (gets latest automatically)
  - Manual installers need to re-run `create-skill-zip.py`
  - Document migration in changelog

**Risk 2: Path issues on Windows**
- **Likelihood:** Very Low
- **Impact:** Medium
- **Mitigation:**
  - OneDrive detection already tested and working
  - `.expanduser().resolve()` handles all edge cases
  - Testing on actual Windows environment

**Risk 3: Migration command data loss**
- **Likelihood:** Very Low
- **Impact:** High
- **Mitigation:**
  - Migration appends, never overwrites
  - Validation before import
  - Clear error messages
  - Users should backup before migration

## References

### Internal
- Current SKILL.md: `plugins/productivity-suite/skills/note-taking/SKILL.md`
- Current script: `plugins/productivity-suite/skills/note-taking/hooks/notes_manager.py`
- CLAUDE.md conventions: `CLAUDE.md:24,122,179`
- Distribution script: `scripts/create-skill-zip.py`

### External

**Official Anthropic Skills:**
- skill-creator: https://github.com/anthropics/skills/tree/main/skill-creator
  - Uses `scripts/` directory (not `hooks/`)
  - Contains: `init_skill.py`, `package_skill.py`, `quick_validate.py`
- document-skills/pdf: https://github.com/anthropics/skills/tree/main/document-skills/pdf
  - Uses `scripts/` directory
  - 8+ utility scripts for PDF operations

**Claude Code Documentation:**
- Hooks Reference: https://code.claude.com/docs/en/hooks
  - Defines hooks as `.claude/settings.json` event callbacks
  - NOT the same as utility scripts
- Skills Structure: https://github.com/anthropics/skills/blob/main/agent_skills_spec.md
  - Official directory structure uses `scripts/`

**Research Documents:**
- Cross-platform paths: `docs/research-cross-platform-paths.md`
- Hooks vs scripts: `docs/research-hooks-vs-utility-scripts.md`
- Analysis document: `docs/analysis-notes-manager-issues.md`

## Visual Aid: Before/After Structure

```
BEFORE (Incorrect):
note-taking/
├── SKILL.md
├── hooks/                    ❌ Misleading name
│   └── notes_manager.py
├── templates/
└── examples/

AFTER (Correct):
note-taking/
├── SKILL.md
├── scripts/                  ✅ Clear, conventional
│   └── notes_manager.py
├── templates/
└── examples/
```

## Implementation Checklist

### Pre-Implementation
- [x] Research completed (repository, best practices, framework)
- [x] Issues documented with specific line numbers
- [x] Migration plan validated
- [ ] Windows environment available for testing

### Development
- [ ] Rename `hooks/` to `scripts/` using `git mv`
- [ ] Update SKILL.md (13 references)
- [ ] Update CLAUDE.md (3 references)
- [ ] Update README.md (all references)
- [ ] Add `.expanduser().resolve()` to NOTES_DIR
- [ ] Implement `clean-index` command
- [ ] Implement `validate` command
- [ ] Implement `migrate` command
- [ ] Enhance `get_info()` with OneDrive detection
- [ ] Update `main()` command dispatcher

### Testing
- [ ] Test existing commands (add, search, append, reindex, stats, info)
- [ ] Test new `clean-index` command
- [ ] Test new `validate` command
- [ ] Test new `migrate` command with sample files
- [ ] Test custom NOTES_DIR with tilde (`~/custom`)
- [ ] Test on Windows (with OneDrive)
- [ ] Test on Windows (without OneDrive)
- [ ] Test on macOS
- [ ] Test on Linux (if available)

### Documentation
- [ ] Replace all `cp` examples with `migrate` command
- [ ] Replace all `rm` examples with `clean-index` command
- [ ] Update all script path references
- [ ] Change "hooks" terminology to "scripts" or "operations"
- [ ] Add migration guide in SKILL.md
- [ ] Document new commands in SKILL.md
- [ ] Update troubleshooting section

### Distribution
- [ ] Regenerate ZIP: `python scripts/create-skill-zip.py`
- [ ] Verify ZIP contains `scripts/` not `hooks/`
- [ ] Test ZIP installation on fresh environment
- [ ] Update marketplace listing if needed

### Finalization
- [ ] Commit with descriptive message
- [ ] Create PR linking this issue
- [ ] Update changelog
- [ ] Tag release (if warranted)

---

**Estimated Total Effort:** 90-120 minutes

**Priority:** High (addresses cross-platform compatibility and convention alignment)

**Complexity:** Medium (mostly renaming and documentation, some new code)

**Impact:** High (affects all users, improves cross-platform experience)
