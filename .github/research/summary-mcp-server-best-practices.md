# Summary: MCP Server Best Practices for Dual-Mode Skills

**Date:** 2025-11-20
**For:** Quick reference when implementing MCP servers
**Full Research:** See `research-mcp-server-implementation.md`

---

## TL;DR

**Goal:** Make skills work in both Claude Code (local) and Claude Desktop (remote)

**Solution:** Wrap Python scripts as MCP servers using FastMCP

**Key Insight:** MCP is like USB-C for AI - a universal protocol for connecting AI to tools and data

---

## Quick Start: 3 Steps

### 1. Install FastMCP

```bash
pip install fastmcp
```

### 2. Create MCP Server Wrapper

**File:** `my_tool_mcp_server.py`

```python
#!/usr/bin/env python3
from fastmcp import FastMCP
from my_script import MyLogic  # Your existing logic

mcp = FastMCP(name="my-tool")
logic = MyLogic()

@mcp.tool()
def my_operation(param: str) -> dict:
    """Clear description of what this does."""
    try:
        result = logic.operation(param)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    mcp.run()  # stdio transport by default
```

### 3. Configure Claude Desktop

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "my-tool": {
      "command": "python",
      "args": ["-m", "fastmcp", "run", "/absolute/path/to/my_tool_mcp_server.py"],
      "env": {
        "MY_CONFIG_VAR": "value",
        "MCP_SERVER_MODE": "true"
      }
    }
  }
}
```

**Restart Claude Desktop** - Done!

---

## MCP Concepts

### Three Types of Interactions

**Tools** (Actions)
- Functions the AI can call
- For operations with side effects
- Example: `add_note()`, `search_files()`, `build_docs()`

**Resources** (Data)
- Read-only data sources
- Like GET endpoints in REST API
- Example: File contents, database records, API responses

**Prompts** (Templates)
- Pre-written instruction templates
- Guide users on how to use tools
- Example: "Search notes for {query}"

### Transport: Stdio (Recommended)

- Communication via stdin/stdout
- Most secure (local only, no network)
- No authentication needed (OS-level security)
- Server runs as subprocess of Claude Desktop

---

## Dual-Mode Pattern

### Goal: One Skill, Two Environments

**Claude Code:**
- Direct script execution
- Fast, local access
- Uses existing JSON stdin interface

**Claude Desktop:**
- Routes through MCP server
- Remote environment bridges to local
- Uses same underlying logic

### Implementation

**1. Core Logic (Keep Pure)**

```python
# my_script.py - No I/O specifics
class MyLogic:
    def operation(self, param: str) -> dict:
        # Pure logic here
        return {"result": "success"}
```

**2. CLI Interface (Claude Code)**

```python
# my_script.py - main() for direct execution
import json
import sys

def main():
    input_data = json.loads(sys.stdin.read())
    logic = MyLogic()
    result = logic.operation(input_data["param"])
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

**3. MCP Server (Claude Desktop)**

```python
# my_script_mcp_server.py
from fastmcp import FastMCP
from my_script import MyLogic

mcp = FastMCP(name="my-tool")
logic = MyLogic()

@mcp.tool()
def operation(param: str) -> dict:
    return logic.operation(param)

if __name__ == "__main__":
    mcp.run()
```

### Environment Detection (Optional)

```python
import os
import sys

def is_mcp_server():
    """Detect if running in MCP server mode."""
    return (
        os.environ.get("MCP_SERVER_MODE") == "true" or
        "UV_PYTHON" in os.environ or
        not sys.stdin.isatty()
    )
```

---

## Critical Best Practices

### Error Handling

**CRITICAL:** Only JSON-RPC messages to stdout. All logs to stderr!

```python
import sys
import logging

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr  # NOT stdout!
)

@mcp.tool()
def my_tool(param: str) -> dict:
    try:
        logging.info(f"Executing with {param}")  # Goes to stderr
        result = do_work(param)
        return {"status": "success", "result": result}
    except Exception as e:
        logging.exception("Error")  # Goes to stderr
        return {"status": "error", "message": str(e)}
```

### Security

**Stdio transport is secure by design:**
- No authentication needed
- Relies on OS-level security
- Data never leaves local machine

**Secrets management:**
```json
{
  "env": {
    "API_KEY": "your-secret-here",
    "DATABASE_URL": "postgresql://..."
  }
}
```

**Never:**
- Log secrets to stderr
- Hard-code secrets in code
- Return sensitive data in error messages

### Path Handling

```python
from pathlib import Path

class MyLogic:
    def __init__(self, data_dir: str = None):
        # Priority: param > env var > default
        if data_dir:
            self.data_dir = Path(data_dir)
        elif "MY_DATA_DIR" in os.environ:
            self.data_dir = Path(os.environ["MY_DATA_DIR"])
        else:
            self.data_dir = Path.home() / "my_data"

        # Always resolve to absolute path
        self.data_dir = self.data_dir.resolve()

        # Create if needed
        self.data_dir.mkdir(parents=True, exist_ok=True)
```

---

## Tool Design Patterns

### Pattern 1: One Tool Per Operation (Recommended)

**Pros:**
- Claude understands available operations
- Better tool discovery
- Clear schemas and validation

```python
@mcp.tool()
def add_note(heading: str, content: str) -> dict:
    """Add a new note entry."""
    return manager.add_note(heading, content)

@mcp.tool()
def search_notes(query: str, limit: int = 10) -> dict:
    """Search across all notes."""
    return manager.search_notes(query, limit)

@mcp.tool()
def delete_note(note_id: str) -> dict:
    """Delete a note by ID."""
    return manager.delete_note(note_id)
```

### Pattern 2: Unified Command Tool

**Pros:**
- Less code duplication
- Mirrors JSON stdin interface

```python
@mcp.tool()
def notes_command(command: str, **kwargs) -> dict:
    """
    Execute notes command.

    Args:
        command: One of: add, search, delete
        **kwargs: Command-specific parameters
    """
    if command == "add":
        return manager.add_note(kwargs["heading"], kwargs["content"])
    elif command == "search":
        return manager.search_notes(kwargs["query"], kwargs.get("limit", 10))
    # ...
```

**Recommendation:** Use Pattern 1 for better UX

### Pattern 3: Wrapping External Programs

```python
import subprocess

@mcp.tool()
def run_external_tool(input_file: str, output_dir: str) -> dict:
    """Run external command-line tool."""
    try:
        # Validate inputs
        input_path = Path(input_file).resolve()
        if not input_path.exists():
            return {"status": "error", "message": "Input file not found"}

        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        # Execute with timeout
        result = subprocess.run(
            ["external_tool", str(input_path), str(output_path)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "output_dir": str(output_path),
                "stdout": result.stdout
            }
        else:
            return {
                "status": "error",
                "message": "Command failed",
                "stderr": result.stderr
            }

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Command timed out"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

## Testing Workflow

### 1. Unit Test Core Logic

```python
import pytest

def test_add_note():
    manager = NotesManager("/tmp/test_notes")
    result = manager.add_note("Test", "Content")
    assert result["status"] == "success"
```

### 2. Test with MCP Inspector

```bash
# Install
npm install -g @modelcontextprotocol/inspector

# Run
mcp-inspector python my_tool_mcp_server.py

# Or with FastMCP
mcp-inspector fastmcp run my_tool_mcp_server.py
```

The inspector provides:
- Interactive tool testing
- Raw message viewing
- Protocol validation

### 3. Test in Claude Desktop

1. Add to `claude_desktop_config.json`
2. Restart Claude Desktop
3. Use natural language to trigger tools
4. Check stderr logs for errors

---

## Common Pitfalls

### 1. Logging to stdout

**Wrong:**
```python
print("Debug info")  # Breaks JSON-RPC protocol!
```

**Right:**
```python
logging.info("Debug info")  # Goes to stderr
```

### 2. Relative Paths in Config

**Wrong:**
```json
{
  "args": ["./server.py"]  // Relative path fails
}
```

**Right:**
```json
{
  "args": ["/absolute/path/to/server.py"]
}
```

### 3. Missing Error Handling

**Wrong:**
```python
@mcp.tool()
def my_tool(param: str):
    return do_work(param)  # Crashes on error
```

**Right:**
```python
@mcp.tool()
def my_tool(param: str) -> dict:
    try:
        result = do_work(param)
        return {"status": "success", "result": result}
    except Exception as e:
        logging.exception("Error in my_tool")
        return {"status": "error", "message": str(e)}
```

### 4. Exposing Secrets in Errors

**Wrong:**
```python
return {"error": f"Database connection failed: {connection_string}"}
```

**Right:**
```python
logging.error(f"Database connection failed: {connection_string}")
return {"error": "Database connection failed"}
```

---

## FastMCP vs Official SDK

### FastMCP (Recommended for Most Cases)

**Pros:**
- Minimal boilerplate
- Automatic schema generation
- Built-in testing utilities
- Production features included

**Example:**
```python
from fastmcp import FastMCP

mcp = FastMCP(name="my-tool")

@mcp.tool()
def my_function(param: str) -> str:
    return f"Result: {param}"

mcp.run()
```

### Official SDK

**Pros:**
- Full protocol control
- More explicit
- Better for complex servers

**Example:**
```python
from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from mcp.server.models import InitializationOptions

# More verbose setup...
```

**Recommendation:** Start with FastMCP, switch to SDK if you need fine-grained control

---

## Deployment Options

### Local (stdio) - Recommended

```json
{
  "command": "python",
  "args": ["server.py"]
}
```

### With Dependency Management (uv)

```json
{
  "command": "uv",
  "args": ["--directory", "/path/to/server", "run", "server.py"]
}
```

### With Virtual Environment

```json
{
  "command": "/path/to/venv/bin/python",
  "args": ["server.py"]
}
```

### Desktop Extensions (.mcpb) - Future

- Single-click installation
- Bundles code and dependencies
- Simplified distribution
- Coming soon from Anthropic

---

## Next Steps

### For Notes Manager Skill

1. Refactor `notes_manager.py` to separate logic from I/O
2. Create `notes_mcp_server.py` with individual tools
3. Test with MCP Inspector
4. Update documentation with dual-mode setup

### For ePublisher AutoMap

1. Create MCP server wrapper for AutoMap executable
2. Expose tools: `build_docs()`, `validate_project()`, etc.
3. Handle long-running builds with timeouts
4. Provide progress feedback to users

### General Pattern

1. Extract core logic to library
2. Keep CLI interface (Claude Code)
3. Add MCP wrapper (Claude Desktop)
4. Test both modes
5. Document setup for both environments

---

## Resources

**Official:**
- MCP Spec: https://modelcontextprotocol.io/
- FastMCP: https://github.com/jlowin/fastmcp
- FastMCP Docs: https://gofastmcp.com/

**Tools:**
- MCP Inspector: `npm install -g @modelcontextprotocol/inspector`
- FastMCP: `pip install fastmcp`

**Examples:**
- Notes servers: https://github.com/edvardlindelof/notes-mcp
- Python executor: https://github.com/maxim-saplin/mcp_safe_local_python_executor

---

**Remember:**

1. Stdio transport = secure by default
2. Stdout = JSON-RPC only, Stderr = logs
3. One tool per operation for better UX
4. Test with Inspector before Claude Desktop
5. Absolute paths in config files

**Full research in:** `research-mcp-server-implementation.md`
