#!/usr/bin/env python3
"""
Tool Registry module for Jarvis.

This module provides a registry for tools that can be used by Jarvis.
"""

import inspect
from typing import Dict, List, Any, Optional, Callable, Set, Tuple

class ToolRegistry:
    """Registry for tools that can be used by Jarvis."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.tool_categories: Dict[str, List[str]] = {}
        self.required_tools: Set[str] = set()
    
    def register_tool(self, name: str, tool_function: Callable, description: str, 
                     category: str = "general", required: bool = False) -> None:
        """Register a new tool.
        
        Args:
            name: The name of the tool.
            tool_function: The function that implements the tool.
            description: A description of the tool.
            category: The category of the tool.
            required: Whether the tool is required for Jarvis to function.
        """
        # Get the function signature
        signature = inspect.signature(tool_function)
        parameters = []
        
        for param_name, param in signature.parameters.items():
            # Skip 'self' parameter for methods
            if param_name == 'self':
                continue
            
            param_info = {
                "name": param_name,
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                "default": None if param.default == inspect.Parameter.empty else param.default,
                "required": param.default == inspect.Parameter.empty
            }
            parameters.append(param_info)
        
        # Get the return type
        return_type = str(signature.return_annotation) if signature.return_annotation != inspect.Signature.empty else "Any"
        
        # Register the tool
        self.tools[name] = {
            "function": tool_function,
            "description": description,
            "category": category,
            "parameters": parameters,
            "return_type": return_type,
            "required": required
        }
        
        # Add to category
        if category not in self.tool_categories:
            self.tool_categories[category] = []
        self.tool_categories[category].append(name)
        
        # Add to required tools if necessary
        if required:
            self.required_tools.add(name)
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool by name.
        
        Args:
            name: The name of the tool.
            
        Returns:
            The tool function, or None if the tool does not exist.
        """
        tool = self.tools.get(name)
        if tool:
            return tool["function"]
        return None
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a tool.
        
        Args:
            name: The name of the tool.
            
        Returns:
            Information about the tool, or None if the tool does not exist.
        """
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """List available tools, optionally filtered by category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            A dictionary of tool names to tool information.
        """
        if category:
            return {name: self.tools[name] for name in self.tool_categories.get(category, [])}
        return self.tools
    
    def get_tool_descriptions(self, category: Optional[str] = None) -> str:
        """Get tool descriptions for prompting the LLM.
        
        Args:
            category: The category to filter by.
            
        Returns:
            A string containing tool descriptions.
        """
        descriptions = []
        tools = self.list_tools(category)
        
        for name, tool_info in tools.items():
            # Skip the function itself
            tool_info_copy = tool_info.copy()
            tool_info_copy.pop("function", None)
            
            # Format the description
            description = f"Tool: {name}\n"
            description += f"Description: {tool_info['description']}\n"
            description += f"Category: {tool_info['category']}\n"
            
            # Format the parameters
            if tool_info["parameters"]:
                description += "Parameters:\n"
                for param in tool_info["parameters"]:
                    default_str = f" (default: {param['default']})" if param["default"] is not None else ""
                    required_str = " (required)" if param["required"] else ""
                    description += f"  - {param['name']}: {param['type']}{default_str}{required_str}\n"
            
            # Format the return type
            description += f"Returns: {tool_info['return_type']}\n"
            
            descriptions.append(description)
        
        return "\n".join(descriptions)
    
    def get_required_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get the required tools.
        
        Returns:
            A dictionary of required tool names to tool information.
        """
        return {name: self.tools[name] for name in self.required_tools}
    
    def call_tool(self, name: str, **kwargs) -> Any:
        """Call a tool by name.
        
        Args:
            name: The name of the tool.
            **kwargs: The arguments to pass to the tool.
            
        Returns:
            The result of calling the tool.
            
        Raises:
            ValueError: If the tool does not exist.
            TypeError: If the arguments are invalid.
        """
        tool_function = self.get_tool(name)
        if not tool_function:
            raise ValueError(f"Tool '{name}' does not exist.")
        
        try:
            return tool_function(**kwargs)
        except TypeError as e:
            # Get the tool info
            tool_info = self.get_tool_info(name)
            
            # Format the expected parameters
            expected_params = []
            for param in tool_info["parameters"]:
                default_str = f" (default: {param['default']})" if param["default"] is not None else ""
                required_str = " (required)" if param["required"] else ""
                expected_params.append(f"{param['name']}: {param['type']}{default_str}{required_str}")
            
            # Format the provided parameters
            provided_params = [f"{key}: {type(value).__name__}" for key, value in kwargs.items()]
            
            # Raise a more informative error
            raise TypeError(f"Invalid arguments for tool '{name}'.\n"
                           f"Expected: {', '.join(expected_params)}\n"
                           f"Provided: {', '.join(provided_params)}\n"
                           f"Original error: {str(e)}")
    
    def register_tools_from_module(self, module, category: str = "general") -> None:
        """Register all tools from a module.
        
        Args:
            module: The module to register tools from.
            category: The category to register the tools under.
        """
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, "_jarvis_tool"):
                tool_info = getattr(obj, "_jarvis_tool")
                self.register_tool(
                    name=tool_info.get("name", name),
                    tool_function=obj,
                    description=tool_info.get("description", ""),
                    category=tool_info.get("category", category),
                    required=tool_info.get("required", False)
                )


def tool(name: Optional[str] = None, description: str = "", category: str = "general", required: bool = False):
    """Decorator to mark a function as a Jarvis tool.
    
    Args:
        name: The name of the tool. If not provided, the function name will be used.
        description: A description of the tool.
        category: The category of the tool.
        required: Whether the tool is required for Jarvis to function.
        
    Returns:
        The decorated function.
    """
    def decorator(func):
        func._jarvis_tool = {
            "name": name or func.__name__,
            "description": description,
            "category": category,
            "required": required
        }
        return func
    return decorator


# Global tool registry
_registry = None

def get_registry() -> ToolRegistry:
    """Get the global tool registry.
    
    Returns:
        The global tool registry.
    """
    global _registry
    
    if _registry is None:
        _registry = ToolRegistry()
    
    return _registry
