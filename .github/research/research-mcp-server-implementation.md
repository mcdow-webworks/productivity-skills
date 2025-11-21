# Research: MCP Server Implementation for Dual-Mode Skills

**Date:** 2025-11-20
**Purpose:** Research how to implement MCP (Model Context Protocol) servers that enable Claude Desktop to execute local programs, enabling skills that work in both Claude Code (local) and Claude Desktop (remote).

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [MCP Architecture Overview](#mcp-architecture-overview)
3. [Implementation Patterns](#implementation-patterns)
4. [Dual-Mode Skill Design](#dual-mode-skill-design)
5. [Notes Manager MCP Implementation](#notes-manager-mcp-implementation)
6. [Security and Best Practices](#security-and-best-practices)
7. [Future Extensibility](#future-extensibility)
8. [Recommendations](#recommendations)
9. [References](#references)

---

## Executive Summary

**Key Finding:** MCP servers provide a standardized bridge between Claude Desktop's remote environment and local machine resources through a simple client-server protocol.

**Core Concept:** MCP is like USB-C for AI applications - a universal protocol for connecting AI models to data sources and tools.

**Implementation Path:**
- Use **FastMCP** (Python) for rapid development with minimal boilerplate
- Expose Python scripts as **tools** (actions) rather than resources (data)
- Deploy via **stdio transport** for local execution (most secure)
- Configure through `claude_desktop_config.json` for automatic server launching

**Dual-Mode Strategy:**
- Skills should detect execution environment (MCP server vs direct execution)
- Fall back gracefully between direct script invocation (Claude Code) and MCP server calls (Claude Desktop)
- Use environment variables for detection (e.g., `MCP_SERVER_MODE`)

---

## MCP Architecture Overview

### Core Components

The MCP architecture consists of three main components:

**1. Hosts**
- Applications like Claude Desktop, IDEs (VS Code), or standalone applications
- Create and manage MCP clients
- Enforce security policies and handle authorization
- Coordinate between different MCP clients

**2. MCP Clients**
- Connectors within hosts that maintain 1:1 stateful sessions with MCP servers
- Implement the client side of the Model Context Protocol
- Handle protocol communication and message routing

**3. MCP Servers**
- Launched by clients to perform desired work
- Can use any languages, tools, or processes needed
- Expose capabilities through tools, resources, and prompts

### Protocol Components

MCP provides three primary interaction types:

**Tools (Model-controlled)**
- Functions that LLMs can call to perform specific actions
- Similar to function calling in other LLM frameworks
- Tools handle actions like creating files, querying databases, calling APIs
- The AI decides when to invoke tools based on user requests

**Resources (Application-controlled)**
- Data sources that LLMs can access (like GET endpoints in REST API)
- Provide data without performing significant computation or side effects
- Consumed by the application itself, not directly by the model
- Examples: file contents, database records, API responses

**Prompts (User-controlled)**
- Predefined instruction templates the server provides
- Conversation starters that guide users on how to use tools
- Save users from guessing the right way to phrase requests
- Standardize how models perform common tasks

### Transport Mechanisms

**Stdio Transport (Recommended for Local)**
- Communication via standard input/output streams
- Server runs as subprocess of the host application
- Most secure option - data never leaves local machine
- No network exposure or attack surface
- No authentication needed (OS-level security)

**HTTP/SSE Transport**
- For remote servers or multi-client scenarios
- Requires authentication and authorization
- Suitable for cloud deployments or shared services

**Desktop Extensions (.mcpb)**
- New packaging format introduced in 2025
- Single-click installation for MCP servers
- Bundles server code and all dependencies
- Simplifies distribution and management

---

## Implementation Patterns

### FastMCP vs Official SDK

**Official Python SDK (`mcp`)**
- Baseline protocol implementation
- More verbose, requires more boilerplate
- Full control over protocol details
- Best for complex, production-critical servers

**FastMCP (`fastmcp`)**
- Extends official SDK with production features
- Minimal boilerplate through decorator-based API
- Automatic schema generation from type hints
- Built-in authentication, testing, and deployment tools
- FastMCP 1.0 was incorporated into official SDK in 2024
- FastMCP 2.0 continues active development with advanced features

**Recommendation:** Use FastMCP for rapid development, especially when wrapping existing Python scripts.

### Basic Server Structure (FastMCP)

```python
from fastmcp import FastMCP

# Initialize server
mcp = FastMCP(name="MyServer", json_response=True)

# Define tools with decorators
@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description for AI to understand when to use."""
    # Implementation
    return result

# Run server (stdio transport by default)
if __name__ == "__main__":
    mcp.run()
```

### Tool Implementation Pattern

```python
@mcp.tool()
async def execute_command(
    command: str,
    timeout: int = 30
) -> dict:
    """
    Execute a local command and return results.

    Args:
        command: Command to execute
        timeout: Maximum execution time in seconds

    Returns:
        Dictionary with stdout, stderr, and return code
    """
    try:
        result = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            result.communicate(),
            timeout=timeout
        )

        return {
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": result.returncode
        }
    except asyncio.TimeoutError:
        return {"error": "Command timed out"}
    except Exception as e:
        return {"error": str(e)}
```

### Wrapping External Scripts

**Pattern 1: Subprocess Execution**

```python
import subprocess
import json

@mcp.tool()
def run_python_script(script_path: str, input_data: dict) -> dict:
    """Run external Python script with JSON I/O."""
    try:
        result = subprocess.run(
            ["python", script_path],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}
```

**Pattern 2: Direct Import (Same Process)**

```python
from pathlib import Path
import sys

# Add script directory to path
script_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(script_dir))

# Import and wrap
from notes_manager import NotesManager

@mcp.tool()
def add_note(heading: str, content: str) -> dict:
    """Add a new note entry."""
    manager = NotesManager()
    return manager.add_note(heading, content)
```

**Trade-offs:**
- **Subprocess:** Better isolation, but slower and more overhead
- **Direct Import:** Faster, but shares memory and state
- **Recommendation:** Use direct import for simple scripts, subprocess for complex or untrusted code

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "notes-manager": {
      "command": "python",
      "args": [
        "-m",
        "fastmcp",
        "run",
        "/absolute/path/to/notes_mcp_server.py"
      ],
      "env": {
        "NOTES_DIR": "/path/to/notes",
        "MCP_SERVER_MODE": "true"
      }
    }
  }
}
```

**Alternative using `uv` (recommended for dependency management):**

```json
{
  "mcpServers": {
    "notes-manager": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/server/directory",
        "run",
        "notes_mcp_server.py"
      ],
      "env": {
        "NOTES_DIR": "/path/to/notes",
        "MCP_SERVER_MODE": "true"
      }
    }
  }
}
```

---

## Dual-Mode Skill Design

### Environment Detection

```python
import os
import sys

def get_execution_mode():
    """Detect whether running in MCP server or direct execution mode."""
    # Check for explicit MCP mode flag
    if os.environ.get("MCP_SERVER_MODE") == "true":
        return "mcp_server"

    # Check for uv subprocess indicators
    if "UV_PYTHON" in os.environ:
        return "mcp_server"

    # Check if stdin is a pipe (indicates subprocess)
    if not sys.stdin.isatty():
        return "mcp_server"

    # Default to direct execution
    return "direct"
```

### Dual-Mode Implementation Pattern

**SKILL.md (skill definition)**

```markdown
---
name: note-taking
description: Manage markdown notes in a searchable second brain system. ALWAYS use when user says "Note that", "Add a note", "What did I note about", or "Search my notes".
---

# Note-Taking Skill

This skill enables Claude to manage your markdown notes.

## Usage

- "Note that Python uses 0-based indexing"
- "What did I note about MCP servers?"
- "Add to the MCP note: FastMCP is recommended"

## Implementation

The skill automatically detects whether it's running in:
- **Claude Code**: Uses direct script execution for fast, local access
- **Claude Desktop**: Routes through MCP server for remote access

No configuration needed - works seamlessly in both environments.
```

**notes_manager.py (refactored for dual-mode)**

```python
#!/usr/bin/env python3
"""
Notes Manager - Dual Mode Support

Can run as:
1. Direct script with JSON stdin/stdout (Claude Code)
2. Imported module (MCP server)
"""

import json
import sys
from pathlib import Path
from typing import Optional

class NotesManager:
    """Core notes management logic."""

    def __init__(self, notes_dir: Optional[str] = None):
        self.notes_dir = Path(notes_dir or os.environ.get(
            "NOTES_DIR",
            Path.home() / "Documents" / "notes"
        ))

    def add_note(self, heading: str, content: str) -> dict:
        """Add a new note entry."""
        # Implementation...
        return {"status": "success", "entry": entry}

    def search_notes(self, query: str, limit: int = 10) -> dict:
        """Search across all notes."""
        # Implementation...
        return {"status": "success", "results": results}

    def append_to_note(self, search_term: str, content: str) -> dict:
        """Append to existing note."""
        # Implementation...
        return {"status": "success", "updated_entry": entry}

def main():
    """CLI interface for direct execution."""
    # Read JSON from stdin
    input_data = json.loads(sys.stdin.read())

    manager = NotesManager()
    command = input_data.get("command")

    # Route to appropriate method
    if command == "add":
        result = manager.add_note(
            input_data["heading"],
            input_data["content"]
        )
    elif command == "search":
        result = manager.search_notes(
            input_data["query"],
            input_data.get("limit", 10)
        )
    elif command == "append":
        result = manager.append_to_note(
            input_data["search_term"],
            input_data["content"]
        )
    else:
        result = {"status": "error", "message": f"Unknown command: {command}"}

    # Output JSON to stdout
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

**notes_mcp_server.py (MCP wrapper)**

```python
#!/usr/bin/env python3
"""MCP Server for Notes Manager."""

from fastmcp import FastMCP
from notes_manager import NotesManager
import os

# Set environment variable for detection
os.environ["MCP_SERVER_MODE"] = "true"

# Initialize FastMCP server
mcp = FastMCP(name="notes-manager")

# Initialize notes manager
manager = NotesManager()

@mcp.tool()
def add_note(heading: str, content: str) -> dict:
    """
    Add a new note entry.

    Args:
        heading: Note heading in format "Category - Brief description"
        content: Note content (supports markdown, code blocks, etc.)

    Returns:
        Dictionary with status and created entry details
    """
    return manager.add_note(heading, content)

@mcp.tool()
def search_notes(query: str, limit: int = 10) -> dict:
    """
    Search across all notes.

    Args:
        query: Search query (searches headings and content)
        limit: Maximum number of results to return

    Returns:
        Dictionary with status and list of matching entries
    """
    return manager.search_notes(query, limit)

@mcp.tool()
def append_to_note(search_term: str, content: str) -> dict:
    """
    Append content to an existing note entry.

    Args:
        search_term: Term to find the note (exact phrase match preferred)
        content: Content to append

    Returns:
        Dictionary with status and updated entry
    """
    return manager.append_to_note(search_term, content)

if __name__ == "__main__":
    mcp.run()
```

### SKILL.md Hook Pattern (Claude Code)

```python
#!/usr/bin/env python3
"""Hook script for note-taking skill in Claude Code."""

import json
import sys
import subprocess
from pathlib import Path

# Get skill root directory
SKILL_ROOT = Path(__file__).parent.parent

def execute_via_script(command: str, **kwargs) -> dict:
    """Execute via direct script invocation."""
    script_path = SKILL_ROOT / "scripts" / "notes_manager.py"

    input_data = {"command": command, **kwargs}

    result = subprocess.run(
        ["python", str(script_path)],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return {"status": "error", "message": result.stderr}

def main():
    # Parse Claude Code's natural language request
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""

    # Simple pattern matching (can be enhanced with NLP)
    if "note that" in user_input.lower() or "add a note" in user_input.lower():
        # Extract heading and content from user_input
        result = execute_via_script("add", heading=heading, content=content)
    elif "search" in user_input.lower() or "what did i note" in user_input.lower():
        result = execute_via_script("search", query=query)
    elif "update" in user_input.lower() or "append" in user_input.lower():
        result = execute_via_script("append", search_term=search_term, content=content)
    else:
        result = {"status": "error", "message": "Could not understand request"}

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

---

## Notes Manager MCP Implementation

### Recommended Approach

**Option A: Expose Individual Commands as Separate Tools** (Recommended)

**Pros:**
- Claude can directly understand available operations
- Better tool discovery and selection
- Clearer schemas and validation
- Easier to extend with new operations

**Cons:**
- More boilerplate (one function per operation)
- Slightly larger server code

**Implementation:**

```python
from fastmcp import FastMCP
from notes_manager import NotesManager

mcp = FastMCP(name="notes-manager")
manager = NotesManager()

@mcp.tool()
def add_note(heading: str, content: str) -> dict:
    """Add a new note entry with automatic timestamp."""
    return manager.add_note(heading, content)

@mcp.tool()
def search_notes(query: str, limit: int = 10) -> dict:
    """Search across all notes with relevance scoring."""
    return manager.search_notes(query, limit)

@mcp.tool()
def append_to_note(search_term: str, content: str) -> dict:
    """Append to existing note (requires minimum relevance score ≥50)."""
    return manager.append_to_note(search_term, content)

@mcp.tool()
def get_stats() -> dict:
    """Get statistics about notes (total entries, recent activity)."""
    return manager.get_stats()

@mcp.tool()
def reindex_notes() -> dict:
    """Rebuild search index (use if notes modified externally)."""
    return manager.reindex()
```

**Option B: Single Unified Tool with Command Parameter**

**Pros:**
- Less code duplication
- Mirrors existing JSON stdin interface
- Easier to maintain parity with direct execution mode

**Cons:**
- Claude must specify command parameter
- Less discoverable (all operations under one tool)
- Schema less specific

**Implementation:**

```python
@mcp.tool()
def notes_command(command: str, **kwargs) -> dict:
    """
    Execute notes management command.

    Args:
        command: One of: add, search, append, stats, reindex
        **kwargs: Command-specific parameters

    Commands:
        - add: heading, content
        - search: query, limit (optional)
        - append: search_term, content
        - stats: (no additional params)
        - reindex: (no additional params)
    """
    if command == "add":
        return manager.add_note(kwargs["heading"], kwargs["content"])
    elif command == "search":
        return manager.search_notes(kwargs["query"], kwargs.get("limit", 10))
    # ... etc
```

**Recommendation:** Use Option A (individual tools) for better UX and discoverability.

### File System Path Handling

```python
from pathlib import Path
import os

class NotesManager:
    def __init__(self, notes_dir: Optional[str] = None):
        # Priority: explicit parameter > env var > default
        if notes_dir:
            self.notes_dir = Path(notes_dir)
        elif "NOTES_DIR" in os.environ:
            self.notes_dir = Path(os.environ["NOTES_DIR"])
        else:
            # Smart default with OneDrive detection (from existing code)
            onedrive_docs = Path.home() / "OneDrive" / "Documents" / "notes"
            local_docs = Path.home() / "Documents" / "notes"

            if onedrive_docs.exists():
                self.notes_dir = onedrive_docs
            else:
                self.notes_dir = local_docs

        # Ensure absolute path
        self.notes_dir = self.notes_dir.resolve()

        # Create if doesn't exist
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def _get_monthly_file(self, date: Optional[datetime] = None) -> Path:
        """Get path to monthly notes file."""
        if date is None:
            date = datetime.now()

        year_dir = self.notes_dir / str(date.year)
        year_dir.mkdir(exist_ok=True)

        filename = f"{date.month:02d}-{date.strftime('%B')}.md"
        return year_dir / filename
```

**Key Principles:**
1. Always use `Path` objects for cross-platform compatibility
2. Resolve to absolute paths early
3. Create directories as needed with `mkdir(parents=True, exist_ok=True)`
4. Support environment variable configuration
5. Provide sensible defaults with OneDrive detection

---

## Security and Best Practices

### Stdio Transport Security

**Key Insight:** Stdio transport has NO authentication mechanism, and this is by design.

**Security Model:**
- Communication occurs exclusively on local system via stdin/stdout
- Data never leaves local environment
- Protected from network threats (eavesdropping, MITM attacks)
- Only compromise vector: attacker already has local machine control
- If system is secure, stdio channel is secure by default

**Implication:** Stdio transport relies on OS-level security rather than protocol-level authentication.

### Secrets Management

**Best Practices:**

1. **Environment Variables** (Recommended)
   ```json
   {
     "mcpServers": {
       "my-server": {
         "command": "python",
         "args": ["server.py"],
         "env": {
           "API_KEY": "secret-key-here",
           "DATABASE_URL": "postgresql://..."
         }
       }
     }
   }
   ```

2. **Secure Local Files**
   - Store secrets in `~/.config/myapp/secrets.json`
   - Use OS-level file permissions (chmod 600)
   - Read at server initialization

3. **Infisical CLI** (Advanced)
   - Inject secrets on-the-fly without storing in files
   - Prevents accidental leakage
   - Better for teams/shared environments

**Never:**
- Hard-code secrets in server code
- Store secrets in `claude_desktop_config.json` directly (it's in plaintext)
- Log secrets to stderr

### Error Handling

**Critical Rule:** MCP servers must ONLY write JSON-RPC messages to stdout. All logs and errors go to stderr.

```python
import sys
import logging

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # CRITICAL: stderr, not stdout
)

logger = logging.getLogger(__name__)

@mcp.tool()
def my_tool(param: str) -> dict:
    """Tool with proper error handling."""
    try:
        # Log to stderr
        logger.info(f"Executing my_tool with param: {param}")

        # Perform operation
        result = perform_operation(param)

        logger.info("Operation successful")
        return {"status": "success", "result": result}

    except ValueError as e:
        # Log full error to stderr (for debugging)
        logger.error(f"Validation error: {e}", exc_info=True)

        # Return sanitized error to client
        return {
            "status": "error",
            "error_type": "validation_error",
            "message": "Invalid input parameter"
        }

    except Exception as e:
        # Log unexpected errors
        logger.exception("Unexpected error in my_tool")

        # Return generic error (don't leak system details)
        return {
            "status": "error",
            "error_type": "internal_error",
            "message": "An unexpected error occurred"
        }
```

**Key Principles:**
1. **Defensive coding**: Wrap all tool logic in try/catch
2. **Specific exceptions first**: Catch specific errors before generic ones
3. **Sanitize responses**: Don't expose system details to users
4. **Log internally**: Full details to stderr for debugging
5. **Graceful degradation**: Return valid responses even on errors

### Retry and Circuit Breaking

For transient failures (network issues, rate limits):

```python
import asyncio
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1.0):
    """Decorator for retrying operations with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except TransientError as e:
                    if attempt == max_retries - 1:
                        raise

                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt)
                    jitter = delay * 0.1 * (2 * asyncio.random() - 1)
                    await asyncio.sleep(delay + jitter)

                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay:.2f}s")

            raise Exception("Max retries exceeded")
        return wrapper
    return decorator

@mcp.tool()
@retry_with_backoff(max_retries=3)
async def fetch_external_data(url: str) -> dict:
    """Fetch data with automatic retry on failure."""
    # Implementation...
```

### Debugging Best Practices

**Use MCP Inspector** (Official debugging tool)

```bash
# Install
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector python server.py

# Or with FastMCP CLI
mcp-inspector fastmcp run server.py
```

The inspector provides:
- Interactive tool testing
- Raw message viewing
- Protocol validation
- Request/response inspection

**Logging Strategy:**

```python
import sys
import logging

# Development: verbose logging
if os.environ.get("DEBUG") == "true":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
else:
    # Production: warnings and errors only
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
```

**Testing Strategy:**

1. **Unit tests** for core logic (NotesManager methods)
2. **Integration tests** using MCP Inspector or in-memory client
3. **End-to-end tests** with Claude Desktop

```python
# Example unit test
import pytest
from notes_manager import NotesManager

def test_add_note():
    manager = NotesManager(notes_dir="/tmp/test_notes")
    result = manager.add_note("Test - Note", "Test content")

    assert result["status"] == "success"
    assert "entry" in result
    assert result["entry"]["heading"] == "Test - Note"

# Example integration test with FastMCP
from fastmcp.testing import FastMCPTransport

async def test_add_note_tool():
    async with FastMCPTransport(mcp) as client:
        result = await client.call_tool(
            "add_note",
            heading="Test - Note",
            content="Test content"
        )

        assert result["status"] == "success"
```

---

## Future Extensibility

### Wrapping Arbitrary Command-Line Programs

**Pattern for External Executables:**

```python
import subprocess
from pathlib import Path

@mcp.tool()
def run_epublisher_automap(
    config_file: str,
    output_dir: str,
    format: str = "webhelp"
) -> dict:
    """
    Run ePublisher AutoMap to generate documentation.

    Args:
        config_file: Path to .WWP project file
        output_dir: Where to generate output
        format: Output format (webhelp, pdf, etc.)

    Returns:
        Dictionary with status and output paths
    """
    try:
        # Validate inputs
        config_path = Path(config_file).resolve()
        if not config_path.exists():
            return {
                "status": "error",
                "message": f"Config file not found: {config_file}"
            }

        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        # Construct command
        cmd = [
            "ePublisher",  # Assume in PATH
            "automap",
            str(config_path),
            "--output", str(output_path),
            "--format", format
        ]

        logger.info(f"Executing: {' '.join(cmd)}")

        # Execute with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "output_dir": str(output_path),
                "stdout": result.stdout
            }
        else:
            logger.error(f"ePublisher failed: {result.stderr}")
            return {
                "status": "error",
                "message": "Build failed",
                "stderr": result.stderr
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Build timed out after 5 minutes"
        }
    except Exception as e:
        logger.exception("Unexpected error in run_epublisher_automap")
        return {
            "status": "error",
            "message": str(e)
        }
```

**Key Considerations:**

1. **PATH Environment:** Ensure executable is in PATH or use absolute path
2. **Timeouts:** Always set reasonable timeouts for long-running processes
3. **Working Directory:** Set `cwd` parameter if needed
4. **Input Validation:** Validate file paths before execution
5. **Output Capture:** Capture both stdout and stderr
6. **Progress Reporting:** For long operations, consider streaming output

### Multi-Tool Server Pattern

```python
from fastmcp import FastMCP

# Create server with multiple related tools
mcp = FastMCP(name="documentation-tools")

@mcp.tool()
def build_docs(config: str) -> dict:
    """Build documentation from source."""
    # Implementation...

@mcp.tool()
def validate_links(docs_dir: str) -> dict:
    """Check for broken links in documentation."""
    # Implementation...

@mcp.tool()
def generate_pdf(html_dir: str) -> dict:
    """Convert HTML documentation to PDF."""
    # Implementation...

# Resource for accessing built docs
@mcp.resource("docs://{doc_id}")
def get_documentation(doc_id: str) -> str:
    """Retrieve generated documentation."""
    # Implementation...
```

### Server Composition

For complex systems, compose multiple servers:

```python
from fastmcp import FastMCP

# Create main server
main = FastMCP(name="productivity-suite")

# Import sub-servers
from notes_mcp_server import mcp as notes_server
from tasks_mcp_server import mcp as tasks_server

# Mount sub-servers
main.mount("/notes", notes_server)
main.mount("/tasks", tasks_server)

# Tools are now available as:
# - notes/add_note
# - notes/search_notes
# - tasks/create_task
# - tasks/list_tasks
```

### Performance Considerations

**Caching Strategy:**

```python
from functools import lru_cache
import hashlib

class NotesManager:
    def __init__(self):
        self._index_cache = None
        self._index_hash = None

    def _load_index(self):
        """Load index with caching."""
        index_path = self.notes_dir / ".index.json"

        if not index_path.exists():
            return self._rebuild_index()

        # Check if index file changed
        with open(index_path, 'rb') as f:
            current_hash = hashlib.md5(f.read()).hexdigest()

        if current_hash != self._index_hash:
            # Reload from disk
            with open(index_path) as f:
                self._index_cache = json.load(f)
            self._index_hash = current_hash

        return self._index_cache
```

**Async Operations:**

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for I/O-bound operations
executor = ThreadPoolExecutor(max_workers=4)

@mcp.tool()
async def search_notes_async(query: str) -> dict:
    """Async search for better concurrency."""
    loop = asyncio.get_event_loop()

    # Run blocking I/O in thread pool
    result = await loop.run_in_executor(
        executor,
        manager.search_notes,
        query
    )

    return result
```

---

## Recommendations

### For Notes Manager Skill

1. **Refactor for Dual Mode**
   - Keep `notes_manager.py` as pure logic (no I/O specifics)
   - Create `notes_mcp_server.py` as MCP wrapper
   - Maintain existing JSON stdin interface for Claude Code compatibility

2. **MCP Server Implementation**
   - Use FastMCP for minimal boilerplate
   - Expose each command as separate tool (better UX)
   - Tools: `add_note`, `search_notes`, `append_to_note`, `get_stats`, `reindex_notes`

3. **Configuration**
   - Support `NOTES_DIR` environment variable
   - Keep OneDrive detection logic
   - Add `MCP_SERVER_MODE` env var for explicit detection

4. **Testing**
   - Test both direct execution and MCP server modes
   - Use MCP Inspector for interactive testing
   - Verify Claude Desktop integration end-to-end

### For Future Skills (ePublisher AutoMap)

1. **Wrapper Pattern**
   - Create MCP server that wraps command-line executable
   - Validate inputs (file paths, parameters)
   - Set appropriate timeouts (builds can be long)
   - Capture and return both stdout and stderr

2. **Tools to Expose**
   - `build_documentation`: Run full build
   - `validate_project`: Check project config
   - `list_formats`: Show available output formats
   - `get_build_status`: Check if build is running

3. **Resources to Expose**
   - `projects://{project_id}/config`: Project configuration
   - `builds://{build_id}/output`: Build artifacts
   - `builds://{build_id}/logs`: Build logs

### General Best Practices

1. **Start Simple**
   - Begin with stdio transport for local use
   - Add HTTP/SSE later if needed for remote access
   - Use FastMCP for rapid prototyping

2. **Security First**
   - Never log to stdout (breaks protocol)
   - Sanitize error messages (don't leak system details)
   - Use environment variables for secrets
   - Validate all inputs

3. **Error Handling**
   - Wrap all operations in try/catch
   - Log detailed errors to stderr
   - Return user-friendly errors to client
   - Implement retries for transient failures

4. **Testing**
   - Unit test core logic separately
   - Use MCP Inspector for integration testing
   - Test in both Claude Code and Claude Desktop
   - Verify error handling and edge cases

5. **Documentation**
   - Write clear tool descriptions (Claude reads these!)
   - Document expected parameters and return values
   - Provide usage examples in SKILL.md
   - Include troubleshooting guide

---

## References

### Official Documentation

1. **Model Context Protocol Specification**
   - Homepage: https://modelcontextprotocol.io/
   - Specification: https://modelcontextprotocol.io/specification/
   - Architecture: https://modelcontextprotocol.io/docs/concepts/architecture
   - Transports: https://modelcontextprotocol.io/docs/concepts/transports

2. **Anthropic MCP Resources**
   - Announcement: https://www.anthropic.com/news/model-context-protocol
   - Claude Docs: https://docs.claude.com/en/docs/mcp
   - Desktop Extensions: https://www.anthropic.com/engineering/desktop-extensions

3. **Python SDK**
   - Official SDK: https://github.com/modelcontextprotocol/python-sdk
   - FastMCP: https://github.com/jlowin/fastmcp
   - FastMCP Docs: https://gofastmcp.com/

### Tutorials and Guides

4. **Getting Started**
   - Claude Desktop MCP Setup: https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop
   - Connect Local Servers: https://modelcontextprotocol.io/docs/develop/connect-local-servers
   - Building MCP Servers: https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python

5. **Security and Best Practices**
   - MCP Security: https://www.mcpevals.io/blog/mcp-security-best-practices
   - Error Handling: https://mcpcat.io/guides/error-handling-custom-mcp-servers/
   - Debugging: https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices

### Example Implementations

6. **Notes Servers**
   - notes-mcp: https://github.com/edvardlindelof/notes-mcp
   - Notes MCP Server (Mastra): https://mastra.ai/en/guides/guide/notes-mcp-server
   - mcp-notes (StarrStack): https://glama.ai/mcp/servers/@StarrStack/mcp-notes

7. **Other Examples**
   - Safe Python Executor: https://github.com/maxim-saplin/mcp_safe_local_python_executor
   - Python Template: https://github.com/sontallive/mcp-server-python-template
   - Filesystem Server: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem

### Tools

8. **Development Tools**
   - MCP Inspector: `npm install -g @modelcontextprotocol/inspector`
   - FastMCP CLI: `pip install fastmcp`
   - Official Python SDK: `pip install mcp`

### Community Resources

9. **Discussions and Forums**
   - MCP GitHub Discussions: https://github.com/orgs/modelcontextprotocol/discussions
   - Awesome MCP Servers: https://mcpservers.org/
   - Docker MCP Toolkit: https://www.docker.com/blog/the-model-context-protocol-simplifying-building-ai-apps-with-anthropic-claude-desktop-and-docker/

---

## Appendices

### Appendix A: Quick Start Checklist

**To create an MCP server for an existing Python script:**

- [ ] Install FastMCP: `pip install fastmcp`
- [ ] Create `{script_name}_mcp_server.py`
- [ ] Import script logic or use subprocess to call it
- [ ] Define tools with `@mcp.tool()` decorators
- [ ] Add proper error handling (try/catch all operations)
- [ ] Configure logging to stderr (not stdout!)
- [ ] Test with MCP Inspector: `mcp-inspector fastmcp run server.py`
- [ ] Add to `claude_desktop_config.json`
- [ ] Restart Claude Desktop
- [ ] Test end-to-end with natural language queries

### Appendix B: Troubleshooting Guide

**Server not appearing in Claude Desktop:**
- Check `claude_desktop_config.json` syntax (valid JSON?)
- Verify file paths are absolute, not relative
- Restart Claude Desktop completely (quit and relaunch)
- Check server logs in stderr

**Tools not executing:**
- Verify tool is decorated with `@mcp.tool()`
- Check tool function signature (type hints required)
- Test with MCP Inspector first
- Look for errors in stderr logs

**JSON-RPC errors:**
- Ensure NOTHING goes to stdout except JSON-RPC messages
- Move all print() statements to logging (stderr)
- Check for startup errors before server is ready

**File not found errors:**
- Use absolute paths in configuration
- Verify paths exist and are accessible
- Check environment variables are set correctly
- Test path resolution in isolation

### Appendix C: Environment Variables Reference

**Standard MCP Variables:**
- `MCP_SERVER_MODE`: "true" when running as MCP server
- `UV_PYTHON`: Set by uv when running in managed environment

**Notes Manager Variables:**
- `NOTES_DIR`: Root directory for notes storage
- `DEBUG`: "true" for verbose logging

**Common Claude Desktop Variables:**
- `APPDATA` (Windows): Location of Claude Desktop config
- `HOME`: User home directory
- `PATH`: Executable search path

### Appendix D: File Locations

**Claude Desktop Config:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**MCP Server Logs:**
- Stdout: JSON-RPC messages only (don't log here!)
- Stderr: All logging, errors, debug output
- Can redirect stderr to file for persistent logs

**Notes Storage (default):**
- `~/Documents/notes/` (or `~/OneDrive/Documents/notes/` if OneDrive present)
- Structure: `YYYY/MM-Month.md`
- Index: `.index.json` in root

---

**End of Research Document**

*This research was conducted on 2025-11-20 using official documentation, community resources, and real-world implementation examples. The recommendations are based on current best practices and may evolve as the MCP protocol and tooling mature.*
