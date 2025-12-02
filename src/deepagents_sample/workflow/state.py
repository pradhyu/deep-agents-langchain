"""State management for LangGraph workflows."""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    State shared across the LangGraph workflow.
    
    This state is passed between nodes in the graph and maintains
    the context of the entire workflow execution.
    
    Attributes:
        messages: Conversation history (accumulated across nodes)
        current_task: The current task being processed
        results: Results from various agents (accumulated)
        agent_history: List of agents that have processed this state
        error: Error message if something went wrong
        next_agent: Which agent should process next (for routing)
        final_output: The final result of the workflow
    """
    
    # Messages are accumulated (appended) across nodes
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Current task being processed
    current_task: str
    
    # Results dictionary is merged across nodes
    results: Annotated[Dict[str, Any], operator.add]
    
    # Agent history is accumulated
    agent_history: Annotated[List[str], operator.add]
    
    # Error handling
    error: Optional[str]
    
    # Routing information
    next_agent: Optional[str]
    
    # Final output
    final_output: Optional[str]


def create_initial_state(task: str) -> AgentState:
    """
    Create an initial state for a workflow.
    
    Args:
        task: The initial task to process
        
    Returns:
        Initial AgentState
    """
    return AgentState(
        messages=[],
        current_task=task,
        results={},
        agent_history=[],
        error=None,
        next_agent=None,
        final_output=None
    )


def add_agent_to_history(state: AgentState, agent_name: str) -> AgentState:
    """
    Add an agent to the execution history.
    
    Args:
        state: Current state
        agent_name: Name of the agent to add
        
    Returns:
        Updated state
    """
    state["agent_history"].append(agent_name)
    return state


def add_result(state: AgentState, agent_name: str, result: Any) -> AgentState:
    """
    Add a result from an agent to the state.
    
    Args:
        state: Current state
        agent_name: Name of the agent
        result: Result to add
        
    Returns:
        Updated state
    """
    state["results"][agent_name] = result
    return state


def set_error(state: AgentState, error: str) -> AgentState:
    """
    Set an error in the state.
    
    Args:
        state: Current state
        error: Error message
        
    Returns:
        Updated state
    """
    state["error"] = error
    return state


def set_next_agent(state: AgentState, agent_name: Optional[str]) -> AgentState:
    """
    Set which agent should process next.
    
    Args:
        state: Current state
        agent_name: Name of next agent (None for end)
        
    Returns:
        Updated state
    """
    state["next_agent"] = agent_name
    return state
