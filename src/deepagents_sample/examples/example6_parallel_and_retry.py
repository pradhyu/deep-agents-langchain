#!/usr/bin/env python3
"""
Example 6: Parallel Execution and Error Recovery

Demonstrates:
- Parallel agent execution for better performance
- Automatic retry logic for failed operations
- Error recovery strategies
- Graceful degradation
"""

import os
import asyncio
import logging
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from deepagents_sample.agents import ResearchAgent, AnalysisAgent
from deepagents_sample.middleware import MiddlewareChain, MetricsMiddleware
from deepagents_sample.tools import CommandTool
from deepagents_sample.utils import setup_logger

logger = setup_logger("example6", level=logging.INFO)


# ============================================================================
# 1. PARALLEL EXECUTION
# ============================================================================

async def parallel_research(tasks: List[str]) -> List[Dict[str, Any]]:
    """
    Execute multiple research tasks in parallel.
    
    Args:
        tasks: List of research tasks
        
    Returns:
        List of results
    """
    logger.info("="*70)
    logger.info("PARALLEL RESEARCH EXECUTION")
    logger.info("="*70)
    logger.info(f"Executing {len(tasks)} tasks in parallel...")
    
    async def research_task(task: str, index: int) -> Dict[str, Any]:
        """Single research task."""
        logger.info(f"[Task {index + 1}] Starting: {task[:50]}...")
        
        # Simulate research (in real scenario, use actual agent)
        await asyncio.sleep(1)  # Simulate work
        
        result = f"Research result for: {task}"
        logger.info(f"[Task {index + 1}] ✓ Complete")
        
        return {
            "task": task,
            "result": result,
            "index": index
        }
    
    # Execute all tasks in parallel
    import time
    start_time = time.time()
    
    results = await asyncio.gather(*[
        research_task(task, i) for i, task in enumerate(tasks)
    ])
    
    duration = time.time() - start_time
    
    logger.info(f"\n✓ All {len(tasks)} tasks complete in {duration:.2f}s")
    logger.info(f"  Sequential would take: ~{len(tasks):.0f}s")
    logger.info(f"  Speedup: {len(tasks) / duration:.1f}x")
    
    return results


async def parallel_tool_execution(commands: List[str]) -> List[Dict[str, Any]]:
    """
    Execute multiple tool commands in parallel.
    
    Args:
        commands: List of commands to execute
        
    Returns:
        List of results
    """
    logger.info("="*70)
    logger.info("PARALLEL TOOL EXECUTION")
    logger.info("="*70)
    
    tool = CommandTool(timeout=10, allowed_commands=["echo", "date", "pwd", "uname"])
    
    async def execute_command(cmd: str, index: int) -> Dict[str, Any]:
        """Execute single command."""
        logger.info(f"[Command {index + 1}] {cmd}")
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, tool.run, cmd)
        
        return {
            "command": cmd,
            "success": response.success,
            "result": response.result if response.success else response.error,
            "execution_time": response.execution_time
        }
    
    import time
    start_time = time.time()
    
    results = await asyncio.gather(*[
        execute_command(cmd, i) for i, cmd in enumerate(commands)
    ])
    
    duration = time.time() - start_time
    
    logger.info(f"\n✓ Executed {len(commands)} commands in {duration:.2f}s")
    
    for result in results:
        status = "✓" if result["success"] else "✗"
        logger.info(f"  {status} {result['command']}: {result['result'][:50]}")
    
    return results


# ============================================================================
# 2. ERROR RECOVERY & RETRY LOGIC
# ============================================================================

class RetryableAgent:
    """
    Agent with automatic retry logic.
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.attempt_count = 0
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def process_with_retry(self, task: str) -> str:
        """
        Process task with automatic retry on failure.
        
        Args:
            task: Task to process
            
        Returns:
            Result
            
        Raises:
            Exception: If all retries fail
        """
        self.attempt_count += 1
        logger.info(f"Attempt {self.attempt_count}: {task[:50]}...")
        
        # Simulate occasional failures
        import random
        if random.random() < 0.3:  # 30% failure rate
            logger.warning(f"  ✗ Attempt {self.attempt_count} failed (simulated)")
            raise ConnectionError("Simulated connection error")
        
        logger.info(f"  ✓ Attempt {self.attempt_count} succeeded")
        return f"Result for: {task}"


class FallbackAgent:
    """
    Agent with fallback strategies.
    """
    
    def __init__(self):
        self.primary_available = True
        self.fallback_count = 0
    
    def process(self, task: str) -> str:
        """
        Process with fallback to alternative method.
        
        Args:
            task: Task to process
            
        Returns:
            Result
        """
        try:
            # Try primary method
            if self.primary_available:
                return self._process_primary(task)
            else:
                raise Exception("Primary unavailable")
        
        except Exception as e:
            logger.warning(f"Primary method failed: {e}")
            logger.info("Falling back to alternative method...")
            self.fallback_count += 1
            return self._process_fallback(task)
    
    def _process_primary(self, task: str) -> str:
        """Primary processing method."""
        logger.info("Using primary method (GPT-4)")
        return f"Primary result: {task}"
    
    def _process_fallback(self, task: str) -> str:
        """Fallback processing method."""
        logger.info("Using fallback method (GPT-3.5)")
        return f"Fallback result: {task}"


class CircuitBreaker:
    """
    Circuit breaker pattern for error handling.
    """
    
    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """
        Call function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open
        """
        if self.state == "OPEN":
            # Check if timeout has passed
            import time
            if time.time() - self.last_failure_time > self.timeout:
                logger.info("Circuit breaker: OPEN → HALF_OPEN")
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset if in HALF_OPEN
            if self.state == "HALF_OPEN":
                logger.info("Circuit breaker: HALF_OPEN → CLOSED")
                self.state = "CLOSED"
                self.failure_count = 0
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            
            if self.failure_count >= self.failure_threshold:
                import time
                self.last_failure_time = time.time()
                self.state = "OPEN"
                logger.error(f"Circuit breaker: CLOSED → OPEN (failures: {self.failure_count})")
            
            raise


# ============================================================================
# 3. GRACEFUL DEGRADATION
# ============================================================================

class ResilientWorkflow:
    """
    Workflow with graceful degradation.
    """
    
    def __init__(self):
        self.services = {
            "llm": True,
            "tools": True,
            "cache": True
        }
    
    def process(self, task: str) -> Dict[str, Any]:
        """
        Process with graceful degradation.
        
        Args:
            task: Task to process
            
        Returns:
            Result with degradation info
        """
        result = {
            "task": task,
            "result": None,
            "degraded": False,
            "services_used": []
        }
        
        # Try full-featured processing
        if all(self.services.values()):
            logger.info("✓ All services available - full processing")
            result["result"] = f"Full result: {task}"
            result["services_used"] = ["llm", "tools", "cache"]
            return result
        
        # Degraded mode
        result["degraded"] = True
        
        if self.services["llm"]:
            logger.warning("⚠️  Degraded mode: LLM only (no tools/cache)")
            result["result"] = f"LLM-only result: {task}"
            result["services_used"] = ["llm"]
        
        elif self.services["cache"]:
            logger.warning("⚠️  Degraded mode: Cache only")
            result["result"] = f"Cached result: {task}"
            result["services_used"] = ["cache"]
        
        else:
            logger.error("✗ Critical: All services unavailable")
            result["result"] = "Service temporarily unavailable"
            result["services_used"] = []
        
        return result


# ============================================================================
# EXAMPLE EXECUTION
# ============================================================================

async def run_example():
    """Run the parallel execution and error recovery example."""
    
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 6: PARALLEL EXECUTION & ERROR RECOVERY")
    logger.info("="*70)
    logger.info("Demonstrates parallel execution, retry logic, and error recovery.\n")
    
    # Part 1: Parallel Execution
    logger.info("\n" + "="*70)
    logger.info("PART 1: PARALLEL EXECUTION")
    logger.info("="*70)
    
    tasks = [
        "Research topic A",
        "Research topic B",
        "Research topic C",
        "Research topic D"
    ]
    
    results = await parallel_research(tasks)
    logger.info(f"\n✓ Completed {len(results)} parallel tasks")
    
    # Part 2: Parallel Tool Execution
    logger.info("\n" + "="*70)
    logger.info("PART 2: PARALLEL TOOL EXECUTION")
    logger.info("="*70)
    
    commands = [
        "echo 'Hello'",
        "date",
        "pwd",
        "uname -a"
    ]
    
    tool_results = await parallel_tool_execution(commands)
    
    # Part 3: Retry Logic
    logger.info("\n" + "="*70)
    logger.info("PART 3: AUTOMATIC RETRY LOGIC")
    logger.info("="*70)
    
    retryable = RetryableAgent(max_retries=3)
    
    try:
        result = retryable.process_with_retry("Important task")
        logger.info(f"✓ Final result: {result}")
    except Exception as e:
        logger.error(f"✗ All retries failed: {e}")
    
    # Part 4: Fallback Strategy
    logger.info("\n" + "="*70)
    logger.info("PART 4: FALLBACK STRATEGY")
    logger.info("="*70)
    
    fallback_agent = FallbackAgent()
    fallback_agent.primary_available = False  # Simulate primary failure
    
    result = fallback_agent.process("Analyze data")
    logger.info(f"Result: {result}")
    logger.info(f"Fallback count: {fallback_agent.fallback_count}")
    
    # Part 5: Circuit Breaker
    logger.info("\n" + "="*70)
    logger.info("PART 5: CIRCUIT BREAKER PATTERN")
    logger.info("="*70)
    
    circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=5)
    
    def unreliable_service():
        """Simulated unreliable service."""
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("Service error")
        return "Success"
    
    # Try multiple calls
    for i in range(5):
        try:
            result = circuit_breaker.call(unreliable_service)
            logger.info(f"Call {i + 1}: ✓ {result}")
        except Exception as e:
            logger.warning(f"Call {i + 1}: ✗ {e}")
    
    logger.info(f"Circuit breaker state: {circuit_breaker.state}")
    
    # Part 6: Graceful Degradation
    logger.info("\n" + "="*70)
    logger.info("PART 6: GRACEFUL DEGRADATION")
    logger.info("="*70)
    
    workflow = ResilientWorkflow()
    
    # Full service
    result = workflow.process("Task 1")
    logger.info(f"Result: {result['result']}")
    logger.info(f"Degraded: {result['degraded']}")
    
    # Degraded service
    workflow.services["tools"] = False
    workflow.services["cache"] = False
    
    result = workflow.process("Task 2")
    logger.info(f"Result: {result['result']}")
    logger.info(f"Degraded: {result['degraded']}")
    logger.info(f"Services used: {result['services_used']}")
    
    # Key takeaways
    logger.info("\n" + "="*70)
    logger.info("KEY TAKEAWAYS")
    logger.info("="*70)
    logger.info("1. Parallel execution provides 3-4x speedup")
    logger.info("2. Automatic retry handles transient failures")
    logger.info("3. Fallback strategies ensure availability")
    logger.info("4. Circuit breakers prevent cascade failures")
    logger.info("5. Graceful degradation maintains service")
    logger.info("")
    logger.info("Benefits:")
    logger.info("- Better performance with parallelization")
    logger.info("- Higher reliability with retry logic")
    logger.info("- Improved availability with fallbacks")
    logger.info("- System protection with circuit breakers")
    logger.info("- Continuous service with degradation")


if __name__ == "__main__":
    asyncio.run(run_example())
