"""Base middleware interface for agent request/response interception."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime


class AgentRequest:
    """Represents an agent request with metadata."""
    
    def __init__(
        self,
        agent_name: str,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_name = agent_name
        self.input_data = input_data
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.request_id = id(self)
    
    def __repr__(self) -> str:
        return f"AgentRequest(agent={self.agent_name}, id={self.request_id})"


class AgentResponse:
    """Represents an agent response with metadata."""
    
    def __init__(
        self,
        agent_name: str,
        output_data: Any,
        request_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_name = agent_name
        self.output_data = output_data
        self.request_id = request_id
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def __repr__(self) -> str:
        return f"AgentResponse(agent={self.agent_name}, id={self.request_id})"


class BaseMiddleware(ABC):
    """
    Base class for middleware components that intercept agent requests and responses.
    
    Middleware can be chained together to create a pipeline of processing steps.
    Each middleware can inspect, modify, or log requests and responses.
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.next_middleware: Optional[BaseMiddleware] = None
    
    @abstractmethod
    def process_request(self, request: AgentRequest) -> AgentRequest:
        """
        Process an incoming agent request.
        
        Args:
            request: The agent request to process
            
        Returns:
            The processed (potentially modified) request
        """
        pass
    
    @abstractmethod
    def process_response(self, response: AgentResponse) -> AgentResponse:
        """
        Process an outgoing agent response.
        
        Args:
            response: The agent response to process
            
        Returns:
            The processed (potentially modified) response
        """
        pass
    
    def set_next(self, middleware: "BaseMiddleware") -> "BaseMiddleware":
        """
        Chain another middleware after this one.
        
        Args:
            middleware: The next middleware in the chain
            
        Returns:
            The next middleware for fluent chaining
        """
        self.next_middleware = middleware
        return middleware
    
    def execute_request_chain(self, request: AgentRequest) -> AgentRequest:
        """
        Execute the full middleware chain for a request.
        
        Args:
            request: The initial request
            
        Returns:
            The request after passing through all middleware
        """
        processed_request = self.process_request(request)
        
        if self.next_middleware:
            return self.next_middleware.execute_request_chain(processed_request)
        
        return processed_request
    
    def execute_response_chain(self, response: AgentResponse) -> AgentResponse:
        """
        Execute the full middleware chain for a response (in reverse order).
        
        Args:
            response: The initial response
            
        Returns:
            The response after passing through all middleware
        """
        if self.next_middleware:
            response = self.next_middleware.execute_response_chain(response)
        
        return self.process_response(response)


class MiddlewareChain:
    """
    Manages a chain of middleware components.
    
    Example:
        chain = MiddlewareChain()
        chain.add(LoggingMiddleware())
        chain.add(MetricsMiddleware())
        
        request = AgentRequest("my_agent", "input")
        processed_request = chain.process_request(request)
    """
    
    def __init__(self):
        self.middlewares: List[BaseMiddleware] = []
    
    def add(self, middleware: BaseMiddleware) -> "MiddlewareChain":
        """
        Add a middleware to the chain.
        
        Args:
            middleware: The middleware to add
            
        Returns:
            Self for fluent chaining
        """
        if self.middlewares:
            self.middlewares[-1].set_next(middleware)
        self.middlewares.append(middleware)
        return self
    
    def process_request(self, request: AgentRequest) -> AgentRequest:
        """
        Process a request through the entire middleware chain.
        
        Args:
            request: The request to process
            
        Returns:
            The processed request
        """
        if not self.middlewares:
            return request
        
        return self.middlewares[0].execute_request_chain(request)
    
    def process_response(self, response: AgentResponse) -> AgentResponse:
        """
        Process a response through the entire middleware chain (in reverse).
        
        Args:
            response: The response to process
            
        Returns:
            The processed response
        """
        if not self.middlewares:
            return response
        
        return self.middlewares[0].execute_response_chain(response)
