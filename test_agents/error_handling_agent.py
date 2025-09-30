"""
Error Handling Agent - Demonstrates proper error handling
Run with: uv run error_handling_agent.py
"""
import asyncio
from claude_agent_sdk import (
    query,
    CLINotFoundError,
    ProcessError,
    CLIJSONDecodeError,
    ClaudeAgentOptions
)


async def test_error_handling():
    """Test various error handling scenarios."""
    print("=== Testing Error Handling ===\n")

    # Test 1: Successful query
    print("Test 1: Successful Query")
    try:
        async for message in query(prompt="Say hello"):
            print(f"Success: {message}")
    except CLINotFoundError:
        print("ERROR: Claude Code CLI not found!")
        print("Install with: npm install -g @anthropic-ai/claude-code")
    except ProcessError as e:
        print(f"ERROR: Process failed with exit code: {e.exit_code}")
        print(f"stderr: {e.stderr}")
    except CLIJSONDecodeError as e:
        print(f"ERROR: Failed to parse response: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")

    print("\n" + "="*50 + "\n")

    # Test 2: Query with invalid options (testing graceful handling)
    print("Test 2: Query with Edge Case Options")
    try:
        options = ClaudeAgentOptions(
            max_turns=1,  # Very limited turns
            allowed_tools=["Read"]  # Limited tools
        )
        async for message in query(
            prompt="Calculate the square root of 144",
            options=options
        ):
            print(f"Response: {message}")
    except Exception as e:
        print(f"Handled error gracefully: {type(e).__name__}: {e}")

    print("\n" + "="*50 + "\n")

    # Test 3: Testing with invalid model (if it fails)
    print("Test 3: Handling Configuration Issues")
    try:
        options = ClaudeAgentOptions(
            system_prompt="Test agent",
            permission_mode="acceptEdits"
        )
        async for message in query(
            prompt="What is 1+1?",
            options=options
        ):
            print(f"Success: {message}")
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}")
        print(f"Details: {e}")


if __name__ == "__main__":
    asyncio.run(test_error_handling())