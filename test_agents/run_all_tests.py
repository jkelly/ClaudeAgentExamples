"""
Run All Tests - Execute all test agents sequentially
Run with: uv run run_all_tests.py
"""
import asyncio
import sys
from pathlib import Path


async def run_test(test_name: str, test_module: str):
    """Run a single test agent."""
    print("\n" + "="*70)
    print(f"RUNNING: {test_name}")
    print("="*70 + "\n")

    try:
        # Import and run the test
        module = __import__(test_module)
        if hasattr(module, 'main'):
            await module.main()
        else:
            # Try to find the main async function
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and attr_name.startswith('test_'):
                    await attr()
                    break

        print(f"\n✓ {test_name} completed successfully")
        return True
    except Exception as e:
        print(f"\n✗ {test_name} failed: {e}")
        return False


async def main():
    """Run all test agents."""
    print("="*70)
    print("Claude Agent SDK - Test Suite")
    print("="*70)

    tests = [
        ("Simple Query Agent", "simple_query_agent"),
        ("Conversation Agent", "conversation_agent"),
        ("Custom Tools Agent", "custom_tools_agent"),
        ("Hooks Agent", "hooks_agent"),
        ("File Processor Agent", "file_processor_agent"),
        ("Error Handling Agent", "error_handling_agent"),
    ]

    results = []
    for test_name, test_module in tests:
        result = await run_test(test_name, test_module)
        results.append((test_name, result))
        await asyncio.sleep(1)  # Brief pause between tests

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")
    print("="*70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)