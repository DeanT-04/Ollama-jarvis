#!/usr/bin/env python3
"""
Tests for the planner module.
"""

import unittest
from unittest.mock import patch, MagicMock

from jarvis.core.planner import Planner

class TestPlanner(unittest.TestCase):
    """Test cases for the planner module."""
    
    def setUp(self):
        """Set up the test environment."""
        # Patch the get_config function
        self.get_config_patcher = patch("jarvis.core.planner.get_config")
        self.mock_get_config = self.get_config_patcher.start()
        self.mock_get_config.return_value = "llama3"
        
        # Patch the OllamaClient class
        self.ollama_client_patcher = patch("jarvis.core.planner.OllamaClient")
        self.mock_ollama_client = self.ollama_client_patcher.start()
        
        # Configure the mock OllamaClient instance
        self.mock_client_instance = MagicMock()
        self.mock_ollama_client.return_value = self.mock_client_instance
        
        # Configure the mock generate method
        self.mock_client_instance.generate.return_value = {
            "response": """
OVERVIEW:
This is a test overview.

STEPS:
1. Step 1 description
   - Substep 1.1
   - Substep 1.2
   CODE: print('Hello, world!')
   EXPECTED OUTCOME: The message "Hello, world!" will be printed to the console.

2. Step 2 description
   - Substep 2.1
   - Substep 2.2
   CODE: echo 'Hello, world!'
   EXPECTED OUTCOME: The message "Hello, world!" will be printed to the console.

CONSIDERATIONS:
- Consideration 1
- Consideration 2
"""
        }
    
    def tearDown(self):
        """Clean up after the tests."""
        # Stop the patchers
        self.get_config_patcher.stop()
        self.ollama_client_patcher.stop()
    
    def test_init(self):
        """Test initializing the planner."""
        planner = Planner()
        
        self.assertEqual(planner.model, "llama3")
        self.assertEqual(planner.client, self.mock_client_instance)
    
    def test_create_plan(self):
        """Test creating a plan."""
        planner = Planner()
        
        task = "Print 'Hello, world!' to the console."
        context = "The user wants to print a greeting message."
        
        plan = planner.create_plan(task, context)
        
        # Check that the generate method was called with the correct arguments
        self.mock_client_instance.generate.assert_called_once()
        args, kwargs = self.mock_client_instance.generate.call_args
        
        # Check that the prompt includes the task and context
        self.assertIn(task, kwargs["prompt"])
        self.assertIn(context, kwargs["prompt"])
        
        # Check that the plan was parsed correctly
        self.assertEqual(plan["overview"], "This is a test overview.")
        self.assertEqual(len(plan["steps"]), 2)
        self.assertEqual(plan["steps"][0]["description"], "Step 1 description")
        self.assertEqual(len(plan["steps"][0]["substeps"]), 2)
        self.assertEqual(plan["steps"][0]["substeps"][0], "Substep 1.1")
        self.assertEqual(plan["steps"][0]["code"], "print('Hello, world!')")
        self.assertEqual(plan["steps"][0]["expected_outcome"], "The message \"Hello, world!\" will be printed to the console.")
        self.assertEqual(len(plan["considerations"]), 2)
        self.assertEqual(plan["considerations"][0], "Consideration 1")
    
    def test_create_planning_prompt(self):
        """Test creating a planning prompt."""
        planner = Planner()
        
        task = "Print 'Hello, world!' to the console."
        context = "The user wants to print a greeting message."
        
        prompt = planner._create_planning_prompt(task, context)
        
        # Check that the prompt includes the task and context
        self.assertIn(task, prompt)
        self.assertIn(context, prompt)
        
        # Check that the prompt includes the expected sections
        self.assertIn("OVERVIEW:", prompt)
        self.assertIn("STEPS:", prompt)
        self.assertIn("CONSIDERATIONS:", prompt)
    
    def test_parse_planning_response(self):
        """Test parsing a planning response."""
        planner = Planner()
        
        response = """
OVERVIEW:
This is a test overview.

STEPS:
1. Step 1 description
   - Substep 1.1
   - Substep 1.2
   CODE: print('Hello, world!')
   EXPECTED OUTCOME: The message "Hello, world!" will be printed to the console.

2. Step 2 description
   - Substep 2.1
   - Substep 2.2
   CODE: echo 'Hello, world!'
   EXPECTED OUTCOME: The message "Hello, world!" will be printed to the console.

CONSIDERATIONS:
- Consideration 1
- Consideration 2
"""
        
        plan = planner._parse_planning_response(response)
        
        # Check that the plan was parsed correctly
        self.assertEqual(plan["overview"], "This is a test overview.")
        self.assertEqual(len(plan["steps"]), 2)
        self.assertEqual(plan["steps"][0]["description"], "Step 1 description")
        self.assertEqual(len(plan["steps"][0]["substeps"]), 2)
        self.assertEqual(plan["steps"][0]["substeps"][0], "Substep 1.1")
        self.assertEqual(plan["steps"][0]["code"], "print('Hello, world!')")
        self.assertEqual(plan["steps"][0]["expected_outcome"], "The message \"Hello, world!\" will be printed to the console.")
        self.assertEqual(len(plan["considerations"]), 2)
        self.assertEqual(plan["considerations"][0], "Consideration 1")
    
    def test_execute_step(self):
        """Test executing a step."""
        planner = Planner()
        
        step = {
            "description": "Print 'Hello, world!' to the console.",
            "substeps": ["Open a terminal", "Type the command"],
            "code": "print('Hello, world!')",
            "expected_outcome": "The message 'Hello, world!' will be printed to the console."
        }
        
        result = planner.execute_step(step)
        
        # Check that the result has the expected structure
        self.assertTrue(result["success"])
        self.assertEqual(result["output"], "Step executed successfully.")
        self.assertEqual(result["error"], "")

if __name__ == "__main__":
    unittest.main()
