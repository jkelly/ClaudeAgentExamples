# Claude Agent Examples

A collection of example agents demonstrating the capabilities of the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk). These examples showcase various patterns and use cases for building AI agents with Claude.

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Claude Code CLI (install with: `npm install -g @anthropic-ai/claude-code`)
- Claude Code setup with a Anthropic API key set in your environment or through the Pro or Max Plan.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/jkelly/ClaudeAgentExamples.git
cd ClaudeAgentExamples
```

2. Install dependencies:
```bash
cd test_agents
uv sync
```

## Agent Examples

### 1. Simple Query Agent ([simple_query_agent.py](test_agents/simple_query_agent.py))

Demonstrates basic `query()` usage with the SDK.

**Features:**
- Simple single-turn queries
- Configuring agent options (system prompts, allowed tools, permissions)
- Basic agent configuration patterns

**Run:**
```bash
uv run simple_query_agent.py
```

### 2. Conversation Agent ([conversation_agent.py](test_agents/conversation_agent.py))

Shows how to maintain continuous conversations with context preservation.

**Features:**
- Multi-turn conversations
- Context retention across queries
- Using `ClaudeSDKClient` for stateful interactions
- Processing assistant responses with `TextBlock` content

**Run:**
```bash
uv run conversation_agent.py
```

### 3. Custom Tools Agent ([custom_tools_agent.py](test_agents/custom_tools_agent.py))

Demonstrates creating and using custom tools with Claude.

**Features:**
- Creating custom tools with the `@tool` decorator
- Setting up MCP (Model Context Protocol) servers
- Tool definitions with typed parameters
- Multiple tool usage in a single session

**Custom Tools Included:**
- `calculate` - Safe mathematical expression evaluator
- `get_time` - Current date/time retrieval
- `reverse_string` - String reversal utility

**Run:**
```bash
uv run custom_tools_agent.py
```

### 4. Hooks Agent ([hooks_agent.py](test_agents/hooks_agent.py))

Shows how to use hooks for security validation and logging.

**Features:**
- Pre-tool-use hooks for security validation
- Blocking dangerous commands before execution
- Tool usage logging and monitoring
- Hook matchers for targeted or global hook application

**Run:**
```bash
uv run hooks_agent.py
```

### 5. File Processor Agent ([file_processor_agent.py](test_agents/file_processor_agent.py))

A real-world example demonstrating file system analysis capabilities.

**Features:**
- Custom file analysis tools
- File statistics gathering (lines, words, characters)
- Directory traversal and file extension counting
- Integration with built-in file tools (Read, Write, Glob, Grep)

**Run:**
```bash
uv run file_processor_agent.py
```

### 6. Error Handling Agent ([error_handling_agent.py](test_agents/error_handling_agent.py))

Demonstrates proper error handling patterns.

**Features:**
- Catching SDK-specific exceptions (`CLINotFoundError`, `ProcessError`, `CLIJSONDecodeError`)
- Graceful degradation with limited options
- Error recovery patterns
- Testing edge cases

**Run:**
```bash
uv run error_handling_agent.py
```

### 7. Interactive Agent ([interactive_agent.py](test_agents/interactive_agent.py))

A fully interactive chatbot with MS SQL Server integration.

**Features:**
- Interactive REPL-style interface
- MS SQL Server database tools (requires `pyodbc`)
- Database exploration (list databases, tables, stored procedures)
- Schema inspection and querying
- Security measures (read-only queries, query sanitization)

**SQL Server Tools:**
- `list_databases` - List all databases on the server
- `list_tables` - List tables in a database
- `get_table_schema` - Get column definitions and types
- `query_table` - Execute SELECT queries (read-only, limited to 100 rows)
- `list_stored_procedures` - List all stored procedures
- `get_stored_procedure` - View stored procedure definitions

**Additional Requirements:**
```bash
pip install pyodbc
```

**Run:**
```bash
uv run interactive_agent.py
```

### 8. Multi-Provider Agent ([multi_provider_agent.py](test_agents/multi_provider_agent.py))

Demonstrates using the Claude Agent SDK with different AI model providers via Anthropic-compatible endpoints.

**Features:**
- Support for multiple AI providers using Claude Agent SDK
- Uses `env` parameter in `ClaudeAgentOptions` to configure different providers
- Uses `model` parameter to specify provider-specific models
- Automatic provider detection based on available API keys
- Interactive mode with provider switching
- Side-by-side comparison testing

**Supported Providers:**
- **Claude** - Anthropic's Claude models (default)
- **GLM 4.6** - Z.AI's coding-focused model via Anthropic-compatible endpoint
- **Deepseek** - Advanced Chinese AI model with Anthropic API compatibility

**Key SDK Features Demonstrated:**
- `env` parameter for custom base URLs and authentication
- `model` parameter for specifying different models
- Environment-based configuration without hardcoding credentials

**Setup:**
1. Copy `.env.example` to `.env`:
   ```bash
   cp test_agents/.env.example test_agents/.env
   ```
2. Add API keys for the providers you want to use
3. Install dependencies: `uv sync`

**Usage:**
```bash
# Run comparison test (default)
uv run multi_provider_agent.py

# Run comparison test explicitly
uv run multi_provider_agent.py --compare

# Test specific provider
uv run multi_provider_agent.py --claude
uv run multi_provider_agent.py --glm
uv run multi_provider_agent.py --deepseek

# Interactive mode
uv run multi_provider_agent.py --interactive
```

## Running All Tests

To run all test agents sequentially:

```bash
uv run run_all_tests.py
```

This will execute each agent example and provide a summary of results.

## Project Structure

```
ClaudeAgentExamples/
├── test_agents/
│   ├── simple_query_agent.py       # Basic query patterns
│   ├── conversation_agent.py       # Multi-turn conversations
│   ├── custom_tools_agent.py       # Custom tool creation
│   ├── hooks_agent.py              # Security and logging hooks
│   ├── file_processor_agent.py     # File system analysis
│   ├── error_handling_agent.py     # Error handling patterns
│   ├── interactive_agent.py        # Interactive chatbot with SQL
│   ├── multi_provider_agent.py     # Multi-provider AI models
│   ├── run_all_tests.py            # Test runner
│   ├── .env.example                # Environment variables template
│   ├── pyproject.toml              # Project dependencies
│   └── uv.lock                     # Dependency lock file
├── AI_DOCS/                        # Comprehensive SDK documentation
│   ├── README.md                   # Documentation index
│   ├── 01-SDK-Overview-and-Getting-Started.md
│   ├── 02-API-Reference.md
│   ├── 03-Custom-Tools-and-MCP.md
│   ├── 04-Permissions-and-Security.md
│   ├── 05-Advanced-Topics.md
│   └── 06-Examples-and-Best-Practices.md
└── README.md                       # This file
```

## Key Concepts

### Agent Options

Configure agent behavior using `ClaudeAgentOptions`:
- `system_prompt` - Custom instructions for the agent
- `permission_mode` - Control file/system access (`acceptEdits`, `bypassPermissions`, etc.)
- `allowed_tools` - Whitelist specific tools
- `mcp_servers` - Add custom tool servers
- `max_turns` - Limit conversation length

### Custom Tools

Create tools with the `@tool` decorator:
```python
@tool("tool_name", "Tool description", {"param": type})
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": "result"}]}
```

### Hooks

Intercept and control tool execution:
```python
async def my_hook(input_data, tool_use_id, context):
    # Validation logic
    return {"hookSpecificOutput": {...}}
```

## Documentation

Comprehensive documentation is available in the [AI_DOCS](AI_DOCS/) folder:

- **[Getting Started](AI_DOCS/01-SDK-Overview-and-Getting-Started.md)** - Installation, quick start, core concepts
- **[API Reference](AI_DOCS/02-API-Reference.md)** - Complete API documentation
- **[Custom Tools & MCP](AI_DOCS/03-Custom-Tools-and-MCP.md)** - Extend Claude's capabilities
- **[Permissions & Security](AI_DOCS/04-Permissions-and-Security.md)** - Secure your agents
- **[Advanced Topics](AI_DOCS/05-Advanced-Topics.md)** - Subagents, context management, production
- **[Examples & Best Practices](AI_DOCS/06-Examples-and-Best-Practices.md)** - Patterns and tips

## Learn More

- [Claude Agent SDK Documentation](https://github.com/anthropics/claude-agent-sdk)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## License

See the main repository for license information.
