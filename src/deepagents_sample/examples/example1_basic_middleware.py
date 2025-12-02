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
from langchain_openai import ChatOpenAI

from deepagents_sample.middleware import (
    MiddlewareChain,
    LoggingMiddleware,
    MetricsMiddleware,
    AgentRequest,
    AgentResponse
)
from deepagents_sample.agents import CoordinatorAgent


def run_example():
    """Run the basic middleware example."""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: BASIC MIDDLEWARE USAGE")
    print("="*70)
    print("\nThis example demonstrates middleware interception of agent communications.")
    print("Watch how LoggingMiddleware and MetricsMiddleware process each request/response.\n")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Using mock mode.\n")
        use_llm = False
    else:
        use_llm = True
    
    # Create middleware chain
    print("Step 1: Creating middleware chain...")
    print("  - Adding LoggingMiddleware (captures all communications)")
    print("  - Adding MetricsMiddleware (tracks performance)\n")
    
    middleware_chain = MiddlewareChain()
    logging_middleware = LoggingMiddleware(verbose=True)
    metrics_middleware = MetricsMiddleware()
    
    middleware_chain.add(logging_middleware)
    middleware_chain.add(metrics_middleware)
    
    # Create agent with middleware
    print("Step 2: Creating CoordinatorAgent with middleware...\n")
    
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
    print("Step 3: Demonstrating middleware interception...\n")
    print("-" * 70)
    
    # Example 1: Simple request/response
    print("\n[Example 1: Simple Task]\n")
    
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
    print("\n[Example 2: Data Query]\n")
    
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
        print("\n[Example 3: Real Agent with Middleware]\n")
        
        result = coordinator.process("What is the capital of France?")
        print(f"\nAgent Result: {result}\n")
    
    # Display metrics summary
    print("\n" + "-" * 70)
    print("\nStep 4: Displaying collected metrics...\n")
    metrics_middleware.print_summary()
    
    # Key takeaways
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Middleware intercepts ALL agent communications
2. LoggingMiddleware provides visibility into request/response flow
3. MetricsMiddleware tracks timing and performance
4. Multiple middleware can be chained together
5. Middleware doesn't alter the core agent logic
6. Each request/response pair is tracked with a unique ID

Middleware is essential for:
- Debugging agent interactions
- Performance monitoring
- Audit logging
- Request/response transformation
- Error tracking
    """)


if __name__ == "__main__":
    run_example()
