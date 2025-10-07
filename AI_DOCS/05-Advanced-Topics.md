# Claude Agent SDK - Advanced Topics

## Table of Contents
- [Subagents](#subagents)
- [System Prompts and Configuration](#system-prompts-and-configuration)
- [Streaming vs Single Message Mode](#streaming-vs-single-message-mode)
- [Context Management](#context-management)
- [Error Handling](#error-handling)
- [Production Deployment](#production-deployment)

## Subagents

Subagents are specialized AI agents orchestrated by the main agent. They provide several powerful benefits for complex workflows.

### Why Use Subagents?

**1. Context Management**
- Maintain separate contexts from the main agent
- Prevent information overload
- Keep interactions focused on specific tasks

**2. Parallelization**
- Run multiple subagents concurrently
- Dramatically speed up complex workflows
- Example: Simultaneously run code review, security scan, and test coverage

**3. Specialized Instructions**
- Tailored system prompts for specific expertise
- Reduce noise in main agent's instructions
- Provide domain-specific constraints

**4. Tool Restrictions**
- Limit subagents to specific tools
- Reduce risk of unintended actions
- Control capabilities per task

### Defining Subagents

Two primary methods:

#### 1. Programmatic Definition (Recommended)

Define subagents directly in code:

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    agents=[
        {
            "name": "code_reviewer",
            "description": "Review code for quality, best practices, and potential bugs",
            "prompt": "You are an expert code reviewer. Focus on code quality, "
                     "maintainability, and potential bugs. Provide specific, "
                     "actionable feedback.",
            "tools": ["Read", "Grep", "Glob"],
            "model": "claude-sonnet-4-5-20250929"  # Optional
        },
        {
            "name": "security_scanner",
            "description": "Scan code for security vulnerabilities",
            "prompt": "You are a security expert. Identify potential security "
                     "vulnerabilities, unsafe patterns, and suggest fixes.",
            "tools": ["Read", "Grep", "Glob"]
        },
        {
            "name": "test_coverage_analyzer",
            "description": "Analyze test coverage and suggest improvements",
            "prompt": "You are a testing expert. Analyze test coverage and "
                     "identify untested code paths.",
            "tools": ["Read", "Grep", "Bash"]
        }
    ]
)
```

**Configuration Options:**
- `name`: Unique identifier for the subagent
- `description`: When to use this agent (main agent uses this)
- `prompt`: System prompt for the subagent
- `tools`: List of allowed tools (subset of main agent's tools)
- `model` (optional): Override model for this subagent

#### 2. Filesystem-Based Definition

Create markdown files in `.claude/agents/` directory:

**`.claude/agents/code_reviewer.md`:**
```markdown
---
description: Review code for quality and best practices
tools:
  - Read
  - Grep
  - Glob
---

You are an expert code reviewer. Focus on:
- Code quality and maintainability
- Best practices and patterns
- Potential bugs and edge cases

Provide specific, actionable feedback.
```

**`.claude/agents/security_scanner.md`:**
```markdown
---
description: Scan code for security vulnerabilities
tools:
  - Read
  - Grep
---

You are a security expert. Identify:
- SQL injection risks
- XSS vulnerabilities
- Authentication issues
- Data exposure risks

Suggest specific fixes.
```

### Using Subagents

The SDK automatically detects and invokes subagents based on task context.

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
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

    async with ClaudeSDKClient(options=options) as client:
        # Main agent will automatically invoke code_reviewer subagent
        await client.query("Review the authentication code in src/auth.py")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

if __name__ == "__main__":
    asyncio.run(main())
```

### Parallel Subagent Execution

```python
# Main agent can invoke multiple subagents in parallel
options = ClaudeAgentOptions(
    agents=[
        {
            "name": "code_reviewer",
            "description": "Review code quality",
            "prompt": "Expert code reviewer",
            "tools": ["Read", "Grep"]
        },
        {
            "name": "security_scanner",
            "description": "Scan for security issues",
            "prompt": "Security expert",
            "tools": ["Read", "Grep"]
        },
        {
            "name": "performance_analyzer",
            "description": "Analyze performance",
            "prompt": "Performance expert",
            "tools": ["Read", "Bash"]
        }
    ]
)

# Main agent can run all three in parallel
await client.query(
    "Analyze src/app.py for code quality, security, and performance issues"
)
```

### Subagent Best Practices

**1. Clear, Specific Descriptions**

The main agent uses descriptions to decide when to invoke subagents.

```python
# Good: Specific and actionable
"description": "Review Python code for PEP 8 compliance and best practices"

# Bad: Too vague
"description": "Help with code"
```

**2. Appropriate Tool Restrictions**

```python
# Code reviewer doesn't need write access
{
    "name": "code_reviewer",
    "tools": ["Read", "Grep", "Glob"]  # Read-only
}

# Test runner needs bash access
{
    "name": "test_runner",
    "tools": ["Read", "Bash"]  # Can execute tests
}
```

**3. Focused System Prompts**

```python
# Good: Specific expertise and constraints
{
    "prompt": "You are a Python security expert. Focus only on security "
             "vulnerabilities. Do not comment on code style or performance."
}

# Bad: Too general
{
    "prompt": "You help with code"
}
```

## System Prompts and Configuration

### Four Methods to Modify System Prompts

#### 1. CLAUDE.md Files (Project-Level)

Create a `CLAUDE.md` file in your project directory:

**`CLAUDE.md`:**
```markdown
# Project Guidelines

This is a Python web application using FastAPI.

## Code Standards
- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Prefer async/await for I/O operations

## Testing
- Write pytest tests for all new features
- Maintain >80% code coverage
```

**Enable in code:**
```python
options = ClaudeAgentOptions(
    settingSources=['project']  # Load CLAUDE.md
)
```

#### 2. Output Styles (Reusable Configurations)

Saved configurations in `~/.claude/output-styles/`.

**Create an output style:**
```markdown
# Python Expert Style

You are an expert Python developer specializing in:
- Clean, maintainable code
- Type safety with mypy
- Comprehensive testing
- Performance optimization

Always provide type hints and docstrings.
```

**Use in code:**
```python
# Activate via settings or specify in options
options = ClaudeAgentOptions(
    output_style="python_expert"
)
```

#### 3. Append to System Prompt

Add to Claude's default prompt without replacing it:

```python
options = ClaudeAgentOptions(
    system_prompt="Additional instructions: Always use type hints. "
                 "Prefer composition over inheritance. "
                 "Write comprehensive docstrings.",
    append_to_system_prompt=True  # Preserve default prompt
)
```

#### 4. Complete Custom System Prompt

Replace the default system prompt entirely:

```python
options = ClaudeAgentOptions(
    system_prompt="""You are a Python expert assistant.

Capabilities:
- You can read and write files
- You can execute bash commands
- You can search the web

Guidelines:
- Always validate inputs
- Provide type hints
- Write clear, maintainable code
- Include error handling

When using tools:
- Read: Read file contents
- Write: Create or overwrite files
- Bash: Execute shell commands
- Grep: Search file contents
"""
)
```

**Warning:** You must include tool instructions when replacing the system prompt.

### Choosing the Right Method

| Method | Use Case |
|--------|----------|
| CLAUDE.md | Team-wide project guidelines |
| Output Styles | Reusable persona configurations |
| Append | Add specific preferences |
| Custom | Complete control, custom instructions |

## Streaming vs Single Message Mode

### Streaming Input Mode (Recommended)

Persistent, interactive sessions with full capabilities.

```python
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def streaming_example():
    async with ClaudeSDKClient() as client:
        # Send first query
        await client.query("What's the capital of France?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

        # Send follow-up (context preserved)
        await client.query("What's its population?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
```

**Advantages:**
- Image uploads supported
- Queued messages
- Tool integration
- Lifecycle hooks
- Real-time feedback
- Context persistence across multiple queries

**Best for:**
- Interactive applications
- Multi-turn conversations
- Complex workflows
- Real-time user interaction

### Single Message Mode

Simpler, one-shot responses.

```python
from claude_agent_sdk import query

async def single_message_example():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)
```

**Limitations:**
- No image attachments
- No dynamic message queuing
- No real-time interruption
- No hook integration
- Limited multi-turn conversation

**Best for:**
- Stateless environments (Lambda functions)
- Simple queries
- No conversation context needed
- Batch processing

### When to Use Each

```python
# Use Streaming for interactive chat
async with ClaudeSDKClient() as client:
    while True:
        user_input = input("You: ")
        await client.query(user_input)
        async for message in client.receive_response():
            # Process response
            pass

# Use Single Message for batch processing
async def process_items(items):
    for item in items:
        async for message in query(prompt=f"Analyze: {item}"):
            save_result(message)
```

## Context Management

### Managing Conversation Context

**Context automatically persists** within a `ClaudeSDKClient` session:

```python
async with ClaudeSDKClient() as client:
    # Query 1
    await client.query("My favorite color is blue")
    # ... process response

    # Query 2 - Claude remembers previous context
    await client.query("What's my favorite color?")
    # Claude will answer: "blue"
```

### Context Limits

**Managing Long Conversations:**

```python
options = ClaudeAgentOptions(
    max_turns=10  # Limit conversation length
)
```

**Context Compaction Strategies:**
1. Limit `max_turns`
2. Use subagents for separate contexts
3. Summarize and restart conversation
4. Use file system for persistent data

### Using File System for Context

```python
# Store context in files instead of conversation
await client.query(
    "Analyze the user data and save a summary to analysis.md"
)

# Later, reference the file
await client.query(
    "Read analysis.md and suggest improvements"
)
```

### Subagents for Context Isolation

```python
options = ClaudeAgentOptions(
    agents=[
        {
            "name": "data_analyzer",
            "description": "Analyze data files",
            "prompt": "You analyze data. Keep analysis focused.",
            "tools": ["Read", "Bash"]
        }
    ]
)

# Main agent delegates to subagent
# Subagent has its own context, separate from main
await client.query("Analyze data.csv for trends")
```

## Error Handling

### Exception Types

```python
from claude_agent_sdk import CLINotFoundError, ProcessError, CLIJSONDecodeError

try:
    async for message in query(prompt="Hello"):
        print(message)

except CLINotFoundError:
    print("ERROR: Claude Code CLI not found!")
    print("Install with: npm install -g @anthropic-ai/claude-code")

except ProcessError as e:
    print(f"ERROR: CLI process failed with exit code: {e.exit_code}")
    print(f"stderr: {e.stderr}")

except CLIJSONDecodeError as e:
    print(f"ERROR: Failed to parse CLI response: {e}")

except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
```

### Graceful Degradation

```python
async def resilient_query(prompt: str):
    """Query with fallback behavior."""
    try:
        async for message in query(prompt=prompt):
            return message

    except CLINotFoundError:
        return "ERROR: Claude Code not available. Please install the CLI."

    except ProcessError as e:
        if e.exit_code == 1:
            return "ERROR: Claude Code encountered an error. Check your API key."
        else:
            return f"ERROR: Unexpected process error: {e.stderr}"

    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"
```

### Retry Logic

```python
import asyncio

async def query_with_retry(prompt: str, max_retries: int = 3):
    """Query with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            async for message in query(prompt=prompt):
                return message

        except ProcessError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1}/{max_retries} in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise

        except CLINotFoundError:
            # Don't retry if CLI not found
            raise
```

### Tool-Specific Error Handling

```python
from claude_agent_sdk import tool
from typing import Any

@tool("safe_divide", "Divide two numbers", {"a": float, "b": float})
async def safe_divide(args: dict[str, Any]) -> dict[str, Any]:
    """Divide with error handling."""
    try:
        a = args["a"]
        b = args["b"]

        if b == 0:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Division by zero"
                }],
                "is_error": True
            }

        result = a / b
        return {
            "content": [{
                "type": "text",
                "text": f"Result: {result}"
            }]
        }

    except (KeyError, TypeError) as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Invalid input: {e}"
            }],
            "is_error": True
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Unexpected error: {e}"
            }],
            "is_error": True
        }
```

## Production Deployment

### Environment Configuration

```python
import os
from claude_agent_sdk import ClaudeAgentOptions

# Load from environment
options = ClaudeAgentOptions(
    permission_mode=os.getenv("AGENT_PERMISSION_MODE", "default"),
    cwd=os.getenv("AGENT_WORKING_DIR", os.getcwd()),
    max_turns=int(os.getenv("AGENT_MAX_TURNS", "20"))
)
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

# Install Node.js for Claude Code CLI
RUN apt-get update && apt-get install -y nodejs npm

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Run agent
CMD ["python", "agent.py"]
```

**requirements.txt:**
```
claude-agent-sdk>=0.1.0
```

### Monitoring and Logging

```python
import logging
from claude_agent_sdk import HookMatcher, ClaudeAgentOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Logging hook
async def production_logger(input_data, tool_use_id, context):
    """Production logging hook."""
    tool_name = input_data.get('tool_name')
    logger.info(f"Tool invoked: {tool_name}", extra={
        'tool_name': tool_name,
        'tool_use_id': tool_use_id,
        'input': input_data.get('tool_input')
    })
    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [HookMatcher(hooks=[production_logger])]
    }
)
```

### Health Checks

```python
from claude_agent_sdk import query, CLINotFoundError

async def health_check() -> bool:
    """Check if agent is operational."""
    try:
        async for message in query(prompt="ping", options=ClaudeAgentOptions(max_turns=1)):
            return True
    except CLINotFoundError:
        return False
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
```

### Rate Limiting in Production

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_calls: int, period: timedelta):
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)

    async def check(self, key: str) -> bool:
        """Check if rate limit is exceeded."""
        now = datetime.now()

        # Clean old entries
        self.calls[key] = [
            ts for ts in self.calls[key]
            if now - ts < self.period
        ]

        # Check limit
        if len(self.calls[key]) >= self.max_calls:
            return False

        self.calls[key].append(now)
        return True

# Usage
limiter = RateLimiter(max_calls=100, period=timedelta(minutes=1))

async def rate_limited_hook(input_data, tool_use_id, context):
    tool_name = input_data.get('tool_name')

    if not await limiter.check(tool_name):
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': 'Rate limit exceeded'
            }
        }
    return {}
```

## Summary

**Advanced Features:**
- ✅ Subagents for specialization and parallelization
- ✅ System prompt customization (4 methods)
- ✅ Streaming for interactive, single message for simple
- ✅ Context management strategies
- ✅ Comprehensive error handling
- ✅ Production-ready deployment patterns

**Next Steps:**
- [Examples and Best Practices](./06-Examples-and-Best-Practices.md) - Complete working examples

## Resources

- [Official Documentation](https://docs.claude.com/en/docs/claude-code/sdk/sdk-overview)
- [Subagents Guide](https://docs.claude.com/en/docs/claude-code/sdk/subagents)
- [System Prompts Guide](https://docs.claude.com/en/docs/claude-code/sdk/modifying-system-prompts)
