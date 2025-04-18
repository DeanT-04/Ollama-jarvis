#!/usr/bin/env python3
"""
MCP tools integration for Jarvis CLI.

This module provides integration with the Model Context Protocol (MCP) SDK,
allowing Jarvis to expose tools and resources to LLM applications.
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.fastmcp import FastMCP

# Import Jarvis modules
from web_search import search_web, format_search_results
from workspace_utils import get_workspace_state, read_file, list_directory, format_directory_listing

# Configuration
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_workspace")

class JarvisMCPServer:
    """MCP server for Jarvis CLI."""
    
    def __init__(self, name: str = "jarvis-mcp"):
        """Initialize the MCP server.
        
        Args:
            name: The name of the MCP server.
        """
        self.mcp = FastMCP(name)
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
            return format_search_results(results)
        
        @self.mcp.tool()
        def execute_python(code: str) -> str:
            """Execute Python code in the Jarvis workspace.
            
            Args:
                code: The Python code to execute.
                
            Returns:
                The output of the executed code.
            """
            import tempfile
            import subprocess
            
            try:
                # Create a temporary script file
                with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR, suffix='.py', delete=False) as f:
                    f.write(code.encode())
                    script_path = f.name
                
                # Execute the script
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=WORKSPACE_DIR
                )
                stdout, stderr = process.communicate()
                
                # Clean up
                os.unlink(script_path)
                
                if stderr:
                    return f"Error:\n{stderr.decode()}"
                
                return stdout.decode()
            except Exception as e:
                return f"Error: {str(e)}"
        
        @self.mcp.tool()
        def execute_bash(code: str) -> str:
            """Execute Bash/PowerShell commands in the Jarvis workspace.
            
            Args:
                code: The Bash/PowerShell code to execute.
                
            Returns:
                The output of the executed code.
            """
            import tempfile
            import subprocess
            
            try:
                # Create a temporary script file
                with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR, suffix='.sh', delete=False) as f:
                    f.write(code.encode())
                    script_path = f.name
                
                # Make the script executable
                os.chmod(script_path, 0o755)
                
                # Execute the script
                if os.name == 'nt':  # Windows
                    # Use PowerShell to execute the script
                    process = subprocess.Popen(
                        ['powershell', '-Command', f"Get-Content '{script_path}' | powershell -"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=WORKSPACE_DIR
                    )
                else:  # Unix/Linux/Mac
                    process = subprocess.Popen(
                        ['/bin/bash', script_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=WORKSPACE_DIR
                    )
                
                stdout, stderr = process.communicate()
                
                # Clean up
                os.unlink(script_path)
                
                if stderr:
                    return f"Error:\n{stderr.decode()}"
                
                return stdout.decode()
            except Exception as e:
                return f"Error: {str(e)}"
    
    def setup_resources(self):
        """Set up the MCP resources."""
        
        @self.mcp.resource("workspace://state")
        def workspace_state() -> str:
            """Get the current state of the Jarvis workspace.
            
            Returns:
                The current state of the workspace.
            """
            return get_workspace_state(WORKSPACE_DIR)
        
        @self.mcp.resource("workspace://files/{path}")
        def workspace_file(path: str) -> str:
            """Get the contents of a file in the Jarvis workspace.
            
            Args:
                path: The path to the file, relative to the workspace directory.
                
            Returns:
                The contents of the file.
            """
            content, success = read_file(WORKSPACE_DIR, path)
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
            items = list_directory(WORKSPACE_DIR, path)
            return format_directory_listing(items)
    
    def run(self):
        """Run the MCP server."""
        self.mcp.run()


def main():
    """Main function to run the Jarvis MCP server."""
    server = JarvisMCPServer()
    server.run()


if __name__ == "__main__":
    main()
