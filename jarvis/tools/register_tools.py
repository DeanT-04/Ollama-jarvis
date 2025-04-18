#!/usr/bin/env python3
"""
Tool registration for Jarvis.

This module registers all available tools with the Jarvis tool registry.
"""

from jarvis.core.tool_registry import get_registry
from jarvis.tools import search_tools, agent_tools

def register_all_tools():
    """Register all available tools with the Jarvis tool registry."""
    registry = get_registry()
    
    # Register search tools
    registry.register_tools_from_module(search_tools, category="search")
    
    # Register agent tools
    registry.register_tools_from_module(agent_tools, category="agent")
    
    print(f"Registered {len(registry.tools)} tools in {len(registry.tool_categories)} categories.")
    
    # Print the registered tools by category
    for category, tools in registry.tool_categories.items():
        print(f"Category '{category}': {len(tools)} tools")
        for tool_name in tools:
            print(f"  - {tool_name}")

if __name__ == "__main__":
    register_all_tools()
