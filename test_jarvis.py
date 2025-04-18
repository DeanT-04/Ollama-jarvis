#!/usr/bin/env python3
"""
Test script for Jarvis CLI.

This script tests the basic functionality of the Jarvis CLI,
including code execution and error handling.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from jarvis_cli import (
    Memory,
    extract_code_blocks,
    execute_bash,
    execute_python,
    WORKSPACE_DIR
)


class TestJarvisCLI(unittest.TestCase):
    """Test cases for Jarvis CLI."""

    def setUp(self):
        """Set up the test environment."""
        # Ensure the workspace directory exists
        os.makedirs(WORKSPACE_DIR, exist_ok=True)

    @patch('jarvis_cli.Mem0Memory')
    def test_memory(self, mock_mem0_memory):
        """Test the Memory class."""
        # Create a mock for the mem0 memory
        mock_mem0 = MagicMock()
        mock_mem0_memory.return_value = mock_mem0
        mock_mem0.search.return_value = {"results": [{"memory": "Test memory"}]}

        memory = Memory()

        # Test adding messages
        memory.add_user_message("Hello")
        memory.add_assistant_message("Hi there!")
        memory.add_execution_result("print('test')", "python", "test", "", True)

        # Verify mem0 add was called
        self.assertEqual(mock_mem0.add.call_count, 3)

        # Test getting conversation history
        history = memory.get_conversation_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hi there!")

        # Test getting full history
        full_history = memory.get_full_history()
        self.assertEqual(len(full_history), 3)

        # Test searching memories
        memories = memory.search_memories("test query")
        mock_mem0.search.assert_called_once_with(query="test query", user_id="jarvis_user", limit=5)
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0]["memory"], "Test memory")

    def test_extract_code_blocks(self):
        """Test extracting code blocks from text."""
        text = """
        Here's a Python script:

        ```python
        print("Hello, world!")
        ```

        And here's a Bash script:

        ```bash
        echo "Hello, world!"
        ```
        """

        code_blocks = extract_code_blocks(text)
        self.assertEqual(len(code_blocks), 2)
        self.assertEqual(code_blocks[0][0], "python")
        self.assertEqual(code_blocks[0][1], 'print("Hello, world!")')
        self.assertEqual(code_blocks[1][0], "bash")
        self.assertEqual(code_blocks[1][1], 'echo "Hello, world!"')

    def test_execute_python(self):
        """Test executing Python code."""
        code = 'print("Hello from Python!")'
        stdout, stderr, return_code = execute_python(code)

        self.assertEqual(return_code, 0)
        self.assertEqual(stdout.strip(), "Hello from Python!")
        self.assertEqual(stderr, "")

    def test_execute_python_error(self):
        """Test executing Python code with an error."""
        code = 'print("Hello from Python!"'  # Missing closing parenthesis
        stdout, stderr, return_code = execute_python(code)

        self.assertNotEqual(return_code, 0)
        self.assertNotEqual(stderr, "")

    def test_execute_bash(self):
        """Test executing Bash code."""
        code = 'echo "Hello from Bash!"'
        stdout, stderr, return_code = execute_bash(code)

        self.assertEqual(return_code, 0)
        self.assertEqual(stdout.strip(), "Hello from Bash!")
        self.assertEqual(stderr, "")

    def test_execute_bash_error(self):
        """Test executing Bash code with an error."""
        code = 'cd /nonexistent_directory'
        stdout, stderr, return_code = execute_bash(code)

        self.assertNotEqual(return_code, 0)
        self.assertNotEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
