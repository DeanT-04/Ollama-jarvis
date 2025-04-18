#!/usr/bin/env python3
"""
Test script for the MCP integration in Jarvis CLI.

This script tests the basic functionality of the MCP integration,
including tools and resources.
"""

from mcp_tools import JarvisMCPServer

def main():
    """Main function to test the MCP integration."""
    print("Testing MCP integration...")
    
    # Create the MCP server
    server = JarvisMCPServer("jarvis-test")
    
    # Print the available tools and resources
    print("\nAvailable tools:")
    for tool in server.mcp.tools:
        print(f"- {tool.__name__}: {tool.__doc__}")
    
    print("\nAvailable resources:")
    for resource in server.mcp.resources:
        print(f"- {resource.pattern}: {resource.handler.__doc__}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
