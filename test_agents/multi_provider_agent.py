"""
Multi-Provider Agent - Demonstrates using different AI model providers with Claude Agent SDK
Supports: GLM 4.6 (Z.AI) and Deepseek via Anthropic-compatible endpoints

Run with: uv run multi_provider_agent.py

Requirements:
- Copy .env.example to .env and configure your API keys
- Install dependencies: uv sync
"""
import asyncio
import os
from typing import Literal
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

# Load environment variables from .env file
load_dotenv()

ProviderType = Literal["claude", "glm", "deepseek"]


class MultiProviderConfig:
    """Configuration for different AI providers."""

    @staticmethod
    def get_provider_config(provider: ProviderType) -> tuple[dict[str, str], str]:
        """
        Get environment variables and model name for a provider.

        Args:
            provider: The provider type (claude, glm, deepseek)

        Returns:
            Tuple of (env_vars dict, model_name)
        """
        if provider == "claude":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in .env file")
            return {}, "claude-sonnet-4-5-20250929"

        elif provider == "glm":
            api_key = os.getenv("GLM_API_KEY")
            if not api_key:
                raise ValueError("GLM_API_KEY not set in .env file")
            return {
                "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
                "ANTHROPIC_AUTH_TOKEN": api_key
            }, "glm-4.6"

        elif provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not set in .env file")
            return {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com",
                "ANTHROPIC_AUTH_TOKEN": api_key
            }, "deepseek-chat"

        else:
            raise ValueError(f"Unknown provider: {provider}")


async def query_with_provider(prompt: str, provider: ProviderType) -> None:
    """
    Query using a specific provider.

    Args:
        prompt: The user's query
        provider: Which provider to use (claude, glm, or deepseek)
    """
    try:
        env_vars, model = MultiProviderConfig.get_provider_config(provider)

        options = ClaudeAgentOptions(
            model=model,
            env=env_vars,
            system_prompt=f"You are a helpful AI assistant powered by {provider.upper()}."
        )

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text)

    except ValueError as e:
        print(f"Configuration Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")


async def run_comparison_test():
    """Run the same query across all configured providers."""
    test_prompt = "Explain what a binary search tree is in one sentence."

    providers: list[ProviderType] = []

    # Check which providers are available
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("claude")
    if os.getenv("GLM_API_KEY"):
        providers.append("glm")
    if os.getenv("DEEPSEEK_API_KEY"):
        providers.append("deepseek")

    if not providers:
        print("Error: No API keys configured. Please set up your .env file.")
        print("See .env.example for required variables.")
        return

    print("=" * 70)
    print("Multi-Provider Comparison Test")
    print("=" * 70)
    print(f"\nTest Query: {test_prompt}\n")
    print("=" * 70)

    for provider in providers:
        print(f"\n[{provider.upper()}]")
        print("-" * 70)
        await query_with_provider(test_prompt, provider)

    print("\n" + "=" * 70)
    print("Comparison test completed!")
    print("=" * 70)


async def run_specific_test(provider: ProviderType):
    """Test a specific provider with a simple query."""
    print("=" * 70)
    print(f"{provider.upper()} Test")
    print("=" * 70)

    prompt = "What is the capital of France? Answer in one sentence."
    print(f"\nQuery: {prompt}\n")
    print("-" * 70)

    await query_with_provider(prompt, provider)

    print("\n" + "=" * 70)


async def interactive_mode():
    """Run in interactive mode allowing provider selection."""
    available_providers: list[ProviderType] = []

    if os.getenv("ANTHROPIC_API_KEY"):
        available_providers.append("claude")
    if os.getenv("GLM_API_KEY"):
        available_providers.append("glm")
    if os.getenv("DEEPSEEK_API_KEY"):
        available_providers.append("deepseek")

    if not available_providers:
        print("Error: No API keys configured. Please set up your .env file.")
        print("See .env.example for required variables.")
        return

    print("=" * 70)
    print("Multi-Provider Agent - Interactive Mode")
    print("=" * 70)
    print(f"\nAvailable providers: {', '.join(available_providers)}")
    print("\nCommands:")
    print("  /claude <prompt>   - Query Claude (Anthropic)")
    print("  /glm <prompt>      - Query GLM 4.6 (Z.AI)")
    print("  /deepseek <prompt> - Query Deepseek")
    print("  /all <prompt>      - Query all available providers")
    print("  /quit              - Exit")
    print("=" * 70)

    current_provider = available_providers[0]
    print(f"\nDefault provider: {current_provider.upper()}")

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input == "/quit":
                print("Goodbye!")
                break

            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                prompt = parts[1] if len(parts) > 1 else ""

                if not prompt and command != "/quit":
                    print("Error: Please provide a prompt")
                    continue

                if command == "/claude" and "claude" in available_providers:
                    print(f"\n[CLAUDE]")
                    print("-" * 70)
                    await query_with_provider(prompt, "claude")
                elif command == "/glm" and "glm" in available_providers:
                    print(f"\n[GLM]")
                    print("-" * 70)
                    await query_with_provider(prompt, "glm")
                elif command == "/deepseek" and "deepseek" in available_providers:
                    print(f"\n[DEEPSEEK]")
                    print("-" * 70)
                    await query_with_provider(prompt, "deepseek")
                elif command == "/all":
                    for provider in available_providers:
                        print(f"\n[{provider.upper()}]")
                        print("-" * 70)
                        await query_with_provider(prompt, provider)
                else:
                    print(f"Error: Unknown or unavailable command '{command}'")
            else:
                # Use current default provider
                print(f"\n[{current_provider.upper()}]")
                print("-" * 70)
                await query_with_provider(user_input, current_provider)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


async def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] in ["--interactive", "-i"]:
            await interactive_mode()
        elif sys.argv[1] == "--compare":
            await run_comparison_test()
        elif sys.argv[1] in ["--claude", "--glm", "--deepseek"]:
            provider = sys.argv[1].replace("--", "")
            await run_specific_test(provider)
        else:
            print("Usage:")
            print("  uv run multi_provider_agent.py              # Run comparison test")
            print("  uv run multi_provider_agent.py --interactive # Interactive mode")
            print("  uv run multi_provider_agent.py --compare    # Run comparison test")
            print("  uv run multi_provider_agent.py --claude     # Test Claude only")
            print("  uv run multi_provider_agent.py --glm        # Test GLM only")
            print("  uv run multi_provider_agent.py --deepseek   # Test Deepseek only")
    else:
        # Default: run comparison test
        await run_comparison_test()


if __name__ == "__main__":
    asyncio.run(main())
