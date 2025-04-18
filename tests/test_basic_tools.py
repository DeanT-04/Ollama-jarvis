#!/usr/bin/env python3
"""
Tests for the basic tools module.
"""

import os
import json
import unittest
import subprocess
from unittest.mock import patch, MagicMock

from jarvis.tools.basic_tools import (
    get_datetime,
    get_system_info,
    get_environment_variables,
    list_files,
    read_file,
    write_file,
    delete_file,
    create_directory,
    run_shell_command,
    parse_json,
    stringify_json
)

class TestBasicTools(unittest.TestCase):
    """Test cases for the basic tools module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for testing
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_workspace")
        os.makedirs(self.test_dir, exist_ok=True)

        # Create a test file
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file, "w") as f:
            f.write("Test content")

        # Patch the get_config function
        self.get_config_patcher = patch("jarvis.tools.basic_tools.get_config")
        self.mock_get_config = self.get_config_patcher.start()
        self.mock_get_config.return_value = self.test_dir

    def tearDown(self):
        """Clean up after the tests."""
        # Stop the patcher
        self.get_config_patcher.stop()

        # Remove the test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        # Remove the test directory if it exists
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_get_datetime(self):
        """Test getting the current date and time."""
        # Get the current date and time
        result = get_datetime()

        # Check that the result has the expected keys
        self.assertIn("iso", result)
        self.assertIn("year", result)
        self.assertIn("month", result)
        self.assertIn("day", result)
        self.assertIn("hour", result)
        self.assertIn("minute", result)
        self.assertIn("second", result)
        self.assertIn("microsecond", result)
        self.assertIn("timestamp", result)
        self.assertIn("timezone", result)

    def test_get_system_info(self):
        """Test getting system information."""
        # Get the system information
        result = get_system_info()

        # Check that the result has the expected keys
        self.assertIn("platform", result)
        self.assertIn("system", result)
        self.assertIn("release", result)
        self.assertIn("version", result)
        self.assertIn("architecture", result)
        self.assertIn("machine", result)
        self.assertIn("processor", result)
        self.assertIn("python_version", result)
        self.assertIn("python_implementation", result)
        self.assertIn("python_compiler", result)

    def test_get_environment_variables(self):
        """Test getting environment variables."""
        # Get all environment variables
        result = get_environment_variables()

        # Check that the result is a dictionary
        self.assertIsInstance(result, dict)

        # Get specific environment variables
        result = get_environment_variables(variables=["PATH"])

        # Check that the result contains the specified variables
        self.assertIn("PATH", result)

    def test_list_files(self):
        """Test listing files."""
        # List files in the test directory
        result = list_files(self.test_dir)

        # Check that the result contains the test file
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "test_file.txt")
        self.assertEqual(result[0]["type"], "file")

        # List files recursively
        result = list_files(self.test_dir, recursive=True)

        # Check that the result contains the test file
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "test_file.txt")

        # List files in a non-existent directory
        result = list_files("non_existent_directory")

        # Check that the result is empty
        self.assertEqual(result, [])

        # List files in a directory outside the workspace
        self.mock_get_config.return_value = "/workspace"
        result = list_files("/outside_workspace")

        # Check that the result is empty
        self.assertEqual(result, [])

    def test_read_file(self):
        """Test reading a file."""
        # Read the test file
        result = read_file(self.test_file)

        # Check that the result is successful
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "Test content")
        self.assertEqual(result["info"]["name"], "test_file.txt")

        # Read a non-existent file
        result = read_file("non_existent_file.txt")

        # Check that the result is not successful
        self.assertFalse(result["success"])
        self.assertIn("does not exist", result["error"])

        # Read a file outside the workspace
        self.mock_get_config.return_value = "/workspace"
        result = read_file("/outside_workspace/file.txt")

        # Check that the result is not successful
        self.assertFalse(result["success"])

        # Reset the mock_get_config to return the test_dir
        self.mock_get_config.return_value = self.test_dir

        # Read a directory
        result = read_file(self.test_dir)

        # Check that the result is not successful
        self.assertFalse(result["success"])

    def test_write_file(self):
        """Test writing to a file."""
        # Write to a new file
        new_file = os.path.join(self.test_dir, "new_file.txt")
        result = write_file(new_file, "New content")

        # Check that the result is successful
        self.assertTrue(result["success"])
        self.assertIn("written successfully", result["message"])
        self.assertEqual(result["info"]["name"], "new_file.txt")

        # Check that the file was created with the correct content
        with open(new_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "New content")

        # Append to the file
        result = write_file(new_file, " Appended content", append=True)

        # Check that the result is successful
        self.assertTrue(result["success"])

        # Check that the content was appended
        with open(new_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "New content Appended content")

        # Write to a file outside the workspace
        self.mock_get_config.return_value = "/workspace"
        result = write_file("/outside_workspace/file.txt", "Content")

        # Check that the result is not successful
        self.assertFalse(result["success"])
        self.assertIn("outside the workspace", result["error"])

        # Clean up
        if os.path.exists(new_file):
            os.remove(new_file)

    def test_delete_file(self):
        """Test deleting a file."""
        # Create a file to delete
        file_to_delete = os.path.join(self.test_dir, "file_to_delete.txt")
        with open(file_to_delete, "w") as f:
            f.write("Content to delete")

        # Delete the file
        result = delete_file(file_to_delete)

        # Check that the result is successful
        self.assertTrue(result["success"])
        self.assertIn("deleted successfully", result["message"])

        # Check that the file was deleted
        self.assertFalse(os.path.exists(file_to_delete))

        # Delete a non-existent file
        result = delete_file("non_existent_file.txt")

        # Check that the result is not successful
        self.assertFalse(result["success"])
        self.assertIn("does not exist", result["error"])

        # Delete a file outside the workspace
        self.mock_get_config.return_value = "/workspace"
        result = delete_file("/outside_workspace/file.txt")

        # Check that the result is not successful
        self.assertFalse(result["success"])

    def test_create_directory(self):
        """Test creating a directory."""
        # Create a new directory
        new_dir = os.path.join(self.test_dir, "new_directory")
        result = create_directory(new_dir)

        # Check that the result is successful
        self.assertTrue(result["success"])
        self.assertIn("created successfully", result["message"])
        self.assertEqual(result["info"]["name"], "new_directory")

        # Check that the directory was created
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))

        # Create a directory outside the workspace
        self.mock_get_config.return_value = "/workspace"
        result = create_directory("/outside_workspace/directory")

        # Check that the result is not successful
        self.assertFalse(result["success"])
        self.assertIn("outside the workspace", result["error"])

        # Clean up
        if os.path.exists(new_dir):
            os.rmdir(new_dir)

    def test_run_shell_command(self):
        """Test running a shell command."""
        # Patch the subprocess.Popen function
        with patch("jarvis.tools.basic_tools.subprocess.Popen") as mock_popen:
            # Configure the mock process
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"stdout", b"stderr")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            # Run a command
            result = run_shell_command("echo Hello")

            # Check that the result is successful
            self.assertTrue(result["success"])
            self.assertEqual(result["stdout"], "stdout")
            self.assertEqual(result["stderr"], "stderr")
            self.assertEqual(result["returncode"], 0)

            # Check that the subprocess.Popen function was called with the correct arguments
            mock_popen.assert_called_once_with(
                "echo Hello",
                stdout=unittest.mock.ANY,
                stderr=unittest.mock.ANY,
                shell=True,
                cwd=self.test_dir
            )

            # Run a command that times out
            mock_process.communicate.side_effect = subprocess.TimeoutExpired("echo Hello", 30)
            mock_process.communicate.return_value = (b"stdout", b"stderr")

            # Run a command
            result = run_shell_command("echo Hello", timeout=30)

            # Check that the result is not successful
            self.assertFalse(result["success"])
            self.assertIn("timed out", result["error"])

            # Run a dangerous command
            result = run_shell_command("rm -rf /")

            # Check that the result is not successful
            self.assertFalse(result["success"])
            self.assertIn("dangerous command", result["error"])

            # Run a command in high security mode
            self.mock_get_config.side_effect = lambda key, default=None: {
                "WORKSPACE_DIR": self.test_dir,
                "SECURITY_LEVEL": "high"
            }.get(key, default)

            result = run_shell_command("echo Hello")

            # Check that the result is not successful
            self.assertFalse(result["success"])
            self.assertIn("not allowed in high security mode", result["error"])

    def test_parse_json(self):
        """Test parsing JSON."""
        # Parse valid JSON
        result = parse_json('{"key": "value"}')

        # Check that the result is successful
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], {"key": "value"})

        # Parse invalid JSON
        result = parse_json("invalid json")

        # Check that the result is not successful
        self.assertFalse(result["success"])
        self.assertIn("Error parsing JSON", result["error"])

    def test_stringify_json(self):
        """Test stringifying JSON."""
        # Stringify a dictionary
        result = stringify_json({"key": "value"})

        # Check that the result is successful
        self.assertTrue(result["success"])
        self.assertEqual(json.loads(result["json"]), {"key": "value"})

        # Stringify with indentation
        result = stringify_json({"key": "value"}, indent=2)

        # Check that the result is successful
        self.assertTrue(result["success"])
        self.assertIn("  ", result["json"])

        # Stringify an unstringifiable object
        class UnstringifiableObject:
            pass

        result = stringify_json(UnstringifiableObject())

        # Check that the result is not successful
        self.assertFalse(result["success"])
        self.assertIn("Error converting to JSON", result["error"])

if __name__ == "__main__":
    unittest.main()
