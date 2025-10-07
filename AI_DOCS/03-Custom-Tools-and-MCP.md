# Claude Agent SDK - Custom Tools and MCP

## Table of Contents
- [Introduction](#introduction)
- [Creating Custom Tools](#creating-custom-tools)
- [Tool Design Best Practices](#tool-design-best-practices)
- [MCP Servers](#mcp-servers)
- [SDK MCP Servers](#sdk-mcp-servers)
- [External MCP Servers](#external-mcp-servers)
- [Tool Naming Conventions](#tool-naming-conventions)
- [Real-World Examples](#real-world-examples)

## Introduction

The Claude Agent SDK allows you to extend Claude's capabilities through custom tools. Tools are functions that Claude can invoke to perform specific actions, gather information, or interact with external systems.

**Why Create Custom Tools?**
- Integrate with domain-specific APIs
- Access proprietary data sources
- Perform specialized calculations
- Interact with databases or external services
- Extend Claude's capabilities for your use case

## Creating Custom Tools

### The `@tool` Decorator

Use the `@tool` decorator to create custom tools.

**Syntax:**
```python
@tool(name: str, description: str, input_schema: dict[str, type])
async def tool_function(args: dict[str, Any]) -> dict[str, Any]:
    # Tool implementation
    pass
```

**Parameters:**
- `name`: Unique tool identifier
- `description`: Clear description of what the tool does (Claude uses this to decide when to use it)
- `input_schema`: Dictionary mapping parameter names to Python types

**Return Format:**
```python
{
    "content": [
        {
            "type": "text",
            "text": "Result or message"
        }
    ],
    "is_error": False  # Optional: True if operation failed
}
```

### Basic Example: Calculator

```python
from claude_agent_sdk import tool
from typing import Any

@tool("calculate", "Perform safe mathematical calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """Safe calculator using restricted eval."""
    try:
        # Restrict eval to prevent code injection
        result = eval(args["expression"], {"__builtins__": {}})
        return {
            "content": [{
                "type": "text",
                "text": f"Result: {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error calculating: {str(e)}"
            }],
            "is_error": True
        }
```

### Example: Get Current Time

```python
from datetime import datetime

@tool("get_time", "Get the current date and time", {})
async def get_time(args: dict[str, Any]) -> dict[str, Any]:
    """Returns current date and time."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "content": [{
            "type": "text",
            "text": f"Current time: {current_time}"
        }]
    }
```

### Example: String Manipulation

```python
@tool("reverse_string", "Reverse a string", {"text": str})
async def reverse_string(args: dict[str, Any]) -> dict[str, Any]:
    """Reverses the provided string."""
    text = args["text"]
    reversed_text = text[::-1]
    return {
        "content": [{
            "type": "text",
            "text": f"Reversed: {reversed_text}"
        }]
    }
```

### Example: File Analysis

```python
import os

@tool("analyze_file", "Analyze file contents and provide statistics", {"file_path": str})
async def analyze_file(args: dict[str, Any]) -> dict[str, Any]:
    """Analyze a file and return statistics."""
    file_path = args["file_path"]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)

        return {
            "content": [{
                "type": "text",
                "text": f"File Analysis for {file_path}:\n"
                       f"- Lines: {lines}\n"
                       f"- Words: {words}\n"
                       f"- Characters: {chars}\n"
                       f"- File size: {os.path.getsize(file_path)} bytes"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error analyzing file: {str(e)}"
            }],
            "is_error": True
        }
```

## Tool Design Best Practices

### 1. Clear Descriptions

Claude uses tool descriptions to decide when to invoke them. Make them specific and action-oriented.

**Good:**
```python
@tool("query_database", "Execute a SELECT query on the products database and return results", {...})
```

**Bad:**
```python
@tool("db", "Database stuff", {...})
```

### 2. Validate Inputs

Always validate and sanitize inputs, especially for security-sensitive operations.

```python
@tool("execute_query", "Execute a database query", {"query": str})
async def execute_query(args: dict[str, Any]) -> dict[str, Any]:
    query = args["query"]

    # Security: Only allow SELECT queries
    if not query.strip().upper().startswith("SELECT"):
        return {
            "content": [{
                "type": "text",
                "text": "Error: Only SELECT queries are allowed"
            }],
            "is_error": True
        }

    # Execute query...
```

### 3. Handle Errors Gracefully

Return meaningful error messages with `is_error: True`.

```python
try:
    # Tool operation
    result = perform_operation()
    return {
        "content": [{"type": "text", "text": result}]
    }
except ValueError as e:
    return {
        "content": [{"type": "text", "text": f"Invalid input: {e}"}],
        "is_error": True
    }
except Exception as e:
    return {
        "content": [{"type": "text", "text": f"Unexpected error: {e}"}],
        "is_error": True
    }
```

### 4. Keep Tools Focused

Each tool should do one thing well. Split complex operations into multiple tools.

**Good:**
```python
@tool("list_databases", "List all databases on the server", {...})
@tool("list_tables", "List all tables in a specific database", {...})
@tool("get_table_schema", "Get the schema of a specific table", {...})
```

**Bad:**
```python
@tool("database_operations", "Do various database things", {...})
```

### 5. Provide Rich Output

Include relevant details in responses to help Claude make informed decisions.

```python
@tool("check_service_status", "Check if a service is running", {"service_name": str})
async def check_service_status(args: dict[str, Any]) -> dict[str, Any]:
    status = get_service_status(args["service_name"])
    return {
        "content": [{
            "type": "text",
            "text": f"Service: {status['name']}\n"
                   f"Status: {status['state']}\n"
                   f"Uptime: {status['uptime']}\n"
                   f"CPU: {status['cpu_usage']}%\n"
                   f"Memory: {status['memory_usage']}MB"
        }]
    }
```

## MCP Servers

Model Context Protocol (MCP) servers are the mechanism for registering and managing custom tools.

### Three Types of MCP Servers

1. **SDK MCP Servers** - Run within your application
2. **stdio Servers** - External processes communicating via stdin/stdout
3. **HTTP/SSE Servers** - Remote servers over network

## SDK MCP Servers

SDK MCP servers run directly in your Python application, providing the simplest way to add custom tools.

### Creating an SDK MCP Server

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

# Define tools
@tool("tool1", "Description", {...})
async def tool1(args):
    # Implementation
    pass

@tool("tool2", "Description", {...})
async def tool2(args):
    # Implementation
    pass

# Create server
server = create_sdk_mcp_server(
    name="my_server",
    version="1.0.0",
    tools=[tool1, tool2]
)
```

### Using SDK MCP Server

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

options = ClaudeAgentOptions(
    mcp_servers={"my": server},
    allowed_tools=[
        "mcp__my__tool1",
        "mcp__my__tool2"
    ]
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Use my custom tools")
    # Process response...
```

### Complete SDK MCP Example

```python
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock
)
from typing import Any
from datetime import datetime

# Define custom tools
@tool("calculate", "Perform mathematical calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    try:
        result = eval(args["expression"], {"__builtins__": {}})
        return {
            "content": [{"type": "text", "text": f"Result: {result}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "is_error": True
        }

@tool("get_time", "Get current date and time", {})
async def get_time(args: dict[str, Any]) -> dict[str, Any]:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "content": [{"type": "text", "text": f"Current time: {current_time}"}]
    }

@tool("reverse_string", "Reverse a string", {"text": str})
async def reverse_string(args: dict[str, Any]) -> dict[str, Any]:
    reversed_text = args["text"][::-1]
    return {
        "content": [{"type": "text", "text": f"Reversed: {reversed_text}"}]
    }

async def main():
    # Create MCP server with tools
    utilities_server = create_sdk_mcp_server(
        name="utilities",
        version="1.0.0",
        tools=[calculate, get_time, reverse_string]
    )

    # Configure agent
    options = ClaudeAgentOptions(
        mcp_servers={"utils": utilities_server},
        allowed_tools=[
            "mcp__utils__calculate",
            "mcp__utils__get_time",
            "mcp__utils__reverse_string"
        ]
    )

    # Use agent
    async with ClaudeSDKClient(options=options) as client:
        await client.query("What's 123 * 456 and what time is it?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

if __name__ == "__main__":
    asyncio.run(main())
```

## External MCP Servers

External MCP servers run as separate processes, useful for:
- Language-agnostic tools
- Shared tools across multiple agents
- Resource-intensive operations
- Pre-built MCP servers from the ecosystem

### Configuration via `.mcp.json`

Create a `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed"],
      "env": {
        "ALLOWED_PATHS": "/Users/me/projects"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Using External MCP Servers

```python
options = ClaudeAgentOptions(
    allowed_tools=[
        "mcp__filesystem__read_file",
        "mcp__filesystem__write_file",
        "mcp__github__create_issue"
    ],
    # .mcp.json is automatically loaded
)
```

### HTTP/SSE MCP Servers

For remote MCP servers:

```json
{
  "mcpServers": {
    "remote_service": {
      "url": "https://api.example.com/mcp",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer token123"
      }
    }
  }
}
```

## Tool Naming Conventions

### Built-in Tools
- Simple names: `Read`, `Write`, `Bash`, `Grep`, etc.

### MCP Tools
Format: `mcp__<server_name>__<tool_name>`

Examples:
- `mcp__utils__calculate`
- `mcp__database__query_table`
- `mcp__github__create_issue`

### When Specifying `allowed_tools`

```python
options = ClaudeAgentOptions(
    allowed_tools=[
        # Built-in tools
        "Read",
        "Write",
        "Bash",

        # MCP tools (must use full name)
        "mcp__my_server__my_tool",
        "mcp__my_server__another_tool"
    ]
)
```

## Real-World Examples

### Database Tools

```python
import pyodbc
from claude_agent_sdk import tool
from typing import Any

@tool("list_databases", "Get a list of all databases on the SQL Server", {"server": str})
async def list_databases(args: dict[str, Any]) -> dict[str, Any]:
    """List all databases on SQL Server."""
    server = args.get("server", "localhost")
    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sys.databases ORDER BY name")
        databases = [row.name for row in cursor.fetchall()]

        conn.close()

        return {
            "content": [{
                "type": "text",
                "text": f"Databases on {server}:\n" + "\n".join(f"  - {db}" for db in databases)
            }]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "is_error": True
        }

@tool("query_table", "Execute a SELECT query (read-only, max 100 rows)",
      {"server": str, "database": str, "query": str})
async def query_table(args: dict[str, Any]) -> dict[str, Any]:
    """Execute a SELECT query."""
    server = args.get("server", "localhost")
    database = args["database"]
    query = args["query"]

    # Security: Only allow SELECT
    if not query.strip().upper().startswith("SELECT"):
        return {
            "content": [{"type": "text", "text": "Error: Only SELECT queries allowed"}],
            "is_error": True
        }

    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        # Add TOP 100 limit
        if "TOP" not in query.upper():
            query = query.replace("SELECT", "SELECT TOP 100", 1)

        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        # Format results
        result = f"Query results ({len(rows)} rows):\n\n"
        result += " | ".join(columns) + "\n"
        result += "-" * 50 + "\n"
        for row in rows[:100]:
            result += " | ".join(str(val) if val else "NULL" for val in row) + "\n"

        return {"content": [{"type": "text", "text": result}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "is_error": True
        }
```

### File Processing Tools

```python
import os

@tool("count_extensions", "Count files by extension in a directory", {"directory": str})
async def count_extensions(args: dict[str, Any]) -> dict[str, Any]:
    """Count files by their extensions."""
    directory = args["directory"]
    try:
        extension_counts = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1] or "no_extension"
                extension_counts[ext] = extension_counts.get(ext, 0) + 1

        result_text = f"File extension counts in {directory}:\n"
        for ext, count in sorted(extension_counts.items(), key=lambda x: x[1], reverse=True):
            result_text += f"  {ext}: {count}\n"

        return {"content": [{"type": "text", "text": result_text}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "is_error": True
        }
```

## Summary

- Use `@tool` decorator to create custom tools
- Create SDK MCP servers with `create_sdk_mcp_server()`
- Configure external MCP servers via `.mcp.json`
- Follow naming convention: `mcp__<server>__<tool>`
- Validate inputs and handle errors gracefully
- Keep tools focused and well-described
- Use clear, action-oriented descriptions

## Next Steps

- [Permissions and Security](./04-Permissions-and-Security.md) - Secure your custom tools
- [Advanced Topics](./05-Advanced-Topics.md) - Hooks, subagents, and more
- [Examples](./06-Examples-and-Best-Practices.md) - More practical examples
