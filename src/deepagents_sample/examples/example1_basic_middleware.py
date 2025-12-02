#!/usr/bin/env python3
"""
Example 1: Basic Middleware Usage

This example demonstrates how middleware intercepts and processes
agent requests and responses. It shows:
- LoggingMiddleware capturing all communications
- MetricsMiddleware tracking performance
- Middleware chaining
- Request/response flow visibility
"""

import os
import logging
from langchain_openai import ChatOpenAI

from deepagents_sample.middleware import (
    MiddlewareChain,
    LoggingMiddleware,
    MetricsMiddleware,
    AgentRequest,
    AgentResponse
)
from deepagents_sample.agents import CoordinatorAgent
from deepagents_sample.utils import setup_logger

# Set up logging
logger = setup_logger("example1", level=logging.INFO)


def run_example():
    """Run the basic middleware example."""
    
    logger.info("="*70)
    logger.info("EXAMPLE 1: BASIC MIDDLEWARE USAGE")
    logger.info("="*70)
    logger.info("This example demonstrates middleware interception of agent communications.")
    logger.info("Watch how LoggingMiddleware and MetricsMiddleware process each request/response.")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set. Using mock mode.")
        use_llm = False
    else:
        use_llm = True
    
    # Create middleware chain
    logger.info("Step 1: Creating middleware chain...")
    logger.info("  - Adding LoggingMiddleware (captures all communications)")
    logger.info("  - Adding MetricsMiddleware (tracks performance)")
    
    # Create separate loggers for middleware
    middleware_logger = setup_logger("middleware", level=logging.DEBUG)
    metrics_logger = setup_logger("metrics", level=logging.INFO)
    
    middleware_chain = MiddlewareChain()
    logging_middleware = LoggingMiddleware(verbose=True, logger=middleware_logger)
    metrics_middleware = MetricsMiddleware(logger=metrics_logger)
    
    middleware_chain.add(logging_middleware)
    middleware_chain.add(metrics_middleware)
    
    # Create agent with middleware
    logger.info("Step 2: Creating CoordinatorAgent with middleware...")
    
    if use_llm:
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        coordinator = CoordinatorAgent(
            model=model,
            middleware_chain=middleware_chain,
            name="coordinator"
        )
    else:
        # Mock mode - demonstrate middleware without LLM
        coordinator = None
    
    # Demonstrate middleware with manual requests/responses
    logger.info("Step 3: Demonstrating middleware interception...")
    logger.info("-" * 70)
    
    # Example 1: Simple request/response
    logger.info("[Example 1: Simple Task]")
    
    request1 = AgentRequest(
        agent_name="coordinator",
        input_data="Analyze the current system status",
        metadata={"priority": "high"}
    )
    
    processed_request1 = middleware_chain.process_request(request1)
    
    # Simulate agent processing
    response1 = AgentResponse(
        agent_name="coordinator",
        output_data="System status: All services operational",
        request_id=processed_request1.request_id,
        metadata={"status": "success"}
    )
    
    processed_response1 = middleware_chain.process_response(response1)
    
    # Example 2: Another request/response
    logger.info("[Example 2: Data Query]")
    
    request2 = AgentRequest(
        agent_name="coordinator",
        input_data="Query user database for active users",
        metadata={"priority": "medium"}
    )
    
    processed_request2 = middleware_chain.process_request(request2)
    
    response2 = AgentResponse(
        agent_name="coordinator",
        output_data="Found 150 active users in the database",
        request_id=processed_request2.request_id,
        metadata={"status": "success", "count": 150}
    )
    
    processed_response2 = middleware_chain.process_response(response2)
    
    # Example 3: Using actual agent if LLM available
    if use_llm and coordinator:
        logger.info("[Example 3: Real Agent with Middleware]")
        
        result = coordinator.process("What is the capital of France?")
        logger.info(f"Agent Result: {result}")
    
    # Display metrics summary
    logger.info("-" * 70)
    logger.info("Step 4: Displaying collected metrics...")
    metrics_middleware.print_summary()
    
    # Key takeaways
    logger.info("="*70)
    logger.info("KEY TAKEAWAYS")
    logger.info("="*70)
    logger.info("1. Middleware intercepts ALL agent communications")
    logger.info("2. LoggingMiddleware provides visibility into request/response flow")
    logger.info("3. MetricsMiddleware tracks timing and performance")
    logger.info("4. Multiple middleware can be chained together")
    logger.info("5. Middleware doesn't alter the core agent logic")
    logger.info("6. Each request/response pair is tracked with a unique ID")
    logger.info("")
    logger.info("Middleware is essential for:")
    logger.info("- Debugging agent interactions")
    logger.info("- Performance monitoring")
    logger.info("- Audit logging")
    logger.info("- Request/response transformation")
    logger.info("- Error tracking")


if __name__ == "__main__":
    run_example()
