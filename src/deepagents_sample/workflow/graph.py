"""LangGraph workflow for agent orchestration."""

from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from .state import AgentState
from ..agents import CoordinatorAgent, ResearchAgent, AnalysisAgent
from ..middleware import MiddlewareChain


def create_agent_workflow(
    coordinator: CoordinatorAgent,
    research_agent: ResearchAgent,
    analysis_agent: AnalysisAgent
):
    """
    Create a LangGraph workflow with coordinator and subagents.
    
    The workflow:
    1. Starts with the coordinator
    2. Coordinator decides which subagent to use
    3. Routes to research or analysis agent
    4. Subagent processes and returns to coordinator
    5. Coordinator aggregates and produces final output
    
    Args:
        coordinator: The coordinator agent
        research_agent: The research subagent
        analysis_agent: The analysis subagent
        
    Returns:
        Compiled LangGraph workflow
    """
    
    # Define node functions
    def coordinator_node(state: AgentState) -> AgentState:
        """
        Coordinator node that analyzes the task and routes to subagents.
        """
        task = state["current_task"]
        
        # Add to agent history
        state["agent_history"] = state.get("agent_history", []) + ["coordinator"]
        
        # Check if we have results from subagents
        if state.get("results"):
            # Aggregate results
            results_list = [
                {"agent": agent, "result": result}
                for agent, result in state["results"].items()
            ]
            final_output = coordinator.aggregate_results(results_list)
            
            state["final_output"] = final_output
            state["next_agent"] = None  # End workflow
            state["messages"] = state.get("messages", []) + [
                AIMessage(content=f"Coordinator aggregated results: {final_output}")
            ]
        else:
            # Analyze task and decide routing
            prompt = f"""Analyze this task and decide which agent should handle it:

Task: {task}

Available agents:
- research_agent: Gathers information, executes commands, queries data
- analysis_agent: Analyzes data, generates insights, creates summaries

Respond with ONLY the agent name (research_agent or analysis_agent) that should handle this task."""
            
            state["messages"] = state.get("messages", []) + [
                HumanMessage(content=prompt)
            ]
            
            # Get coordinator decision
            response = coordinator.process(prompt)
            
            # Determine next agent based on response
            if "research" in response.lower():
                state["next_agent"] = "research"
            elif "analysis" in response.lower():
                state["next_agent"] = "analysis"
            else:
                # Default to research
                state["next_agent"] = "research"
            
            state["messages"] = state.get("messages", []) + [
                AIMessage(content=f"Coordinator routing to: {state['next_agent']}")
            ]
        
        return state
    
    def research_node(state: AgentState) -> AgentState:
        """
        Research agent node that gathers information.
        """
        task = state["current_task"]
        
        # Add to agent history
        state["agent_history"] = state.get("agent_history", []) + ["research_agent"]
        
        # Process with research agent
        result = research_agent.process(task)
        
        # Add result to state
        results = state.get("results", {})
        results["research_agent"] = result
        state["results"] = results
        
        state["messages"] = state.get("messages", []) + [
            AIMessage(content=f"Research agent completed: {result[:200]}...")
        ]
        
        # Route back to coordinator
        state["next_agent"] = "coordinator"
        
        return state
    
    def analysis_node(state: AgentState) -> AgentState:
        """
        Analysis agent node that analyzes data.
        """
        task = state["current_task"]
        
        # Add to agent history
        state["agent_history"] = state.get("agent_history", []) + ["analysis_agent"]
        
        # Process with analysis agent
        result = analysis_agent.process(task)
        
        # Add result to state
        results = state.get("results", {})
        results["analysis_agent"] = result
        state["results"] = results
        
        state["messages"] = state.get("messages", []) + [
            AIMessage(content=f"Analysis agent completed: {result[:200]}...")
        ]
        
        # Route back to coordinator
        state["next_agent"] = "coordinator"
        
        return state
    
    def route_after_coordinator(
        state: AgentState
    ) -> Literal["research", "analysis", "end"]:
        """
        Routing function to determine next node after coordinator.
        """
        next_agent = state.get("next_agent")
        
        if next_agent == "research":
            return "research"
        elif next_agent == "analysis":
            return "analysis"
        else:
            return "end"
    
    def route_after_subagent(
        state: AgentState
    ) -> Literal["coordinator", "end"]:
        """
        Routing function after subagent execution.
        """
        # Always route back to coordinator after subagent
        return "coordinator"
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    
    # Set entry point
    workflow.set_entry_point("coordinator")
    
    # Add conditional edges from coordinator
    workflow.add_conditional_edges(
        "coordinator",
        route_after_coordinator,
        {
            "research": "research",
            "analysis": "analysis",
            "end": END
        }
    )
    
    # Add edges from subagents back to coordinator
    workflow.add_conditional_edges(
        "research",
        route_after_subagent,
        {
            "coordinator": "coordinator",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "analysis",
        route_after_subagent,
        {
            "coordinator": "coordinator",
            "end": END
        }
    )
    
    # Compile the graph
    return workflow.compile()


def run_workflow(
    workflow,
    task: str,
    verbose: bool = True
) -> dict:
    """
    Run the workflow with a given task.
    
    Args:
        workflow: Compiled LangGraph workflow
        task: Task to process
        verbose: Whether to print progress
        
    Returns:
        Final state dictionary
    """
    from .state import create_initial_state
    
    # Create initial state
    initial_state = create_initial_state(task)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Starting workflow with task: {task}")
        print(f"{'='*60}\n")
    
    # Run the workflow
    final_state = workflow.invoke(initial_state)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Workflow completed")
        print(f"Agent history: {' -> '.join(final_state.get('agent_history', []))}")
        print(f"{'='*60}\n")
        
        if final_state.get("final_output"):
            print(f"Final Output:\n{final_state['final_output']}\n")
    
    return final_state
