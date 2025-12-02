"""Base classes for MCP (Model Context Protocol) tool integration."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MCPToolRequest(BaseModel):
    """
    Request format for MCP tools.
    
    Standardizes how tools receive parameters and configuration.
    """
    tool_name: str = Field(description="Name of the tool to invoke")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    timeout: int = Field(default=30, description="Timeout in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MCPToolResponse(BaseModel):
    """
    Response format from MCP tools.
    
    Provides consistent structure for tool results, including
    success status, result data, error information, and timing.
    """
    success: bool = Field(description="Whether the tool execution succeeded")
    result: Any = Field(default=None, description="Tool execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: float = Field(description="Execution time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MCPTool(ABC):
    """
    Base class for MCP (Model Context Protocol) tools.
    
    MCP tools provide external capabilities to agents, such as:
    - Executing system commands
    - Querying databases
    - Searching files
    - Calling APIs
    
    Each tool must implement the _run method with its specific logic.
    The base class handles common concerns like timing, error handling,
    and response formatting.
    
    Example:
        class MyTool(MCPTool):
            name = "my_tool"
            description = "Does something useful"
            
            def _run(self, param1: str, param2: int) -> str:
                return f"Result: {param1} {param2}"
    """
    
    # Subclasses should override these
    name: str = "base_tool"
    description: str = "Base MCP tool"
    
    def __init__(self):
        """Initialize the MCP tool."""
        self.call_count = 0
        self.total_execution_time = 0.0
    
    @abstractmethod
    def _run(self, **kwargs) -> Any:
        """
        Execute the tool's core logic.
        
        Subclasses must implement this method with their specific functionality.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
            
        Raises:
            Exception: If tool execution fails
        """
        pass
    
    def run(self, **kwargs) -> MCPToolResponse:
        """
        Execute the tool with error handling and timing.
        
        This method wraps _run with:
        - Execution timing
        - Error handling
        - Response formatting
        - Call counting
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            MCPToolResponse with result or error information
        """
        start_time = time.time()
        self.call_count += 1
        
        try:
            result = self._run(**kwargs)
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            
            return MCPToolResponse(
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    "tool_name": self.name,
                    "call_count": self.call_count
                }
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            
            return MCPToolResponse(
                success=False,
                error=str(e),
                execution_time=execution_time,
                metadata={
                    "tool_name": self.name,
                    "call_count": self.call_count,
                    "error_type": type(e).__name__
                }
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about tool usage.
        
        Returns:
            Dictionary with call count and timing information
        """
        avg_time = (
            self.total_execution_time / self.call_count
            if self.call_count > 0
            else 0
        )
        
        return {
            "tool_name": self.name,
            "call_count": self.call_count,
            "total_time": round(self.total_execution_time, 3),
            "avg_time": round(avg_time, 3)
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
