# Implementation Plan

- [x] 1. Initialize project structure with uv and dependencies
  - Create pyproject.toml with LangChain v1+, LangGraph, and DeepAgents dependencies
  - Set up project directory structure with src/deepagents_sample layout
  - Create __init__.py files for all package modules
  - Create sample.json data file for JSON search examples
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Implement middleware components
  - [x] 2.1 Create base middleware interface
    - Define middleware protocol/base class with process_request and process_response methods
    - Implement middleware chaining mechanism
    - _Requirements: 2.1, 2.5_
  
  - [x] 2.2 Implement LoggingMiddleware
    - Create logging middleware that captures agent requests and responses
    - Add timestamp and agent identification to logs
    - Implement formatted console output for visibility
    - _Requirements: 2.2, 2.3, 2.4, 2.5_
  
  - [x] 2.3 Implement MetricsMiddleware
    - Create metrics middleware that tracks execution time and call counts
    - Implement performance metric collection and reporting
    - Add metric summary output functionality
    - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [x] 3. Implement MCP tool wrappers
  - [x] 3.1 Create MCP base tool class
    - Implement base MCPTool class following MCP specification
    - Define tool request/response data models
    - Add error handling and timeout mechanisms
    - _Requirements: 5.1, 5.5_
  
  - [x] 3.2 Implement CommandTool for shell execution
    - Create CommandTool that safely executes shell commands
    - Implement timeout and security constraints
    - Add command output capture and formatting
    - _Requirements: 5.2, 5.4, 5.5_
  
  - [x] 3.3 Implement JSONSearchTool with jq
    - Create JSONSearchTool that executes jq queries on JSON files
    - Implement file reading and jq command execution
    - Add query result parsing and error handling
    - _Requirements: 5.3, 5.4, 5.5_

- [x] 4. Implement agent classes
  - [x] 4.1 Create CoordinatorAgent
    - Implement main coordinator agent with task delegation logic
    - Configure agent with middleware support
    - Add subagent management and result aggregation
    - _Requirements: 3.1, 3.2, 6.2_
  
  - [x] 4.2 Create ResearchAgent
    - Implement research agent with MCP tool access
    - Configure agent to use CommandTool and JSONSearchTool
    - Add information gathering and formatting capabilities
    - _Requirements: 3.1, 3.2, 5.4, 6.2_
  
  - [x] 4.3 Create AnalysisAgent
    - Implement analysis agent for data processing
    - Configure agent with JSONSearchTool access
    - Add data analysis and summary generation logic
    - _Requirements: 3.1, 3.2, 5.4, 6.2_

- [x] 5. Implement LangGraph workflow integration
  - [x] 5.1 Define AgentState data model
    - Create TypedDict for LangGraph state management
    - Define state fields for messages, tasks, results, and history
    - _Requirements: 3.3, 3.4, 6.3_
  
  - [x] 5.2 Create LangGraph workflow with subagents
    - Build state machine with coordinator and subagent nodes
    - Implement state transitions and routing logic
    - Add conditional edges based on task types
    - Wire up agent communication through state
    - _Requirements: 3.2, 3.3, 3.4, 6.2, 6.5_

- [x] 6. Create example scripts
  - [x] 6.1 Implement Example 1: Basic middleware usage
    - Create example showing middleware interception
    - Demonstrate logging and metrics middleware in action
    - Add clear console output with explanations
    - _Requirements: 2.4, 4.4, 7.1, 7.2, 7.4_
  
  - [x] 6.2 Implement Example 2: LangGraph with subagents
    - Create example demonstrating hierarchical agent workflow
    - Show coordinator delegating to research and analysis agents
    - Display state transitions and agent communication
    - _Requirements: 3.5, 4.4, 6.1, 7.1, 7.2, 7.4_
  
  - [x] 6.3 Implement Example 3: MCP tool integration
    - Create example showing MCP tools in agent workflows
    - Demonstrate CommandTool and JSONSearchTool usage
    - Show tool registration and invocation patterns
    - _Requirements: 5.4, 5.5, 6.1, 7.1, 7.2, 7.4_
  
  - [x] 6.4 Create run_all.py main entry point
    - Implement script that runs all examples sequentially
    - Add menu or command-line interface for example selection
    - Include error handling and clear output separation
    - _Requirements: 7.1, 7.3, 7.5_

- [x] 7. Create documentation and README
  - [x] 7.1 Write comprehensive README.md
    - Add project overview and feature descriptions
    - Document uv installation and setup instructions
    - Provide step-by-step guide for running examples
    - Include environment variable configuration
    - Add troubleshooting section
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [x] 7.2 Add inline code documentation
    - Write docstrings for all classes and functions
    - Add explanatory comments for complex logic
    - Include usage examples in docstrings
    - _Requirements: 4.4, 6.1_

- [ ]* 8. Add error handling and resilience
  - Implement comprehensive error handling in middleware
  - Add retry logic for transient agent failures
  - Implement timeout handling for MCP tools
  - Add graceful degradation for tool failures
  - _Requirements: 6.4_

- [ ]* 9. Create validation tests
  - Write unit tests for middleware components
  - Create integration tests for complete workflows
  - Add validation for all example scripts
  - Test with mock LLM responses
  - _Requirements: 7.3_
