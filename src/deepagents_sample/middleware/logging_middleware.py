"""Logging middleware for capturing and displaying agent communications."""

import json
import logging
from typing import Any
from datetime import datetime

from .base import BaseMiddleware, AgentRequest, AgentResponse


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware that logs all agent requests and responses with timestamps.
    
    This middleware provides visibility into agent communications by:
    - Logging when requests are sent to agents
    - Logging when responses are received from agents
    - Including timestamps and agent identification
    - Formatting output for easy reading
    
    Example:
        middleware = LoggingMiddleware()
        request = AgentRequest("research_agent", "Find information about AI")
        processed_request = middleware.process_request(request)
    """
    
    def __init__(self, verbose: bool = True, logger: logging.Logger = None):
        """
        Initialize the logging middleware.
        
        Args:
            verbose: If True, log detailed information including data content
            logger: Optional logger instance (creates one if not provided)
        """
        super().__init__("LoggingMiddleware")
        self.verbose = verbose
        self.logger = logger or logging.getLogger(__name__)
    
    def _format_data(self, data: Any, max_length: int = 200) -> str:
        """
        Format data for logging, truncating if necessary.
        
        Args:
            data: The data to format
            max_length: Maximum length of formatted string
            
        Returns:
            Formatted string representation of data
        """
        if isinstance(data, (dict, list)):
            formatted = json.dumps(data, indent=2)
        else:
            formatted = str(data)
        
        if len(formatted) > max_length:
            return formatted[:max_length] + "..."
        return formatted
    
    def _log(self, message: str, level: str = "INFO"):
        """
        Log a message with timestamp and level.
        
        Args:
            message: The message to log
            level: Log level (INFO, DEBUG, etc.)
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    
    def process_request(self, request: AgentRequest) -> AgentRequest:
        """
        Log an incoming agent request.
        
        Captures:
        - Agent name
        - Request ID
        - Timestamp
        - Input data (if verbose mode is enabled)
        
        Args:
            request: The agent request to log
            
        Returns:
            The unmodified request (logging doesn't alter data)
        """
        self._log(f"→ REQUEST to agent '{request.agent_name}' (ID: {request.request_id})")
        
        if self.verbose and request.input_data:
            formatted_input = self._format_data(request.input_data)
            self._log(f"  Input: {formatted_input}", level="DEBUG")
        
        if request.metadata:
            self._log(f"  Metadata: {request.metadata}", level="DEBUG")
        
        return request
    
    def process_response(self, response: AgentResponse) -> AgentResponse:
        """
        Log an outgoing agent response.
        
        Captures:
        - Agent name
        - Request ID (for correlation)
        - Timestamp
        - Output data (if verbose mode is enabled)
        
        Args:
            response: The agent response to log
            
        Returns:
            The unmodified response (logging doesn't alter data)
        """
        self._log(f"← RESPONSE from agent '{response.agent_name}' (ID: {response.request_id})")
        
        if self.verbose and response.output_data:
            formatted_output = self._format_data(response.output_data)
            self._log(f"  Output: {formatted_output}", level="DEBUG")
        
        if response.metadata:
            self._log(f"  Metadata: {response.metadata}", level="DEBUG")
        
        return response
