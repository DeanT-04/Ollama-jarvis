#!/usr/bin/env python3
"""
MCP integration for Jarvis.

This module provides integration with the Model Context Protocol (MCP) SDK,
allowing Jarvis to expose tools and resources to LLM applications.
"""

import os
import sys
from typing import Dict, List, Any, Optional

from jarvis.config import get_config
from jarvis.core.executor import execute_python, execute_bash
from jarvis.tools.search import search_web, format_search_results_legacy
from jarvis.tools.workspace import get_workspace_state, read_file, list_directory, format_directory_listing

class JarvisMCPServer:
    """MCP server for Jarvis."""
    
    def __init__(self, name: str = "jarvis-mcp"):
        """Initialize the MCP server.
        
        Args:
            name: The name of the MCP server.
        """
        # Import MCP here to avoid circular imports
        import mcp.types as types
        from mcp.server.fastmcp import FastMCP
        
        self.mcp = FastMCP(name)
        self.workspace_dir = get_config("WORKSPACE_DIR")
        self.setup_tools()
        self.setup_resources()
    
    def setup_tools(self):
        """Set up the MCP tools."""
        
        @self.mcp.tool()
        def search(query: str) -> str:
            """Search the web for information.
            
            Args:
                query: The search query.
                
            Returns:
                The search results as a formatted string.
            """
            results = search_web(query)
            return format_search_results_legacy(results)
        
        @self.mcp.tool()
        def execute_python_code(code: str) -> str:
            """Execute Python code in the Jarvis workspace.
            
            Args:
                code: The Python code to execute.
                
            Returns:
                The output of the executed code.
            """
            stdout, stderr, return_code = execute_python(code, self.workspace_dir)
            
            if stderr:
                return f"Error:\n{stderr}"
            
            return stdout
        
        @self.mcp.tool()
        def execute_bash_code(code: str) -> str:
            """Execute Bash/PowerShell commands in the Jarvis workspace.
            
            Args:
                code: The Bash/PowerShell code to execute.
                
            Returns:
                The output of the executed code.
            """
            stdout, stderr, return_code = execute_bash(code, self.workspace_dir)
            
            if stderr:
                return f"Error:\n{stderr}"
            
            return stdout
    
    def setup_resources(self):
        """Set up the MCP resources."""
        
        @self.mcp.resource("workspace://state")
        def workspace_state() -> str:
            """Get the current state of the Jarvis workspace.
            
            Returns:
                The current state of the workspace.
            """
            return get_workspace_state(self.workspace_dir)
        
        @self.mcp.resource("workspace://files/{path}")
        def workspace_file(path: str) -> str:
            """Get the contents of a file in the Jarvis workspace.
            
            Args:
                path: The path to the file, relative to the workspace directory.
                
            Returns:
                The contents of the file.
            """
            content, success = read_file(path, self.workspace_dir)
            if not success:
                return f"Error: {content}"
            return content
        
        @self.mcp.resource("workspace://directory/{path}")
        def workspace_directory(path: str = "") -> str:
            """List the contents of a directory in the Jarvis workspace.
            
            Args:
                path: The path to the directory, relative to the workspace directory.
                
            Returns:
                A formatted listing of the directory contents.
            """
            items = list_directory(path, self.workspace_dir)
            return format_directory_listing(items)
    
    def run(self):
        """Run the MCP server."""
        self.mcp.run()
