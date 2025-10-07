# Claude Agent SDK - Permissions and Security

## Table of Contents
- [Introduction](#introduction)
- [Permission Modes](#permission-modes)
- [Allowed Tools](#allowed-tools)
- [Hooks](#hooks)
- [Permission Evaluation Order](#permission-evaluation-order)
- [Security Best Practices](#security-best-practices)
- [Real-World Security Examples](#real-world-security-examples)

## Introduction

The Claude Agent SDK provides multiple layers of security controls to ensure your agents operate safely and within defined boundaries. Understanding these controls is critical for building secure, production-ready agents.

**Four Complementary Permission Controls:**

1. **Permission Modes** - Global settings for tool behavior
2. **Allowed Tools** - Whitelist specific tools
3. **Hooks** - Runtime validation and monitoring
4. **Permission Rules** (settings.json) - Declarative allow/deny patterns

These controls work together to provide defense-in-depth security.

## Permission Modes

Permission modes set the global security posture for your agent.

### Available Modes

#### `default` (Recommended for Production)
Standard permission checks with user confirmation for sensitive operations.

```python
options = ClaudeAgentOptions(
    permission_mode="default"
)
```

**Use when:**
- Running in interactive mode
- User oversight is available
- Safety is paramount

#### `acceptEdits`
Automatically approves file edit operations, but maintains other permission checks.

```python
options = ClaudeAgentOptions(
    permission_mode="acceptEdits"
)
```

**Use when:**
- Agent needs to modify files frequently
- Working in a sandboxed environment
- File operations are the primary task

**Caution:** Still allows file modifications without confirmation.

#### `bypassPermissions`
Allows all tool uses without permission checks.

```python
options = ClaudeAgentOptions(
    permission_mode="bypassPermissions"
)
```

**Use when:**
- Running in completely isolated environments
- Full automation is required
- You have other security controls in place

**Warning:** Use with extreme caution. Only in trusted, sandboxed environments.

#### `plan` (Not Currently Supported)
Read-only mode where tools can only gather information.

```python
options = ClaudeAgentOptions(
    permission_mode="plan"
)
```

**Intended use:**
- Planning phases
- Information gathering
- No system modifications

### Choosing the Right Mode

```python
# Development - Interactive testing
dev_options = ClaudeAgentOptions(permission_mode="default")

# CI/CD - Automated testing
ci_options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Bash"]
)

# Sandboxed automation
sandbox_options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    allowed_tools=["Read"],  # Still restrict tools!
    cwd="/sandboxed/directory"
)
```

## Allowed Tools

The `allowed_tools` parameter creates a whitelist of permitted tools.

### Basic Usage

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Glob", "Grep"]
)
```

**If `allowed_tools` is:**
- **Not specified**: All tools available (based on permission mode)
- **Empty list `[]`**: No tools available
- **List of tools**: Only specified tools available

### Built-in Tools Reference

```python
# File Operations
allowed_tools = ["Read", "Write", "Edit", "Glob", "Grep"]

# System Operations
allowed_tools = ["Bash"]

# Web Operations
allowed_tools = ["WebSearch", "WebFetch"]

# Notebook Operations
allowed_tools = ["NotebookEdit"]
```

### MCP Tools

Custom tools must use the full MCP name format.

```python
# Format: mcp__<server_name>__<tool_name>
options = ClaudeAgentOptions(
    allowed_tools=[
        "Read",  # Built-in
        "mcp__utils__calculate",  # Custom tool
        "mcp__database__query_table"  # Custom tool
    ]
)
```

### Read-Only Agent Example

```python
# Safe agent for information gathering only
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep", "WebSearch", "WebFetch"],
    permission_mode="default"
)
```

### Task-Specific Agent Example

```python
# Code review agent - can only read and search
code_review_options = ClaudeAgentOptions(
    system_prompt="You are a code review expert. Analyze code quality and suggest improvements.",
    allowed_tools=["Read", "Glob", "Grep"],
    permission_mode="default"
)

# File processing agent - can read and write
file_processor_options = ClaudeAgentOptions(
    system_prompt="You are a file processing assistant.",
    allowed_tools=["Read", "Write", "Glob", "mcp__analyzer__analyze_file"],
    permission_mode="acceptEdits"
)
```

## Hooks

Hooks provide fine-grained, runtime control over tool execution.

### Hook Types

- **PreToolUse**: Execute before a tool is called (can block execution)
- **PostToolUse**: Execute after a tool completes

### Creating a Security Hook

```python
from claude_agent_sdk import HookContext
from typing import Any

async def security_validator(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Block dangerous commands before execution."""

    if input_data.get('tool_name') == 'Bash':
        command = input_data.get('tool_input', {}).get('command', '')

        # Define dangerous patterns
        dangerous_patterns = [
            'rm -rf /',
            'del /f',
            'format',
            'dd if=',
            'mkfs',
            ':(){:|:&};:',  # Fork bomb
            '> /dev/sda',    # Disk operations
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                print(f"[SECURITY] Blocked dangerous command: {command}")
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': f'Dangerous command blocked: contains "{pattern}"'
                    }
                }

    return {}  # Allow operation
```

### Creating a Logging Hook

```python
async def tool_logger(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Log all tool usage for audit trail."""
    import logging

    tool_name = input_data.get('tool_name', 'unknown')
    tool_input = input_data.get('tool_input', {})

    logging.info(f"Tool called: {tool_name}")

    if tool_name == 'Bash':
        logging.info(f"Command: {tool_input.get('command', 'N/A')}")
    elif tool_name in ['Write', 'Edit']:
        logging.info(f"File: {tool_input.get('file_path', 'N/A')}")

    return {}  # Don't block
```

### Registering Hooks

```python
from claude_agent_sdk import HookMatcher, ClaudeAgentOptions

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            # Security hook specifically for Bash commands
            HookMatcher(matcher='Bash', hooks=[security_validator]),

            # Logging hook for all tools
            HookMatcher(hooks=[tool_logger])
        ]
    }
)
```

### Hook Matchers

**Specific Tool:**
```python
HookMatcher(matcher='Bash', hooks=[bash_security_hook])
```

**All Tools:**
```python
HookMatcher(hooks=[universal_logger])
```

**Multiple Hooks:**
```python
hooks={
    'PreToolUse': [
        HookMatcher(matcher='Bash', hooks=[bash_validator, bash_logger]),
        HookMatcher(matcher='Write', hooks=[file_write_validator]),
        HookMatcher(hooks=[global_audit_logger])
    ]
}
```

### Complete Hook Example

```python
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
    AssistantMessage,
    TextBlock
)
from typing import Any

async def security_validator(input_data, tool_use_id, context):
    """Block dangerous commands."""
    if input_data.get('tool_name') == 'Bash':
        command = input_data.get('tool_input', {}).get('command', '')
        dangerous = ['rm -rf /', 'del /f', 'format', 'dd if=']

        for pattern in dangerous:
            if pattern in command:
                print(f"[SECURITY] Blocked: {command}")
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': f'Blocked: {pattern}'
                    }
                }
    return {}

async def tool_logger(input_data, tool_use_id, context):
    """Log all tool usage."""
    tool_name = input_data.get('tool_name', 'unknown')
    print(f"[AUDIT] Tool used: {tool_name}")
    return {}

async def main():
    options = ClaudeAgentOptions(
        hooks={
            'PreToolUse': [
                HookMatcher(matcher='Bash', hooks=[security_validator]),
                HookMatcher(hooks=[tool_logger])
            ]
        },
        allowed_tools=["Read", "Bash", "Glob"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("List Python files in current directory")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Permission Evaluation Order

Understanding the order of permission evaluation is crucial:

1. **Hooks Execute First** - PreToolUse hooks can block immediately
2. **Deny Rules Checked** - Explicit denials (settings.json)
3. **Permission Modes Applied** - Global mode (default, acceptEdits, etc.)
4. **Allow Rules Checked** - Explicit allows (settings.json)
5. **`canUseTool` Callback** - Final dynamic check (if implemented)

**Example Flow:**

```
Tool Use Request: Bash command "rm -rf /"
    ↓
1. PreToolUse Hook → BLOCKED (dangerous command)
    ↓
2. Evaluation stops, tool not executed
```

```
Tool Use Request: Read "config.json"
    ↓
1. PreToolUse Hook → Pass (logged, not blocked)
    ↓
2. Deny Rules → Pass (not denied)
    ↓
3. Permission Mode → "default" (allowed with confirmation)
    ↓
4. Allow Rules → Pass (reading allowed)
    ↓
5. Tool executes
```

## Security Best Practices

### 1. Principle of Least Privilege

Only grant the minimum tools necessary.

```python
# Good: Specific tools for specific tasks
code_review_options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"]
)

# Bad: All tools when only reading is needed
bad_options = ClaudeAgentOptions(
    permission_mode="bypassPermissions"
)
```

### 2. Layer Security Controls

Use multiple security mechanisms together.

```python
options = ClaudeAgentOptions(
    # Layer 1: Restrict permission mode
    permission_mode="acceptEdits",

    # Layer 2: Whitelist tools
    allowed_tools=["Read", "Write", "Glob"],

    # Layer 3: Add security hooks
    hooks={
        'PreToolUse': [
            HookMatcher(hooks=[security_validator, audit_logger])
        ]
    },

    # Layer 4: Restrict working directory
    cwd="/safe/sandbox/directory"
)
```

### 3. Validate Custom Tool Inputs

```python
@tool("execute_query", "Execute database query", {"query": str})
async def execute_query(args: dict[str, Any]) -> dict[str, Any]:
    query = args["query"].strip()

    # Validation 1: Only SELECT
    if not query.upper().startswith("SELECT"):
        return {
            "content": [{"type": "text", "text": "Error: Only SELECT allowed"}],
            "is_error": True
        }

    # Validation 2: No dangerous keywords
    dangerous = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"]
    if any(keyword in query.upper() for keyword in dangerous):
        return {
            "content": [{"type": "text", "text": "Error: Dangerous keyword detected"}],
            "is_error": True
        }

    # Validation 3: Limit rows
    if "LIMIT" not in query.upper():
        query += " LIMIT 100"

    # Execute safely...
```

### 4. Sanitize File Paths

```python
import os

@tool("read_config", "Read configuration file", {"filename": str})
async def read_config(args: dict[str, Any]) -> dict[str, Any]:
    filename = args["filename"]

    # Validation 1: No path traversal
    if ".." in filename or filename.startswith("/"):
        return {
            "content": [{"type": "text", "text": "Error: Invalid path"}],
            "is_error": True
        }

    # Validation 2: Restrict to config directory
    safe_dir = "/app/config"
    full_path = os.path.join(safe_dir, filename)

    # Validation 3: Ensure path is within safe directory
    if not os.path.abspath(full_path).startswith(safe_dir):
        return {
            "content": [{"type": "text", "text": "Error: Path outside allowed directory"}],
            "is_error": True
        }

    # Read safely...
```

### 5. Use Environment Isolation

```python
import subprocess

@tool("run_script", "Run analysis script", {"script": str})
async def run_script(args: dict[str, Any]) -> dict[str, Any]:
    script = args["script"]

    # Run in isolated environment
    result = subprocess.run(
        ["python", script],
        capture_output=True,
        timeout=30,  # Prevent infinite loops
        cwd="/sandboxed/directory",  # Isolated directory
        env={  # Restricted environment
            "PATH": "/usr/bin",
            "PYTHONPATH": "/sandboxed/libs"
        }
    )

    return {
        "content": [{"type": "text", "text": result.stdout.decode()}]
    }
```

### 6. Implement Rate Limiting

```python
from datetime import datetime, timedelta
from collections import defaultdict

# Simple rate limiter
rate_limits = defaultdict(list)

async def rate_limited_hook(input_data, tool_use_id, context):
    """Limit tool calls per minute."""
    tool_name = input_data.get('tool_name')
    now = datetime.now()

    # Clean old entries
    rate_limits[tool_name] = [
        ts for ts in rate_limits[tool_name]
        if now - ts < timedelta(minutes=1)
    ]

    # Check limit
    if len(rate_limits[tool_name]) >= 10:  # Max 10/min
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': 'Rate limit exceeded'
            }
        }

    # Record this call
    rate_limits[tool_name].append(now)
    return {}
```

## Real-World Security Examples

### Secure Database Agent

```python
options = ClaudeAgentOptions(
    system_prompt="You are a read-only database analyst.",

    # Only allow read operations
    allowed_tools=[
        "mcp__db__list_databases",
        "mcp__db__list_tables",
        "mcp__db__get_schema",
        "mcp__db__query_table"  # SELECT only, enforced in tool
    ],

    # Standard permissions
    permission_mode="default",

    # Security hooks
    hooks={
        'PreToolUse': [
            HookMatcher(hooks=[audit_logger, rate_limiter])
        ]
    }
)
```

### Secure File Processor

```python
import os

options = ClaudeAgentOptions(
    system_prompt="You process files in the data directory only.",

    # File operations only
    allowed_tools=["Read", "Write", "Glob", "mcp__analyzer__analyze_file"],

    # Auto-accept edits (within restricted directory)
    permission_mode="acceptEdits",

    # Restrict to specific directory
    cwd=os.path.abspath("/data/processing"),

    # Security hooks
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='Write', hooks=[validate_write_path]),
            HookMatcher(hooks=[audit_logger])
        ]
    }
)

async def validate_write_path(input_data, tool_use_id, context):
    """Ensure writes only to allowed directory."""
    if input_data.get('tool_name') == 'Write':
        file_path = input_data.get('tool_input', {}).get('file_path', '')

        allowed_dir = "/data/processing"
        abs_path = os.path.abspath(file_path)

        if not abs_path.startswith(allowed_dir):
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': f'Writes only allowed in {allowed_dir}'
                }
            }
    return {}
```

### Secure Code Review Agent

```python
options = ClaudeAgentOptions(
    system_prompt="You are a code review expert. Analyze code quality.",

    # Read-only tools
    allowed_tools=["Read", "Glob", "Grep"],

    # Strictest permission mode
    permission_mode="default",

    # Audit all tool usage
    hooks={
        'PreToolUse': [HookMatcher(hooks=[audit_logger])],
        'PostToolUse': [HookMatcher(hooks=[result_logger])]
    }
)
```

## Summary

**Security Checklist:**

- [ ] Choose appropriate `permission_mode`
- [ ] Whitelist only necessary tools with `allowed_tools`
- [ ] Implement PreToolUse hooks for validation
- [ ] Add audit logging hooks
- [ ] Validate all custom tool inputs
- [ ] Sanitize file paths and prevent traversal
- [ ] Use environment isolation
- [ ] Implement rate limiting
- [ ] Restrict working directory with `cwd`
- [ ] Layer multiple security controls

**Remember:**
- **Defense in Depth**: Use multiple security layers
- **Least Privilege**: Grant minimum necessary permissions
- **Validation**: Never trust inputs
- **Monitoring**: Log and audit tool usage
- **Isolation**: Use sandboxed environments when possible

## Next Steps

- [Advanced Topics](./05-Advanced-Topics.md) - Subagents, context management
- [Examples](./06-Examples-and-Best-Practices.md) - Complete working examples
