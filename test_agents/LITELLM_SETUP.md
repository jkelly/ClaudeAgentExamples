# Using OpenAI Models with Claude Agent SDK via LiteLLM

This guide explains how to use OpenAI models (GPT-4o, GPT-4.1, o1, etc.) with the Claude Agent SDK using LiteLLM as a translation proxy.

## The Challenge

The Claude Agent SDK uses Anthropic's Messages API format, while OpenAI uses a different API format. OpenAI's newer Responses API doesn't provide Anthropic-compatible endpoints.

## The Solution: LiteLLM Proxy

[LiteLLM](https://github.com/BerriAI/litellm) is an open-source proxy server that:
- Accepts requests in Anthropic's Messages API format
- Translates them to OpenAI's Chat Completions format
- Sends requests to OpenAI models
- Translates responses back to Anthropic format
- Returns them to the Claude Agent SDK

This allows you to use OpenAI models (GPT-4o, o1, etc.) with the Claude Agent SDK seamlessly.

## Installation

### 1. Install LiteLLM

```bash
pip install 'litellm[proxy]'
```

### 2. Create LiteLLM Configuration

Create a file `litellm_config.yaml` in the `test_agents` directory:

```yaml
model_list:
  # OpenAI GPT-4o
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  # OpenAI GPT-4o Mini
  - model_name: gpt-4o-mini
    litellm_params:
      model: gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

  # OpenAI o1 (reasoning model)
  - model_name: o1
    litellm_params:
      model: o1
      api_key: os.environ/OPENAI_API_KEY

  # OpenAI o1-mini
  - model_name: o1-mini
    litellm_params:
      model: o1-mini
      api_key: os.environ/OPENAI_API_KEY

# General settings
general_settings:
  master_key: sk-1234  # Replace with a secure key for authentication
```

### 3. Add OpenAI API Key to .env

```bash
# Add to your .env file
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

## Running LiteLLM Proxy

### Start the Proxy Server

In a separate terminal, navigate to the `test_agents` directory and run:

```bash
litellm --config litellm_config.yaml --port 4000
```

You should see:
```
LiteLLM: Proxy running on http://0.0.0.0:4000
```

**Keep this terminal running** - the proxy needs to be active for the Claude Agent SDK to communicate with OpenAI.

### Test the Proxy

In another terminal, test that the proxy is working:

```bash
curl -X POST 'http://localhost:4000/anthropic/v1/messages' \
  -H 'x-api-key: sk-1234' \
  -H 'anthropic-version: 2023-06-01' \
  -H 'content-type: application/json' \
  -d '{
    "model": "gpt-4o",
    "max_tokens": 100,
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

## Using with Claude Agent SDK

### Update .env File

Add LiteLLM configuration to your `.env`:

```bash
# LiteLLM Proxy Configuration
LITELLM_BASE_URL=http://localhost:4000/anthropic
LITELLM_API_KEY=sk-1234

# OpenAI API Key (for LiteLLM)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

### Configure in multi_provider_agent.py

The multi-provider agent can be configured to use OpenAI via LiteLLM:

```python
# Configure for OpenAI GPT-4o via LiteLLM
options = ClaudeAgentOptions(
    model="gpt-4o",  # or "o1", "gpt-4o-mini", etc.
    env={
        "ANTHROPIC_BASE_URL": "http://localhost:4000/anthropic",
        "ANTHROPIC_AUTH_TOKEN": "sk-1234"  # LiteLLM master key
    }
)
```

## Usage Examples

### Basic Query

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def query_openai():
    options = ClaudeAgentOptions(
        model="gpt-4o",
        env={
            "ANTHROPIC_BASE_URL": "http://localhost:4000/anthropic",
            "ANTHROPIC_AUTH_TOKEN": "sk-1234"
        }
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is the capital of France?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

asyncio.run(query_openai())
```

### Using Different OpenAI Models

```python
# GPT-4o Mini (faster, cheaper)
options = ClaudeAgentOptions(
    model="gpt-4o-mini",
    env={
        "ANTHROPIC_BASE_URL": "http://localhost:4000/anthropic",
        "ANTHROPIC_AUTH_TOKEN": "sk-1234"
    }
)

# o1 (advanced reasoning)
options = ClaudeAgentOptions(
    model="o1",
    env={
        "ANTHROPIC_BASE_URL": "http://localhost:4000/anthropic",
        "ANTHROPIC_AUTH_TOKEN": "sk-1234"
    }
)
```

## Running as Background Service

### Using Docker

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    command: ["--config", "/app/config.yaml", "--port", "4000"]
```

Run with:
```bash
docker-compose up -d
```

### Using systemd (Linux)

Create `/etc/systemd/system/litellm.service`:

```ini
[Unit]
Description=LiteLLM Proxy Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/test_agents
Environment="OPENAI_API_KEY=your-key"
ExecStart=/usr/local/bin/litellm --config litellm_config.yaml --port 4000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable litellm
sudo systemctl start litellm
```

## Troubleshooting

### Connection Refused Error

**Error:** `Connection refused when connecting to http://localhost:4000`

**Solution:** Make sure LiteLLM proxy is running:
```bash
litellm --config litellm_config.yaml --port 4000
```

### Authentication Error

**Error:** `Authentication failed` or `Invalid API key`

**Solution:**
1. Check that `LITELLM_API_KEY` in `.env` matches `master_key` in `litellm_config.yaml`
2. Verify `OPENAI_API_KEY` is set correctly

### Model Not Found

**Error:** `Model 'gpt-4o' not found`

**Solution:**
1. Check that the model is listed in `litellm_config.yaml`
2. Verify your OpenAI API key has access to the model

### Rate Limits

LiteLLM respects OpenAI's rate limits. If you hit rate limits:
1. Reduce request frequency
2. Upgrade your OpenAI plan
3. Configure retry logic in LiteLLM config

## Advanced Configuration

### Adding Multiple Providers

You can configure LiteLLM to support multiple providers simultaneously:

```yaml
model_list:
  # OpenAI Models
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  # Azure OpenAI
  - model_name: azure-gpt-4
    litellm_params:
      model: azure/gpt-4
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY

  # Local Models via Ollama
  - model_name: llama3
    litellm_params:
      model: ollama/llama3
      api_base: http://localhost:11434
```

### Caching and Cost Tracking

LiteLLM supports caching and cost tracking:

```yaml
general_settings:
  master_key: sk-1234
  database_url: "postgresql://..."  # For cost tracking
  cache: true
  cache_type: "redis"
  redis_host: "localhost"
  redis_port: 6379
```

## Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [Supported Models](https://docs.litellm.ai/docs/providers)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

## Limitations

### OpenAI Responses API
The newer OpenAI Responses API is **not yet supported** through this method. LiteLLM uses OpenAI's Chat Completions API, which is compatible with GPT-4o, o1, and other chat models.

### Feature Parity
Some Anthropic-specific features may not work perfectly with OpenAI models:
- Extended thinking (Anthropic-specific)
- PDF processing (Anthropic-specific)
- Prompt caching (different implementations)

### Network Latency
Using LiteLLM adds a small amount of latency due to the translation layer, typically < 50ms.

## Cost Comparison

When using OpenAI via LiteLLM with Claude Agent SDK:

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| GPT-4o | $2.50 | $10.00 |
| GPT-4o Mini | $0.15 | $0.60 |
| o1 | $15.00 | $60.00 |
| Claude Sonnet 4.5 | $3.00 | $15.00 |

LiteLLM itself is free and open-source with no additional costs.
