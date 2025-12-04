# Technology Stack - DeepAgents Sample Project

## Core Technologies

### ✅ LangChain v1.0+
**Usage**: Core framework for building LLM applications
- `langchain>=1.0.0`
- `langchain-core>=1.0.0`
- `langchain-openai>=0.1.0`
- `langchain-community>=0.3.0`

**Where Used**:
- Agent implementations (CoordinatorAgent, ResearchAgent, AnalysisAgent)
- Message handling (HumanMessage, AIMessage, SystemMessage)
- LLM integration (ChatOpenAI)

### ✅ LangGraph
**Usage**: State machine and workflow orchestration
- `langgraph>=0.2.0`

**Where Used**:
- `src/deepagents_sample/workflow/graph.py` - Main workflow implementation
- Uses `StateGraph` for building the agent workflow
- Conditional routing between agents
- State management with TypedDict

**Key Features Used**:
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)
workflow.add_conditional_edges(...)
```

### ✅ DeepAgents Patterns
**Usage**: Multi-agent system architecture patterns

**Implemented Patterns**:
1. **Hierarchical Agents**: Coordinator delegates to specialized subagents
2. **State Management**: Shared state across workflow using TypedDict
3. **Conditional Routing**: Task-based agent selection
4. **Result Aggregation**: Coordinator combines subagent results

**Note**: While we follow DeepAgents patterns, we're using LangGraph's StateGraph as the orchestration engine, which is the recommended approach in LangChain v1+.

---

## Additional Technologies

### Python Standard Library
- `logging` - Professional logging system
- `subprocess` - Command execution for tools
- `json` - JSON processing
- `pathlib` - File path handling
- `typing` - Type hints and TypedDict

### External Tools
- **jq** - JSON query processor (optional)
- **uv** - Fast Python package manager

---

## Architecture Components

### 1. Middleware Layer
**Technology**: Custom implementation using Python classes
- BaseMiddleware (abstract base class)
- LoggingMiddleware (logging module)
- MetricsMiddleware (time tracking)
- MiddlewareChain (chain of responsibility pattern)

### 2. MCP Tools
**Technology**: Custom implementation following MCP specification
- MCPTool base class
- CommandTool (subprocess)
- JSONSearchTool (jq via subprocess)
- Pydantic for data models

### 3. Agents
**Technology**: LangChain + Custom implementation
- Uses ChatOpenAI for LLM
- Custom agent classes with middleware support
- Tool integration

### 4. Workflow Engine
**Technology**: LangGraph StateGraph
- State management with TypedDict
- Conditional routing
- Node-based workflow
- Automatic state accumulation

---

## Comparison: LangChain vs LangGraph

### What We're Using

| Feature | Technology | File |
|---------|-----------|------|
| Workflow Orchestration | **LangGraph StateGraph** | `workflow/graph.py` |
| State Management | **LangGraph + TypedDict** | `workflow/state.py` |
| Agents | **LangChain + Custom** | `agents/*.py` |
| LLM Integration | **LangChain (ChatOpenAI)** | All agent files |
| Tools | **Custom MCP Tools** | `tools/*.py` |
| Middleware | **Custom Implementation** | `middleware/*.py` |

### Why LangGraph?

LangGraph is the **recommended** way to build multi-agent systems in LangChain v1+:

**Advantages**:
1. ✅ **State Management**: Built-in state handling with TypedDict
2. ✅ **Conditional Routing**: Easy to route between agents based on conditions
3. ✅ **Visualization**: Can visualize workflow graphs
4. ✅ **Debugging**: Better debugging with state inspection
5. ✅ **Persistence**: Can save and resume workflows
6. ✅ **Streaming**: Built-in support for streaming responses

**Our Implementation**:
```python
# Using LangGraph StateGraph
workflow = StateGraph(AgentState)

# Add nodes (agents)
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)

# Add conditional routing
workflow.add_conditional_edges(
    "coordinator",
    route_after_coordinator,
    {
        "research": "research",
        "analysis": "analysis",
        "end": END
    }
)

# Compile and run
app = workflow.compile()
result = app.invoke(initial_state)
```

---

## DeepAgents Features Demonstrated

### ✅ Currently Implemented

1. **Hierarchical Agent Structure**
   - Coordinator agent at the top
   - Specialized subagents (Research, Analysis)
   - Clear delegation patterns

2. **State Management**
   - Shared state across workflow
   - State accumulation (messages, results, history)
   - Type-safe with TypedDict

3. **Tool Integration**
   - MCP-compliant tools
   - Tool registration with agents
   - Error handling and timeouts

4. **Middleware Pattern**
   - Request/response interception
   - Logging and metrics
   - Chainable middleware

5. **Conditional Routing**
   - Task-based agent selection
   - Dynamic workflow paths
   - Result aggregation

### 🔄 Additional DeepAgents Features (Not Yet Implemented)

These could be added to enhance the project:

1. **Memory Systems**
   - Long-term memory for agents
   - Conversation history persistence
   - Context retrieval

2. **Streaming Responses**
   - Real-time agent output
   - Progressive result display
   - Token-by-token streaming

3. **Human-in-the-Loop**
   - Approval gates
   - User input during workflow
   - Interactive decision points

4. **Parallel Execution**
   - Multiple agents running simultaneously
   - Concurrent tool calls
   - Result synchronization

5. **Error Recovery**
   - Automatic retry logic
   - Fallback strategies
   - Graceful degradation

6. **Agent Reflection**
   - Self-evaluation
   - Result validation
   - Iterative improvement

7. **Multi-Modal Support**
   - Image processing
   - Audio handling
   - Document parsing

8. **Advanced Routing**
   - Semantic routing
   - Intent classification
   - Dynamic agent selection

---

## Dependencies

### Core Dependencies
```toml
[project]
dependencies = [
    "langchain>=1.0.0",           # Core LangChain
    "langchain-openai>=0.1.0",    # OpenAI integration
    "langgraph>=0.2.0",           # Workflow orchestration
    "langchain-community>=0.3.0", # Community tools
    "langchain-core>=1.0.0",      # Core abstractions
]
```

### Why These Versions?
- **LangChain 1.0+**: Latest stable version with improved APIs
- **LangGraph 0.2+**: Stable StateGraph implementation
- **LangChain-OpenAI**: For ChatOpenAI model integration

---

## Summary

**What We're Using**:
- ✅ **LangChain v1.0+** for core LLM functionality
- ✅ **LangGraph** for workflow orchestration (StateGraph)
- ✅ **DeepAgents patterns** for multi-agent architecture
- ✅ **Custom middleware** for cross-cutting concerns
- ✅ **MCP tools** for external capabilities
- ✅ **Python logging** for professional output

**Architecture Style**:
- Hierarchical multi-agent system
- State-based workflow with LangGraph
- Middleware for observability
- Tool integration for external capabilities

**This is a modern, production-ready implementation using the latest LangChain/LangGraph patterns!** 🚀
