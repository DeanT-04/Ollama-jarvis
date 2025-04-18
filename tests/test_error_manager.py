#!/usr/bin/env python3
"""
Tests for the error manager module.
"""

import unittest
from unittest.mock import patch

from jarvis.core.error_manager import ErrorManager

class TestErrorManager(unittest.TestCase):
    """Test cases for the error manager module."""

    def setUp(self):
        """Set up the test environment."""
        self.error_manager = ErrorManager()

    def test_handle_import_error(self):
        """Test handling an import error."""
        # Create an import error
        try:
            import non_existent_module
        except ImportError as e:
            error = e

        # Handle the error
        context = {"code": "import non_existent_module", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "missing_package")
        self.assertEqual(result["error_type"], "ModuleNotFoundError")
        self.assertIn("non_existent_module", result["error_message"])
        self.assertIn("non_existent_module", result["suggestion"])
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_syntax_error(self):
        """Test handling a syntax error."""
        # Create a syntax error
        try:
            eval("print('Hello, world!'")
        except SyntaxError as e:
            error = e

        # Handle the error
        context = {"code": "print('Hello, world!'", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "syntax_error")
        self.assertEqual(result["error_type"], "SyntaxError")
        self.assertIn("syntax", result["suggestion"].lower())
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_name_error(self):
        """Test handling a name error."""
        # Create a name error
        try:
            undefined_variable
        except NameError as e:
            error = e

        # Handle the error
        context = {"code": "print(undefined_variable)", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "undefined_variable")
        self.assertEqual(result["error_type"], "NameError")
        self.assertIn("undefined_variable", result["suggestion"])
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_type_error(self):
        """Test handling a type error."""
        # Create a type error
        try:
            "string" + 123
        except TypeError as e:
            error = e

        # Handle the error
        context = {"code": "result = 'string' + 123", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "type_error")
        self.assertEqual(result["error_type"], "TypeError")
        self.assertIn("type", result["suggestion"].lower())
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_index_error(self):
        """Test handling an index error."""
        # Create an index error
        try:
            [1, 2, 3][10]
        except IndexError as e:
            error = e

        # Handle the error
        context = {"code": "numbers = [1, 2, 3]\nprint(numbers[10])", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "index_out_of_range")
        self.assertEqual(result["error_type"], "IndexError")
        self.assertIn("index", result["suggestion"].lower())
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_key_error(self):
        """Test handling a key error."""
        # Create a key error
        try:
            {"a": 1}["b"]
        except KeyError as e:
            error = e

        # Handle the error
        context = {"code": "data = {'a': 1}\nprint(data['b'])", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "key_error")
        self.assertEqual(result["error_type"], "KeyError")
        self.assertIn("key", result["suggestion"].lower())
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_file_not_found_error(self):
        """Test handling a file not found error."""
        # Create a file not found error
        try:
            open("non_existent_file.txt")
        except FileNotFoundError as e:
            error = e

        # Handle the error
        context = {"code": "with open('non_existent_file.txt') as f:\n    print(f.read())", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "file_not_found")
        self.assertEqual(result["error_type"], "FileNotFoundError")
        self.assertIn("file", result["suggestion"].lower())
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_zero_division_error(self):
        """Test handling a zero division error."""
        # Create a zero division error
        try:
            1 / 0
        except ZeroDivisionError as e:
            error = e

        # Handle the error
        context = {"code": "result = 1 / 0", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "division_by_zero")
        self.assertEqual(result["error_type"], "ZeroDivisionError")
        self.assertIn("zero", result["suggestion"].lower())
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_value_error(self):
        """Test handling a value error."""
        # Create a value error
        try:
            int("not a number")
        except ValueError as e:
            error = e

        # Handle the error
        context = {"code": "number = int('not a number')", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "value_error")
        self.assertEqual(result["error_type"], "ValueError")
        self.assertIn("value", result["suggestion"].lower())
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_handle_unknown_error(self):
        """Test handling an unknown error."""
        # Create a custom error
        class CustomError(Exception):
            pass

        error = CustomError("This is a custom error")

        # Handle the error
        context = {"code": "# Some code that raises a custom error", "language": "python"}
        result = self.error_manager.handle_error(error, context)

        # Check the result
        self.assertEqual(result["strategy"], "default")
        self.assertEqual(result["error_type"], "CustomError")
        self.assertIn("error", result["suggestion"].lower())
        self.assertEqual(result["updated_code"], context["code"])
        self.assertFalse(result["fixed"])

    def test_get_error_history(self):
        """Test getting the error history."""
        # Create and handle some errors
        for i in range(5):
            error = ValueError(f"Test error {i}")
            context = {"code": f"# Code that raises error {i}", "language": "python"}
            self.error_manager.handle_error(error, context)

        # Get the error history
        history = self.error_manager.get_error_history()

        # Check the history
        self.assertEqual(len(history), 5)
        for i, entry in enumerate(history):
            self.assertEqual(entry["error_type"], "ValueError")
            self.assertEqual(entry["error_message"], f"Test error {i}")
            self.assertEqual(entry["context"]["code"], f"# Code that raises error {i}")

        # Get a limited history
        limited_history = self.error_manager.get_error_history(limit=2)

        # Check the limited history
        self.assertEqual(len(limited_history), 2)
        self.assertEqual(limited_history[0]["error_message"], "Test error 3")
        self.assertEqual(limited_history[1]["error_message"], "Test error 4")

    def test_clear_error_history(self):
        """Test clearing the error history."""
        # Create and handle some errors
        for i in range(3):
            error = ValueError(f"Test error {i}")
            context = {"code": f"# Code that raises error {i}", "language": "python"}
            self.error_manager.handle_error(error, context)

        # Check that the history has entries
        self.assertEqual(len(self.error_manager.get_error_history()), 3)

        # Clear the history
        self.error_manager.clear_error_history()

        # Check that the history is empty
        self.assertEqual(len(self.error_manager.get_error_history()), 0)

if __name__ == "__main__":
    unittest.main()
