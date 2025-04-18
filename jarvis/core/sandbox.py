#!/usr/bin/env python3
"""
Sandbox module for Jarvis.

This module provides a secure execution environment for running code.
It implements various sandboxing techniques to prevent malicious code execution.
"""

import os
import sys
import tempfile
import subprocess
import platform
import shutil
from typing import Dict, List, Tuple, Any

from jarvis.config import get_config

class Sandbox:
    """Sandbox for executing code securely."""
    
    def __init__(self, workspace_dir: str = None):
        """Initialize the sandbox.
        
        Args:
            workspace_dir: The workspace directory to execute code in.
                If not provided, the default workspace directory from the configuration will be used.
        """
        self.workspace_dir = workspace_dir or get_config("WORKSPACE_DIR")
        self.security_level = get_config("SECURITY_LEVEL", "medium")
        
        # Create the workspace directory if it doesn't exist
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # Check if Docker is available
        self.docker_available = self._check_docker_available()
        
        # Set up the sandbox based on the security level
        if self.security_level == "high" and not self.docker_available:
            print("Warning: High security level requested but Docker is not available.")
            print("Falling back to medium security level.")
            self.security_level = "medium"
        
        print(f"Sandbox initialized with security level: {self.security_level}")
        if self.security_level == "high":
            print("Using Docker for sandboxing.")
    
    def execute_code(self, code: str, language: str) -> Tuple[str, str, int]:
        """Execute code in the sandbox.
        
        Args:
            code: The code to execute.
            language: The language of the code.
            
        Returns:
            A tuple (stdout, stderr, return_code).
        """
        language = language.lower()
        
        # Check if the language is supported
        if language not in self.get_supported_languages():
            return "", f"Unsupported language: {language}", 1
        
        # Execute the code based on the security level
        if self.security_level == "high" and self.docker_available:
            return self._execute_in_docker(code, language)
        else:
            return self._execute_locally(code, language)
    
    def get_supported_languages(self) -> List[str]:
        """Get a list of supported languages.
        
        Returns:
            A list of supported languages.
        """
        languages = ["python", "bash", "javascript"]
        
        # Add aliases
        language_aliases = {
            "py": "python",
            "sh": "bash",
            "shell": "bash",
            "js": "javascript"
        }
        
        # Add aliases to the list
        for alias, lang in language_aliases.items():
            if lang in languages and alias not in languages:
                languages.append(alias)
        
        return languages
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available.
        
        Returns:
            True if Docker is available, False otherwise.
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _execute_locally(self, code: str, language: str) -> Tuple[str, str, int]:
        """Execute code locally with basic sandboxing.
        
        Args:
            code: The code to execute.
            language: The language of the code.
            
        Returns:
            A tuple (stdout, stderr, return_code).
        """
        # Map language aliases to their actual language
        language_map = {
            "python": "python",
            "py": "python",
            "bash": "bash",
            "sh": "bash",
            "shell": "bash",
            "javascript": "javascript",
            "js": "javascript"
        }
        
        # Get the actual language
        actual_language = language_map.get(language, language)
        
        # Execute the code based on the language
        if actual_language == "python":
            return self._execute_python_locally(code)
        elif actual_language == "bash":
            return self._execute_bash_locally(code)
        elif actual_language == "javascript":
            return self._execute_javascript_locally(code)
        else:
            return "", f"Unsupported language: {language}", 1
    
    def _execute_python_locally(self, code: str) -> Tuple[str, str, int]:
        """Execute Python code locally.
        
        Args:
            code: The Python code to execute.
            
        Returns:
            A tuple (stdout, stderr, return_code).
        """
        # Check for potentially dangerous imports
        dangerous_imports = [
            "os.system", "subprocess", "pty", "popen", 
            "exec", "eval", "compile", "__import__", 
            "importlib", "builtins", "globals", "locals"
        ]
        
        for dangerous_import in dangerous_imports:
            if dangerous_import in code:
                return "", f"Error: Use of potentially dangerous function '{dangerous_import}' is not allowed.", 1
        
        try:
            # Create a temporary script file
            with tempfile.NamedTemporaryFile(dir=self.workspace_dir, suffix='.py', delete=False) as f:
                f.write(code.encode())
                script_path = f.name
            
            # Set resource limits
            if platform.system() != "Windows":
                # On Unix-like systems, use ulimit
                cmd_prefix = "ulimit -t 30 -v 512000 && "
            else:
                # On Windows, we can't easily set resource limits
                cmd_prefix = ""
            
            # Execute the script with restricted permissions
            process = subprocess.Popen(
                [cmd_prefix + sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.workspace_dir,
                shell=(platform.system() == "Windows")
            )
            
            # Set a timeout
            try:
                stdout, stderr = process.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return stdout.decode() if stdout else "", "Execution timed out after 30 seconds.", 1
            
            # Clean up
            os.unlink(script_path)
            
            return stdout.decode() if stdout else "", stderr.decode() if stderr else "", process.returncode
        except Exception as e:
            return "", str(e), 1
    
    def _execute_bash_locally(self, code: str) -> Tuple[str, str, int]:
        """Execute Bash code locally.
        
        Args:
            code: The Bash code to execute.
            
        Returns:
            A tuple (stdout, stderr, return_code).
        """
        # Check for potentially dangerous commands
        dangerous_commands = [
            "rm -rf", "mkfs", "dd", ">", ">>", 
            "chmod", "chown", "sudo", "su", 
            "apt", "yum", "dnf", "pacman", "brew"
        ]
        
        for dangerous_command in dangerous_commands:
            if dangerous_command in code:
                return "", f"Error: Use of potentially dangerous command '{dangerous_command}' is not allowed.", 1
        
        try:
            # Create a temporary script file
            with tempfile.NamedTemporaryFile(dir=self.workspace_dir, suffix='.sh', delete=False) as f:
                f.write(code.encode())
                script_path = f.name
            
            # Make the script executable
            os.chmod(script_path, 0o755)
            
            # Execute the script
            if platform.system() == "Windows":
                # Use PowerShell on Windows
                process = subprocess.Popen(
                    ['powershell', '-Command', f"Get-Content '{script_path}' | powershell -"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.workspace_dir
                )
            else:
                # Use Bash on Unix-like systems
                process = subprocess.Popen(
                    ['/bin/bash', script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.workspace_dir
                )
            
            # Set a timeout
            try:
                stdout, stderr = process.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return stdout.decode() if stdout else "", "Execution timed out after 30 seconds.", 1
            
            # Clean up
            os.unlink(script_path)
            
            return stdout.decode() if stdout else "", stderr.decode() if stderr else "", process.returncode
        except Exception as e:
            return "", str(e), 1
    
    def _execute_javascript_locally(self, code: str) -> Tuple[str, str, int]:
        """Execute JavaScript code locally.
        
        Args:
            code: The JavaScript code to execute.
            
        Returns:
            A tuple (stdout, stderr, return_code).
        """
        # Check if Node.js is installed
        try:
            subprocess.run(
                ["node", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            return "", "Error: Node.js is not installed or not in the PATH.", 1
        
        # Check for potentially dangerous operations
        dangerous_operations = [
            "require('child_process')", "require('fs')", 
            "process.exit", "process.env", "process.kill"
        ]
        
        for dangerous_operation in dangerous_operations:
            if dangerous_operation in code:
                return "", f"Error: Use of potentially dangerous operation '{dangerous_operation}' is not allowed.", 1
        
        try:
            # Create a temporary script file
            with tempfile.NamedTemporaryFile(dir=self.workspace_dir, suffix='.js', delete=False) as f:
                f.write(code.encode())
                script_path = f.name
            
            # Execute the script
            process = subprocess.Popen(
                ['node', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.workspace_dir
            )
            
            # Set a timeout
            try:
                stdout, stderr = process.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return stdout.decode() if stdout else "", "Execution timed out after 30 seconds.", 1
            
            # Clean up
            os.unlink(script_path)
            
            return stdout.decode() if stdout else "", stderr.decode() if stderr else "", process.returncode
        except Exception as e:
            return "", str(e), 1
    
    def _execute_in_docker(self, code: str, language: str) -> Tuple[str, str, int]:
        """Execute code in a Docker container.
        
        Args:
            code: The code to execute.
            language: The language of the code.
            
        Returns:
            A tuple (stdout, stderr, return_code).
        """
        # Map languages to Docker images
        language_images = {
            "python": "python:3.9-slim",
            "py": "python:3.9-slim",
            "bash": "bash:5.1",
            "sh": "bash:5.1",
            "shell": "bash:5.1",
            "javascript": "node:16-slim",
            "js": "node:16-slim"
        }
        
        # Map languages to file extensions
        language_extensions = {
            "python": "py",
            "py": "py",
            "bash": "sh",
            "sh": "sh",
            "shell": "sh",
            "javascript": "js",
            "js": "js"
        }
        
        # Map languages to commands
        language_commands = {
            "python": "python",
            "py": "python",
            "bash": "bash",
            "sh": "bash",
            "shell": "bash",
            "javascript": "node",
            "js": "node"
        }
        
        # Get the Docker image, file extension, and command for the language
        image = language_images.get(language)
        extension = language_extensions.get(language)
        command = language_commands.get(language)
        
        if not image or not extension or not command:
            return "", f"Unsupported language for Docker execution: {language}", 1
        
        try:
            # Create a temporary script file
            with tempfile.NamedTemporaryFile(dir=self.workspace_dir, suffix=f'.{extension}', delete=False) as f:
                f.write(code.encode())
                script_path = f.name
                script_name = os.path.basename(script_path)
            
            # Run the code in a Docker container
            docker_cmd = [
                "docker", "run",
                "--rm",                                  # Remove the container after execution
                "--network=none",                        # Disable network access
                "--memory=512m",                         # Limit memory usage
                "--cpus=1",                              # Limit CPU usage
                "--user=nobody",                         # Run as a non-root user
                "--cap-drop=ALL",                        # Drop all capabilities
                "--security-opt=no-new-privileges",      # Prevent privilege escalation
                "-v", f"{os.path.abspath(script_path)}:/app/{script_name}:ro",  # Mount the script as read-only
                "-w", "/app",                            # Set the working directory
                image,                                   # Use the appropriate image
                command, script_name                     # Run the script
            ]
            
            # Execute the Docker command
            process = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Set a timeout
            try:
                stdout, stderr = process.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return stdout.decode() if stdout else "", "Execution timed out after 30 seconds.", 1
            
            # Clean up
            os.unlink(script_path)
            
            return stdout.decode() if stdout else "", stderr.decode() if stderr else "", process.returncode
        except Exception as e:
            return "", str(e), 1
