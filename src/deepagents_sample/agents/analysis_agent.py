"""Analysis agent for processing and analyzing data."""

from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..middleware import AgentRequest, AgentResponse, MiddlewareChain
from ..tools import JSONSearchTool


class AnalysisAgent:
    """
    Analysis agent that processes and analyzes gathered information.
    
    The analysis agent:
    - Analyzes data from JSON files
    - Generates summaries and insights
    - Performs data transformations
    - Uses middleware for logging and metrics
    
    Example:
        agent = AnalysisAgent(
            model=ChatOpenAI(model="gpt-4"),
            middleware_chain=my_middleware
        )
        result = agent.process("Analyze user distribution by role")
    """
    
    def __init__(
        self,
        model: Optional[ChatOpenAI] = None,
        middleware_chain: Optional[MiddlewareChain] = None,
        name: str = "analysis_agent"
    ):
        """
        Initialize the analysis agent.
        
        Args:
            model: LangChain LLM model (defaults to gpt-4o-mini)
            middleware_chain: Optional middleware chain for request/response processing
            name: Agent name for identification
        """
        self.name = name
        self.model = model or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.middleware_chain = middleware_chain
        self.conversation_history: List[BaseMessage] = []
        
        # Initialize JSON tool for data analysis
        self.json_tool = JSONSearchTool(check_jq=False)
    
    def _create_request(self, input_data: Any) -> AgentRequest:
        """Create an agent request for middleware processing."""
        return AgentRequest(
            agent_name=self.name,
            input_data=input_data,
            metadata={"type": "analysis"}
        )
    
    def _create_response(self, output_data: Any, request_id: int) -> AgentResponse:
        """Create an agent response for middleware processing."""
        return AgentResponse(
            agent_name=self.name,
            output_data=output_data,
            request_id=request_id,
            metadata={"type": "analysis"}
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
    
    def analyze_json_data(self, file_path: str, query: str) -> Dict[str, Any]:
        """
        Analyze JSON data using jq query.
        
        Args:
            file_path: Path to JSON file
            query: jq query expression
            
        Returns:
            Dictionary with query result and metadata
        """
        response = self.json_tool.run(file_path=file_path, jq_query=query)
        
        return {
            "success": response.success,
            "data": response.result if response.success else None,
            "error": response.error if not response.success else None,
            "execution_time": response.execution_time
        }
    
    def process(self, task: str, data: Optional[Any] = None) -> str:
        """
        Process an analysis task.
        
        Args:
            task: The analysis task description
            data: Optional data to analyze
            
        Returns:
            Analysis results
        """
        # Process through middleware
        request, processed_task = self._process_with_middleware(task)
        
        # Build system prompt
        system_prompt = f"""You are an analysis agent named '{self.name}'.
Your role is to analyze data and provide insights.

You can:
- Identify patterns and trends
- Generate summaries
- Compare and contrast data points
- Provide statistical insights
- Make recommendations based on data

Provide clear, structured analysis with specific findings."""
        
        # Add data to task if provided
        full_task = processed_task
        if data:
            import json
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data, indent=2)
            else:
                data_str = str(data)
            full_task += f"\n\nData to analyze:\n{data_str}"
        
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
    
    def analyze_with_queries(
        self,
        task: str,
        file_path: str,
        queries: List[Dict[str, str]]
    ) -> str:
        """
        Perform analysis using multiple JSON queries.
        
        Args:
            task: Analysis task description
            file_path: Path to JSON file
            queries: List of dicts with 'name' and 'query' keys
            
        Returns:
            Analysis results with query outputs
        """
        # Process through middleware
        request, processed_task = self._process_with_middleware(task)
        
        results = [f"Analysis Task: {processed_task}\n"]
        results.append(f"Data Source: {file_path}\n")
        
        # Execute each query
        query_results = {}
        for q in queries:
            query_name = q.get("name", "unnamed")
            query_expr = q.get("query", ".")
            
            results.append(f"\n--- {query_name} ---")
            results.append(f"Query: {query_expr}")
            
            analysis = self.analyze_json_data(file_path, query_expr)
            
            if analysis["success"]:
                import json
                if isinstance(analysis["data"], (dict, list)):
                    data_str = json.dumps(analysis["data"], indent=2)
                else:
                    data_str = str(analysis["data"])
                results.append(f"Result:\n{data_str}")
                query_results[query_name] = analysis["data"]
            else:
                results.append(f"Error: {analysis['error']}")
        
        # Generate analysis summary using LLM
        results.append("\n--- Analysis Summary ---")
        
        import json
        summary_prompt = f"""Based on the following query results, provide an analysis summary:

{json.dumps(query_results, indent=2)}

Task: {processed_task}"""
        
        messages = [HumanMessage(content=summary_prompt)]
        llm_response = self.model.invoke(messages)
        results.append(llm_response.content)
        
        # Combine results
        output = "\n".join(results)
        
        # Process through middleware
        result = self._finalize_with_middleware(output, request)
        
        return result
    
    def compare_data(
        self,
        file_path: str,
        query1: str,
        query2: str,
        comparison_task: str
    ) -> str:
        """
        Compare two data sets from the same file.
        
        Args:
            file_path: Path to JSON file
            query1: First jq query
            query2: Second jq query
            comparison_task: What to compare
            
        Returns:
            Comparison analysis
        """
        # Get both data sets
        result1 = self.analyze_json_data(file_path, query1)
        result2 = self.analyze_json_data(file_path, query2)
        
        if not result1["success"] or not result2["success"]:
            return f"Error: Could not retrieve data for comparison"
        
        # Use LLM to compare
        import json
        prompt = f"""Compare the following two data sets:

Dataset 1:
{json.dumps(result1['data'], indent=2)}

Dataset 2:
{json.dumps(result2['data'], indent=2)}

Comparison task: {comparison_task}

Provide a detailed comparison with specific insights."""
        
        return self.process(prompt)
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get statistics about tool usage."""
        return {
            "json_tool": self.json_tool.get_stats()
        }
    
    def reset_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
