"""Research agent for gathering information using MCP tools."""

from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..middleware import AgentRequest, AgentResponse, MiddlewareChain
from ..tools import CommandTool, JSONSearchTool


class ResearchAgent:
    """
    Research agent that gathers information using MCP tools.
    
    The research agent:
    - Executes system commands via CommandTool
    - Queries JSON data via JSONSearchTool
    - Formats and presents findings
    - Uses middleware for logging and metrics
    
    Example:
        agent = ResearchAgent(
            model=ChatOpenAI(model="gpt-4"),
            middleware_chain=my_middleware
        )
        result = agent.process("Find all engineers in the data")
    """
    
    def __init__(
        self,
        model: Optional[ChatOpenAI] = None,
        middleware_chain: Optional[MiddlewareChain] = None,
        name: str = "research_agent"
    ):
        """
        Initialize the research agent.
        
        Args:
            model: LangChain LLM model (defaults to gpt-4o-mini)
            middleware_chain: Optional middleware chain for request/response processing
            name: Agent name for identification
        """
        self.name = name
        self.model = model or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.middleware_chain = middleware_chain
        self.conversation_history: List[BaseMessage] = []
        
        # Initialize MCP tools
        self.command_tool = CommandTool(
            timeout=30,
            allowed_commands=["echo", "ls", "cat", "date", "pwd", "whoami", "uname"]
        )
        self.json_tool = JSONSearchTool(check_jq=False)  # Don't check on init
        
        self.tools = {
            "command": self.command_tool,
            "json_search": self.json_tool
        }
    
    def _create_request(self, input_data: Any) -> AgentRequest:
        """Create an agent request for middleware processing."""
        return AgentRequest(
            agent_name=self.name,
            input_data=input_data,
            metadata={"type": "research"}
        )
    
    def _create_response(self, output_data: Any, request_id: int) -> AgentResponse:
        """Create an agent response for middleware processing."""
        return AgentResponse(
            agent_name=self.name,
            output_data=output_data,
            request_id=request_id,
            metadata={"type": "research"}
        )
    
    def _process_with_middleware(self, input_data: Any) -> tuple[AgentRequest, Any]:
        """Process input through middleware chain if available."""
        request = self._create_request(input_data)
        
        if self.middleware_chain:
            request = self.middleware_chain.process_request(request)
        
        return request, request.input_data
    
    def _finalize_with_middleware(
        self,
        output_data: Any,
        request: AgentRequest
    ) -> Any:
        """Process output through middleware chain if available."""
        response = self._create_response(output_data, request.request_id)
        
        if self.middleware_chain:
            response = self.middleware_chain.process_response(response)
        
        return response.output_data
    
    def execute_command(self, command: str) -> str:
        """
        Execute a system command using CommandTool.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output or error message
        """
        response = self.command_tool.run(command=command)
        
        if response.success:
            return f"Command output:\n{response.result}"
        else:
            return f"Command failed: {response.error}"
    
    def search_json(self, file_path: str, query: str) -> str:
        """
        Search JSON file using jq query.
        
        Args:
            file_path: Path to JSON file
            query: jq query expression
            
        Returns:
            Query result or error message
        """
        response = self.json_tool.run(file_path=file_path, jq_query=query)
        
        if response.success:
            import json
            # Format result nicely
            if isinstance(response.result, (dict, list)):
                return json.dumps(response.result, indent=2)
            return str(response.result)
        else:
            return f"Query failed: {response.error}"
    
    def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a research task.
        
        Args:
            task: The research task description
            context: Optional context (e.g., file paths, commands to run)
            
        Returns:
            Research findings
        """
        # Process through middleware
        request, processed_task = self._process_with_middleware(task)
        
        # Build system prompt
        system_prompt = f"""You are a research agent named '{self.name}'.
Your role is to gather information using available tools.

Available tools:
- execute_command: Run safe system commands (echo, ls, cat, date, pwd, whoami, uname)
- search_json: Query JSON files using jq syntax

For the given task, describe what information you would gather and how.
If context is provided with specific files or commands, mention how you would use them."""
        
        # Add context to task if provided
        full_task = processed_task
        if context:
            full_task += f"\n\nContext: {context}"
        
        # Add to conversation history
        self.conversation_history.append(HumanMessage(content=full_task))
        
        # Get LLM response
        messages = [
            SystemMessage(content=system_prompt),
            *self.conversation_history
        ]
        response = self.model.invoke(messages)
        
        # Add response to history
        self.conversation_history.append(AIMessage(content=response.content))
        
        # Process through middleware
        result = self._finalize_with_middleware(response.content, request)
        
        return result
    
    def process_with_tools(
        self,
        task: str,
        json_file: Optional[str] = None,
        jq_query: Optional[str] = None,
        command: Optional[str] = None
    ) -> str:
        """
        Process a task and actually execute tools.
        
        Args:
            task: Task description
            json_file: Optional JSON file to query
            jq_query: Optional jq query to execute
            command: Optional command to execute
            
        Returns:
            Research findings with tool results
        """
        # Process through middleware
        request, processed_task = self._process_with_middleware(task)
        
        results = [f"Research Task: {processed_task}\n"]
        
        # Execute command if provided
        if command:
            results.append(f"\n--- Command Execution ---")
            results.append(f"Command: {command}")
            cmd_result = self.execute_command(command)
            results.append(cmd_result)
        
        # Execute JSON query if provided
        if json_file and jq_query:
            results.append(f"\n--- JSON Query ---")
            results.append(f"File: {json_file}")
            results.append(f"Query: {jq_query}")
            json_result = self.search_json(json_file, jq_query)
            results.append(json_result)
        
        # Combine results
        output = "\n".join(results)
        
        # Process through middleware
        result = self._finalize_with_middleware(output, request)
        
        return result
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """
        Get statistics about tool usage.
        
        Returns:
            Dictionary with stats for each tool
        """
        return {
            "command_tool": self.command_tool.get_stats(),
            "json_tool": self.json_tool.get_stats()
        }
    
    def reset_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
