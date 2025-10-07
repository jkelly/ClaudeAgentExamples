# Claude Agent SDK - Overview and Getting Started

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Authentication](#authentication)

## Introduction

The Claude Agent SDK is a production-ready toolkit for building AI agents powered by Claude. Built on the same infrastructure that powers Claude Code, the SDK provides:

- **Advanced Context Management**: Automatically manages conversation context and memory
- **Rich Tool Ecosystem**: Built-in tools for file operations, web search, code execution, and more
- **Fine-grained Permissions**: Control exactly what your agent can and cannot do
- **MCP Integration**: Extend with Model Context Protocol for custom capabilities
- **Multi-language Support**: Available in Python and TypeScript

### Supported Agent Types

- **Coding Agents**: SRE, security review, code review, development assistants
- **Business Agents**: Legal analysis, finance, customer support
- **Research Agents**: Data analysis, information gathering
- **Personal Assistants**: Task automation, workflow optimization

## Installation

### Python

```bash
pip install claude-agent-sdk
```

**Requirements:**
- Python 3.10 or higher
- Claude Code CLI (install with: `npm install -g @anthropic-ai/claude-code`)

### TypeScript/JavaScript

```bash
npm install @anthropic-ai/claude-agent-sdk
```

## Prerequisites

Before using the SDK, you need:

1. **Claude API Key** (from [Claude Console](https://console.anthropic.com/))
2. **Claude Code CLI** installed and configured
3. API key set in your environment or through Claude Code Pro/Max plan

## Quick Start

### Python: Simple Query

```python
import asyncio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

if __name__ == "__main__":
    asyncio.run(main())
```

### Python: Conversational Agent

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def main():
    async with ClaudeSDKClient() as client:
        # First question
        await client.query("What's the capital of France?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up question - Claude remembers context
        await client.query("What's the population of that city?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Concepts

### 1. Agent Options

Configure agent behavior using `ClaudeAgentOptions`:

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt="You are an expert Python developer",
    permission_mode='acceptEdits',
    allowed_tools=["Read", "Write", "Bash"],
    max_turns=10,
    cwd="/path/to/working/directory"
)
```

**Key Options:**
- `system_prompt`: Define agent's role and behavior
- `permission_mode`: Control tool permissions (`default`, `acceptEdits`, `bypassPermissions`)
- `allowed_tools`: Whitelist specific tools
- `mcp_servers`: Register custom MCP servers
- `max_turns`: Limit conversation length
- `cwd`: Set working directory

### 2. Query vs Client

**`query()` - Simple Queries:**
- Best for one-shot questions
- Stateless interactions
- Simpler API

**`ClaudeSDKClient` - Conversational:**
- Maintains context across multiple queries
- Persistent sessions
- Full control over message flow

### 3. Message Types

The SDK uses typed messages for structured communication:

- **AssistantMessage**: Claude's responses
- **TextBlock**: Text content within messages
- **ToolUseBlock**: Tool invocations
- **ToolResultBlock**: Tool execution results

### 4. Input Modes

**Streaming Input Mode (Recommended):**
- Persistent, interactive sessions
- Supports images, queued messages, hooks
- Full agent capabilities
- Real-time feedback

**Single Message Input:**
- One-shot responses
- Simpler but more limited
- Best for stateless environments (e.g., Lambda functions)

## Authentication

The SDK supports three authentication methods:

### 1. Claude Console API Key (Primary)

```python
# Set environment variable
export ANTHROPIC_API_KEY=your_api_key

# Or configure in Claude Code
```

### 2. Amazon Bedrock

For AWS-hosted Claude models:

```python
# Configure AWS credentials
# Use Bedrock-specific endpoints
```

### 3. Google Vertex AI

For Google Cloud-hosted Claude models:

```python
# Configure GCP credentials
# Use Vertex AI-specific endpoints
```

## Agent Development Loop

The recommended approach for building agents:

1. **Gather Context**
   - Use file system for information storage
   - Leverage "agentic search" to find relevant data
   - Utilize subagents for parallel processing

2. **Take Action**
   - Design specific tools as primary agent actions
   - Use bash scripts for flexible computer interactions
   - Generate code for complex operations

3. **Verify Work**
   - Define clear rules for output
   - Use visual feedback when applicable
   - Optionally use another LLM to judge output

4. **Iterate**
   - Test agent performance
   - Analyze failure points
   - Continuously refine tools and search capabilities

## Next Steps

- [API Reference](./02-API-Reference.md) - Detailed API documentation
- [Custom Tools Guide](./03-Custom-Tools-and-MCP.md) - Create custom tools and MCP servers
- [Permissions Guide](./04-Permissions-and-Security.md) - Secure your agents
- [Advanced Topics](./05-Advanced-Topics.md) - Subagents, hooks, and more
- [Examples](./06-Examples-and-Best-Practices.md) - Practical examples

## Resources

- [Official Documentation](https://docs.claude.com/en/docs/claude-code/sdk/sdk-overview)
- [GitHub - TypeScript SDK](https://github.com/anthropics/claude-agent-sdk)
- [GitHub - Python SDK](https://github.com/anthropics/claude-agent-sdk-python)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic API Docs](https://docs.anthropic.com/)
