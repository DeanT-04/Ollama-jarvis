#!/usr/bin/env python3
"""
Tests for the sandbox module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from jarvis.core.sandbox import Sandbox

class TestSandbox(unittest.TestCase):
    """Test cases for the sandbox module."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for testing
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_workspace")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Patch the get_config function to return our test directory
        self.get_config_patcher = patch("jarvis.core.sandbox.get_config")
        self.mock_get_config = self.get_config_patcher.start()
        self.mock_get_config.side_effect = lambda key, default=None: {
            "WORKSPACE_DIR": self.test_dir,
            "SECURITY_LEVEL": "medium"
        }.get(key, default)
        
        # Patch the subprocess.run function
        self.subprocess_run_patcher = patch("jarvis.core.sandbox.subprocess.run")
        self.mock_subprocess_run = self.subprocess_run_patcher.start()
        self.mock_subprocess_run.return_value.returncode = 1  # Docker not available
        
        # Patch the subprocess.Popen function
        self.subprocess_popen_patcher = patch("jarvis.core.sandbox.subprocess.Popen")
        self.mock_subprocess_popen = self.subprocess_popen_patcher.start()
        
        # Configure the mock Popen instance
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"Hello, world!", b"")
        mock_process.returncode = 0
        self.mock_subprocess_popen.return_value = mock_process
    
    def tearDown(self):
        """Clean up after the tests."""
        # Stop the patchers
        self.get_config_patcher.stop()
        self.subprocess_run_patcher.stop()
        self.subprocess_popen_patcher.stop()
        
        # Remove the test directory if it exists
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)
    
    def test_init(self):
        """Test initializing the sandbox."""
        sandbox = Sandbox()
        
        self.assertEqual(sandbox.workspace_dir, self.test_dir)
        self.assertEqual(sandbox.security_level, "medium")
        self.assertFalse(sandbox.docker_available)
    
    def test_get_supported_languages(self):
        """Test getting the supported languages."""
        sandbox = Sandbox()
        
        languages = sandbox.get_supported_languages()
        
        self.assertIn("python", languages)
        self.assertIn("bash", languages)
        self.assertIn("javascript", languages)
        self.assertIn("py", languages)
        self.assertIn("sh", languages)
        self.assertIn("js", languages)
    
    def test_execute_code_python(self):
        """Test executing Python code."""
        sandbox = Sandbox()
        
        code = "print('Hello, world!')"
        language = "python"
        
        stdout, stderr, return_code = sandbox.execute_code(code, language)
        
        self.assertEqual(stdout, "Hello, world!")
        self.assertEqual(stderr, "")
        self.assertEqual(return_code, 0)
        
        # Check that the subprocess.Popen function was called with the correct arguments
        self.mock_subprocess_popen.assert_called_once()
        args, kwargs = self.mock_subprocess_popen.call_args
        
        # Check that the command includes the Python executable
        self.assertTrue(any("python" in str(arg) for arg in args[0]))
        
        # Check that the working directory is set correctly
        self.assertEqual(kwargs["cwd"], self.test_dir)
    
    def test_execute_code_bash(self):
        """Test executing Bash code."""
        sandbox = Sandbox()
        
        code = "echo 'Hello, world!'"
        language = "bash"
        
        stdout, stderr, return_code = sandbox.execute_code(code, language)
        
        self.assertEqual(stdout, "Hello, world!")
        self.assertEqual(stderr, "")
        self.assertEqual(return_code, 0)
        
        # Check that the subprocess.Popen function was called with the correct arguments
        self.mock_subprocess_popen.assert_called_once()
        
        # Reset the mock for the next test
        self.mock_subprocess_popen.reset_mock()
    
    def test_execute_code_javascript(self):
        """Test executing JavaScript code."""
        sandbox = Sandbox()
        
        code = "console.log('Hello, world!')"
        language = "javascript"
        
        # Mock the subprocess.run function to indicate that Node.js is installed
        self.mock_subprocess_run.return_value.returncode = 0
        
        stdout, stderr, return_code = sandbox.execute_code(code, language)
        
        self.assertEqual(stdout, "Hello, world!")
        self.assertEqual(stderr, "")
        self.assertEqual(return_code, 0)
        
        # Check that the subprocess.Popen function was called with the correct arguments
        self.mock_subprocess_popen.assert_called_once()
        args, kwargs = self.mock_subprocess_popen.call_args
        
        # Check that the command includes the Node.js executable
        self.assertTrue(any("node" in str(arg) for arg in args[0]))
        
        # Check that the working directory is set correctly
        self.assertEqual(kwargs["cwd"], self.test_dir)
    
    def test_execute_code_unsupported_language(self):
        """Test executing code in an unsupported language."""
        sandbox = Sandbox()
        
        code = "print('Hello, world!')"
        language = "unsupported"
        
        stdout, stderr, return_code = sandbox.execute_code(code, language)
        
        self.assertEqual(stdout, "")
        self.assertTrue("Unsupported language" in stderr)
        self.assertEqual(return_code, 1)
    
    def test_execute_python_locally_dangerous_imports(self):
        """Test executing Python code with dangerous imports."""
        sandbox = Sandbox()
        
        # Test with os.system
        code = "import os\nos.system('echo Hello, world!')"
        stdout, stderr, return_code = sandbox._execute_python_locally(code)
        
        self.assertEqual(stdout, "")
        self.assertTrue("potentially dangerous function" in stderr)
        self.assertEqual(return_code, 1)
        
        # Test with subprocess
        code = "import subprocess\nsubprocess.run(['echo', 'Hello, world!'])"
        stdout, stderr, return_code = sandbox._execute_python_locally(code)
        
        self.assertEqual(stdout, "")
        self.assertTrue("potentially dangerous function" in stderr)
        self.assertEqual(return_code, 1)
        
        # Test with eval
        code = "eval('print(\"Hello, world!\")')"
        stdout, stderr, return_code = sandbox._execute_python_locally(code)
        
        self.assertEqual(stdout, "")
        self.assertTrue("potentially dangerous function" in stderr)
        self.assertEqual(return_code, 1)
    
    def test_execute_bash_locally_dangerous_commands(self):
        """Test executing Bash code with dangerous commands."""
        sandbox = Sandbox()
        
        # Test with rm -rf
        code = "rm -rf /tmp/test"
        stdout, stderr, return_code = sandbox._execute_bash_locally(code)
        
        self.assertEqual(stdout, "")
        self.assertTrue("potentially dangerous command" in stderr)
        self.assertEqual(return_code, 1)
        
        # Test with sudo
        code = "sudo echo 'Hello, world!'"
        stdout, stderr, return_code = sandbox._execute_bash_locally(code)
        
        self.assertEqual(stdout, "")
        self.assertTrue("potentially dangerous command" in stderr)
        self.assertEqual(return_code, 1)
    
    def test_execute_javascript_locally_dangerous_operations(self):
        """Test executing JavaScript code with dangerous operations."""
        sandbox = Sandbox()
        
        # Mock the subprocess.run function to indicate that Node.js is installed
        self.mock_subprocess_run.return_value.returncode = 0
        
        # Test with require('fs')
        code = "const fs = require('fs');\nfs.readFileSync('/etc/passwd');"
        stdout, stderr, return_code = sandbox._execute_javascript_locally(code)
        
        self.assertEqual(stdout, "")
        self.assertTrue("potentially dangerous operation" in stderr)
        self.assertEqual(return_code, 1)
        
        # Test with process.exit
        code = "process.exit(1);"
        stdout, stderr, return_code = sandbox._execute_javascript_locally(code)
        
        self.assertEqual(stdout, "")
        self.assertTrue("potentially dangerous operation" in stderr)
        self.assertEqual(return_code, 1)

if __name__ == "__main__":
    unittest.main()
