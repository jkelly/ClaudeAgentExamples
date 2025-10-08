# Claude Agent Examples

A collection of example agents demonstrating the capabilities of the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk). These examples showcase various patterns and use cases for building AI agents with Claude.

## What's Included

✅ **9 Complete Agent Examples** - From basic queries to production-ready applications
✅ **Multi-Provider Support** - Use Claude, GLM 4.6, Deepseek, and OpenAI models
✅ **Creative AI Applications** - Story writer with GPT-5 reasoning support
✅ **Custom Tools & Hooks** - Extend functionality and add security
✅ **Production Patterns** - Error handling, permissions, and best practices
✅ **Comprehensive Documentation** - 6 detailed guides covering all SDK features

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

3. (Optional) Configure API keys for multi-provider support:
```bash
cp .env.example .env
# Edit .env and add your API keys for the providers you want to use
```

**Note:** Most examples work with just the `ANTHROPIC_API_KEY` (configured via Claude Code). The `.env` file is needed for:
- **Multi-Provider Agent** - Testing GLM 4.6, Deepseek, or OpenAI models
- **Story Writer OpenAI Agent** - Using OpenAI models for creative writing

## Quick Start Guide

**New to the SDK?** Start here:
1. **[Simple Query Agent](#1-simple-query-agent-simple_query_agentpy)** - Learn basic query patterns
2. **[Conversation Agent](#2-conversation-agent-conversation_agentpy)** - Multi-turn conversations
3. **[Custom Tools Agent](#3-custom-tools-agent-custom_tools_agentpy)** - Create custom tools

**Working with different AI providers?**
- **[Multi-Provider Agent](#8-multi-provider-agent-multi_provider_agentpy)** - Use GLM, Deepseek, or OpenAI with Claude SDK
- **[Story Writer OpenAI Agent](#9-story-writer-openai-agent-story_writer_openai_agentpy)** - Direct OpenAI integration for creative writing

**Building production agents?**
- **[Hooks Agent](#4-hooks-agent-hooks_agentpy)** - Security validation and logging
- **[Error Handling Agent](#6-error-handling-agent-error_handling_agentpy)** - Robust error handling
- **[File Processor Agent](#5-file-processor-agent-file_processor_agentpy)** - Real-world file analysis

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
- **Claude** (`claude-sonnet-4-5-20250929`) - Anthropic's Claude models (default)
  - Uses standard `ANTHROPIC_API_KEY` from Claude Code configuration
  - Direct integration - works out of the box
- **GLM 4.6** (`glm-4.6`) - Z.AI's coding-focused model
  - Endpoint: `https://api.z.ai/api/anthropic`
  - Cost: Starting at $3/month for Coding Plan
  - Sign up: [https://www.z.ai/](https://www.z.ai/)
  - Direct integration - works out of the box
- **Deepseek** (`deepseek-chat`) - Advanced Chinese AI model
  - Endpoint: `https://api.deepseek.com/anthropic`
  - Sign up: [https://platform.deepseek.com/](https://platform.deepseek.com/)
  - Direct integration - works out of the box
- **OpenAI** (`gpt-4o`, `o1`, etc.) - OpenAI models including GPT-4o and o1
  - Via LiteLLM proxy translation layer
  - Sign up: [https://platform.openai.com/](https://platform.openai.com/)
  - **Requires LiteLLM proxy** - See [LITELLM_SETUP.md](test_agents/LITELLM_SETUP.md)

**Key SDK Features Demonstrated:**
- `env` parameter for custom base URLs (`ANTHROPIC_BASE_URL`) and authentication (`ANTHROPIC_AUTH_TOKEN`)
- `model` parameter for specifying different models
- Environment-based configuration using `.env` file
- No hardcoded credentials

**Configuration (.env.example):**
```bash
# Direct Providers (work out-of-the-box)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GLM_API_KEY=your_glm_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# OpenAI via LiteLLM (requires proxy setup)
OPENAI_API_KEY=your_openai_api_key_here
LITELLM_BASE_URL=http://localhost:4000/anthropic
LITELLM_API_KEY=sk-1234
OPENAI_MODEL=gpt-5  # or gpt-4o, gpt-5-mini, o1, etc.

# GPT-5 Parameters (for story_writer_openai_agent.py)
OPENAI_REASONING_EFFORT=medium  # minimal/low/medium/high
OPENAI_VERBOSITY=medium         # low/medium/high
```

**Setup:**
1. Copy `.env.example` to `.env`:
   ```bash
   cp test_agents/.env.example test_agents/.env
   ```
2. Edit `.env` and add API keys for the providers you want to use
   - You only need to configure the providers you want to test
   - The agent automatically detects which providers are available
3. Install dependencies (if not already done):
   ```bash
   uv sync
   ```
4. **(Optional) For OpenAI support:**
   - Install LiteLLM: `pip install 'litellm[proxy]'`
   - Start proxy: `litellm --config test_agents/litellm_config.yaml --port 4000`
   - See [LITELLM_SETUP.md](test_agents/LITELLM_SETUP.md) for detailed instructions

**Usage:**
```bash
# Run comparison test (default) - queries all configured providers
uv run multi_provider_agent.py

# Run comparison test explicitly
uv run multi_provider_agent.py --compare

# Test specific provider
uv run multi_provider_agent.py --claude
uv run multi_provider_agent.py --glm
uv run multi_provider_agent.py --deepseek
uv run multi_provider_agent.py --openai  # Requires LiteLLM proxy

# Interactive mode - switch between providers on the fly
uv run multi_provider_agent.py --interactive
```

**Interactive Mode Commands:**
```
/claude <prompt>   - Query Claude (Anthropic)
/glm <prompt>      - Query GLM 4.6 (Z.AI)
/deepseek <prompt> - Query Deepseek
/openai <prompt>   - Query OpenAI (GPT-4o via LiteLLM)
/all <prompt>      - Query all available providers
/quit              - Exit
```

**OpenAI Integration:**

The multi-provider agent supports OpenAI models (GPT-4o, o1, etc.) through LiteLLM, which acts as a translation proxy:
- LiteLLM accepts Anthropic Messages API format requests
- Translates them to OpenAI Chat Completions format
- Returns responses in Anthropic format for the Claude Agent SDK

This allows seamless integration without modifying the SDK. See [LITELLM_SETUP.md](test_agents/LITELLM_SETUP.md) for:
- Installation and configuration
- Running the proxy server
- Docker deployment options
- Troubleshooting guide
- Advanced features (caching, cost tracking, multiple providers)

### 9. Story Writer OpenAI Agent ([story_writer_openai_agent.py](test_agents/story_writer_openai_agent.py))

A creative writing agent that generates multi-day stories with character development using OpenAI models via LiteLLM.

**Features:**
- Multi-day story generation with automatic date progression
- Character profile creation with backstories and birthdays
- Storyboard planning before writing
- Maintains context across story days
- Outputs formatted Markdown files
- Interactive mode for custom prompts
- Direct LiteLLM integration (no proxy required)

**GPT-5 Support:**
- **Reasoning Effort**: Control thinking depth (minimal/low/medium/high)
- **Verbosity**: Control output length (low/medium/high)
- Optimized for complex creative tasks

**Supported Models:**
- **GPT-4o** - Latest flagship model (recommended)
- **GPT-4o Mini** - Faster and cheaper option
- **GPT-5** - Advanced reasoning for complex narratives (when available)
- **GPT-5 Mini/Nano** - Efficient reasoning models

**How It Works:**
1. Creates detailed character profiles with backstories
2. Generates a storyboard outlining the entire narrative arc
3. Writes each day's narrative following the storyboard
4. Maintains conversation context for continuity
5. Outputs complete story as formatted Markdown

**Setup:**
```bash
# Set OpenAI API key in .env
cp test_agents/.env.example test_agents/.env
# Edit .env and set OPENAI_API_KEY

# Install dependencies
uv sync
```

**Configuration (.env):**
```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional - Model selection
OPENAI_MODEL=gpt-4o  # or gpt-5, gpt-5-mini, gpt-4o-mini

# Optional - GPT-5 only parameters
OPENAI_REASONING_EFFORT=medium  # minimal/low/medium/high
OPENAI_VERBOSITY=medium         # low/medium/high
```

**Usage:**
```bash
# Interactive mode (prompts for story premise and duration)
uv run story_writer_openai_agent.py

# Example output: story_openai_20250107_143022.md
```

**Programmatic Usage:**
```python
# Edit the __main__ section to customize:
asyncio.run(write_multi_day_story(
    initial_prompt="A detective solving a mysterious case in Tokyo",
    num_days=7,
    output_file="my_story.md",
    story_start_date="2025-07-01"
))
```

**Output Format:**
- **Markdown file** with metadata header
- **Story Planning** section with character profiles and storyboard
- **The Story** section with day-by-day narrative
- Each day labeled with actual dates (e.g., "Day 1: July 21, 2025 (Monday)")

**Example Workflow:**
1. User provides premise: "A young chef discovers a magical cookbook"
2. Agent creates character profiles (name, age, birthday, backstory)
3. Agent creates storyboard for 3-day narrative
4. Agent writes detailed narrative for each day
5. Complete story saved to `story_openai_TIMESTAMP.md`

**Comparison with multi_provider_agent.py:**
- **story_writer_openai_agent.py**: Direct LiteLLM usage, no proxy needed, creative writing focus
- **multi_provider_agent.py**: Uses Claude Agent SDK via LiteLLM proxy, multi-provider support

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
│   ├── story_writer_openai_agent.py # Creative story writer (OpenAI)
│   ├── run_all_tests.py            # Test runner
│   ├── LITELLM_SETUP.md            # OpenAI integration guide
│   ├── .env.example                # Environment variables template
│   ├── .env                        # Your API keys (not in git)
│   ├── litellm_config.yaml         # LiteLLM proxy configuration
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
├── .gitignore                      # Git ignore rules
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

### Multi-Provider Configuration

Use the `env` and `model` parameters in `ClaudeAgentOptions` to configure different AI providers:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# Configure for GLM 4.6
options = ClaudeAgentOptions(
    model="glm-4.6",
    env={
        "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
        "ANTHROPIC_AUTH_TOKEN": "your_glm_api_key"
    }
)

# Configure for Deepseek
options = ClaudeAgentOptions(
    model="deepseek-chat",
    env={
        "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
        "ANTHROPIC_AUTH_TOKEN": "your_deepseek_api_key"
    }
)
```

**Environment Variables (.env file):**
```bash
# Copy .env.example to .env
cp test_agents/.env.example test_agents/.env

# Edit .env with your API keys

# Direct Providers
ANTHROPIC_API_KEY=sk-ant-...        # For Claude (default)
GLM_API_KEY=glm-...                 # For GLM 4.6 (optional)
DEEPSEEK_API_KEY=sk-...             # For Deepseek (optional)

# OpenAI (for multi_provider_agent.py with LiteLLM proxy)
OPENAI_API_KEY=sk-proj-...          # For OpenAI models (optional)
LITELLM_BASE_URL=http://localhost:4000/anthropic
LITELLM_API_KEY=sk-1234
OPENAI_MODEL=gpt-5                  # or gpt-4o, gpt-5-mini, o1, etc.

# GPT-5 Parameters (for story_writer_openai_agent.py)
OPENAI_REASONING_EFFORT=medium      # minimal/low/medium/high
OPENAI_VERBOSITY=medium             # low/medium/high
```

**Important:** The `.env` file is ignored by git (see `.gitignore`) to protect your API keys.

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
