"""
Hooks Agent - Demonstrates using hooks for security and logging
Run with: uv run hooks_agent.py
"""
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
    AssistantMessage,
    TextBlock
)
from typing import Any


async def security_validator(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Block dangerous commands before execution."""
    if input_data.get('tool_name') == 'Bash':
        command = input_data.get('tool_input', {}).get('command', '')
        dangerous_patterns = ['rm -rf /', 'del /f', 'format', 'dd if=']

        for pattern in dangerous_patterns:
            if pattern in command:
                print(f"[SECURITY] Blocked dangerous command: {command}")
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': f'Dangerous command blocked: contains "{pattern}"'
                    }
                }
    return {}


async def tool_logger(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Log all tool usage."""
    tool_name = input_data.get('tool_name', 'unknown')
    tool_input = input_data.get('tool_input', {})
    print(f"[HOOK] Tool used: {tool_name}")
    if tool_name == 'Bash':
        print(f"[HOOK] Command: {tool_input.get('command', 'N/A')}")
    return {}


async def test_hooks():
    """Test security hooks and logging."""
    print("=== Testing Hooks for Security and Logging ===\n")

    options = ClaudeAgentOptions(
        hooks={
            'PreToolUse': [
                HookMatcher(matcher='Bash', hooks=[security_validator]),
                HookMatcher(hooks=[tool_logger])  # Applies to all tools
            ]
        },
        allowed_tools=["Read", "Write", "Bash", "Glob"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        # Test 1: Safe command
        print("Test 1: List files (safe command)")
        await client.query("List all Python files in the current directory")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        print("\n" + "="*50 + "\n")

        # Test 2: This would be blocked by security hook (if attempted)
        print("Test 2: Attempting potentially dangerous operation")
        print("(Security hooks will intercept if Claude tries dangerous commands)")
        await client.query("Show me the current directory")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


if __name__ == "__main__":
    asyncio.run(test_hooks())