"""
Custom Tools Agent - Demonstrates creating and using custom tools
Run with: uv run custom_tools_agent.py
"""
import asyncio
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock
)
from typing import Any
from datetime import datetime


@tool("calculate", "Perform mathematical calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """Safe calculator tool."""
    try:
        # Use a restricted eval for safety
        result = eval(args["expression"], {"__builtins__": {}})
        return {
            "content": [{
                "type": "text",
                "text": f"Result: {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: {str(e)}"
            }],
            "is_error": True
        }


@tool("get_time", "Get current time", {})
async def get_time(args: dict[str, Any]) -> dict[str, Any]:
    """Returns the current date and time."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "content": [{
            "type": "text",
            "text": f"Current time: {current_time}"
        }]
    }


@tool("reverse_string", "Reverse a string", {"text": str})
async def reverse_string(args: dict[str, Any]) -> dict[str, Any]:
    """Reverses the provided string."""
    text = args["text"]
    reversed_text = text[::-1]
    return {
        "content": [{
            "type": "text",
            "text": f"Reversed: {reversed_text}"
        }]
    }


async def test_custom_tools():
    """Test custom tools with Claude."""
    print("=== Testing Custom Tools ===\n")

    # Create an MCP server with custom tools
    utilities_server = create_sdk_mcp_server(
        name="utilities",
        version="1.0.0",
        tools=[calculate, get_time, reverse_string]
    )

    # Configure Claude to use custom tools
    options = ClaudeAgentOptions(
        mcp_servers={"utils": utilities_server},
        allowed_tools=[
            "mcp__utils__calculate",
            "mcp__utils__get_time",
            "mcp__utils__reverse_string"
        ]
    )

    async with ClaudeSDKClient(options=options) as client:
        # Test 1: Multiple tool usage
        print("Test 1: What's 123 * 456 and what time is it?")
        await client.query("What's 123 * 456 and what time is it?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        print("\n" + "="*50 + "\n")

        # Test 2: String reversal
        print("Test 2: Reverse the string 'Hello World'")
        await client.query("Reverse the string 'Hello World'")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


if __name__ == "__main__":
    asyncio.run(test_custom_tools())