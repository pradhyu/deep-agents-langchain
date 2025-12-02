#!/usr/bin/env python3
"""
Example 2: LangGraph with Subagents

This example demonstrates hierarchical agent orchestration using LangGraph:
- Coordinator agent that delegates tasks
- Research and Analysis subagents
- State management across workflow
- Agent communication patterns
- Automatic routing based on task type
"""

import os
from langchain_openai import ChatOpenAI

from deepagents_sample.agents import CoordinatorAgent, ResearchAgent, AnalysisAgent
from deepagents_sample.middleware import MiddlewareChain, LoggingMiddleware, MetricsMiddleware
from deepagents_sample.workflow import create_agent_workflow, run_workflow


def run_example():
    """Run the LangGraph subagents example."""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: LANGGRAPH WITH SUBAGENTS")
    print("="*70)
    print("\nThis example demonstrates hierarchical agent orchestration with LangGraph.")
    print("The coordinator delegates tasks to specialized subagents.\n")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. This example requires an OpenAI API key.")
        print("Please set OPENAI_API_KEY environment variable and try again.\n")
        print("Example: export OPENAI_API_KEY='your-key-here'\n")
        return
    
    # Create middleware chain
    print("Step 1: Setting up middleware...")
    middleware_chain = MiddlewareChain()
    middleware_chain.add(LoggingMiddleware(verbose=False))  # Less verbose for clarity
    middleware_chain.add(MetricsMiddleware())
    print("  ✓ Middleware chain created\n")
    
    # Create agents
    print("Step 2: Creating agents...")
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    coordinator = CoordinatorAgent(
        model=model,
        middleware_chain=middleware_chain,
        name="coordinator"
    )
    print("  ✓ Coordinator agent created")
    
    research_agent = ResearchAgent(
        model=model,
        middleware_chain=middleware_chain,
        name="research_agent"
    )
    print("  ✓ Research agent created")
    
    analysis_agent = AnalysisAgent(
        model=model,
        middleware_chain=middleware_chain,
        name="analysis_agent"
    )
    print("  ✓ Analysis agent created\n")
    
    # Register subagents with coordinator
    print("Step 3: Registering subagents with coordinator...")
    coordinator.register_subagent("research_agent", research_agent)
    coordinator.register_subagent("analysis_agent", analysis_agent)
    print("  ✓ Subagents registered\n")
    
    # Create workflow
    print("Step 4: Building LangGraph workflow...")
    workflow = create_agent_workflow(
        coordinator=coordinator,
        research_agent=research_agent,
        analysis_agent=analysis_agent
    )
    print("  ✓ Workflow compiled\n")
    
    # Example 1: Research task
    print("="*70)
    print("EXAMPLE 2A: RESEARCH TASK")
    print("="*70)
    
    research_task = "Gather information about the current system environment"
    print(f"\nTask: {research_task}")
    print("\nExpected flow: Coordinator → Research Agent → Coordinator → End\n")
    
    result1 = run_workflow(workflow, research_task, verbose=True)
    
    print(f"\nFinal Output:\n{result1.get('final_output', 'No output')}\n")
    
    # Example 2: Analysis task
    print("\n" + "="*70)
    print("EXAMPLE 2B: ANALYSIS TASK")
    print("="*70)
    
    analysis_task = "Analyze the distribution of users by role in our system"
    print(f"\nTask: {analysis_task}")
    print("\nExpected flow: Coordinator → Analysis Agent → Coordinator → End\n")
    
    result2 = run_workflow(workflow, analysis_task, verbose=True)
    
    print(f"\nFinal Output:\n{result2.get('final_output', 'No output')}\n")
    
    # Display metrics
    print("="*70)
    print("WORKFLOW METRICS")
    print("="*70)
    
    # Get metrics from middleware
    metrics_middleware = middleware_chain.middlewares[1]  # MetricsMiddleware
    metrics_middleware.print_summary()
    
    # Key takeaways
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. LangGraph manages complex multi-agent workflows
2. Coordinator analyzes tasks and routes to appropriate subagents
3. State is maintained across the entire workflow
4. Agents communicate through shared state
5. Conditional routing based on task type
6. Automatic aggregation of subagent results

Workflow Structure:
┌─────────────┐
│ Coordinator │ ← Entry point
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌──────┐ ┌──────────┐
│Research│ │ Analysis │ ← Subagents
└───┬───┘ └────┬─────┘
    │          │
    └────┬─────┘
         ▼
   ┌──────────┐
   │Coordinator│ ← Aggregation
   └──────────┘
         │
         ▼
       [END]

Benefits:
- Clear separation of concerns
- Reusable agent components
- Scalable architecture
- Easy to add new agents
- Built-in state management
    """)


if __name__ == "__main__":
    run_example()
