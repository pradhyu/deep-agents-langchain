#!/usr/bin/env python3
"""
Example 3: MCP Tool Integration

This example demonstrates how agents use MCP (Model Context Protocol) tools
to interact with external systems:
- CommandTool for executing shell commands
- JSONSearchTool for querying JSON data with jq
- Tool registration and invocation
- Error handling and timeouts
- Tool usage statistics
"""

import os
from pathlib import Path

from deepagents_sample.tools import CommandTool, JSONSearchTool
from deepagents_sample.agents import ResearchAgent, AnalysisAgent
from deepagents_sample.middleware import MiddlewareChain, LoggingMiddleware, MetricsMiddleware


def run_example():
    """Run the MCP tools example."""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: MCP TOOL INTEGRATION")
    print("="*70)
    print("\nThis example demonstrates how agents use MCP tools to interact")
    print("with external systems and data sources.\n")
    
    # Part 1: CommandTool demonstration
    print("="*70)
    print("PART 1: COMMAND TOOL")
    print("="*70)
    print("\nCommandTool allows agents to execute shell commands safely.\n")
    
    print("Step 1: Creating CommandTool with allowed commands...")
    command_tool = CommandTool(
        timeout=10,
        allowed_commands=["echo", "ls", "date", "pwd", "whoami", "uname"]
    )
    print("  ✓ CommandTool created with security constraints\n")
    
    # Execute various commands
    commands = [
        ("echo 'Hello from MCP Tool!'", "Simple echo command"),
        ("date", "Get current date/time"),
        ("pwd", "Print working directory"),
        ("uname -a", "System information"),
    ]
    
    print("Step 2: Executing commands...\n")
    for cmd, description in commands:
        print(f"[{description}]")
        print(f"Command: {cmd}")
        
        response = command_tool.run(command=cmd)
        
        if response.success:
            print(f"✓ Output: {response.result}")
            print(f"  Execution time: {response.execution_time:.3f}s")
        else:
            print(f"✗ Error: {response.error}")
        print()
    
    # Show tool stats
    print("Command Tool Statistics:")
    stats = command_tool.get_stats()
    print(f"  Total calls: {stats['call_count']}")
    print(f"  Total time: {stats['total_time']:.3f}s")
    print(f"  Average time: {stats['avg_time']:.3f}s\n")
    
    # Part 2: JSONSearchTool demonstration
    print("="*70)
    print("PART 2: JSON SEARCH TOOL")
    print("="*70)
    print("\nJSONSearchTool uses jq to query JSON data.\n")
    
    # Check if jq is installed
    print("Step 1: Checking jq installation...")
    try:
        json_tool = JSONSearchTool(check_jq=True)
        print("  ✓ jq is installed and ready\n")
    except RuntimeError as e:
        print(f"  ✗ {e}")
        print("\nSkipping JSON tool examples. Please install jq to continue.\n")
        json_tool = None
    
    if json_tool:
        # Find sample data file
        data_file = Path("data/sample.json")
        if not data_file.exists():
            print(f"  ✗ Sample data file not found: {data_file}")
            print("  Creating sample data...\n")
            data_file.parent.mkdir(exist_ok=True)
            # Would need to create sample data here
        
        if data_file.exists():
            print(f"Step 2: Querying JSON data from {data_file}...\n")
            
            queries = [
                (".", "Get all data"),
                (".users | length", "Count users"),
                (".users[0]", "Get first user"),
                ('.users[] | select(.role == "engineer")', "Filter engineers"),
                (".users[].name", "Extract all names"),
                (".projects[] | select(.status == \"active\")", "Active projects"),
                (".metrics.total_budget", "Get total budget"),
            ]
            
            for query, description in queries:
                print(f"[{description}]")
                print(f"Query: {query}")
                
                response = json_tool.run(file_path=str(data_file), jq_query=query)
                
                if response.success:
                    import json
                    if isinstance(response.result, (dict, list)):
                        result_str = json.dumps(response.result, indent=2)
                    else:
                        result_str = str(response.result)
                    
                    # Truncate long results
                    if len(result_str) > 200:
                        result_str = result_str[:200] + "..."
                    
                    print(f"✓ Result:\n{result_str}")
                    print(f"  Execution time: {response.execution_time:.3f}s")
                else:
                    print(f"✗ Error: {response.error}")
                print()
            
            # Show tool stats
            print("JSON Tool Statistics:")
            stats = json_tool.get_stats()
            print(f"  Total calls: {stats['call_count']}")
            print(f"  Total time: {stats['total_time']:.3f}s")
            print(f"  Average time: {stats['avg_time']:.3f}s\n")
    
    # Part 3: Agents using tools
    print("="*70)
    print("PART 3: AGENTS WITH MCP TOOLS")
    print("="*70)
    print("\nDemonstrating how agents integrate and use MCP tools.\n")
    
    # Create middleware
    middleware = MiddlewareChain()
    middleware.add(LoggingMiddleware(verbose=False))
    middleware.add(MetricsMiddleware())
    
    # Create research agent (has both tools)
    print("Step 1: Creating ResearchAgent with MCP tools...")
    
    # Check if we have API key for agent creation
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        research_agent = ResearchAgent(
            model=model,
            middleware_chain=middleware,
            name="research_agent"
        )
        print("  ✓ Research agent created with CommandTool and JSONSearchTool\n")
    else:
        print("  ⚠️  OPENAI_API_KEY not set. Skipping agent examples.")
        print("  Tools still work independently!\n")
        research_agent = None
    
    # Use agent with tools
    if research_agent:
        print("Step 2: Agent executing tools...\n")
        
        print("[Research Task: System Info]")
        result = research_agent.process_with_tools(
            task="Get system information",
            command="uname -a"
        )
        print(result)
        print()
        
        if json_tool and data_file.exists():
            print("[Research Task: User Data]")
            result = research_agent.process_with_tools(
                task="Find all engineers in the system",
                json_file=str(data_file),
                jq_query='.users[] | select(.role == "engineer")'
            )
            print(result)
            print()
            
            # Create analysis agent
            print("Step 3: Creating AnalysisAgent for data analysis...")
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            analysis_agent = AnalysisAgent(
                model=model,
                middleware_chain=middleware,
                name="analysis_agent"
            )
            print("  ✓ Analysis agent created\n")
            
            print("[Analysis Task: Project Analysis]")
            result = analysis_agent.analyze_with_queries(
                task="Analyze project data",
                file_path=str(data_file),
                queries=[
                    {"name": "Total Projects", "query": ".projects | length"},
                    {"name": "Active Projects", "query": '.projects[] | select(.status == "active") | .name'},
                    {"name": "Total Budget", "query": ".metrics.total_budget"},
                ]
            )
            print(result)
            print()
    else:
        print("Step 2: Skipping agent examples (no API key)\n")
    
    # Show agent tool stats
    if research_agent:
        print("="*70)
        print("AGENT TOOL USAGE STATISTICS")
        print("="*70)
        print("\nResearch Agent:")
        research_stats = research_agent.get_tool_stats()
        for tool_name, stats in research_stats.items():
            print(f"  {tool_name}:")
            print(f"    Calls: {stats['call_count']}")
            print(f"    Total time: {stats['total_time']:.3f}s")
        
        if json_tool and data_file.exists() and 'analysis_agent' in locals():
            print("\nAnalysis Agent:")
            analysis_stats = analysis_agent.get_tool_stats()
            for tool_name, stats in analysis_stats.items():
                print(f"  {tool_name}:")
                print(f"    Calls: {stats['call_count']}")
                print(f"    Total time: {stats['total_time']:.3f}s")
    
    # Key takeaways
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. MCP tools provide external capabilities to agents
2. CommandTool enables safe shell command execution
3. JSONSearchTool uses jq for powerful JSON querying
4. Tools have built-in error handling and timeouts
5. Tool usage is tracked with statistics
6. Agents can use multiple tools together

Tool Benefits:
- Standardized interface (MCPTool base class)
- Automatic error handling
- Performance tracking
- Security constraints (allowed commands)
- Consistent response format

Common Use Cases:
- System information gathering
- Data extraction and transformation
- File operations
- API calls (can be extended)
- Database queries (can be extended)

Security Considerations:
- Command whitelisting
- Timeout protection
- Input validation
- Sandboxing (can be added)
    """)


if __name__ == "__main__":
    run_example()
