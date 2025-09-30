"""
Simple Query Agent - Demonstrates basic query() usage
Run with: uv run simple_query_agent.py
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def test_simple_query():
    """Test basic query functionality."""
    print("=== Test 1: Simple Math Query ===")
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

    print("\n=== Test 2: Query with Options ===")
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode='acceptEdits',
        allowed_tools=["Read", "Write", "Bash"],
    )

    async for message in query(
        prompt="List 3 Python best practices briefly",
        options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(test_simple_query())