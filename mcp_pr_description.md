# Add MCP Integration for Tools and Resources

## Overview
This PR adds integration with the Model Context Protocol (MCP) SDK, allowing Jarvis to expose its tools and resources to LLM applications. This enables other applications to leverage Jarvis's capabilities through a standardized protocol.

## Key Changes

### MCP Server Implementation
- Added `mcp_tools.py` module with a complete MCP server implementation
- Exposed Jarvis tools (search, execute_python, execute_bash) via MCP
- Exposed Jarvis resources (workspace state, files, directories) via MCP

### Tool Integration
- Implemented search tool for web search functionality
- Implemented execute_python tool for Python code execution
- Implemented execute_bash tool for Bash/PowerShell code execution

### Resource Integration
- Implemented workspace state resource to get the current state of the workspace
- Implemented file resource to read files in the workspace
- Implemented directory resource to list directory contents in the workspace

### Documentation
- Updated README.md with information about the MCP integration
- Added setup instructions for running the MCP server

### Testing
- Added test script for verifying the MCP integration

## Future Work
- Enhance the MCP server with more tools and resources
- Implement authentication and authorization for the MCP server
- Integrate with more LLM applications
