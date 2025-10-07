# Claude Agent SDK - Complete Documentation

This folder contains comprehensive documentation for the Claude Agent SDK, created from official documentation and practical examples.

## Documentation Structure

### 1. [SDK Overview and Getting Started](./01-SDK-Overview-and-Getting-Started.md)
**Start here if you're new to the SDK**

- Introduction to the Claude Agent SDK
- Installation and prerequisites
- Quick start examples
- Core concepts (Agent Options, Query vs Client, Message Types)
- Authentication methods
- Agent development loop

### 2. [API Reference](./02-API-Reference.md)
**Complete API documentation**

- Core functions (`query()`, `ClaudeSDKClient`)
- Configuration objects (`ClaudeAgentOptions`)
- Message types (`AssistantMessage`, `TextBlock`, etc.)
- Tool decorators (`@tool`, `create_sdk_mcp_server()`)
- Hook types (`HookMatcher`, `HookContext`)
- Exception handling (CLINotFoundError, ProcessError, etc.)
- Complete code examples

### 3. [Custom Tools and MCP](./03-Custom-Tools-and-MCP.md)
**Extend Claude's capabilities**

- Creating custom tools with `@tool` decorator
- Tool design best practices
- MCP (Model Context Protocol) servers
- SDK MCP servers (in-app)
- External MCP servers (stdio, HTTP/SSE)
- Tool naming conventions
- Real-world examples (database tools, file processing)

### 4. [Permissions and Security](./04-Permissions-and-Security.md)
**Secure your agents**

- Permission modes (default, acceptEdits, bypassPermissions)
- Allowed tools whitelisting
- Hooks for security validation
- Permission evaluation order
- Security best practices
- Input validation and sanitization
- Real-world security examples

### 5. [Advanced Topics](./05-Advanced-Topics.md)
**Advanced features and patterns**

- Subagents (specialization and parallelization)
- System prompts and configuration (4 methods)
- Streaming vs Single Message mode
- Context management strategies
- Error handling patterns
- Production deployment
- Monitoring and logging
- Rate limiting

### 6. [Examples and Best Practices](./06-Examples-and-Best-Practices.md)
**Complete working examples**

- Interactive chatbot
- Code review agent with subagents
- Database query assistant
- File processor with security hooks
- Batch processing with error handling
- Common patterns
- Best practices
- Troubleshooting guide
- Performance optimization

## Quick Navigation

### By Use Case

**I want to...**

- **Build a simple chatbot** → [Example 1: Interactive Chatbot](./06-Examples-and-Best-Practices.md#example-1-interactive-chatbot)
- **Create custom tools** → [Custom Tools Guide](./03-Custom-Tools-and-MCP.md#creating-custom-tools)
- **Secure my agent** → [Permissions Guide](./04-Permissions-and-Security.md)
- **Build specialized agents** → [Subagents](./05-Advanced-Topics.md#subagents)
- **Review code automatically** → [Example 2: Code Review Agent](./06-Examples-and-Best-Practices.md#example-2-code-review-agent)
- **Query databases safely** → [Example 3: Database Assistant](./06-Examples-and-Best-Practices.md#example-3-database-query-assistant)
- **Process files securely** → [Example 4: File Processor](./06-Examples-and-Best-Practices.md#example-4-file-processor-with-hooks)
- **Handle errors properly** → [Error Handling](./05-Advanced-Topics.md#error-handling)
- **Deploy to production** → [Production Deployment](./05-Advanced-topics.md#production-deployment)

### By Topic

**Core Concepts**
- [Installation](./01-SDK-Overview-and-Getting-Started.md#installation)
- [Authentication](./01-SDK-Overview-and-Getting-Started.md#authentication)
- [Agent Options](./01-SDK-Overview-and-Getting-Started.md#1-agent-options)
- [Query vs Client](./01-SDK-Overview-and-Getting-Started.md#2-query-vs-client)

**Tools and Capabilities**
- [Built-in Tools](./02-API-Reference.md#allowed_tools-liststr--none)
- [Creating Custom Tools](./03-Custom-Tools-and-MCP.md#creating-custom-tools)
- [MCP Servers](./03-Custom-Tools-and-MCP.md#mcp-servers)
- [Tool Design Best Practices](./03-Custom-Tools-and-MCP.md#tool-design-best-practices)

**Security**
- [Permission Modes](./04-Permissions-and-Security.md#permission-modes)
- [Allowed Tools](./04-Permissions-and-Security.md#allowed-tools)
- [Security Hooks](./04-Permissions-and-Security.md#hooks)
- [Best Practices](./04-Permissions-and-Security.md#security-best-practices)

**Advanced Features**
- [Subagents](./05-Advanced-Topics.md#subagents)
- [System Prompts](./05-Advanced-Topics.md#system-prompts-and-configuration)
- [Input Modes](./05-Advanced-Topics.md#streaming-vs-single-message-mode)
- [Context Management](./05-Advanced-Topics.md#context-management)

## Learning Path

### Beginner
1. Read [SDK Overview](./01-SDK-Overview-and-Getting-Started.md)
2. Try [Quick Start](./01-SDK-Overview-and-Getting-Started.md#quick-start) examples
3. Build [Simple Query Pattern](./06-Examples-and-Best-Practices.md#pattern-1-simple-query-pattern)
4. Experiment with [Interactive Chatbot](./06-Examples-and-Best-Practices.md#example-1-interactive-chatbot)

### Intermediate
1. Learn to [Create Custom Tools](./03-Custom-Tools-and-MCP.md#creating-custom-tools)
2. Understand [Permission System](./04-Permissions-and-Security.md)
3. Implement [Security Hooks](./04-Permissions-and-Security.md#hooks)
4. Build [Database Query Assistant](./06-Examples-and-Best-Practices.md#example-3-database-query-assistant)

### Advanced
1. Master [Subagents](./05-Advanced-Topics.md#subagents)
2. Implement [Production Deployment](./05-Advanced-Topics.md#production-deployment)
3. Optimize [Performance](./06-Examples-and-Best-Practices.md#performance-optimization)
4. Build [Complex Multi-Agent Systems](./06-Examples-and-Best-Practices.md#example-2-code-review-agent)

## Code Examples

All documentation includes working code examples. Here's a quick reference:

### Simple Query
```python
from claude_agent_sdk import query

async for message in query(prompt="What is 2 + 2?"):
    print(message)
```

### Conversation
```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient() as client:
    await client.query("Hello")
    async for message in client.receive_response():
        print(message)
```

### Custom Tool
```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("my_tool", "Description", {"param": str})
async def my_tool(args):
    return {"content": [{"type": "text", "text": "result"}]}

server = create_sdk_mcp_server("my_server", "1.0.0", [my_tool])
```

### Security Hook
```python
from claude_agent_sdk import HookMatcher

async def security_hook(input_data, tool_use_id, context):
    # Validation logic
    if should_block(input_data):
        return {'hookSpecificOutput': {'permissionDecision': 'deny'}}
    return {}

options = ClaudeAgentOptions(
    hooks={'PreToolUse': [HookMatcher(hooks=[security_hook])]}
)
```

## Additional Resources

### Official Documentation
- [Claude Agent SDK Docs](https://docs.claude.com/en/docs/claude-code/sdk/sdk-overview)
- [Anthropic API Reference](https://docs.anthropic.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

### GitHub Repositories
- [Claude Agent SDK - TypeScript](https://github.com/anthropics/claude-agent-sdk)
- [Claude Agent SDK - Python](https://github.com/anthropics/claude-agent-sdk-python)
- [Sample Examples](https://github.com/jkelly/ClaudeAgentExamples)

### Community
- [Anthropic Discord](https://discord.gg/anthropic)
- [GitHub Issues - TypeScript SDK](https://github.com/anthropics/claude-agent-sdk/issues)
- [GitHub Issues - Python SDK](https://github.com/anthropics/claude-agent-sdk-python/issues)

## Documentation Metadata

**Created:** October 2025
**SDK Version:** 0.1.0+
**Last Updated:** October 6, 2025
**Coverage:**
- ✅ Core SDK functionality
- ✅ Custom tools and MCP
- ✅ Permissions and security
- ✅ Subagents
- ✅ Error handling
- ✅ Production deployment
- ✅ Working examples
- ✅ Best practices

## Contributing

Found an error or have a suggestion? Please open an issue or submit a pull request to the [repository](https://github.com/jkelly/ClaudeAgentExamples).

---

**Ready to get started?** Begin with [SDK Overview and Getting Started](./01-SDK-Overview-and-Getting-Started.md)!
