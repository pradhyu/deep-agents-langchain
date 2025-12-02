#!/usr/bin/env python3
"""
Example 4: Streaming Responses

Demonstrates real-time streaming of agent responses for better UX.
Shows token-by-token output as the agent generates responses.
"""

import os
import asyncio
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from deepagents_sample.agents import ResearchAgent
from deepagents_sample.middleware import MiddlewareChain, LoggingMiddleware
from deepagents_sample.utils import setup_logger

logger = setup_logger("example4", level=logging.INFO)


async def stream_agent_response(agent, task: str):
    """
    Stream agent response token by token.
    
    Args:
        agent: The agent to use
        task: Task to process
    """
    logger.info("="*70)
    logger.info("STREAMING AGENT RESPONSE")
    logger.info("="*70)
    logger.info(f"Task: {task}")
    logger.info("-"*70)
    
    # Create streaming model
    streaming_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        streaming=True
    )
    
    # Stream the response
    full_response = ""
    async for chunk in streaming_model.astream([HumanMessage(content=task)]):
        if chunk.content:
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
    
    print("\n")
    logger.info("-"*70)
    logger.info(f"Complete response received ({len(full_response)} chars)")
    
    return full_response


async def stream_workflow_events(workflow, initial_state):
    """
    Stream workflow execution events in real-time.
    
    Args:
        workflow: Compiled LangGraph workflow
        initial_state: Initial state
    """
    logger.info("="*70)
    logger.info("STREAMING WORKFLOW EVENTS")
    logger.info("="*70)
    
    async for event in workflow.astream(initial_state):
        logger.info(f"Event: {list(event.keys())}")
        
        # Show agent transitions
        if "agent_history" in event:
            history = event["agent_history"]
            if history:
                logger.info(f"  → Agent: {history[-1]}")
        
        # Show results
        if "results" in event and event["results"]:
            for agent, result in event["results"].items():
                logger.info(f"  ✓ {agent}: {result[:100]}...")
    
    logger.info("="*70)
    logger.info("Workflow complete!")


async def progressive_research(research_agent, queries):
    """
    Show progressive research results as they come in.
    
    Args:
        research_agent: Research agent instance
        queries: List of queries to execute
    """
    logger.info("="*70)
    logger.info("PROGRESSIVE RESEARCH")
    logger.info("="*70)
    
    results = []
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\n[Query {i}/{len(queries)}] {query}")
        logger.info("-"*70)
        
        # Simulate streaming research
        result = research_agent.process(query)
        results.append(result)
        
        # Show immediate result
        logger.info(f"✓ Result: {result[:200]}...")
        
        # Small delay for demo
        await asyncio.sleep(0.5)
    
    logger.info("\n" + "="*70)
    logger.info(f"All {len(results)} queries complete!")
    
    return results


async def run_example():
    """Run the streaming responses example."""
    
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 4: STREAMING RESPONSES")
    logger.info("="*70)
    logger.info("This example demonstrates real-time streaming of agent outputs.")
    logger.info("Watch responses appear token-by-token for better UX.\n")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set. This example requires an API key.")
        logger.info("Please set OPENAI_API_KEY and try again.\n")
        return
    
    # Example 1: Stream single agent response
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 4A: STREAMING SINGLE RESPONSE")
    logger.info("="*70)
    
    task = "Explain how middleware works in multi-agent systems in 2-3 sentences."
    await stream_agent_response(None, task)
    
    # Example 2: Progressive research
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 4B: PROGRESSIVE RESEARCH")
    logger.info("="*70)
    
    middleware = MiddlewareChain()
    middleware.add(LoggingMiddleware(verbose=False))
    
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    research_agent = ResearchAgent(model=model, middleware_chain=middleware)
    
    queries = [
        "What are the benefits of agent-based systems?",
        "How does LangGraph help with workflows?",
        "What is the role of middleware?"
    ]
    
    await progressive_research(research_agent, queries)
    
    # Key takeaways
    logger.info("\n" + "="*70)
    logger.info("KEY TAKEAWAYS")
    logger.info("="*70)
    logger.info("1. Streaming provides immediate feedback to users")
    logger.info("2. Token-by-token output improves perceived performance")
    logger.info("3. Progressive results show work in progress")
    logger.info("4. Better UX for long-running operations")
    logger.info("5. Can cancel operations mid-stream")
    logger.info("")
    logger.info("Benefits:")
    logger.info("- Immediate user feedback")
    logger.info("- Better perceived performance")
    logger.info("- Can show progress")
    logger.info("- Cancellable operations")


if __name__ == "__main__":
    asyncio.run(run_example())
