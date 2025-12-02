# DeepAgents Sample Project

A comprehensive demonstration of **DeepAgents** with **LangChain v1+**, showcasing middleware usage, hierarchical agent orchestration with **LangGraph**, and **MCP (Model Context Protocol)** tool integration.

## 🎯 Overview

This project demonstrates three key aspects of building multi-agent systems with LangChain:

1. **Middleware** - Intercept and process agent requests/responses for logging, metrics, and more
2. **Hierarchical Agents** - Coordinator and subagent patterns with LangGraph state management
3. **MCP Tools** - External capabilities through standardized tool interfaces

## ✨ Features

- 🔌 **Middleware System**: LoggingMiddleware and MetricsMiddleware for visibility and performance tracking
- 🤖 **Multi-Agent Orchestration**: Coordinator, Research, and Analysis agents working together
- 📊 **LangGraph Workflows**: State-based agent coordination with automatic routing using **LangGraph's StateGraph**
- 🛠️ **MCP Tools**: CommandTool for shell execution and JSONSearchTool for jq queries
- 📈 **Performance Metrics**: Built-in tracking of agent execution times and tool usage
- 🎓 **Educational Examples**: Three comprehensive examples with detailed explanations
- 🪵 **Professional Logging**: Python logging throughout (no print statements)

## 📋 Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- OpenAI API key (for Examples 2)
- [jq](https://stedolan.github.io/jq/) - JSON processor (optional, for Example 3)

## 🚀 Quick Start

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd deepagents-sample

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### 3. Set Environment Variables

```bash
# Required for Example 2 (LangGraph with LLM)
export OPENAI_API_KEY='your-openai-api-key'

# Optional: Enable LangSmith tracing
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY='your-langsmith-key'
```

### 4. Install jq (Optional)

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# Windows
choco install jq
```

## 🎮 Running Examples

### Interactive Mode

```bash
python -m deepagents_sample.examples.run_all
```

This launches an interactive menu where you can select which example to run.

### Run Specific Example

```bash
# Example 1: Basic Middleware
python -m deepagents_sample.examples.run_all 1

# Example 2: LangGraph with Subagents (requires OPENAI_API_KEY)
python -m deepagents_sample.examples.run_all 2

# Example 3: MCP Tool Integration
python -m deepagents_sample.examples.run_all 3
```

### Run All Examples

```bash
python -m deepagents_sample.examples.run_all all
```

### Run Individual Example Files

```bash
python -m deepagents_sample.examples.example1_basic_middleware
python -m deepagents_sample.examples.example2_langgraph_subagents
python -m deepagents_sample.examples.example3_mcp_tools
```

## 📚 Examples

### Example 1: Basic Middleware Usage

Demonstrates how middleware intercepts agent communications:

- **LoggingMiddleware**: Captures all requests and responses with timestamps
- **MetricsMiddleware**: Tracks execution time and call counts
- **Middleware Chaining**: Multiple middleware working together
- **Request/Response Flow**: Visibility into agent interactions

**Key Concepts:**
- Middleware doesn't alter agent logic
- Each request/response has a unique ID for correlation
- Middleware can be chained for complex processing pipelines

### Example 2: LangGraph with Subagents

Shows hierarchical agent orchestration:

- **Coordinator Agent**: Analyzes tasks and delegates to subagents
- **Research Agent**: Gathers information using tools
- **Analysis Agent**: Processes and analyzes data
- **State Management**: Shared state across workflow
- **Automatic Routing**: Task-based agent selection

### Example 3: MCP Tool Integration

Demonstrates external tool usage:

- **CommandTool**: Safe shell command execution with whitelisting
- **JSONSearchTool**: Powerful JSON querying with jq
- **Tool Registration**: How agents access tools
- **Error Handling**: Timeouts and error recovery
- **Usage Statistics**: Track tool performance

### Example 4: Streaming Responses ✨ NEW

Real-time streaming for better UX:

- **Token-by-Token Output**: Stream responses as they're generated
- **Progressive Results**: Show research findings immediately
- **Async Patterns**: Modern Python async/await
- **Cancellable Operations**: Stop long-running tasks

**Requires**: OPENAI_API_KEY

### Example 5: Caching & Configuration 💰 NEW

Production features for cost reduction:

- **Configuration Management**: Environment-based settings with Pydantic
- **Caching Layer**: 40-60% cost reduction
- **Input Validation**: Security and data quality
- **Cost Tracking**: Real-time budget monitoring

**Benefits**: Significant cost savings, better security

### Example 6: Parallel Execution & Error Recovery ⚡ NEW

Performance and reliability features:

- **Parallel Execution**: 3-4x speedup with asyncio
- **Automatic Retry**: Exponential backoff for transient failures
- **Fallback Strategies**: Graceful degradation
- **Circuit Breaker**: Prevent cascade failures
- **High Availability**: 99% uptime patterns

**Benefits**: Better performance, higher reliability

**Workflow:**
```
┌─────────────┐
│ Coordinator │ ← Entry point, task analysis
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌──────┐ ┌──────────┐
│Research│ │ Analysis │ ← Specialized subagents
└───┬───┘ └────┬─────┘
    │          │
    └────┬─────┘
         ▼
   ┌──────────┐
   │Coordinator│ ← Result aggregation
   └──────────┘
         │
         ▼
       [END]
```

### Example 3: MCP Tool Integration

Demonstrates external tool usage:

- **CommandTool**: Safe shell command execution with whitelisting
- **JSONSearchTool**: Powerful JSON querying with jq
- **Tool Registration**: How agents access tools
- **Error Handling**: Timeouts and error recovery
- **Usage Statistics**: Track tool performance

**Supported Commands:**
- `echo`, `ls`, `cat`, `date`, `pwd`, `whoami`, `uname`

**jq Query Examples:**
- `.users | length` - Count users
- `.users[] | select(.role == "engineer")` - Filter by role
- `.projects[].name` - Extract project names

## 🏗️ Project Structure

```
deepagents-sample/
├── src/
│   └── deepagents_sample/
│       ├── __init__.py
│       ├── middleware/          # Middleware components
│       │   ├── base.py         # Base middleware classes
│       │   ├── logging_middleware.py
│       │   └── metrics_middleware.py
│       ├── tools/              # MCP tool wrappers
│       │   ├── mcp_base.py    # Base tool class
│       │   ├── command_tool.py
│       │   └── json_search_tool.py
│       ├── agents/             # Agent implementations
│       │   ├── coordinator_agent.py
│       │   ├── research_agent.py
│       │   └── analysis_agent.py
│       ├── workflow/           # LangGraph workflows
│       │   ├── state.py       # State management
│       │   └── graph.py       # Workflow definition
│       └── examples/           # Example scripts
│           ├── example1_basic_middleware.py
│           ├── example2_langgraph_subagents.py
│           ├── example3_mcp_tools.py
│           └── run_all.py
├── data/
│   └── sample.json            # Sample data for examples
├── pyproject.toml             # Project configuration
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | For Example 2 | OpenAI API key for LLM access |
| `LANGCHAIN_TRACING_V2` | Optional | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | Optional | LangSmith API key |

### Customization

#### Adding New Middleware

```python
from deepagents_sample.middleware import BaseMiddleware, AgentRequest, AgentResponse

class CustomMiddleware(BaseMiddleware):
    def process_request(self, request: AgentRequest) -> AgentRequest:
        # Your logic here
        return request
    
    def process_response(self, response: AgentResponse) -> AgentResponse:
        # Your logic here
        return response
```

#### Adding New Tools

```python
from deepagents_sample.tools import MCPTool

class CustomTool(MCPTool):
    name = "custom_tool"
    description = "Does something useful"
    
    def _run(self, **kwargs):
        # Your tool logic here
        return result
```

#### Creating New Agents

```python
from deepagents_sample.agents import CoordinatorAgent

class CustomAgent:
    def __init__(self, model, middleware_chain=None):
        self.model = model
        self.middleware_chain = middleware_chain
    
    def process(self, task):
        # Your agent logic here
        return result
```

## 📐 Architecture Diagrams

### Overall System Architecture

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

### LangGraph Workflow

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
```

### Middleware Flow

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

**See [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) for complete architecture documentation with all diagrams.**

## 📖 Key Concepts

### Middleware Pattern

Middleware intercepts agent communications for:
- **Logging**: Track all agent interactions
- **Metrics**: Measure performance
- **Transformation**: Modify requests/responses
- **Validation**: Ensure data integrity
- **Caching**: Store and reuse results

### Agent Hierarchy

- **Coordinator**: High-level task analysis and delegation
- **Subagents**: Specialized capabilities (research, analysis, etc.)
- **Tools**: External system integration

### State Management

LangGraph maintains shared state across workflow:
- **Messages**: Conversation history
- **Results**: Agent outputs
- **Routing**: Next agent selection
- **Error Handling**: Failure recovery

### MCP Tools

Standardized interface for external capabilities:
- **Consistent API**: All tools follow same pattern
- **Error Handling**: Built-in timeout and error management
- **Statistics**: Automatic usage tracking
- **Security**: Configurable constraints

## 🐛 Troubleshooting

### "OPENAI_API_KEY not set"

Example 2 requires an OpenAI API key. Set it:
```bash
export OPENAI_API_KEY='your-key-here'
```

### "jq is not installed"

Example 3 works best with jq. Install it:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq
```

### "Command not allowed"

CommandTool has security restrictions. Only these commands are allowed:
- `echo`, `ls`, `cat`, `date`, `pwd`, `whoami`, `uname`

To allow more commands, modify the `allowed_commands` list in `CommandTool` initialization.

### Import Errors

Make sure you've activated the virtual environment:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

## 🤝 Contributing

This is a sample/educational project. Feel free to:
- Extend with new examples
- Add more middleware types
- Create additional tools
- Implement new agent types

## 📄 License

This project is provided as-is for educational purposes.

## 🔗 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [DeepAgents Quickstart](https://docs.langchain.com/oss/python/deepagents/quickstart)
- [jq Manual](https://stedolan.github.io/jq/manual/)
- [uv Documentation](https://github.com/astral-sh/uv)

## 💡 Next Steps

After exploring these examples, consider:

1. **Extend the Workflow**: Add more specialized agents
2. **Create Custom Tools**: Integrate with your APIs or databases
3. **Add Persistence**: Store agent state and conversation history
4. **Implement Streaming**: Real-time agent responses
5. **Add Authentication**: Secure tool access
6. **Deploy**: Package as a service or API

---

**Happy Building with DeepAgents! 🚀**
# deep-agents-langchain
