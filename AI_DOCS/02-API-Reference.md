# Claude Agent SDK - API Reference

## Table of Contents
- [Core Functions](#core-functions)
- [Client Classes](#client-classes)
- [Configuration Objects](#configuration-objects)
- [Message Types](#message-types)
- [Exceptions](#exceptions)

## Core Functions

### `query()`

Execute a simple query without maintaining state.

**Signature:**
```python
async def query(
    prompt: str,
    options: ClaudeAgentOptions | None = None
) -> AsyncIterator[Message]
```

**Parameters:**
- `prompt` (str): The query or instruction for Claude
- `options` (ClaudeAgentOptions, optional): Configuration options

**Returns:**
- AsyncIterator yielding message objects

**Example:**
```python
async for message in query(prompt="What is 2 + 2?"):
    print(message)
```

**With Options:**
```python
options = ClaudeAgentOptions(
    system_prompt="You are a math tutor",
    allowed_tools=["Read"]
)
async for message in query(prompt="Explain calculus", options=options):
    print(message)
```

## Client Classes

### `ClaudeSDKClient`

Main client for conversational, stateful interactions.

**Constructor:**
```python
ClaudeSDKClient(options: ClaudeAgentOptions | None = None)
```

**Methods:**

#### `query(prompt: str) -> None`
Send a query to Claude.

```python
async with ClaudeSDKClient() as client:
    await client.query("What is the capital of France?")
```

#### `receive_response() -> AsyncIterator[Message]`
Receive responses from Claude.

```python
async for message in client.receive_response():
    if isinstance(message, AssistantMessage):
        process_message(message)
```

#### Context Manager Support
Use with `async with` for automatic resource management.

```python
async with ClaudeSDKClient(options=options) as client:
    # Client automatically cleaned up after block
    await client.query("Hello")
    async for message in client.receive_response():
        print(message)
```

## Configuration Objects

### `ClaudeAgentOptions`

Configuration object for customizing agent behavior.

**Attributes:**

#### `system_prompt: str | None`
Custom system instructions for the agent.

```python
options = ClaudeAgentOptions(
    system_prompt="You are an expert Python developer specializing in async programming"
)
```

#### `permission_mode: str`
Control tool permissions. Options:
- `"default"`: Standard permission checks (default)
- `"acceptEdits"`: Automatically approve file edits
- `"bypassPermissions"`: Allow all tool uses (use cautiously)
- `"plan"`: Read-only mode (not currently supported)

```python
options = ClaudeAgentOptions(permission_mode="acceptEdits")
```

#### `allowed_tools: list[str] | None`
Whitelist of tools the agent can use.

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Bash", "Glob", "Grep"]
)
```

**Built-in Tools:**
- `Read`: Read files
- `Write`: Write files
- `Edit`: Edit files
- `Bash`: Execute shell commands
- `Glob`: Find files by pattern
- `Grep`: Search file contents
- `WebSearch`: Search the web
- `WebFetch`: Fetch web pages

**Custom MCP Tools:**
Format: `mcp__<server_name>__<tool_name>`

```python
allowed_tools=["mcp__utils__calculate", "mcp__utils__get_time"]
```

#### `mcp_servers: dict[str, MCPServer] | None`
Register custom MCP servers.

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool("my_tool", "Description", {"param": str})
async def my_tool(args):
    return {"content": [{"type": "text", "text": "result"}]}

server = create_sdk_mcp_server(
    name="my_server",
    version="1.0.0",
    tools=[my_tool]
)

options = ClaudeAgentOptions(
    mcp_servers={"my": server}
)
```

#### `max_turns: int | None`
Limit the number of conversation turns.

```python
options = ClaudeAgentOptions(max_turns=5)
```

#### `cwd: str | None`
Set the working directory for file operations.

```python
import os
options = ClaudeAgentOptions(cwd=os.getcwd())
```

#### `hooks: dict[str, list[HookMatcher]] | None`
Register hooks for tool execution monitoring/control.

```python
options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='Bash', hooks=[security_validator]),
            HookMatcher(hooks=[tool_logger])
        ]
    }
)
```

#### `agents: list[SubagentConfig] | None`
Define subagents programmatically.

```python
options = ClaudeAgentOptions(
    agents=[
        {
            "name": "code_reviewer",
            "description": "Review code for quality",
            "prompt": "You are a code review expert",
            "tools": ["Read", "Grep"]
        }
    ]
)
```

## Message Types

### `AssistantMessage`

Represents Claude's response message.

**Attributes:**
- `content: list[ContentBlock]`: List of content blocks (text, tool use, etc.)
- `role: str`: Always "assistant"

**Example:**
```python
async for message in client.receive_response():
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
```

### `TextBlock`

Text content within a message.

**Attributes:**
- `type: str`: Always "text"
- `text: str`: The text content

**Example:**
```python
if isinstance(block, TextBlock):
    print(f"Claude says: {block.text}")
```

### `ToolUseBlock`

Represents a tool invocation by Claude.

**Attributes:**
- `type: str`: Always "tool_use"
- `id: str`: Unique tool use identifier
- `name: str`: Tool name
- `input: dict`: Tool parameters

### `ToolResultBlock`

Result from tool execution.

**Attributes:**
- `type: str`: Always "tool_result"
- `tool_use_id: str`: ID of the corresponding tool use
- `content: list`: Result content
- `is_error: bool`: Whether the tool execution failed

## Tool Decorators

### `@tool()`

Decorator for creating custom tools.

**Signature:**
```python
def tool(
    name: str,
    description: str,
    input_schema: dict[str, type]
) -> Callable
```

**Parameters:**
- `name`: Tool name
- `description`: What the tool does
- `input_schema`: Dictionary mapping parameter names to types

**Returns:**
- Decorator function

**Example:**
```python
from claude_agent_sdk import tool
from typing import Any

@tool("calculate", "Perform mathematical calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    result = eval(args["expression"], {"__builtins__": {}})
    return {
        "content": [{
            "type": "text",
            "text": f"Result: {result}"
        }]
    }
```

**Tool Return Format:**
```python
{
    "content": [
        {
            "type": "text",
            "text": "The result or message"
        }
    ],
    "is_error": False  # Optional, indicates if tool failed
}
```

### `create_sdk_mcp_server()`

Create an MCP server from custom tools.

**Signature:**
```python
def create_sdk_mcp_server(
    name: str,
    version: str,
    tools: list[Callable]
) -> MCPServer
```

**Parameters:**
- `name`: Server name
- `version`: Server version
- `tools`: List of tool functions (decorated with @tool)

**Returns:**
- MCPServer instance

**Example:**
```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool("get_time", "Get current time", {})
async def get_time(args):
    from datetime import datetime
    return {
        "content": [{
            "type": "text",
            "text": datetime.now().isoformat()
        }]
    }

server = create_sdk_mcp_server(
    name="utilities",
    version="1.0.0",
    tools=[get_time]
)
```

## Hook Types

### `HookMatcher`

Matches hooks to specific tools or all tools.

**Constructor:**
```python
HookMatcher(
    matcher: str | None = None,
    hooks: list[Callable]
)
```

**Parameters:**
- `matcher`: Tool name to match (None = all tools)
- `hooks`: List of hook functions

**Example:**
```python
# Hook for specific tool
HookMatcher(matcher='Bash', hooks=[security_validator])

# Hook for all tools
HookMatcher(hooks=[tool_logger])
```

### Hook Function Signature

```python
async def hook_function(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]
```

**Parameters:**
- `input_data`: Tool invocation data (tool_name, tool_input)
- `tool_use_id`: Unique identifier for this tool use
- `context`: Additional context information

**Return:**
- Dictionary with hook-specific output (e.g., permission decisions)

**Example:**
```python
async def security_validator(input_data, tool_use_id, context):
    if input_data.get('tool_name') == 'Bash':
        command = input_data.get('tool_input', {}).get('command', '')
        if 'rm -rf /' in command:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'Dangerous command blocked'
                }
            }
    return {}
```

### `HookContext`

Context information passed to hooks.

**Attributes:**
- Additional contextual data about the current agent state

## Exceptions

### `CLINotFoundError`

Raised when Claude Code CLI is not installed or not found in PATH.

**Example:**
```python
from claude_agent_sdk import CLINotFoundError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLINotFoundError:
    print("ERROR: Claude Code CLI not found!")
    print("Install with: npm install -g @anthropic-ai/claude-code")
```

### `ProcessError`

Raised when the CLI process fails.

**Attributes:**
- `exit_code: int`: Process exit code
- `stderr: str`: Error output

**Example:**
```python
from claude_agent_sdk import ProcessError

try:
    async for message in query(prompt="Hello"):
        print(message)
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
    print(f"Error: {e.stderr}")
```

### `CLIJSONDecodeError`

Raised when CLI output cannot be parsed as JSON.

**Example:**
```python
from claude_agent_sdk import CLIJSONDecodeError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLIJSONDecodeError as e:
    print(f"Failed to parse CLI response: {e}")
```

## Complete Example

```python
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    CLINotFoundError,
    ProcessError,
    tool,
    create_sdk_mcp_server
)
from typing import Any

# Define custom tool
@tool("greet", "Greet a person", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    name = args["name"]
    return {
        "content": [{
            "type": "text",
            "text": f"Hello, {name}! Nice to meet you."
        }]
    }

async def main():
    # Create MCP server
    server = create_sdk_mcp_server(
        name="greeter",
        version="1.0.0",
        tools=[greet]
    )

    # Configure options
    options = ClaudeAgentOptions(
        system_prompt="You are a friendly assistant",
        permission_mode="acceptEdits",
        allowed_tools=["mcp__greeter__greet"],
        mcp_servers={"greeter": server}
    )

    # Run agent
    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query("Please greet Alice")
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"Claude: {block.text}")
    except CLINotFoundError:
        print("ERROR: Claude Code CLI not installed")
    except ProcessError as e:
        print(f"ERROR: Process failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```
