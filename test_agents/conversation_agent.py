"""
Conversation Agent - Demonstrates continuous conversation with context
Run with: uv run conversation_agent.py
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock


async def test_continuous_conversation():
    """Test continuous conversation with context preservation."""
    print("=== Testing Continuous Conversation ===\n")

    async with ClaudeSDKClient() as client:
        # First question
        print("User: What's the capital of France?")
        await client.query("What's the capital of France?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        print("\n" + "="*50 + "\n")

        # Follow-up question - Claude remembers the context
        print("User: What's the population of that city?")
        await client.query("What's the population of that city?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        print("\n" + "="*50 + "\n")

        # Another follow-up
        print("User: Tell me one famous landmark there.")
        await client.query("Tell me one famous landmark there.")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


if __name__ == "__main__":
    asyncio.run(test_continuous_conversation())