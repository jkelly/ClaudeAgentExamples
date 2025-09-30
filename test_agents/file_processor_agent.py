"""
File Processor Agent - Real-world example of file analysis
Run with: uv run file_processor_agent.py
"""
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock
)
from typing import Any
import os


@tool("analyze_file", "Analyze file contents and provide insights", {"file_path": str})
async def analyze_file(args: dict[str, Any]) -> dict[str, Any]:
    """Analyze a file and return statistics."""
    file_path = args["file_path"]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)

        return {
            "content": [{
                "type": "text",
                "text": f"File Analysis for {file_path}:\n"
                       f"- Lines: {lines}\n"
                       f"- Words: {words}\n"
                       f"- Characters: {chars}\n"
                       f"- File size: {os.path.getsize(file_path)} bytes"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error analyzing file: {str(e)}"
            }],
            "is_error": True
        }


@tool("count_extensions", "Count files by extension in a directory", {"directory": str})
async def count_extensions(args: dict[str, Any]) -> dict[str, Any]:
    """Count files by their extensions."""
    directory = args["directory"]
    try:
        extension_counts = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1] or "no_extension"
                extension_counts[ext] = extension_counts.get(ext, 0) + 1

        result_text = f"File extension counts in {directory}:\n"
        for ext, count in sorted(extension_counts.items(), key=lambda x: x[1], reverse=True):
            result_text += f"  {ext}: {count}\n"

        return {
            "content": [{
                "type": "text",
                "text": result_text
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error counting extensions: {str(e)}"
            }],
            "is_error": True
        }


async def test_file_processor():
    """Test file processing agent."""
    print("=== File Processing Agent ===\n")

    # Create custom tool server
    analysis_server = create_sdk_mcp_server(
        name="file_analyzer",
        version="1.0.0",
        tools=[analyze_file, count_extensions]
    )

    options = ClaudeAgentOptions(
        system_prompt="You are a file processing assistant that can analyze files and perform operations.",
        allowed_tools=[
            "Read", "Write", "Glob", "Grep",
            "mcp__file_analyzer__analyze_file",
            "mcp__file_analyzer__count_extensions"
        ],
        mcp_servers={"analyzer": analysis_server},
        permission_mode="acceptEdits",
        cwd=os.getcwd()
    )

    async with ClaudeSDKClient(options=options) as client:
        # Test 1: Count extensions in test_agents directory
        print("Test 1: Analyze the test_agents directory")
        await client.query("Count the file extensions in the test_agents directory")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        print("\n" + "="*50 + "\n")

        # Test 2: Analyze a specific file
        print("Test 2: Analyze this script file")
        await client.query("Analyze the file_processor_agent.py file in test_agents directory")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


if __name__ == "__main__":
    asyncio.run(test_file_processor())