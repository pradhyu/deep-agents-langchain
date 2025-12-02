"""Command execution tool for running shell commands safely."""

import subprocess
import shlex
from typing import Optional

from .mcp_base import MCPTool


class CommandTool(MCPTool):
    """
    MCP tool for executing shell commands safely.
    
    This tool allows agents to run system commands with:
    - Timeout protection
    - Output capture (stdout and stderr)
    - Security constraints (configurable allowed commands)
    - Error handling
    
    Example:
        tool = CommandTool()
        response = tool.run(command="echo 'Hello World'")
        print(response.result)  # "Hello World"
    
    Security Note:
        In production, you should implement command whitelisting
        or sandboxing to prevent malicious command execution.
    """
    
    name = "execute_command"
    description = "Execute shell commands and return their output"
    
    def __init__(self, timeout: int = 30, allowed_commands: Optional[list] = None):
        """
        Initialize the command tool.
        
        Args:
            timeout: Default timeout in seconds for command execution
            allowed_commands: Optional list of allowed command prefixes for security
        """
        super().__init__()
        self.default_timeout = timeout
        self.allowed_commands = allowed_commands
    
    def _is_command_allowed(self, command: str) -> bool:
        """
        Check if a command is allowed to execute.
        
        Args:
            command: The command to check
            
        Returns:
            True if command is allowed, False otherwise
        """
        if self.allowed_commands is None:
            # No restrictions if allowed_commands is not set
            return True
        
        # Check if command starts with any allowed prefix
        command_base = command.split()[0] if command.strip() else ""
        return any(
            command_base.startswith(allowed)
            for allowed in self.allowed_commands
        )
    
    def _run(
        self,
        command: str,
        timeout: Optional[int] = None,
        shell: bool = True
    ) -> str:
        """
        Execute a shell command and return its output.
        
        Args:
            command: The shell command to execute
            timeout: Timeout in seconds (uses default if not specified)
            shell: Whether to execute through shell (default: True)
            
        Returns:
            Command output (stdout and stderr combined)
            
        Raises:
            ValueError: If command is not allowed
            subprocess.TimeoutExpired: If command exceeds timeout
            subprocess.CalledProcessError: If command returns non-zero exit code
        """
        if not command or not command.strip():
            raise ValueError("Command cannot be empty")
        
        # Security check
        if not self._is_command_allowed(command):
            raise ValueError(
                f"Command not allowed: {command.split()[0]}. "
                f"Allowed commands: {self.allowed_commands}"
            )
        
        # Use provided timeout or default
        exec_timeout = timeout if timeout is not None else self.default_timeout
        
        try:
            # Execute command with timeout
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=exec_timeout,
                check=True
            )
            
            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            
            return output.strip() if output else "(no output)"
        
        except subprocess.TimeoutExpired:
            raise TimeoutError(
                f"Command timed out after {exec_timeout} seconds: {command}"
            )
        
        except subprocess.CalledProcessError as e:
            # Include error output in exception message
            error_msg = f"Command failed with exit code {e.returncode}: {command}"
            if e.stderr:
                error_msg += f"\n{e.stderr}"
            raise RuntimeError(error_msg)
    
    def run_safe(self, command: str, **kwargs) -> dict:
        """
        Execute command and return a safe dictionary response.
        
        This is a convenience method that always returns a dict,
        never raises exceptions.
        
        Args:
            command: The command to execute
            **kwargs: Additional arguments for _run
            
        Returns:
            Dictionary with 'success', 'output', and optional 'error' keys
        """
        response = self.run(command=command, **kwargs)
        
        return {
            "success": response.success,
            "output": response.result if response.success else None,
            "error": response.error if not response.success else None,
            "execution_time": response.execution_time
        }
