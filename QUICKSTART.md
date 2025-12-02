# Quick Start Guide

Get up and running with DeepAgents in 5 minutes!

## 1. Install Dependencies (30 seconds)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

## 2. Run Your First Example (1 minute)

```bash
# Example 1: Middleware (no API key needed)
python -m deepagents_sample.examples.example1_basic_middleware
```

You'll see:
- Middleware intercepting requests/responses
- Logging with timestamps
- Performance metrics
- Request/response correlation

## 3. Try the Tools (2 minutes)

```bash
# Example 3: MCP Tools (no API key needed)
python -m deepagents_sample.examples.example3_mcp_tools
```

You'll see:
- CommandTool executing shell commands
- JSONSearchTool querying data with jq
- Tool statistics and performance tracking

## 4. Full Workflow with LangGraph (2 minutes)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='your-key-here'

# Example 2: LangGraph with Subagents
python -m deepagents_sample.examples.example2_langgraph_subagents
```

You'll see:
- Coordinator delegating to subagents
- State management across workflow
- Automatic task routing
- Result aggregation

## 5. Interactive Mode

```bash
# Run all examples with interactive menu
python -m deepagents_sample.examples.run_all
```

Select examples from the menu:
1. Basic Middleware Usage
2. LangGraph with Subagents
3. MCP Tool Integration
4. Run All Examples

## What You'll Learn

### Example 1: Middleware
- How middleware intercepts agent communications
- Logging and metrics collection
- Middleware chaining patterns

### Example 2: LangGraph
- Hierarchical agent orchestration
- State management
- Automatic routing
- Result aggregation

### Example 3: MCP Tools
- Tool integration patterns
- Safe command execution
- JSON querying with jq
- Error handling and timeouts

## Next Steps

1. **Explore the Code**: Check out `src/deepagents_sample/`
2. **Read the Docs**: See `README.md` for detailed information
3. **Extend**: Add your own agents, tools, or middleware
4. **Build**: Create your own multi-agent application!

## Common Issues

### "OPENAI_API_KEY not set"
Only Example 2 needs this. Examples 1 and 3 work without it.

### "jq is not installed"
Install jq for full Example 3 functionality:
```bash
brew install jq  # macOS
```

### Import errors
Make sure you activated the virtual environment:
```bash
source .venv/bin/activate
```

## Project Structure

```
src/deepagents_sample/
├── middleware/     # Request/response interception
├── tools/          # MCP tool wrappers
├── agents/         # Agent implementations
├── workflow/       # LangGraph workflows
└── examples/       # Runnable examples
```

## Key Files

- `README.md` - Full documentation
- `pyproject.toml` - Dependencies
- `data/sample.json` - Sample data for examples
- `.project-summary.md` - Implementation details

---

**Ready to build with DeepAgents? Start with Example 1! 🚀**
