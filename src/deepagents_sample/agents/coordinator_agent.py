"""Coordinator agent for orchestrating subagents."""

from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from ..middleware import AgentRequest, AgentResponse, MiddlewareChain


class CoordinatorAgent:
    """
    Main coordinator agent that orchestrates task delegation to subagents.
    
    The coordinator:
    - Receives high-level tasks
    - Decomposes them into subtasks
    - Delegates to appropriate subagents
    - Aggregates results
    - Uses middleware for logging and metrics
    
    Example:
        coordinator = CoordinatorAgent(
            model=ChatOpenAI(model="gpt-4"),
            middleware_chain=my_middleware
        )
        result = coordinator.process("Analyze user data")
    """
    
    def __init__(
        self,
        model: Optional[ChatOpenAI] = None,
        middleware_chain: Optional[MiddlewareChain] = None,
        name: str = "coordinator"
    ):
        """
        Initialize the coordinator agent.
        
        Args:
            model: LangChain LLM model (defaults to gpt-4o-mini)
            middleware_chain: Optional middleware chain for request/response processing
            name: Agent name for identification
        """
        self.name = name
        self.model = model or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.middleware_chain = middleware_chain
        self.subagents: Dict[str, Any] = {}
        self.conversation_history: List[BaseMessage] = []
    
    def register_subagent(self, name: str, agent: Any) -> None:
        """
        Register a subagent that can be delegated to.
        
        Args:
            name: Unique name for the subagent
            agent: The subagent instance
        """
        self.subagents[name] = agent
    
    def _create_request(self, input_data: Any) -> AgentRequest:
        """Create an agent request for middleware processing."""
        return AgentRequest(
            agent_name=self.name,
            input_data=input_data,
            metadata={"type": "coordinator"}
        )
    
    def _create_response(self, output_data: Any, request_id: int) -> AgentResponse:
        """Create an agent response for middleware processing."""
        return AgentResponse(
            agent_name=self.name,
            output_data=output_data,
            request_id=request_id,
            metadata={"type": "coordinator"}
        )
    
    def _process_with_middleware(self, input_data: Any) -> tuple[AgentRequest, Any]:
        """
        Process input through middleware chain if available.
        
        Returns:
            Tuple of (request, processed_input)
        """
        request = self._create_request(input_data)
        
        if self.middleware_chain:
            request = self.middleware_chain.process_request(request)
        
        return request, request.input_data
    
    def _finalize_with_middleware(
        self,
        output_data: Any,
        request: AgentRequest
    ) -> Any:
        """
        Process output through middleware chain if available.
        
        Returns:
            Processed output
        """
        response = self._create_response(output_data, request.request_id)
        
        if self.middleware_chain:
            response = self.middleware_chain.process_response(response)
        
        return response.output_data
    
    def process(self, task: str) -> str:
        """
        Process a high-level task.
        
        This is a simple implementation that uses the LLM directly.
        In a full implementation, this would analyze the task and
        delegate to appropriate subagents.
        
        Args:
            task: The task description
            
        Returns:
            Task result
        """
        # Process through middleware
        request, processed_task = self._process_with_middleware(task)
        
        # Add to conversation history
        self.conversation_history.append(HumanMessage(content=processed_task))
        
        # Create system message for coordinator role
        system_prompt = f"""You are a coordinator agent named '{self.name}'.
Your role is to analyze tasks and coordinate their execution.

Available subagents: {', '.join(self.subagents.keys()) if self.subagents else 'none'}

For this task, provide a clear response or indicate which subagent should handle it."""
        
        # Get LLM response
        messages = [HumanMessage(content=system_prompt)] + self.conversation_history
        response = self.model.invoke(messages)
        
        # Add response to history
        self.conversation_history.append(AIMessage(content=response.content))
        
        # Process through middleware
        result = self._finalize_with_middleware(response.content, request)
        
        return result
    
    def delegate_to_subagent(
        self,
        subagent_name: str,
        task: str
    ) -> str:
        """
        Delegate a task to a specific subagent.
        
        Args:
            subagent_name: Name of the subagent to delegate to
            task: Task description
            
        Returns:
            Subagent result
            
        Raises:
            ValueError: If subagent not found
        """
        if subagent_name not in self.subagents:
            raise ValueError(
                f"Subagent '{subagent_name}' not found. "
                f"Available: {list(self.subagents.keys())}"
            )
        
        subagent = self.subagents[subagent_name]
        
        # Delegate to subagent (assuming it has a process method)
        if hasattr(subagent, 'process'):
            return subagent.process(task)
        else:
            raise ValueError(f"Subagent '{subagent_name}' does not have a process method")
    
    def aggregate_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Aggregate results from multiple subagents.
        
        Args:
            results: List of results from subagents
            
        Returns:
            Aggregated summary
        """
        # Process through middleware
        request, _ = self._process_with_middleware(results)
        
        # Create aggregation prompt
        results_text = "\n\n".join([
            f"From {r.get('agent', 'unknown')}:\n{r.get('result', '')}"
            for r in results
        ])
        
        prompt = f"""Aggregate and summarize the following results from subagents:

{results_text}

Provide a coherent summary that combines these results."""
        
        messages = [HumanMessage(content=prompt)]
        response = self.model.invoke(messages)
        
        # Process through middleware
        result = self._finalize_with_middleware(response.content, request)
        
        return result
    
    def reset_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
