"""Metrics middleware for tracking agent performance."""

import time
import logging
from typing import Dict, List
from datetime import datetime

from .base import BaseMiddleware, AgentRequest, AgentResponse


class MetricsMiddleware(BaseMiddleware):
    """
    Middleware that tracks performance metrics for agent operations.
    
    This middleware collects:
    - Execution time for each agent call
    - Number of requests per agent
    - Average response times
    - Total processing time
    
    Metrics can be retrieved and displayed at any time to analyze
    agent performance and identify bottlenecks.
    
    Example:
        metrics = MetricsMiddleware()
        # ... process requests ...
        metrics.print_summary()
    """
    
    def __init__(self, logger: logging.Logger = None):
        """Initialize the metrics middleware with empty metric storage."""
        super().__init__("MetricsMiddleware")
        self.request_times: Dict[int, float] = {}  # request_id -> start_time
        self.agent_metrics: Dict[str, List[float]] = {}  # agent_name -> [durations]
        self.total_requests = 0
        self.total_responses = 0
        self.logger = logger or logging.getLogger(__name__)
    
    def process_request(self, request: AgentRequest) -> AgentRequest:
        """
        Record the start time of an agent request.
        
        Args:
            request: The agent request to track
            
        Returns:
            The unmodified request
        """
        # Record start time for this request
        self.request_times[request.request_id] = time.time()
        self.total_requests += 1
        
        # Initialize metrics for this agent if needed
        if request.agent_name not in self.agent_metrics:
            self.agent_metrics[request.agent_name] = []
        
        return request
    
    def process_response(self, response: AgentResponse) -> AgentResponse:
        """
        Calculate and record the execution time for an agent response.
        
        Args:
            response: The agent response to track
            
        Returns:
            The unmodified response with added timing metadata
        """
        self.total_responses += 1
        
        # Calculate duration if we have a start time
        if response.request_id in self.request_times:
            start_time = self.request_times[response.request_id]
            duration = time.time() - start_time
            
            # Store duration for this agent
            if response.agent_name in self.agent_metrics:
                self.agent_metrics[response.agent_name].append(duration)
            
            # Add timing info to response metadata
            response.metadata["execution_time_ms"] = round(duration * 1000, 2)
            
            # Clean up to avoid memory leaks
            del self.request_times[response.request_id]
        
        return response
    
    def get_agent_stats(self, agent_name: str) -> Dict[str, float]:
        """
        Get statistics for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dictionary with min, max, avg, and total time statistics
        """
        if agent_name not in self.agent_metrics or not self.agent_metrics[agent_name]:
            return {
                "count": 0,
                "min_ms": 0,
                "max_ms": 0,
                "avg_ms": 0,
                "total_ms": 0
            }
        
        durations = self.agent_metrics[agent_name]
        total_ms = sum(d * 1000 for d in durations)
        
        return {
            "count": len(durations),
            "min_ms": round(min(durations) * 1000, 2),
            "max_ms": round(max(durations) * 1000, 2),
            "avg_ms": round(total_ms / len(durations), 2),
            "total_ms": round(total_ms, 2)
        }
    
    def get_total_stats(self) -> Dict[str, any]:
        """
        Get overall statistics across all agents.
        
        Returns:
            Dictionary with total requests, responses, and timing info
        """
        all_durations = []
        for durations in self.agent_metrics.values():
            all_durations.extend(durations)
        
        if not all_durations:
            return {
                "total_requests": self.total_requests,
                "total_responses": self.total_responses,
                "total_time_ms": 0,
                "avg_time_ms": 0
            }
        
        total_ms = sum(d * 1000 for d in all_durations)
        
        return {
            "total_requests": self.total_requests,
            "total_responses": self.total_responses,
            "total_time_ms": round(total_ms, 2),
            "avg_time_ms": round(total_ms / len(all_durations), 2)
        }
    
    def print_summary(self):
        """
        Print a formatted summary of all collected metrics.
        
        Displays:
        - Per-agent statistics (count, min, max, avg times)
        - Overall statistics
        - Performance insights
        """
        self.logger.info("=" * 60)
        self.logger.info("METRICS SUMMARY")
        self.logger.info("=" * 60)
        
        # Overall stats
        total_stats = self.get_total_stats()
        self.logger.info("Overall Statistics:")
        self.logger.info(f"  Total Requests:  {total_stats['total_requests']}")
        self.logger.info(f"  Total Responses: {total_stats['total_responses']}")
        self.logger.info(f"  Total Time:      {total_stats['total_time_ms']:.2f} ms")
        self.logger.info(f"  Average Time:    {total_stats['avg_time_ms']:.2f} ms")
        
        # Per-agent stats
        if self.agent_metrics:
            self.logger.info("Per-Agent Statistics:")
            for agent_name in sorted(self.agent_metrics.keys()):
                stats = self.get_agent_stats(agent_name)
                if stats['count'] > 0:
                    self.logger.info(f"  {agent_name}:")
                    self.logger.info(f"    Calls:   {stats['count']}")
                    self.logger.info(f"    Min:     {stats['min_ms']:.2f} ms")
                    self.logger.info(f"    Max:     {stats['max_ms']:.2f} ms")
                    self.logger.info(f"    Average: {stats['avg_ms']:.2f} ms")
                    self.logger.info(f"    Total:   {stats['total_ms']:.2f} ms")
        
        self.logger.info("=" * 60)
    
    def reset(self):
        """Reset all metrics to initial state."""
        self.request_times.clear()
        self.agent_metrics.clear()
        self.total_requests = 0
        self.total_responses = 0
