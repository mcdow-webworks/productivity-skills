# Implementation Plan: Dual-Mode Skills (Claude Code + Claude Desktop)

**Date:** 2025-11-20
**Purpose:** Step-by-step plan to enable skills that work in both Claude Code (local) and Claude Desktop (remote via MCP)
**Status:** Ready for implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Notes Manager Refactoring](#phase-1-notes-manager-refactoring)
3. [Phase 2: MCP Server Implementation](#phase-2-mcp-server-implementation)
4. [Phase 3: Testing and Validation](#phase-3-testing-and-validation)
5. [Phase 4: Documentation Updates](#phase-4-documentation-updates)
6. [Phase 5: Future Skills Pattern](#phase-5-future-skills-pattern)
7. [Success Criteria](#success-criteria)
8. [Timeline and Dependencies](#timeline-and-dependencies)

---

## Overview

### Goal

Enable the note-taking skill (and future skills) to work seamlessly in:
- **Claude Code** (CLI) - Direct script execution via bash
- **Claude Desktop** (Web/App) - Remote execution via MCP server

### Strategy

1. **Refactor** existing `notes_manager.py` to separate pure logic from I/O
2. **Create** MCP server wrapper (`notes_mcp_server.py`)
3. **Maintain** existing JSON stdin interface for Claude Code compatibility
4. **Test** both execution modes independently
5. **Document** setup for both environments

### Key Technologies

- **FastMCP** - Python framework for MCP servers
- **stdio transport** - Secure local communication (no authentication needed)
- **Dual-mode detection** - Environment variables to identify execution context

---

## Phase 1: Notes Manager Refactoring

### 1.1 Extract Core Logic Class

**Objective:** Separate pure business logic from I/O operations

**File:** `plugins/productivity-suite/skills/note-taking/scripts/notes_manager.py`

**Changes:**

1. Create `NotesManager` class with pure methods:
   ```python
   class NotesManager:
       """Core notes management logic (I/O agnostic)."""

       def __init__(self, notes_dir: Optional[str] = None):
           """Initialize with optional notes directory override."""
           self.notes_dir = self._resolve_notes_dir(notes_dir)
           self.index_file = self.notes_dir / '.index.json'

       def _resolve_notes_dir(self, notes_dir: Optional[str]) -> Path:
           """Resolve notes directory with priority: param > env > default."""
           if notes_dir:
               return Path(notes_dir).expanduser().resolve()

           env_dir = os.environ.get('NOTES_DIR')
           if env_dir:
               return Path(env_dir).expanduser().resolve()

           return get_default_notes_dir()

       def add_note(self, heading: str, content: str, category: Optional[str] = None) -> dict:
           """Add a new note entry to current month's file."""
           # Existing logic from add_note() function
           # Returns: {'status': 'success', 'file': '...', 'heading': '...'}

       def search_notes(self, query: str, max_results: int = 10) -> dict:
           """Search for notes matching query across all files."""
           # Existing logic from search_notes() function
           # Returns: {'status': 'success', 'results': [...], 'count': N}

       def append_to_entry(self, search_term: str, new_content: str) -> dict:
           """Find an entry and append content to it."""
           # Existing logic from append_to_entry() function
           # Returns: {'status': 'success', 'heading': '...', 'file': '...'}

       def update_index(self) -> dict:
           """Rebuild the search index from all markdown files."""
           # Existing logic from update_index() function
           # Returns: {'status': 'success', 'total_files': N, 'total_entries': N}

       def get_stats(self) -> dict:
           """Get statistics about the notes system."""
           # Existing logic from get_stats() function

       def get_info(self) -> dict:
           """Get information about notes directory and configuration."""
           # Existing logic from get_info() function

       def validate(self) -> dict:
           """Check all note files for issues."""
           # Existing logic from validate() function

       def migrate(self, source_dir: str) -> dict:
           """Import existing markdown files."""
           # Existing logic from migrate() function

       def clean_index(self) -> dict:
           """Safely remove and rebuild search index."""
           # Existing logic from clean_index() function
   ```

2. Keep existing module-level helper functions:
   - `get_default_notes_dir()`
   - `get_current_month_file()` (move to class method)
   - `extract_entries()`
   - `extract_date_from_file()`
   - `calculate_relevance()`

3. Maintain backward compatibility with CLI interface:
   ```python
   def main():
       """Main entry point for CLI (Claude Code)."""
       # Read command from stdin or command line
       if not sys.stdin.isatty():
           try:
               data = json.load(sys.stdin)
           except json.JSONDecodeError:
               data = {'command': 'help'}
       elif len(sys.argv) > 1:
           data = {'command': sys.argv[1]}
       else:
           data = {'command': 'help'}

       # Initialize manager
       manager = NotesManager()

       # Execute command (unchanged)
       command = data.get('command', 'help')

       if command == 'add':
           result = manager.add_note(
               data.get('heading', 'Untitled'),
               data.get('content', ''),
               data.get('category')
           )
       elif command == 'search':
           result = manager.search_notes(
               data.get('query', ''),
               data.get('max_results', 10)
           )
       # ... (rest of commands)

       # Output result as JSON
       print(json.dumps(result, indent=2))
       return 0

   if __name__ == '__main__':
       sys.exit(main())
   ```

**Testing:**
```bash
# Verify CLI still works
cd plugins/productivity-suite/skills/note-taking
echo '{"command":"info"}' | python scripts/notes_manager.py
echo '{"command":"add","heading":"Test","content":"Test"}' | python scripts/notes_manager.py
```

**Success Criteria:**
- ✅ All existing CLI commands still work
- ✅ NotesManager class has no direct stdin/stdout dependencies
- ✅ All methods return structured dicts (status, message, data)

---

## Phase 2: MCP Server Implementation

### 2.1 Create MCP Server Wrapper

**File:** `plugins/productivity-suite/skills/note-taking/scripts/notes_mcp_server.py`

```python
#!/usr/bin/env python3
"""
MCP Server for Note-Taking Skill
Enables Claude Desktop to execute note operations via Model Context Protocol
"""

import sys
import logging
from pathlib import Path
from fastmcp import FastMCP

# Import core logic
from notes_manager import NotesManager

# Configure logging to stderr (critical for MCP)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # NEVER log to stdout!
)

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(name="notes-manager")

# Initialize notes manager
manager = NotesManager()

@mcp.tool()
def add_note(heading: str, content: str, category: str = None) -> dict:
    """
    Add a new note entry to the current month's file.

    Args:
        heading: Note heading in "Category - Description" format
        content: Full note content with markdown support
        category: Optional explicit category override

    Returns:
        dict with status, file, heading, and path
    """
    try:
        logger.info(f"Adding note: {heading}")
        result = manager.add_note(heading, content, category)
        logger.info(f"Note added successfully: {result.get('file')}")
        return result
    except Exception as e:
        logger.exception("Error adding note")
        return {
            'status': 'error',
            'message': str(e)
        }

@mcp.tool()
def search_notes(query: str, max_results: int = 10) -> dict:
    """
    Search for notes matching query across all files.

    Args:
        query: Search terms to find in headings and content
        max_results: Maximum number of results to return (default: 10)

    Returns:
        dict with status, results list, and count
    """
    try:
        logger.info(f"Searching notes: {query}")
        result = manager.search_notes(query, max_results)
        logger.info(f"Found {result.get('count', 0)} results")
        return result
    except Exception as e:
        logger.exception("Error searching notes")
        return {
            'status': 'error',
            'message': str(e),
            'results': [],
            'count': 0
        }

@mcp.tool()
def append_to_note(search_term: str, content: str) -> dict:
    """
    Find a note and append content to it with timestamp.

    Args:
        search_term: Term to find the target note (requires relevance ≥50)
        content: Content to append (timestamp added automatically)

    Returns:
        dict with status, matched heading, and alternatives if ambiguous
    """
    try:
        logger.info(f"Appending to note: {search_term}")
        result = manager.append_to_entry(search_term, content)

        if result.get('status') == 'success':
            logger.info(f"Appended to: {result.get('heading')}")
        else:
            logger.warning(f"Append failed: {result.get('message')}")

        return result
    except Exception as e:
        logger.exception("Error appending to note")
        return {
            'status': 'error',
            'message': str(e)
        }

@mcp.tool()
def get_stats() -> dict:
    """
    Get statistics about the notes system.

    Returns:
        dict with total entries, files, categories, and top keywords
    """
    try:
        logger.info("Getting statistics")
        result = manager.get_stats()
        return result
    except Exception as e:
        logger.exception("Error getting statistics")
        return {
            'status': 'error',
            'message': str(e)
        }

@mcp.tool()
def reindex_notes() -> dict:
    """
    Rebuild the search index from all markdown files.

    Returns:
        dict with status, total files, and total entries
    """
    try:
        logger.info("Reindexing notes")
        result = manager.update_index()
        logger.info(f"Reindexed {result.get('total_entries')} entries")
        return result
    except Exception as e:
        logger.exception("Error reindexing")
        return {
            'status': 'error',
            'message': str(e)
        }

@mcp.tool()
def get_info() -> dict:
    """
    Get information about notes directory and configuration.

    Returns:
        dict with paths, directory info, and system details
    """
    try:
        logger.info("Getting system info")
        result = manager.get_info()
        return result
    except Exception as e:
        logger.exception("Error getting info")
        return {
            'status': 'error',
            'message': str(e)
        }

@mcp.tool()
def validate_notes() -> dict:
    """
    Check all note files for issues.

    Returns:
        dict with files checked and list of issues found
    """
    try:
        logger.info("Validating notes")
        result = manager.validate()
        logger.info(f"Validated {result.get('files_checked')} files")
        return result
    except Exception as e:
        logger.exception("Error validating")
        return {
            'status': 'error',
            'message': str(e)
        }

@mcp.tool()
def migrate_notes(source_dir: str) -> dict:
    """
    Import existing markdown files from a directory.

    ⚠️ SECURITY: Only migrate from trusted directories.

    Args:
        source_dir: Absolute path to directory with markdown files

    Returns:
        dict with imported count, skipped count, and errors
    """
    try:
        logger.info(f"Migrating notes from: {source_dir}")
        result = manager.migrate(source_dir)
        logger.info(f"Migration complete: {result.get('imported')} imported")
        return result
    except Exception as e:
        logger.exception("Error migrating")
        return {
            'status': 'error',
            'message': str(e)
        }

if __name__ == "__main__":
    logger.info("Starting notes MCP server")
    mcp.run()  # stdio transport by default
```

### 2.2 Install Dependencies

**Requirements file:** `plugins/productivity-suite/skills/note-taking/requirements.txt`

```
fastmcp>=0.1.0
```

**Installation:**
```bash
cd plugins/productivity-suite/skills/note-taking
pip install -r requirements.txt
```

### 2.3 Configure Claude Desktop

**File:** `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "notes-manager": {
      "command": "python",
      "args": [
        "-m", "fastmcp", "run",
        "C:\\Projects\\productivity-skills\\plugins\\productivity-suite\\skills\\note-taking\\scripts\\notes_mcp_server.py"
      ],
      "env": {
        "MCP_SERVER_MODE": "true",
        "NOTES_DIR": "C:\\Users\\mcdow\\OneDrive\\Documents\\notes"
      }
    }
  }
}
```

**Notes:**
- Use absolute paths (no relative paths)
- Use forward slashes in paths even on Windows (`C:/Projects/...` or double backslashes `C:\\Projects\\...`)
- Restart Claude Desktop after config changes

---

## Phase 3: Testing and Validation

### 3.1 Unit Tests

**File:** `plugins/productivity-suite/skills/note-taking/tests/test_notes_manager.py`

```python
import pytest
from pathlib import Path
import tempfile
import shutil
from scripts.notes_manager import NotesManager

@pytest.fixture
def temp_notes_dir():
    """Create temporary notes directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_add_note(temp_notes_dir):
    """Test adding a note."""
    manager = NotesManager(notes_dir=temp_notes_dir)
    result = manager.add_note("Test - Note", "Test content")

    assert result['status'] == 'success'
    assert 'file' in result
    assert result['heading'] == 'Test - Note'

def test_search_notes(temp_notes_dir):
    """Test searching notes."""
    manager = NotesManager(notes_dir=temp_notes_dir)

    # Add test notes
    manager.add_note("Work - Feature X", "Implemented feature X")
    manager.add_note("Learning - Python", "Learned about decorators")

    # Search
    result = manager.search_notes("feature")

    assert result['status'] == 'success'
    assert result['count'] >= 1
    assert any('Feature X' in r['heading'] for r in result['results'])

def test_append_to_entry(temp_notes_dir):
    """Test appending to existing note."""
    manager = NotesManager(notes_dir=temp_notes_dir)

    # Add initial note
    manager.add_note("Work - Bug Fix", "Fixed initial bug")

    # Append
    result = manager.append_to_entry("Bug Fix", "Added unit test")

    assert result['status'] == 'success'
    assert 'Bug Fix' in result['heading']

def test_get_stats(temp_notes_dir):
    """Test getting statistics."""
    manager = NotesManager(notes_dir=temp_notes_dir)

    # Add notes
    manager.add_note("Work - Task 1", "Content 1")
    manager.add_note("Learning - Topic 2", "Content 2")

    result = manager.get_stats()

    assert result['status'] == 'success'
    assert result['total_entries'] >= 2
```

**Run tests:**
```bash
pytest tests/test_notes_manager.py -v
```

### 3.2 MCP Inspector Testing

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test MCP server
cd plugins/productivity-suite/skills/note-taking/scripts
mcp-inspector python notes_mcp_server.py

# Or with FastMCP
mcp-inspector fastmcp run notes_mcp_server.py
```

**Test checklist:**
- ✅ Server starts without errors
- ✅ All 8 tools are discovered
- ✅ Tool schemas are correct
- ✅ add_note works
- ✅ search_notes works
- ✅ append_to_note works
- ✅ Error handling returns proper status

### 3.3 Claude Desktop Integration Testing

**Steps:**

1. Restart Claude Desktop
2. Open new conversation
3. Test natural language triggers:
   - "Note that I am testing the MCP server"
   - "Search my notes for testing"
   - "What are my note statistics?"
   - "Add to my testing note: MCP server works!"

**Validation:**
- ✅ Notes appear in `~/OneDrive/Documents/notes/`
- ✅ Search returns correct results
- ✅ Updates append to correct entries
- ✅ No errors in Claude Desktop console (View > Developer > Developer Tools)

### 3.4 Claude Code Compatibility Testing

**Steps:**

1. Test CLI interface still works:
   ```bash
   cd plugins/productivity-suite/skills/note-taking
   echo '{"command":"add","heading":"CLI Test","content":"Testing CLI"}' | python scripts/notes_manager.py
   ```

2. Test skill in Claude Code:
   ```bash
   # Open Claude Code
   # Ensure skill is configured
   # Test: "Note that I am testing Claude Code compatibility"
   ```

**Validation:**
- ✅ CLI commands work unchanged
- ✅ Claude Code skill still uses bash + stdin interface
- ✅ Both modes write to same notes directory
- ✅ Search works across notes created by both modes

---

## Phase 4: Documentation Updates

### 4.1 Update SKILL.md

**File:** `plugins/productivity-suite/skills/note-taking/SKILL.md`

Add section after line 330:

```markdown
## Dual-Mode Execution

This skill supports two execution modes:

### Claude Code (CLI) - Direct Execution

The skill uses bash commands to call the Python script directly:

```bash
echo '{"command":"add",...}' | python3 ${CLAUDE_SKILL_ROOT}/scripts/notes_manager.py
```

**Advantages:**
- Fast local execution
- No additional setup
- Direct filesystem access

**Requirements:**
- Python 3.7+
- Claude Code installed

### Claude Desktop (Web/App) - MCP Server

The skill routes through an MCP (Model Context Protocol) server that bridges Claude Desktop's remote environment to your local filesystem.

**Advantages:**
- Works in web and desktop app
- Same underlying logic as CLI
- Secure local execution (stdio transport)

**Requirements:**
- Python 3.7+
- FastMCP installed: `pip install fastmcp`
- MCP server configured (see setup below)

### Setup for Claude Desktop

1. **Install FastMCP:**
   ```bash
   pip install fastmcp
   ```

2. **Configure claude_desktop_config.json:**

   **Location:**
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

   **Configuration:**
   ```json
   {
     "mcpServers": {
       "notes-manager": {
         "command": "python",
         "args": [
           "-m", "fastmcp", "run",
           "C:/path/to/productivity-skills/plugins/productivity-suite/skills/note-taking/scripts/notes_mcp_server.py"
         ],
         "env": {
           "MCP_SERVER_MODE": "true",
           "NOTES_DIR": "C:/Users/username/OneDrive/Documents/notes"
         }
       }
     }
   }
   ```

   **Important:**
   - Use **absolute paths** (not relative)
   - Use forward slashes or double backslashes in Windows paths
   - Set `NOTES_DIR` to match your notes location

3. **Restart Claude Desktop**

4. **Test:**
   - Open new conversation
   - Try: "Note that I am testing the MCP server"
   - Check your notes directory for the new entry

### Troubleshooting

**Notes not appearing:**
1. Check Claude Desktop console: View > Developer > Developer Tools
2. Look for MCP server errors in stderr
3. Verify `NOTES_DIR` path is correct
4. Ensure FastMCP is installed: `pip show fastmcp`

**"Tool not found" errors:**
1. Restart Claude Desktop
2. Check config file syntax (valid JSON)
3. Verify absolute paths in config

**Permission errors:**
1. Ensure notes directory exists and is writable
2. Check Python has permissions to create files
```

### 4.2 Update README.md

**File:** `README.md`

Update installation section to include both modes:

```markdown
## Installation

### Claude Code (Recommended for Power Users)

```bash
# Install from Claude Code marketplace
/plugin marketplace add mcdow-webworks/productivity-skills
/plugin install productivity-suite@productivity-skills
```

Or manual installation:

```bash
git clone https://github.com/mcdow-webworks/productivity-skills.git
cp -r plugins/productivity-suite "$APPDATA/Claude/plugins/"
```

### Claude Desktop (Web & App)

The note-taking skill requires an MCP (Model Context Protocol) server to bridge Claude Desktop's remote environment to your local filesystem.

**Setup Steps:**

1. **Install dependencies:**
   ```bash
   cd productivity-skills/plugins/productivity-suite/skills/note-taking
   pip install -r requirements.txt
   ```

2. **Configure MCP server:**

   Edit `claude_desktop_config.json`:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

   Add:
   ```json
   {
     "mcpServers": {
       "notes-manager": {
         "command": "python",
         "args": [
           "-m", "fastmcp", "run",
           "/absolute/path/to/skills/note-taking/scripts/notes_mcp_server.py"
         ],
         "env": {
           "NOTES_DIR": "/path/to/your/notes"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

**See full documentation:** [SKILL.md](plugins/productivity-suite/skills/note-taking/SKILL.md#dual-mode-execution)
```

### 4.3 Update CLAUDE.md

**File:** `CLAUDE.md`

Add section about MCP implementation:

```markdown
## MCP Server Implementation

As of 2025-11-20, the note-taking skill supports dual-mode execution:

**Claude Code:** Direct bash execution via JSON stdin interface
**Claude Desktop:** MCP server bridges remote environment to local filesystem

### Key Implementation Details

**Architecture:**
- Core logic in `NotesManager` class (I/O agnostic)
- CLI interface maintained for Claude Code compatibility
- MCP wrapper exposes 8 separate tools for Claude Desktop
- Both modes use same underlying logic and data

**MCP Server Design:**
- Uses **FastMCP** framework (minimal boilerplate)
- **stdio transport** for security (no network, no auth)
- Individual tools per operation (better UX than unified command)
- All logging to stderr (stdout reserved for JSON-RPC)

**Files:**
- `notes_manager.py` - Core logic + CLI interface
- `notes_mcp_server.py` - MCP wrapper
- `requirements.txt` - FastMCP dependency

**Configuration:**
- `claude_desktop_config.json` - MCP server registration
- `NOTES_DIR` environment variable - Notes location override

### For Future Skills

When creating new skills that need local program execution:

1. **Extract pure logic** to class (no I/O specifics)
2. **Maintain CLI interface** for Claude Code
3. **Create MCP wrapper** with individual tools
4. **Test both modes** independently
5. **Document setup** for both environments

**Pattern applies to:**
- ePublisher AutoMap integration (build tools)
- Any command-line program wrapping
- Local filesystem operations
- Database access

**See research:** `.github/research/research-mcp-server-implementation.md`
```

---

## Phase 5: Future Skills Pattern

### 5.1 Template for ePublisher AutoMap

**File:** `plugins/productivity-suite/skills/epublisher-automap/scripts/automap_mcp_server.py`

```python
#!/usr/bin/env python3
"""
MCP Server for ePublisher AutoMap Skill
Wraps ePublisher AutoMap executable for Claude Desktop
"""

import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

mcp = FastMCP(name="epublisher-automap")

# Configuration
AUTOMAP_EXECUTABLE = Path(os.environ.get('AUTOMAP_PATH', 'ePublisher'))

@mcp.tool()
def build_documentation(
    project_file: str,
    output_dir: str,
    format: str = "webhelp",
    timeout: int = 300
) -> dict:
    """
    Build documentation using ePublisher AutoMap.

    Args:
        project_file: Absolute path to .wwproject file
        output_dir: Absolute path for output
        format: Output format (webhelp, pdf, etc.)
        timeout: Build timeout in seconds (default: 300)

    Returns:
        dict with status, output_dir, and stdout/stderr
    """
    try:
        # Validate inputs
        project_path = Path(project_file).resolve()
        if not project_path.exists():
            return {
                'status': 'error',
                'message': f'Project file not found: {project_file}'
            }

        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Building {project_file} to {output_dir}")

        # Execute AutoMap
        result = subprocess.run(
            [
                str(AUTOMAP_EXECUTABLE),
                'automap',
                str(project_path),
                '--output', str(output_path),
                '--format', format
            ],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            logger.info("Build completed successfully")
            return {
                'status': 'success',
                'output_dir': str(output_path),
                'stdout': result.stdout,
                'format': format
            }
        else:
            logger.error(f"Build failed: {result.stderr}")
            return {
                'status': 'error',
                'message': 'Build failed',
                'stderr': result.stderr,
                'stdout': result.stdout
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Build timed out after {timeout}s")
        return {
            'status': 'error',
            'message': f'Build timed out after {timeout} seconds'
        }
    except Exception as e:
        logger.exception("Unexpected error during build")
        return {
            'status': 'error',
            'message': str(e)
        }

@mcp.tool()
def validate_project(project_file: str) -> dict:
    """
    Validate an ePublisher project file.

    Args:
        project_file: Absolute path to .wwproject file

    Returns:
        dict with validation status and issues
    """
    try:
        project_path = Path(project_file).resolve()
        if not project_path.exists():
            return {
                'status': 'error',
                'message': f'Project file not found: {project_file}'
            }

        logger.info(f"Validating {project_file}")

        result = subprocess.run(
            [str(AUTOMAP_EXECUTABLE), 'validate', str(project_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            'status': 'success' if result.returncode == 0 else 'warning',
            'valid': result.returncode == 0,
            'output': result.stdout,
            'issues': result.stderr if result.stderr else None
        }

    except Exception as e:
        logger.exception("Error validating project")
        return {
            'status': 'error',
            'message': str(e)
        }

@mcp.tool()
def list_formats() -> dict:
    """
    List available output formats.

    Returns:
        dict with available formats
    """
    return {
        'status': 'success',
        'formats': [
            'webhelp',
            'pdf',
            'eclipse',
            'word',
            'chm'
        ]
    }

if __name__ == "__main__":
    logger.info("Starting ePublisher AutoMap MCP server")
    mcp.run()
```

### 5.2 General Pattern Summary

**For any future skill that wraps local programs:**

1. **Core requirements:**
   - Separate pure logic from I/O
   - CLI interface for Claude Code
   - MCP server for Claude Desktop

2. **MCP implementation:**
   - Use FastMCP framework
   - One tool per operation
   - Validate all inputs (especially file paths)
   - Set appropriate timeouts for long operations
   - Log to stderr only

3. **Error handling:**
   - Try/catch all tool functions
   - Return structured errors (status, message)
   - Log exceptions to stderr
   - Don't expose secrets in error messages

4. **Testing:**
   - Unit test core logic
   - Test with MCP Inspector
   - End-to-end in Claude Desktop
   - Verify CLI still works

5. **Documentation:**
   - Setup for both modes
   - Troubleshooting guide
   - Example usage patterns

---

## Success Criteria

### Functionality
- ✅ Notes can be added from Claude Desktop
- ✅ Search works across all notes
- ✅ Updates append to correct entries
- ✅ All 8 operations work in both modes
- ✅ CLI interface remains unchanged

### Architecture
- ✅ Core logic is I/O agnostic
- ✅ No code duplication between CLI and MCP
- ✅ Both modes use same data directory
- ✅ Index updates work from both modes

### Security
- ✅ Stdio transport (no network)
- ✅ No secrets in logs or errors
- ✅ File path validation
- ✅ Proper error handling

### Documentation
- ✅ Setup guide for both modes
- ✅ Troubleshooting section
- ✅ Clear examples
- ✅ Future skills pattern documented

### Testing
- ✅ Unit tests pass
- ✅ MCP Inspector validation
- ✅ Claude Desktop integration works
- ✅ Claude Code compatibility maintained

---

## Timeline and Dependencies

### Phase 1: Refactoring (2-3 hours)
- Extract NotesManager class
- Maintain CLI compatibility
- Test CLI still works

**Dependencies:** None

### Phase 2: MCP Implementation (2-3 hours)
- Create MCP server wrapper
- Install FastMCP
- Configure Claude Desktop

**Dependencies:** Phase 1 complete

### Phase 3: Testing (2-3 hours)
- Write unit tests
- MCP Inspector validation
- End-to-end testing

**Dependencies:** Phases 1-2 complete

### Phase 4: Documentation (1-2 hours)
- Update SKILL.md
- Update README.md
- Update CLAUDE.md

**Dependencies:** Phases 1-3 complete

### Phase 5: Pattern Documentation (1 hour)
- Document general pattern
- Create ePublisher template
- Research findings summary

**Dependencies:** Phases 1-4 complete

**Total estimated time:** 8-12 hours

---

## Next Steps

1. **Review this plan** - Ensure it aligns with goals
2. **Begin Phase 1** - Refactor notes_manager.py
3. **Test incrementally** - Verify each phase before proceeding
4. **Document learnings** - Add to research as issues arise
5. **Create GitHub issue** - Track implementation progress

**Ready to proceed?** Start with Phase 1: Refactoring notes_manager.py
