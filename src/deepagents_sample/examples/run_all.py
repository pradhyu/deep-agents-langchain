#!/usr/bin/env python3
"""
Run All Examples

Main entry point to run all DeepAgents examples sequentially or individually.
"""

import sys
import os
from typing import Optional


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*70)
    print(" "*15 + "DEEPAGENTS SAMPLE PROJECT")
    print(" "*10 + "LangChain v1+ with LangGraph and MCP Tools")
    print("="*70)
    print("\nThis project demonstrates:")
    print("  • Middleware for agent request/response interception")
    print("  • Hierarchical agent orchestration with LangGraph")
    print("  • MCP tool integration for external capabilities")
    print("="*70 + "\n")


def print_menu():
    """Print example selection menu."""
    print("\nAvailable Examples:")
    print("  1. Basic Middleware Usage")
    print("     - LoggingMiddleware and MetricsMiddleware")
    print("     - Request/response interception")
    print("     - Middleware chaining")
    print()
    print("  2. LangGraph with Subagents")
    print("     - Coordinator and subagent orchestration")
    print("     - State management across workflow")
    print("     - Automatic task routing")
    print("     - Requires: OPENAI_API_KEY")
    print()
    print("  3. MCP Tool Integration")
    print("     - CommandTool for shell execution")
    print("     - JSONSearchTool with jq")
    print("     - Agent tool usage patterns")
    print()
    print("  4. Streaming Responses (NEW)")
    print("     - Real-time token-by-token output")
    print("     - Progressive research results")
    print("     - Requires: OPENAI_API_KEY")
    print()
    print("  5. Caching & Configuration (NEW)")
    print("     - Configuration management")
    print("     - Caching layer for cost reduction")
    print("     - Input validation")
    print("     - Cost tracking")
    print()
    print("  6. Parallel Execution & Error Recovery (NEW)")
    print("     - Parallel agent execution")
    print("     - Automatic retry logic")
    print("     - Fallback strategies")
    print("     - Circuit breaker pattern")
    print()
    print("  7. Run All Examples")
    print()
    print("  0. Exit")
    print()


def check_requirements(example_num: int) -> bool:
    """
    Check if requirements are met for an example.
    
    Args:
        example_num: Example number to check
        
    Returns:
        True if requirements are met
    """
    if example_num in [2, 4]:
        if not os.getenv("OPENAI_API_KEY"):
            print(f"\n⚠️  Example {example_num} requires OPENAI_API_KEY environment variable.")
            print("Please set it and try again:")
            print("  export OPENAI_API_KEY='your-key-here'\n")
            return False
    
    if example_num == 3:
        # Check if jq is installed
        import subprocess
        try:
            subprocess.run(
                ["jq", "--version"],
                capture_output=True,
                timeout=5
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            print("\n⚠️  Example 3 works best with jq installed.")
            print("Install jq for full functionality:")
            print("  macOS: brew install jq")
            print("  Ubuntu/Debian: sudo apt-get install jq")
            print("  Windows: choco install jq")
            print("\nContinuing anyway (some features may not work)...\n")
    
    return True


def run_example(example_num: int) -> bool:
    """
    Run a specific example.
    
    Args:
        example_num: Example number (1-6)
        
    Returns:
        True if successful
    """
    if not check_requirements(example_num):
        return False
    
    try:
        if example_num == 1:
            from .example1_basic_middleware import run_example
            run_example()
        elif example_num == 2:
            from .example2_langgraph_subagents import run_example
            run_example()
        elif example_num == 3:
            from .example3_mcp_tools import run_example
            run_example()
        elif example_num == 4:
            from .example4_streaming_responses import run_example
            import asyncio
            asyncio.run(run_example())
        elif example_num == 5:
            from .example5_caching_and_config import run_example
            run_example()
        elif example_num == 6:
            from .example6_parallel_and_retry import run_example
            import asyncio
            asyncio.run(run_example())
        else:
            print(f"Invalid example number: {example_num}")
            return False
        
        return True
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Example interrupted by user.\n")
        return False
    
    except Exception as e:
        print(f"\n\n❌ Error running example: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def run_all_examples():
    """Run all examples sequentially."""
    examples = [1, 2, 3, 4, 5, 6]
    
    print("\n" + "="*70)
    print("RUNNING ALL EXAMPLES")
    print("="*70)
    
    for i, example_num in enumerate(examples, 1):
        print(f"\n\n{'='*70}")
        print(f"RUNNING EXAMPLE {example_num} OF {len(examples)}")
        print(f"{'='*70}\n")
        
        success = run_example(example_num)
        
        if not success:
            print(f"\n⚠️  Example {example_num} did not complete successfully.")
            response = input("\nContinue with remaining examples? (y/n): ")
            if response.lower() != 'y':
                print("\nStopping execution.\n")
                return
        
        if i < len(examples):
            print("\n" + "-"*70)
            input("\nPress Enter to continue to next example...")
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70 + "\n")


def interactive_mode():
    """Run in interactive mode with menu."""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("Select an example (0-4): ").strip()
            
            if choice == '0':
                print("\nGoodbye!\n")
                break
            
            elif choice == '4':
                run_all_examples()
            
            elif choice in ['1', '2', '3', '4', '5', '6']:
                example_num = int(choice)
                run_example(example_num)
                input("\nPress Enter to return to menu...")
            
            else:
                print("\n❌ Invalid choice. Please select 0-4.\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point."""
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg in ['-h', '--help']:
            print("\nUsage:")
            print("  python -m deepagents_sample.examples.run_all [option]")
            print("\nOptions:")
            print("  (none)    Interactive menu")
            print("  1         Run Example 1: Basic Middleware")
            print("  2         Run Example 2: LangGraph Subagents")
            print("  3         Run Example 3: MCP Tools")
            print("  all       Run all examples")
            print("  -h, --help  Show this help")
            print()
            return
        
        elif arg == 'all':
            print_banner()
            run_all_examples()
            return
        
        elif arg in ['1', '2', '3', '4', '5', '6']:
            print_banner()
            example_num = int(arg)
            run_example(example_num)
            return
        
        else:
            print(f"\n❌ Unknown option: {arg}")
            print("Use -h or --help for usage information.\n")
            sys.exit(1)
    
    # No arguments - run interactive mode
    interactive_mode()


if __name__ == "__main__":
    main()
