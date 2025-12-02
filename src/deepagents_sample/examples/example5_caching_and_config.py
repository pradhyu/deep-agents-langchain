#!/usr/bin/env python3
"""
Example 5: Caching and Configuration Management

Demonstrates:
- Configuration management with environment variables
- Caching layer for cost reduction
- Input validation for security
- Cost tracking
"""

import os
import logging
import hashlib
import time
from functools import lru_cache
from typing import Optional
from pydantic import BaseModel, BaseSettings, validator, Field

from deepagents_sample.agents import CoordinatorAgent
from deepagents_sample.middleware import MiddlewareChain, MetricsMiddleware
from deepagents_sample.utils import setup_logger

logger = setup_logger("example5", level=logging.INFO)


# ============================================================================
# 1. CONFIGURATION MANAGEMENT
# ============================================================================

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    Usage:
        # Create .env file with:
        # OPENAI_API_KEY=your-key
        # LOG_LEVEL=INFO
        # CACHE_SIZE=100
        
        settings = Settings()
    """
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cache_size: int = Field(default=100, env="CACHE_SIZE")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    timeout: int = Field(default=30, env="TIMEOUT")
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# ============================================================================
# 2. INPUT VALIDATION
# ============================================================================

class TaskInput(BaseModel):
    """
    Validated task input with security checks.
    """
    task: str = Field(..., min_length=1, max_length=1000)
    priority: str = Field(default="medium")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4000)
    
    @validator('task')
    def validate_task(cls, v):
        """Validate task for security."""
        # Check length
        if len(v) > 1000:
            raise ValueError("Task too long (max 1000 characters)")
        
        # Check for suspicious patterns
        dangerous_patterns = [
            'rm -rf', 'DROP TABLE', '__import__',
            'eval(', 'exec(', 'system('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in v:
                raise ValueError(f"Suspicious pattern detected: {pattern}")
        
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority level."""
        allowed = ['low', 'medium', 'high', 'critical']
        if v not in allowed:
            raise ValueError(f"Priority must be one of: {allowed}")
        return v


# ============================================================================
# 3. CACHING LAYER
# ============================================================================

class CacheManager:
    """
    Manages caching of agent responses to reduce costs.
    """
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, task: str) -> str:
        """Generate cache key from task."""
        return hashlib.md5(task.encode()).hexdigest()
    
    def get(self, task: str) -> Optional[str]:
        """Get cached result if available."""
        key = self._generate_key(task)
        
        if key in self.cache:
            self.hits += 1
            logger.info(f"✓ Cache HIT for task: {task[:50]}...")
            return self.cache[key]
        
        self.misses += 1
        logger.info(f"✗ Cache MISS for task: {task[:50]}...")
        return None
    
    def set(self, task: str, result: str):
        """Cache a result."""
        key = self._generate_key(task)
        
        # Simple LRU: remove oldest if full
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = result
        logger.info(f"✓ Cached result for: {task[:50]}...")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_size": len(self.cache),
            "max_size": self.max_size
        }
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        logger.info("Cache cleared")


# ============================================================================
# 4. COST TRACKING
# ============================================================================

class CostTracker:
    """
    Track API costs in real-time.
    """
    
    # Approximate costs per 1K tokens (as of 2024)
    COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }
    
    def __init__(self):
        self.total_cost = 0.0
        self.calls = []
    
    def track_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task: str = ""
    ):
        """Track a single API call."""
        if model not in self.COSTS:
            logger.warning(f"Unknown model: {model}, using gpt-4o-mini costs")
            model = "gpt-4o-mini"
        
        input_cost = input_tokens / 1000 * self.COSTS[model]["input"]
        output_cost = output_tokens / 1000 * self.COSTS[model]["output"]
        call_cost = input_cost + output_cost
        
        self.total_cost += call_cost
        
        self.calls.append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": call_cost,
            "task": task[:50] if task else ""
        })
        
        logger.info(
            f"💰 Call cost: ${call_cost:.4f} "
            f"(in: {input_tokens}, out: {output_tokens}) "
            f"Total: ${self.total_cost:.4f}"
        )
    
    def get_summary(self) -> dict:
        """Get cost summary."""
        return {
            "total_calls": len(self.calls),
            "total_cost": f"${self.total_cost:.4f}",
            "avg_cost_per_call": f"${self.total_cost / len(self.calls):.4f}" if self.calls else "$0.00",
            "total_input_tokens": sum(c["input_tokens"] for c in self.calls),
            "total_output_tokens": sum(c["output_tokens"] for c in self.calls)
        }


# ============================================================================
# 5. CACHED AGENT
# ============================================================================

class CachedCoordinatorAgent(CoordinatorAgent):
    """
    Coordinator agent with caching support.
    """
    
    def __init__(self, *args, cache_manager: CacheManager = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_manager = cache_manager or CacheManager()
    
    def process(self, task: str) -> str:
        """Process with caching."""
        # Check cache first
        cached_result = self.cache_manager.get(task)
        if cached_result:
            return cached_result
        
        # Process normally
        result = super().process(task)
        
        # Cache result
        self.cache_manager.set(task, result)
        
        return result


# ============================================================================
# EXAMPLE EXECUTION
# ============================================================================

def run_example():
    """Run the caching and configuration example."""
    
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE 5: CACHING AND CONFIGURATION")
    logger.info("="*70)
    logger.info("Demonstrates configuration, caching, validation, and cost tracking.\n")
    
    # Part 1: Configuration Management
    logger.info("="*70)
    logger.info("PART 1: CONFIGURATION MANAGEMENT")
    logger.info("="*70)
    
    try:
        settings = Settings()
        logger.info("✓ Configuration loaded successfully")
        logger.info(f"  Log Level: {settings.log_level}")
        logger.info(f"  Cache Size: {settings.cache_size}")
        logger.info(f"  Max Retries: {settings.max_retries}")
        logger.info(f"  Timeout: {settings.timeout}s")
        logger.info(f"  Caching Enabled: {settings.enable_caching}")
    except Exception as e:
        logger.warning(f"⚠️  Could not load settings: {e}")
        logger.info("Using default configuration")
        settings = None
    
    # Part 2: Input Validation
    logger.info("\n" + "="*70)
    logger.info("PART 2: INPUT VALIDATION")
    logger.info("="*70)
    
    # Valid input
    try:
        valid_task = TaskInput(
            task="Analyze user data and provide insights",
            priority="high"
        )
        logger.info("✓ Valid input accepted:")
        logger.info(f"  Task: {valid_task.task}")
        logger.info(f"  Priority: {valid_task.priority}")
    except Exception as e:
        logger.error(f"✗ Validation failed: {e}")
    
    # Invalid input (too long)
    try:
        invalid_task = TaskInput(task="x" * 1001)
        logger.error("✗ Should have rejected long input!")
    except ValueError as e:
        logger.info(f"✓ Correctly rejected long input: {e}")
    
    # Invalid input (suspicious pattern)
    try:
        suspicious_task = TaskInput(task="Run this: rm -rf /")
        logger.error("✗ Should have rejected suspicious input!")
    except ValueError as e:
        logger.info(f"✓ Correctly rejected suspicious input: {e}")
    
    # Part 3: Caching Layer
    logger.info("\n" + "="*70)
    logger.info("PART 3: CACHING LAYER")
    logger.info("="*70)
    
    cache = CacheManager(max_size=10)
    
    # Simulate some requests
    tasks = [
        "What is machine learning?",
        "Explain neural networks",
        "What is machine learning?",  # Duplicate - should hit cache
        "Define artificial intelligence",
        "What is machine learning?",  # Duplicate - should hit cache
    ]
    
    for task in tasks:
        result = cache.get(task)
        if result is None:
            # Simulate processing
            result = f"Result for: {task}"
            cache.set(task, result)
    
    # Show cache stats
    stats = cache.get_stats()
    logger.info("\nCache Statistics:")
    logger.info(f"  Hits: {stats['hits']}")
    logger.info(f"  Misses: {stats['misses']}")
    logger.info(f"  Hit Rate: {stats['hit_rate']}")
    logger.info(f"  Cache Size: {stats['cache_size']}/{stats['max_size']}")
    
    # Part 4: Cost Tracking
    logger.info("\n" + "="*70)
    logger.info("PART 4: COST TRACKING")
    logger.info("="*70)
    
    cost_tracker = CostTracker()
    
    # Simulate some API calls
    cost_tracker.track_call("gpt-4o-mini", 100, 50, "Task 1")
    cost_tracker.track_call("gpt-4o-mini", 150, 75, "Task 2")
    cost_tracker.track_call("gpt-4o-mini", 200, 100, "Task 3")
    
    # Show cost summary
    summary = cost_tracker.get_summary()
    logger.info("\nCost Summary:")
    logger.info(f"  Total Calls: {summary['total_calls']}")
    logger.info(f"  Total Cost: {summary['total_cost']}")
    logger.info(f"  Avg Cost/Call: {summary['avg_cost_per_call']}")
    logger.info(f"  Total Input Tokens: {summary['total_input_tokens']}")
    logger.info(f"  Total Output Tokens: {summary['total_output_tokens']}")
    
    # Calculate savings from caching
    cache_stats = cache.get_stats()
    if cache_stats['hits'] > 0:
        # Assume average cost per call
        avg_cost = 0.0001  # Approximate
        savings = cache_stats['hits'] * avg_cost
        logger.info(f"\n💰 Estimated savings from caching: ${savings:.4f}")
    
    # Key takeaways
    logger.info("\n" + "="*70)
    logger.info("KEY TAKEAWAYS")
    logger.info("="*70)
    logger.info("1. Configuration management makes deployment easier")
    logger.info("2. Input validation prevents security issues")
    logger.info("3. Caching reduces costs significantly")
    logger.info("4. Cost tracking helps manage budgets")
    logger.info("5. These features are essential for production")
    logger.info("")
    logger.info("Benefits:")
    logger.info("- 40-60% cost reduction with caching")
    logger.info("- Better security with validation")
    logger.info("- Easier deployment with config management")
    logger.info("- Budget control with cost tracking")


if __name__ == "__main__":
    run_example()
