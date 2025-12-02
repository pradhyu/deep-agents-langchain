"""JSON search tool using jq for querying JSON data."""

import json
import subprocess
from pathlib import Path
from typing import Any, Union

from .mcp_base import MCPTool


class JSONSearchTool(MCPTool):
    """
    MCP tool for searching and querying JSON files using jq syntax.
    
    This tool enables agents to:
    - Query JSON files with jq expressions
    - Extract specific fields from complex JSON structures
    - Filter and transform JSON data
    - Handle both file paths and JSON strings
    
    jq is a powerful JSON processor. Examples:
    - '.users[0]' - Get first user
    - '.users[] | select(.role == "engineer")' - Filter by role
    - '.projects | length' - Count projects
    - '.users[].name' - Extract all user names
    
    Example:
        tool = JSONSearchTool()
        response = tool.run(
            file_path="data/sample.json",
            jq_query=".users[] | select(.role == \\"engineer\\")"
        )
        print(response.result)
    """
    
    name = "search_json"
    description = "Search and query JSON files using jq syntax"
    
    def __init__(self, check_jq: bool = True):
        """
        Initialize the JSON search tool.
        
        Args:
            check_jq: Whether to check if jq is installed on initialization
        """
        super().__init__()
        
        if check_jq:
            self._check_jq_installed()
    
    def _check_jq_installed(self) -> bool:
        """
        Check if jq is installed and available.
        
        Returns:
            True if jq is available
            
        Raises:
            RuntimeError: If jq is not installed
        """
        try:
            result = subprocess.run(
                ["jq", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError(
                "jq is not installed. Please install it:\n"
                "  macOS: brew install jq\n"
                "  Ubuntu/Debian: sudo apt-get install jq\n"
                "  Windows: choco install jq"
            )
    
    def _load_json(self, source: Union[str, Path]) -> str:
        """
        Load JSON data from a file or string.
        
        Args:
            source: File path or JSON string
            
        Returns:
            JSON string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        # Check if it's a file path
        path = Path(source)
        if path.exists() and path.is_file():
            with open(path, 'r') as f:
                content = f.read()
                # Validate JSON
                json.loads(content)
                return content
        
        # Try to parse as JSON string
        try:
            json.loads(source)
            return source
        except json.JSONDecodeError:
            raise ValueError(
                f"Source is neither a valid file path nor valid JSON: {source}"
            )
    
    def _run(
        self,
        file_path: str = None,
        json_data: str = None,
        jq_query: str = "."
    ) -> Any:
        """
        Execute a jq query on JSON data.
        
        Args:
            file_path: Path to JSON file (optional if json_data provided)
            json_data: JSON string (optional if file_path provided)
            jq_query: jq query expression (default: "." returns everything)
            
        Returns:
            Query result (parsed as Python object)
            
        Raises:
            ValueError: If neither file_path nor json_data provided
            RuntimeError: If jq execution fails
        """
        if not file_path and not json_data:
            raise ValueError("Either file_path or json_data must be provided")
        
        if not jq_query or not jq_query.strip():
            jq_query = "."
        
        # Load JSON data
        if file_path:
            json_string = self._load_json(file_path)
        else:
            json_string = self._load_json(json_data)
        
        try:
            # Execute jq query
            result = subprocess.run(
                ["jq", jq_query],
                input=json_string,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            
            # Parse jq output back to Python object
            output = result.stdout.strip()
            if not output:
                return None
            
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # If output is not valid JSON (e.g., plain string), return as-is
                return output
        
        except subprocess.CalledProcessError as e:
            error_msg = f"jq query failed: {jq_query}"
            if e.stderr:
                error_msg += f"\n{e.stderr}"
            raise RuntimeError(error_msg)
        
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"jq query timed out: {jq_query}")
    
    def query_file(self, file_path: str, query: str) -> dict:
        """
        Convenience method to query a file and get a safe response.
        
        Args:
            file_path: Path to JSON file
            query: jq query expression
            
        Returns:
            Dictionary with 'success', 'result', and optional 'error' keys
        """
        response = self.run(file_path=file_path, jq_query=query)
        
        return {
            "success": response.success,
            "result": response.result if response.success else None,
            "error": response.error if not response.success else None,
            "execution_time": response.execution_time
        }
    
    def get_field(self, file_path: str, field_path: str) -> Any:
        """
        Extract a specific field from a JSON file.
        
        Args:
            file_path: Path to JSON file
            field_path: Dot-notation path (e.g., "users.0.name")
            
        Returns:
            Field value
        """
        # Convert dot notation to jq syntax
        jq_query = "." + field_path.replace(".", ".")
        response = self.run(file_path=file_path, jq_query=jq_query)
        
        if response.success:
            return response.result
        else:
            raise RuntimeError(f"Failed to get field: {response.error}")
