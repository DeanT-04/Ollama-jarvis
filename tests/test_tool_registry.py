#!/usr/bin/env python3
"""
Tests for the tool registry module.
"""

import unittest
from typing import Dict, List, Any

from jarvis.core.tool_registry import ToolRegistry, tool, get_registry

class TestToolRegistry(unittest.TestCase):
    """Test cases for the tool registry module."""
    
    def setUp(self):
        """Set up the test environment."""
        self.registry = ToolRegistry()
        
        # Define some test tools
        def test_tool1(param1: str, param2: int = 0) -> str:
            """Test tool 1."""
            return f"test_tool1: {param1}, {param2}"
        
        def test_tool2(param1: List[str], param2: Dict[str, Any] = None) -> Dict[str, Any]:
            """Test tool 2."""
            return {"param1": param1, "param2": param2 or {}}
        
        # Register the test tools
        self.registry.register_tool(
            name="test_tool1",
            tool_function=test_tool1,
            description="Test tool 1",
            category="test",
            required=True
        )
        
        self.registry.register_tool(
            name="test_tool2",
            tool_function=test_tool2,
            description="Test tool 2",
            category="test"
        )
        
        # Save the test tools for later use
        self.test_tool1 = test_tool1
        self.test_tool2 = test_tool2
    
    def test_register_tool(self):
        """Test registering a tool."""
        # Check that the tools were registered
        self.assertIn("test_tool1", self.registry.tools)
        self.assertIn("test_tool2", self.registry.tools)
        
        # Check that the tools were added to the correct category
        self.assertIn("test_tool1", self.registry.tool_categories["test"])
        self.assertIn("test_tool2", self.registry.tool_categories["test"])
        
        # Check that the required tool was added to the required tools
        self.assertIn("test_tool1", self.registry.required_tools)
        self.assertNotIn("test_tool2", self.registry.required_tools)
    
    def test_get_tool(self):
        """Test getting a tool."""
        # Get the tools
        tool1 = self.registry.get_tool("test_tool1")
        tool2 = self.registry.get_tool("test_tool2")
        
        # Check that the tools were returned
        self.assertEqual(tool1, self.test_tool1)
        self.assertEqual(tool2, self.test_tool2)
        
        # Check that a non-existent tool returns None
        self.assertIsNone(self.registry.get_tool("non_existent_tool"))
    
    def test_get_tool_info(self):
        """Test getting tool information."""
        # Get the tool info
        tool1_info = self.registry.get_tool_info("test_tool1")
        
        # Check that the tool info was returned
        self.assertEqual(tool1_info["function"], self.test_tool1)
        self.assertEqual(tool1_info["description"], "Test tool 1")
        self.assertEqual(tool1_info["category"], "test")
        self.assertTrue(tool1_info["required"])
        
        # Check the parameters
        self.assertEqual(len(tool1_info["parameters"]), 2)
        self.assertEqual(tool1_info["parameters"][0]["name"], "param1")
        self.assertEqual(tool1_info["parameters"][0]["type"], "<class 'str'>")
        self.assertTrue(tool1_info["parameters"][0]["required"])
        self.assertEqual(tool1_info["parameters"][1]["name"], "param2")
        self.assertEqual(tool1_info["parameters"][1]["type"], "<class 'int'>")
        self.assertFalse(tool1_info["parameters"][1]["required"])
        self.assertEqual(tool1_info["parameters"][1]["default"], 0)
        
        # Check the return type
        self.assertEqual(tool1_info["return_type"], "<class 'str'>")
        
        # Check that a non-existent tool returns None
        self.assertIsNone(self.registry.get_tool_info("non_existent_tool"))
    
    def test_list_tools(self):
        """Test listing tools."""
        # List all tools
        tools = self.registry.list_tools()
        
        # Check that all tools were returned
        self.assertEqual(len(tools), 2)
        self.assertIn("test_tool1", tools)
        self.assertIn("test_tool2", tools)
        
        # List tools by category
        test_tools = self.registry.list_tools(category="test")
        
        # Check that only the test tools were returned
        self.assertEqual(len(test_tools), 2)
        self.assertIn("test_tool1", test_tools)
        self.assertIn("test_tool2", test_tools)
        
        # List tools by a non-existent category
        non_existent_tools = self.registry.list_tools(category="non_existent")
        
        # Check that no tools were returned
        self.assertEqual(len(non_existent_tools), 0)
    
    def test_get_tool_descriptions(self):
        """Test getting tool descriptions."""
        # Get all tool descriptions
        descriptions = self.registry.get_tool_descriptions()
        
        # Check that the descriptions contain the tool names and descriptions
        self.assertIn("Tool: test_tool1", descriptions)
        self.assertIn("Description: Test tool 1", descriptions)
        self.assertIn("Tool: test_tool2", descriptions)
        self.assertIn("Description: Test tool 2", descriptions)
        
        # Get tool descriptions by category
        test_descriptions = self.registry.get_tool_descriptions(category="test")
        
        # Check that only the test tool descriptions were returned
        self.assertIn("Tool: test_tool1", test_descriptions)
        self.assertIn("Tool: test_tool2", test_descriptions)
        
        # Get tool descriptions by a non-existent category
        non_existent_descriptions = self.registry.get_tool_descriptions(category="non_existent")
        
        # Check that no descriptions were returned
        self.assertEqual(non_existent_descriptions, "")
    
    def test_get_required_tools(self):
        """Test getting required tools."""
        # Get the required tools
        required_tools = self.registry.get_required_tools()
        
        # Check that only the required tools were returned
        self.assertEqual(len(required_tools), 1)
        self.assertIn("test_tool1", required_tools)
        self.assertNotIn("test_tool2", required_tools)
    
    def test_call_tool(self):
        """Test calling a tool."""
        # Call the tools
        result1 = self.registry.call_tool("test_tool1", param1="hello")
        result2 = self.registry.call_tool("test_tool2", param1=["a", "b"], param2={"c": "d"})
        
        # Check the results
        self.assertEqual(result1, "test_tool1: hello, 0")
        self.assertEqual(result2, {"param1": ["a", "b"], "param2": {"c": "d"}})
        
        # Check that calling a non-existent tool raises an error
        with self.assertRaises(ValueError):
            self.registry.call_tool("non_existent_tool")
        
        # Check that calling a tool with invalid arguments raises an error
        with self.assertRaises(TypeError):
            self.registry.call_tool("test_tool1", invalid_param="invalid")
    
    def test_tool_decorator(self):
        """Test the tool decorator."""
        # Define a tool using the decorator
        @tool(description="Decorated tool", category="decorated", required=True)
        def decorated_tool(param1: str, param2: int = 0) -> str:
            """Decorated tool."""
            return f"decorated_tool: {param1}, {param2}"
        
        # Check that the tool has the correct attributes
        self.assertTrue(hasattr(decorated_tool, "_jarvis_tool"))
        self.assertEqual(decorated_tool._jarvis_tool["name"], "decorated_tool")
        self.assertEqual(decorated_tool._jarvis_tool["description"], "Decorated tool")
        self.assertEqual(decorated_tool._jarvis_tool["category"], "decorated")
        self.assertTrue(decorated_tool._jarvis_tool["required"])
        
        # Create a module-like object with the decorated tool
        class MockModule:
            pass
        
        mock_module = MockModule()
        mock_module.decorated_tool = decorated_tool
        
        # Register the tools from the mock module
        self.registry.register_tools_from_module(mock_module)
        
        # Check that the tool was registered
        self.assertIn("decorated_tool", self.registry.tools)
        self.assertIn("decorated_tool", self.registry.tool_categories["decorated"])
        self.assertIn("decorated_tool", self.registry.required_tools)
    
    def test_get_registry(self):
        """Test getting the global registry."""
        # Reset the global registry
        import jarvis.core.tool_registry
        jarvis.core.tool_registry._registry = None
        
        # Get the global registry
        registry = get_registry()
        
        # Check that the registry is a ToolRegistry
        self.assertIsInstance(registry, ToolRegistry)
        
        # Get the registry again
        registry2 = get_registry()
        
        # Check that the same registry is returned
        self.assertIs(registry2, registry)

if __name__ == "__main__":
    unittest.main()
