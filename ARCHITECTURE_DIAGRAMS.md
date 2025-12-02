# Architecture Diagrams - DeepAgents Sample Project

## Current Implementation Status

**We ARE using LangGraph!** ✅
- File: `src/deepagents_sample/workflow/graph.py`
- Uses: `StateGraph`, conditional routing, state management

---

## 1. Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DeepAgents Sample Project                     │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │   Middleware   │  │     Agents     │  │   MCP Tools      │  │
│  │   Layer        │  │                │  │                  │  │
│  │                │  │  ┌──────────┐  │  │  ┌────────────┐  │  │
│  │  ┌──────────┐  │  │  │Coordinator│ │  │  │ Command    │  │  │
│  │  │ Logging  │  │  │  └──────────┘  │  │  │ Tool       │  │  │
│  │  └──────────┘  │  │       │        │  │  └────────────┘  │  │
│  │                │  │       ├────────┼──┼──┐               │  │
│  │  ┌──────────┐  │  │       │        │  │  │               │  │
│  │  │ Metrics  │  │  │  ┌────▼────┐   │  │  │ ┌──────────┐ │  │
│  │  └──────────┘  │  │  │Research │   │  │  └─│JSON      │ │  │
│  │                │  │  │ Agent   │───┼──┼────│Search    │ │  │
│  └────────────────┘  │  └─────────┘   │  │    │Tool      │ │  │
│                      │                 │  │    └──────────┘ │  │
│                      │  ┌─────────┐    │  │                 │  │
│                      │  │Analysis │    │  │                 │  │
│                      │  │ Agent   │────┼──┼────────────────┐│  │
│                      │  └─────────┘    │  │                ││  │
│                      └────────────────┘  └────────────────┘│  │
│                                                             │  │
│  ┌──────────────────────────────────────────────────────┐  │  │
│  │              LangGraph Workflow Engine                │  │  │
│  │         (State Management & Routing)                  │  │  │
│  └──────────────────────────────────────────────────────┘  │  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Middleware Flow

```
Request Flow:
                                                                    
    User Input                                                      
        │                                                           
        ▼                                                           
┌───────────────┐                                                  
│  Agent Call   │                                                  
└───────┬───────┘                                                  
        │                                                           
        ▼                                                           
┌───────────────────────────────────────────────────────────┐     
│              Middleware Chain                              │     
│                                                            │     
│  ┌──────────────────┐         ┌──────────────────┐       │     
│  │ LoggingMiddleware│────────▶│MetricsMiddleware │       │     
│  │                  │         │                  │       │     
│  │ • Log request    │         │ • Start timer    │       │     
│  │ • Add timestamp  │         │ • Track call     │       │     
│  └──────────────────┘         └──────────────────┘       │     
│         │                              │                  │     
│         └──────────────┬───────────────┘                  │     
└────────────────────────┼──────────────────────────────────┘     
                         │                                         
                         ▼                                         
                  ┌─────────────┐                                 
                  │    Agent    │                                 
                  │  Processing │                                 
                  └──────┬──────┘                                 
                         │                                         
                         ▼                                         
┌───────────────────────────────────────────────────────────┐     
│              Middleware Chain (Response)                   │     
│                                                            │     
│  ┌──────────────────┐         ┌──────────────────┐       │     
│  │MetricsMiddleware │────────▶│ LoggingMiddleware│       │     
│  │                  │         │                  │       │     
│  │ • Stop timer     │         │ • Log response   │       │     
│  │ • Record metrics │         │ • Add metadata   │       │     
│  └──────────────────┘         └──────────────────┘       │     
└────────────────────────┬──────────────────────────────────┘     
                         │                                         
                         ▼                                         
                    User Output                                    
```

---

## 3. LangGraph Workflow (Current Implementation)

```
                    ┌─────────────────┐
                    │     START       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Coordinator    │
                    │     Agent       │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  Analyze Task   │
                    │  & Route        │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌──────────┐   ┌──────────┐   ┌──────────┐
      │ Research │   │ Analysis │   │   END    │
      │  Agent   │   │  Agent   │   │          │
      └─────┬────┘   └─────┬────┘   └──────────┘
            │              │
            │  Execute     │  Process
            │  Tools       │  Data
            │              │
            ▼              ▼
      ┌──────────┐   ┌──────────┐
      │ Command  │   │   JSON   │
      │  Tool    │   │  Search  │
      └─────┬────┘   └─────┬────┘
            │              │
            └──────┬───────┘
                   │
                   ▼
          ┌────────────────┐
          │  Coordinator   │
          │  (Aggregate)   │
          └────────┬───────┘
                   │
                   ▼
          ┌────────────────┐
          │      END       │
          └────────────────┘

State Flow:
┌─────────────────────────────────────────┐
│ AgentState (TypedDict)                  │
├─────────────────────────────────────────┤
│ • messages: List[BaseMessage]           │
│ • current_task: str                     │
│ • results: Dict[str, Any]               │
│ • agent_history: List[str]              │
│ • next_agent: Optional[str]             │
│ • final_output: Optional[str]           │
└─────────────────────────────────────────┘
         │
         ▼ (passed between nodes)
    [Accumulates data as workflow progresses]
```

---

## 4. MCP Tool Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCPTool Base Class                    │
│                                                          │
│  • Error handling                                       │
│  • Timeout management                                   │
│  • Statistics tracking                                  │
│  • Response formatting                                  │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ▼                            ▼
    ┌────────────────┐          ┌────────────────┐
    │  CommandTool   │          │JSONSearchTool  │
    ├────────────────┤          ├────────────────┤
    │ • Whitelist    │          │ • jq queries   │
    │ • Timeout      │          │ • File reading │
    │ • Output       │          │ • JSON parsing │
    │   capture      │          │ • Result fmt   │
    └────────┬───────┘          └────────┬───────┘
             │                           │
             ▼                           ▼
    ┌────────────────┐          ┌────────────────┐
    │  Shell Exec    │          │  jq Process    │
    │  (subprocess)  │          │  (subprocess)  │
    └────────────────┘          └────────────────┘

Tool Invocation Flow:
    Agent
      │
      ▼
    tool.run(**kwargs)
      │
      ├─▶ Start timer
      ├─▶ Execute _run()
      ├─▶ Stop timer
      ├─▶ Format response
      └─▶ Return MCPToolResponse
```

---

## 5. Agent Hierarchy

```
                    ┌──────────────────────┐
                    │  CoordinatorAgent    │
                    │                      │
                    │  • Task analysis     │
                    │  • Delegation        │
                    │  • Aggregation       │
                    │  • Middleware        │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
        ┌───────────────────┐   ┌───────────────────┐
        │  ResearchAgent    │   │  AnalysisAgent    │
        │                   │   │                   │
        │  • Info gathering │   │  • Data analysis  │
        │  • Tool usage     │   │  • Insights       │
        │  • Middleware     │   │  • Middleware     │
        └─────────┬─────────┘   └─────────┬─────────┘
                  │                       │
          ┌───────┴────────┐      ┌──────┴──────┐
          │                │      │             │
          ▼                ▼      ▼             ▼
    ┌──────────┐    ┌──────────┐ ┌──────────┐  │
    │ Command  │    │   JSON   │ │   JSON   │  │
    │  Tool    │    │  Search  │ │  Search  │  │
    └──────────┘    └──────────┘ └──────────┘  │
                                                │
                                    (shared tool instance)
```

---

## 6. Example 1: Middleware Interception

```
┌─────────────────────────────────────────────────────────────┐
│                    Example 1 Flow                            │
└─────────────────────────────────────────────────────────────┘

Step 1: Create Middleware Chain
    ┌──────────────────┐
    │ MiddlewareChain  │
    │                  │
    │  [Logging] ──▶ [Metrics]
    └──────────────────┘

Step 2: Process Request
    User Input
        │
        ▼
    AgentRequest(
        agent_name="coordinator",
        input_data="Analyze system",
        metadata={...}
    )
        │
        ▼
    [Logging] ──▶ Log: "→ REQUEST to coordinator"
        │
        ▼
    [Metrics] ──▶ Start timer, increment counter
        │
        ▼
    (Request processed)

Step 3: Process Response
    Agent Output
        │
        ▼
    AgentResponse(
        agent_name="coordinator",
        output_data="System OK",
        request_id=123
    )
        │
        ▼
    [Metrics] ──▶ Stop timer, record duration
        │
        ▼
    [Logging] ──▶ Log: "← RESPONSE from coordinator"
        │
        ▼
    (Response returned)

Step 4: Display Metrics
    [Metrics].print_summary()
        │
        ▼
    ┌─────────────────────────┐
    │  Total Requests: 2      │
    │  Total Time: 0.03 ms    │
    │  Avg Time: 0.02 ms      │
    └─────────────────────────┘
```

---

## 7. Example 3: MCP Tool Usage

```
┌─────────────────────────────────────────────────────────────┐
│              Example 3: Tool Integration Flow                │
└─────────────────────────────────────────────────────────────┘

Part 1: CommandTool
    ┌──────────────┐
    │ CommandTool  │
    │ (whitelist)  │
    └──────┬───────┘
           │
           ├─▶ run(command="echo 'test'")
           │       │
           │       ▼
           │   subprocess.run(...)
           │       │
           │       ▼
           │   MCPToolResponse(
           │       success=True,
           │       result="test",
           │       execution_time=0.007s
           │   )
           │
           ├─▶ run(command="date")
           │       │
           │       ▼
           │   (similar flow)
           │
           └─▶ get_stats()
                   │
                   ▼
               {call_count: 4, avg_time: 0.007s}

Part 2: JSONSearchTool
    ┌──────────────┐
    │JSONSearchTool│
    └──────┬───────┘
           │
           ├─▶ run(file="data.json", query=".users | length")
           │       │
           │       ▼
           │   jq process
           │       │
           │       ▼
           │   MCPToolResponse(
           │       success=True,
           │       result=3,
           │       execution_time=0.010s
           │   )
           │
           └─▶ run(file="data.json", query='.users[] | select(...)')
                   │
                   ▼
               (filter results)

Part 3: Agent + Tools
    ResearchAgent
        │
        ├─▶ process_with_tools(
        │       task="Get system info",
        │       command="uname -a"
        │   )
        │       │
        │       ▼
        │   CommandTool.run(...)
        │       │
        │       ▼
        │   Format results
        │
        └─▶ process_with_tools(
                task="Find engineers",
                json_file="data.json",
                jq_query='...'
            )
                │
                ▼
            JSONSearchTool.run(...)
                │
                ▼
            Format results
```

---

## 8. State Management in LangGraph

```
Initial State:
┌─────────────────────────────────────┐
│ messages: []                        │
│ current_task: "Analyze user data"   │
│ results: {}                         │
│ agent_history: []                   │
│ next_agent: None                    │
│ final_output: None                  │
└─────────────────────────────────────┘
         │
         ▼
    Coordinator Node
         │
         ▼
┌─────────────────────────────────────┐
│ messages: [HumanMessage(...)]       │
│ current_task: "Analyze user data"   │
│ results: {}                         │
│ agent_history: ["coordinator"]      │
│ next_agent: "research"              │
│ final_output: None                  │
└─────────────────────────────────────┘
         │
         ▼
    Research Node
         │
         ▼
┌─────────────────────────────────────┐
│ messages: [HumanMessage, AIMessage] │
│ current_task: "Analyze user data"   │
│ results: {                          │
│   "research_agent": "Found 3 users" │
│ }                                   │
│ agent_history: ["coordinator",      │
│                 "research_agent"]   │
│ next_agent: "coordinator"           │
│ final_output: None                  │
└─────────────────────────────────────┘
         │
         ▼
    Coordinator Node (Aggregate)
         │
         ▼
┌─────────────────────────────────────┐
│ messages: [...]                     │
│ current_task: "Analyze user data"   │
│ results: {                          │
│   "research_agent": "Found 3 users" │
│ }                                   │
│ agent_history: ["coordinator",      │
│                 "research_agent",   │
│                 "coordinator"]      │
│ next_agent: None                    │
│ final_output: "Summary: 3 users..." │
└─────────────────────────────────────┘
         │
         ▼
       END
```

---

## Summary

**Current Implementation:**
- ✅ Using LangGraph for workflow orchestration
- ✅ StateGraph with conditional routing
- ✅ TypedDict for type-safe state management
- ✅ Middleware pattern for cross-cutting concerns
- ✅ MCP tools for external capabilities
- ✅ Hierarchical agent architecture

**Key Components:**
1. **LangGraph** - Workflow engine with state management
2. **Middleware** - Request/response interception
3. **Agents** - Coordinator + specialized subagents
4. **Tools** - MCP-compliant external capabilities
5. **State** - Shared context across workflow

All diagrams represent the actual implementation in the project!
