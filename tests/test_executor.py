#!/usr/bin/env python3
"""
Tests for the executor module.
"""

import unittest
from unittest.mock import patch, MagicMock

from jarvis.core.executor import (
    get_sandbox,
    get_error_manager,
    execute_code,
    execute_code_with_error_handling,
    get_supported_languages,
    get_error_history,
    clear_error_history
)

class TestExecutor(unittest.TestCase):
    """Test cases for the executor module."""

    def setUp(self):
        """Set up the test environment."""
        # Reset the global instances
        import jarvis.core.executor
        jarvis.core.executor._sandbox = None
        jarvis.core.executor._error_manager = None

        # Patch the Sandbox class
        self.sandbox_patcher = patch("jarvis.core.executor.Sandbox")
        self.mock_sandbox_class = self.sandbox_patcher.start()

        # Configure the mock Sandbox instance
        self.mock_sandbox_instance = MagicMock()
        self.mock_sandbox_class.return_value = self.mock_sandbox_instance

        # Configure the mock execute_code method
        self.mock_sandbox_instance.execute_code.return_value = ("Hello, world!", "", 0)

        # Configure the mock get_supported_languages method
        self.mock_sandbox_instance.get_supported_languages.return_value = ["python", "bash", "javascript"]

        # Patch the ErrorManager class
        self.error_manager_patcher = patch("jarvis.core.executor.ErrorManager")
        self.mock_error_manager_class = self.error_manager_patcher.start()

        # Configure the mock ErrorManager instance
        self.mock_error_manager_instance = MagicMock()
        self.mock_error_manager_class.return_value = self.mock_error_manager_instance

        # Configure the mock handle_error method
        self.mock_error_manager_instance.handle_error.return_value = {
            "strategy": "test_strategy",
            "error_type": "TestError",
            "error_message": "Test error message",
            "suggestion": "Test suggestion",
            "updated_code": "# Updated code",
            "fixed": False
        }

        # Configure the mock get_error_history method
        self.mock_error_manager_instance.get_error_history.return_value = [
            {
                "error_type": "TestError",
                "error_message": "Test error message",
                "error_traceback": "Test traceback",
                "context": {"code": "# Test code"},
                "timestamp": 123456789.0
            }
        ]

    def tearDown(self):
        """Clean up after the tests."""
        # Stop the patchers
        self.sandbox_patcher.stop()
        self.error_manager_patcher.stop()

    def test_get_sandbox(self):
        """Test getting the sandbox instance."""
        # Get the sandbox instance
        sandbox = get_sandbox()

        # Check that the Sandbox class was called
        self.mock_sandbox_class.assert_called_once()

        # Check that the sandbox instance is the mock instance
        self.assertEqual(sandbox, self.mock_sandbox_instance)

        # Get the sandbox instance again
        sandbox2 = get_sandbox()

        # Check that the Sandbox class was not called again
        self.mock_sandbox_class.assert_called_once()

        # Check that the sandbox instance is the same
        self.assertEqual(sandbox2, sandbox)

    def test_get_error_manager(self):
        """Test getting the error manager instance."""
        # Get the error manager instance
        error_manager = get_error_manager()

        # Check that the ErrorManager class was called
        self.mock_error_manager_class.assert_called_once()

        # Check that the error manager instance is the mock instance
        self.assertEqual(error_manager, self.mock_error_manager_instance)

        # Get the error manager instance again
        error_manager2 = get_error_manager()

        # Check that the ErrorManager class was not called again
        self.mock_error_manager_class.assert_called_once()

        # Check that the error manager instance is the same
        self.assertEqual(error_manager2, error_manager)

    def test_execute_code(self):
        """Test executing code."""
        # Execute some code
        stdout, stderr, return_code = execute_code("print('Hello, world!')", "python")

        # Check that the sandbox's execute_code method was called
        self.mock_sandbox_instance.execute_code.assert_called_once_with("print('Hello, world!')", "python")

        # Check the return values
        self.assertEqual(stdout, "Hello, world!")
        self.assertEqual(stderr, "")
        self.assertEqual(return_code, 0)

    def test_execute_code_with_error_handling_success(self):
        """Test executing code with error handling (success case)."""
        # Configure the mock execute_code method to return success
        self.mock_sandbox_instance.execute_code.return_value = ("Hello, world!", "", 0)

        # Execute some code with error handling
        result = execute_code_with_error_handling("print('Hello, world!')", "python")

        # Check that the sandbox's execute_code method was called
        self.mock_sandbox_instance.execute_code.assert_called_once_with("print('Hello, world!')", "python")

        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(result["stdout"], "Hello, world!")
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["return_code"], 0)
        self.assertFalse(result["error_handled"])
        self.assertIsNone(result["error_info"])

    def test_execute_code_with_error_handling_failure(self):
        """Test executing code with error handling (failure case)."""
        # Configure the mock execute_code method to return failure
        self.mock_sandbox_instance.execute_code.return_value = ("", "NameError: name 'undefined_variable' is not defined", 1)

        # Execute some code with error handling
        result = execute_code_with_error_handling("print(undefined_variable)", "python")

        # Check that the sandbox's execute_code method was called
        self.mock_sandbox_instance.execute_code.assert_called_once_with("print(undefined_variable)", "python")

        # Check that the error manager's handle_error method was called
        self.mock_error_manager_instance.handle_error.assert_called_once()

        # Check the result
        self.assertFalse(result["success"])
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"], "NameError: name 'undefined_variable' is not defined")
        self.assertEqual(result["return_code"], 1)
        self.assertTrue(result["error_handled"])
        self.assertEqual(result["error_info"]["strategy"], "test_strategy")
        self.assertEqual(result["error_info"]["error_type"], "TestError")
        self.assertEqual(result["error_info"]["error_message"], "Test error message")
        self.assertEqual(result["error_info"]["suggestion"], "Test suggestion")
        self.assertEqual(result["error_info"]["updated_code"], "# Updated code")
        self.assertFalse(result["error_info"]["fixed"])

    def test_execute_code_with_error_handling_exception(self):
        """Test executing code with error handling (exception case)."""
        # Configure the mock execute_code method to raise an exception
        self.mock_sandbox_instance.execute_code.side_effect = Exception("Test exception")

        # Execute some code with error handling
        result = execute_code_with_error_handling("print('Hello, world!')", "python")

        # Check that the sandbox's execute_code method was called
        self.mock_sandbox_instance.execute_code.assert_called_once_with("print('Hello, world!')", "python")

        # Check that the error manager's handle_error method was called
        self.mock_error_manager_instance.handle_error.assert_called_once()

        # Check the result
        self.assertFalse(result["success"])
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"], "Test exception")
        self.assertEqual(result["return_code"], 1)
        self.assertTrue(result["error_handled"])
        self.assertEqual(result["error_info"]["strategy"], "test_strategy")
        self.assertEqual(result["error_info"]["error_type"], "TestError")
        self.assertEqual(result["error_info"]["error_message"], "Test error message")
        self.assertEqual(result["error_info"]["suggestion"], "Test suggestion")
        self.assertEqual(result["error_info"]["updated_code"], "# Updated code")
        self.assertFalse(result["error_info"]["fixed"])

    def test_get_supported_languages(self):
        """Test getting the supported languages."""
        # Get the supported languages
        languages = get_supported_languages()

        # Check that the sandbox's get_supported_languages method was called
        self.mock_sandbox_instance.get_supported_languages.assert_called_once()

        # Check the return value
        self.assertEqual(languages, ["python", "bash", "javascript"])

    def test_get_error_history(self):
        """Test getting the error history."""
        # Get the error history
        history = get_error_history()

        # Check that the error manager's get_error_history method was called
        self.mock_error_manager_instance.get_error_history.assert_called_once_with(None)

        # Check the return value
        self.assertEqual(history, [
            {
                "error_type": "TestError",
                "error_message": "Test error message",
                "error_traceback": "Test traceback",
                "context": {"code": "# Test code"},
                "timestamp": 123456789.0
            }
        ])

        # Get a limited error history
        history = get_error_history(limit=5)

        # Check that the error manager's get_error_history method was called with the limit
        self.mock_error_manager_instance.get_error_history.assert_called_with(5)

    def test_clear_error_history(self):
        """Test clearing the error history."""
        # Clear the error history
        clear_error_history()

        # Check that the error manager's clear_error_history method was called
        self.mock_error_manager_instance.clear_error_history.assert_called_once()

if __name__ == "__main__":
    unittest.main()
