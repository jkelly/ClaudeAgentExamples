# Claude Agent SDK - Examples and Best Practices

## Table of Contents
- [Complete Working Examples](#complete-working-examples)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

## Complete Working Examples

### Example 1: Interactive Chatbot

A fully interactive chatbot with conversation history.

```python
"""
Interactive Chatbot with Claude Agent SDK
"""
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock
)

async def interactive_chatbot():
    """Run an interactive chatbot session."""
    print("="*60)
    print("Claude Agent Chatbot")
    print("="*60)
    print("Type 'exit' or 'quit' to end the session\n")

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful, friendly assistant. Be concise and clear.",
        allowed_tools=["WebSearch", "WebFetch"],
        permission_mode="default"
    )

    async with ClaudeSDKClient(options=options) as client:
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue

                await client.query(user_input)

                print("Claude: ", end="", flush=True)
                response_texts = []

                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                response_texts.append(block.text)

                if response_texts:
                    print("\n".join(response_texts))
                else:
                    print("[No text response]")

            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Continuing session...")

if __name__ == "__main__":
    try:
        asyncio.run(interactive_chatbot())
    except KeyboardInterrupt:
        print("\nExiting...")
```

### Example 2: Code Review Agent

Automated code review with multiple specialized subagents.

```python
"""
Code Review Agent with Subagents
"""
import asyncio
import os
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock
)

async def code_review_agent(file_path: str):
    """Perform comprehensive code review."""

    options = ClaudeAgentOptions(
        system_prompt="You coordinate code review by delegating to specialized reviewers.",

        # Define specialized subagents
        agents=[
            {
                "name": "style_reviewer",
                "description": "Review code style, formatting, and PEP 8 compliance",
                "prompt": "You are a Python style expert. Review code for PEP 8 compliance, "
                         "naming conventions, and formatting. Be specific about violations.",
                "tools": ["Read", "Grep"]
            },
            {
                "name": "logic_reviewer",
                "description": "Review code logic, algorithms, and potential bugs",
                "prompt": "You are a logic and algorithm expert. Identify potential bugs, "
                         "edge cases, and logical errors. Suggest improvements.",
                "tools": ["Read", "Grep"]
            },
            {
                "name": "security_reviewer",
                "description": "Review code for security vulnerabilities",
                "prompt": "You are a security expert. Identify security vulnerabilities, "
                         "unsafe patterns, and suggest secure alternatives.",
                "tools": ["Read", "Grep"]
            }
        ],

        allowed_tools=["Read", "Grep", "Glob"],
        permission_mode="default",
        cwd=os.path.dirname(os.path.abspath(file_path))
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            f"Perform a comprehensive code review of {os.path.basename(file_path)}. "
            f"Use your specialized reviewers to check style, logic, and security."
        )

        print(f"Code Review Results for {file_path}")
        print("="*60)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                        print()

async def main():
    # Review a specific file
    await code_review_agent("src/authentication.py")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: Database Query Assistant

Safe database querying with custom tools.

```python
"""
Database Query Assistant with Custom Tools
"""
import asyncio
import pyodbc
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
    HookMatcher
)
from typing import Any

# Custom database tools
@tool("list_databases", "List all databases on the server", {"server": str})
async def list_databases(args: dict[str, Any]) -> dict[str, Any]:
    """List all databases."""
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
                "text": f"Databases:\n" + "\n".join(f"  - {db}" for db in databases)
            }]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "is_error": True
        }

@tool("query_table", "Execute SELECT query (max 100 rows)",
      {"server": str, "database": str, "query": str})
async def query_table(args: dict[str, Any]) -> dict[str, Any]:
    """Execute a SELECT query."""
    server = args.get("server", "localhost")
    database = args["database"]
    query = args["query"]

    # Security: Only SELECT
    if not query.strip().upper().startswith("SELECT"):
        return {
            "content": [{"type": "text", "text": "Error: Only SELECT queries allowed"}],
            "is_error": True
        }

    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        # Limit to 100 rows
        if "TOP" not in query.upper():
            query = query.replace("SELECT", "SELECT TOP 100", 1)

        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        # Format results
        result = f"Results ({len(rows)} rows):\n\n"
        result += " | ".join(columns) + "\n"
        result += "-" * 50 + "\n"
        for row in rows:
            result += " | ".join(str(val) if val else "NULL" for val in row) + "\n"

        return {"content": [{"type": "text", "text": result}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "is_error": True
        }

# Audit hook
async def audit_logger(input_data, tool_use_id, context):
    """Log all database operations."""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    tool_name = input_data.get('tool_name')
    tool_input = input_data.get('tool_input', {})

    if 'query' in tool_input:
        logger.info(f"Query executed: {tool_input['query']}")

    return {}

async def main():
    # Create MCP server
    db_server = create_sdk_mcp_server(
        name="database",
        version="1.0.0",
        tools=[list_databases, query_table]
    )

    options = ClaudeAgentOptions(
        system_prompt="You are a database assistant. Help users query databases safely. "
                     "Always use SELECT queries only. Default server is 'localhost'.",
        mcp_servers={"db": db_server},
        allowed_tools=[
            "mcp__db__list_databases",
            "mcp__db__query_table"
        ],
        hooks={
            'PreToolUse': [HookMatcher(hooks=[audit_logger])]
        },
        permission_mode="default"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("List all databases on the server")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 4: File Processor with Hooks

Secure file processing with validation hooks.

```python
"""
File Processor with Security Hooks
"""
import asyncio
import os
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock
)
from typing import Any

# Custom file analysis tool
@tool("analyze_file", "Analyze file statistics", {"file_path": str})
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
                "text": f"File: {file_path}\n"
                       f"Lines: {lines}\n"
                       f"Words: {words}\n"
                       f"Characters: {chars}\n"
                       f"Size: {os.path.getsize(file_path)} bytes"
            }]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "is_error": True
        }

# Security hooks
async def validate_file_access(input_data, tool_use_id, context):
    """Validate file operations are within allowed directory."""
    tool_name = input_data.get('tool_name')

    if tool_name in ['Read', 'Write', 'Edit']:
        file_path = input_data.get('tool_input', {}).get('file_path', '')
        allowed_dir = "/safe/directory"

        abs_path = os.path.abspath(file_path)

        if not abs_path.startswith(allowed_dir):
            print(f"[SECURITY] Blocked access to: {file_path}")
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': f'File access restricted to {allowed_dir}'
                }
            }

    return {}

async def log_file_operations(input_data, tool_use_id, context):
    """Log all file operations."""
    tool_name = input_data.get('tool_name')
    tool_input = input_data.get('tool_input', {})

    if tool_name in ['Read', 'Write', 'Edit']:
        file_path = tool_input.get('file_path', 'N/A')
        print(f"[AUDIT] {tool_name} operation on: {file_path}")

    return {}

async def main():
    # Create MCP server
    analyzer = create_sdk_mcp_server(
        name="file_analyzer",
        version="1.0.0",
        tools=[analyze_file]
    )

    options = ClaudeAgentOptions(
        system_prompt="You are a file processing assistant.",
        mcp_servers={"analyzer": analyzer},
        allowed_tools=[
            "Read", "Write", "Glob", "Grep",
            "mcp__analyzer__analyze_file"
        ],
        hooks={
            'PreToolUse': [
                HookMatcher(matcher='Read', hooks=[validate_file_access]),
                HookMatcher(matcher='Write', hooks=[validate_file_access]),
                HookMatcher(hooks=[log_file_operations])
            ]
        },
        permission_mode="acceptEdits",
        cwd="/safe/directory"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Analyze all Python files in the current directory")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 5: Batch Processing

Process multiple items with error handling and progress tracking.

```python
"""
Batch Processing with Error Handling
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, CLINotFoundError, ProcessError
from typing import List, Dict

async def process_item(item: str) -> Dict[str, any]:
    """Process a single item."""
    try:
        result_text = ""
        async for message in query(
            prompt=f"Analyze this text: {item}",
            options=ClaudeAgentOptions(max_turns=2)
        ):
            result_text += str(message)

        return {
            "item": item,
            "status": "success",
            "result": result_text
        }

    except Exception as e:
        return {
            "item": item,
            "status": "error",
            "error": str(e)
        }

async def batch_process(items: List[str]) -> List[Dict[str, any]]:
    """Process multiple items concurrently."""
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "item": items[i],
                "status": "error",
                "error": str(result)
            })
        else:
            processed_results.append(result)

    return processed_results

async def main():
    items = [
        "The quick brown fox",
        "Python programming",
        "Machine learning",
        "Data science"
    ]

    print(f"Processing {len(items)} items...")

    results = await batch_process(items)

    # Print summary
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")

    print(f"\nResults:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")

    # Print details
    for result in results:
        print(f"\nItem: {result['item']}")
        print(f"Status: {result['status']}")
        if result['status'] == 'error':
            print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Common Patterns

### Pattern 1: Simple Query Pattern

For one-off questions:

```python
from claude_agent_sdk import query

async def ask_question(question: str) -> str:
    async for message in query(prompt=question):
        return str(message)
```

### Pattern 2: Conversational Pattern

For multi-turn conversations:

```python
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def conversation():
    async with ClaudeSDKClient() as client:
        queries = ["First question", "Follow-up", "Another follow-up"]

        for q in queries:
            await client.query(q)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text)
```

### Pattern 3: Custom Tool Pattern

For extending capabilities:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("my_tool", "Description", {"param": str})
async def my_tool(args):
    # Implementation
    return {"content": [{"type": "text", "text": "result"}]}

server = create_sdk_mcp_server("my_server", "1.0.0", [my_tool])

options = ClaudeAgentOptions(
    mcp_servers={"my": server},
    allowed_tools=["mcp__my__my_tool"]
)
```

### Pattern 4: Security Hook Pattern

For validation and auditing:

```python
from claude_agent_sdk import HookMatcher, ClaudeAgentOptions

async def security_hook(input_data, tool_use_id, context):
    # Validation logic
    if should_block(input_data):
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': 'Security policy violation'
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={'PreToolUse': [HookMatcher(hooks=[security_hook])]}
)
```

### Pattern 5: Subagent Pattern

For specialized tasks:

```python
options = ClaudeAgentOptions(
    agents=[
        {
            "name": "specialist",
            "description": "When to use this specialist",
            "prompt": "Specialized instructions",
            "tools": ["Read", "Grep"]
        }
    ]
)
```

## Best Practices

### 1. Agent Design

**✅ Do:**
- Define clear, specific system prompts
- Use descriptive tool names and descriptions
- Validate all inputs in custom tools
- Handle errors gracefully

**❌ Don't:**
- Use vague system prompts
- Create overly complex, multi-purpose tools
- Trust user inputs without validation
- Let exceptions bubble up unhandled

### 2. Security

**✅ Do:**
- Use permission modes appropriately
- Whitelist only necessary tools
- Implement security hooks for sensitive operations
- Sanitize file paths and prevent traversal
- Log all tool usage for auditing

**❌ Don't:**
- Use `bypassPermissions` in production without isolation
- Allow unrestricted bash access
- Trust file paths without validation
- Skip input validation in custom tools

### 3. Performance

**✅ Do:**
- Use streaming mode for interactive applications
- Limit conversation length with `max_turns`
- Use subagents for parallel processing
- Store context in files for long conversations

**❌ Don't:**
- Hold entire conversation context indefinitely
- Create synchronous blocking operations
- Process items sequentially when parallel is possible

### 4. Error Handling

**✅ Do:**
- Catch specific exceptions (CLINotFoundError, ProcessError)
- Provide meaningful error messages
- Implement retry logic for transient failures
- Log errors for debugging

**❌ Don't:**
- Use bare except clauses
- Ignore errors silently
- Retry on non-transient errors (e.g., CLINotFoundError)

### 5. Tool Design

**✅ Do:**
- Keep tools focused on single responsibilities
- Provide rich, structured output
- Include error information with `is_error: True`
- Write clear descriptions for Claude to understand

**❌ Don't:**
- Create monolithic tools that do everything
- Return bare strings without structure
- Use generic error messages
- Rely on tool names alone (descriptions matter)

## Troubleshooting

### Issue: CLINotFoundError

**Problem:** Claude Code CLI not installed or not in PATH.

**Solution:**
```bash
npm install -g @anthropic-ai/claude-code
```

### Issue: Authentication Errors

**Problem:** API key not configured.

**Solution:**
```bash
# Set environment variable
export ANTHROPIC_API_KEY=your_key_here

# Or configure via Claude Code
claude-code config
```

### Issue: Tool Not Found

**Problem:** Custom tool not accessible.

**Checklist:**
1. Tool registered in MCP server? ✓
2. MCP server added to `mcp_servers`? ✓
3. Tool added to `allowed_tools` with correct format? ✓
4. Format: `mcp__<server_name>__<tool_name>` ✓

**Example:**
```python
# Correct
allowed_tools=["mcp__utils__calculate"]

# Wrong
allowed_tools=["calculate"]  # Missing MCP prefix
```

### Issue: Context Window Full

**Problem:** Conversation too long.

**Solutions:**
1. Set `max_turns` limit
2. Use subagents for separate contexts
3. Summarize and restart conversation
4. Store information in files

```python
options = ClaudeAgentOptions(
    max_turns=10  # Limit conversation length
)
```

### Issue: Permission Denied

**Problem:** Tool blocked by permissions.

**Solutions:**
1. Check `permission_mode`
2. Verify tool in `allowed_tools`
3. Check security hooks
4. Review `cwd` restrictions

```python
# Debug permissions
options = ClaudeAgentOptions(
    permission_mode="default",  # Try different modes
    allowed_tools=["Read", "Write"],  # Verify tool included
    hooks={}  # Temporarily disable hooks to debug
)
```

### Issue: Slow Performance

**Problem:** Agent responds slowly.

**Solutions:**
1. Use parallel subagents
2. Limit `max_turns`
3. Use simpler tools
4. Reduce context size

```python
# Use subagents for parallel processing
options = ClaudeAgentOptions(
    agents=[
        {"name": "worker1", ...},
        {"name": "worker2", ...}
    ]
)
```

## Performance Optimization

### 1. Use Appropriate Modes

```python
# Streaming for interactive
async with ClaudeSDKClient() as client:
    # Interactive conversation
    pass

# Single message for batch
async for message in query(prompt="Analyze"):
    # One-off processing
    pass
```

### 2. Parallel Processing

```python
# Process items in parallel
tasks = [process_item(item) for item in items]
results = await asyncio.gather(*tasks)
```

### 3. Context Management

```python
# Limit context
options = ClaudeAgentOptions(max_turns=10)

# Use files for persistence
await client.query("Save analysis to analysis.md")
# Later: "Read analysis.md and continue"
```

### 4. Tool Optimization

```python
# Efficient tool design
@tool("efficient_search", "Description", {"pattern": str, "limit": int})
async def efficient_search(args):
    # Limit results
    limit = args.get("limit", 100)
    results = search(args["pattern"])[:limit]
    return {"content": [{"type": "text", "text": format_results(results)}]}
```

### 5. Subagent Parallelization

```python
# Multiple subagents run in parallel
options = ClaudeAgentOptions(
    agents=[
        {"name": "analyzer1", "description": "Analyze data", ...},
        {"name": "analyzer2", "description": "Analyze logs", ...},
        {"name": "analyzer3", "description": "Analyze metrics", ...}
    ]
)

# Main agent can invoke all simultaneously
await client.query("Analyze data, logs, and metrics in parallel")
```

## Summary

**Key Takeaways:**
- Start with simple patterns, add complexity as needed
- Always validate inputs and handle errors
- Use multiple security layers
- Choose the right pattern for your use case
- Monitor and log in production
- Optimize for performance when needed

**Resource Checklist:**
- [ ] Clear system prompts
- [ ] Input validation in custom tools
- [ ] Error handling with specific exceptions
- [ ] Security hooks for sensitive operations
- [ ] Appropriate permission modes
- [ ] Logging and monitoring
- [ ] Performance optimization for scale

## Next Steps

1. Review [SDK Overview](./01-SDK-Overview-and-Getting-Started.md) for basics
2. Study [API Reference](./02-API-Reference.md) for details
3. Build custom tools with [Custom Tools Guide](./03-Custom-Tools-and-MCP.md)
4. Secure your agent with [Permissions Guide](./04-Permissions-and-Security.md)
5. Scale with [Advanced Topics](./05-Advanced-Topics.md)
6. Use these examples as templates for your use case

## Resources

- [Claude Agent SDK GitHub](https://github.com/anthropics/claude-agent-sdk)
- [Official Documentation](https://docs.claude.com/en/docs/claude-code/sdk/sdk-overview)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Sample Repository](https://github.com/jkelly/ClaudeAgentExamples)
