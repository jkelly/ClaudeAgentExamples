# Claude Agent SDK Test Agents

This folder contains example test agents demonstrating various features of the Claude Agent SDK.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
- uv package manager: `pip install uv`

## Setup

Install dependencies using uv:

```bash
cd test_agents
uv sync
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Test Agents

### 1. Simple Query Agent (`simple_query_agent.py`)
Demonstrates basic `query()` usage for one-off tasks.

```bash
uv run simple_query_agent.py
```

Features:
- Simple queries
- Configuration options
- System prompts

### 2. Conversation Agent (`conversation_agent.py`)
Shows continuous conversation with context preservation.

```bash
uv run conversation_agent.py
```

Features:
- Multi-turn conversations
- Context retention
- Follow-up questions

### 3. Custom Tools Agent (`custom_tools_agent.py`)
Creates and uses custom tools with Claude.

```bash
uv run custom_tools_agent.py
```

Features:
- Calculator tool
- Time retrieval tool
- String reversal tool
- MCP server integration

### 4. Hooks Agent (`hooks_agent.py`)
Demonstrates security validation and logging using hooks.

```bash
uv run hooks_agent.py
```

Features:
- Pre-tool execution hooks
- Security validation
- Command logging
- Dangerous command blocking

### 5. File Processor Agent (`file_processor_agent.py`)
Real-world file analysis and processing example.

```bash
uv run file_processor_agent.py
```

Features:
- File analysis tool
- Extension counting
- Directory processing
- Custom MCP server

### 6. Error Handling Agent (`error_handling_agent.py`)
Shows proper error handling patterns.

```bash
uv run error_handling_agent.py
```

Features:
- CLINotFoundError handling
- ProcessError handling
- Graceful degradation
- Edge case handling

### 7. Interactive Agent (`interactive_agent.py`)
Full interactive chatbot with conversation loop.

```bash
uv run interactive_agent.py
```

Features:
- Interactive REPL
- Continuous conversation
- File operations
- Command execution

## Running All Tests

To run all test agents sequentially:

```bash
uv run simple_query_agent.py
uv run conversation_agent.py
uv run custom_tools_agent.py
uv run hooks_agent.py
uv run file_processor_agent.py
uv run error_handling_agent.py
uv run interactive_agent.py
```

## Key Concepts Demonstrated

- **query()**: Simple one-off queries without conversation history
- **ClaudeSDKClient**: Advanced client for continuous conversations
- **Custom Tools**: Create tools using `@tool` decorator and MCP servers
- **Hooks**: Intercept and modify behavior at execution points
- **Error Handling**: Robust exception handling patterns
- **Configuration**: Using `ClaudeAgentOptions` for fine-tuned control

## Project Structure

```
test_agents/
├── simple_query_agent.py       # Basic queries
├── conversation_agent.py       # Multi-turn conversations
├── custom_tools_agent.py       # Custom tool creation
├── hooks_agent.py              # Security and logging hooks
├── file_processor_agent.py     # Real-world file processing
├── error_handling_agent.py     # Error handling patterns
├── interactive_agent.py        # Interactive chatbot
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Troubleshooting

If you encounter issues:

1. Ensure Claude Code CLI is installed:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. Verify your API key is set:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

3. Check Python version (must be 3.10+):
   ```bash
   python --version
   ```

4. Reinstall dependencies:
   ```bash
   uv sync --reinstall
   ```