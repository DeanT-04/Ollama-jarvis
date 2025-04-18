#!/usr/bin/env python3
"""
Executor module for Jarvis.

This module provides functions for executing code in various languages
using a secure sandbox environment with error handling and recovery.
"""

import traceback
from typing import Tuple, Optional, List, Dict, Any

# Import the sandbox and error manager modules
from jarvis.core.sandbox import Sandbox
from jarvis.core.error_manager import ErrorManager

# Global instances
_sandbox = None
_error_manager = None

def get_sandbox(workspace_dir: Optional[str] = None) -> Sandbox:
    """Get the sandbox instance.

    Args:
        workspace_dir: The workspace directory to execute code in.
            If not provided, the default workspace directory from the configuration will be used.

    Returns:
        The sandbox instance.
    """
    global _sandbox

    if _sandbox is None:
        _sandbox = Sandbox(workspace_dir)

    return _sandbox

def get_error_manager() -> ErrorManager:
    """Get the error manager instance.

    Returns:
        The error manager instance.
    """
    global _error_manager

    if _error_manager is None:
        _error_manager = ErrorManager()

    return _error_manager

def execute_code(code: str, language: str, workspace_dir: Optional[str] = None) -> Tuple[str, str, int]:
    """Execute code in the specified language using the sandbox.

    Args:
        code: The code to execute.
        language: The language of the code.
        workspace_dir: The workspace directory to execute the code in.
            If not provided, the default workspace directory from the configuration will be used.

    Returns:
        A tuple (stdout, stderr, return_code).
    """
    # Get the sandbox instance
    sandbox = get_sandbox(workspace_dir)

    # Execute the code in the sandbox
    return sandbox.execute_code(code, language)

def execute_code_with_error_handling(code: str, language: str, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """Execute code with error handling and recovery.

    Args:
        code: The code to execute.
        language: The language of the code.
        workspace_dir: The workspace directory to execute the code in.
            If not provided, the default workspace directory from the configuration will be used.

    Returns:
        A dictionary containing the execution result and error handling information.
    """
    # Get the sandbox and error manager instances
    sandbox = get_sandbox(workspace_dir)
    error_manager = get_error_manager()

    try:
        # Execute the code in the sandbox
        stdout, stderr, return_code = sandbox.execute_code(code, language)

        # Check if the execution was successful
        if return_code == 0 and not stderr:
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": return_code,
                "error_handled": False,
                "error_info": None
            }

        # If there was an error, handle it
        error_context = {
            "code": code,
            "language": language,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code
        }

        # Create a generic exception with the stderr as the message
        error = Exception(stderr)

        # Handle the error
        error_info = error_manager.handle_error(error, error_context)

        return {
            "success": False,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
            "error_handled": True,
            "error_info": error_info
        }

    except Exception as e:
        # If an exception was raised during execution, handle it
        error_context = {
            "code": code,
            "language": language,
            "exception": str(e),
            "traceback": traceback.format_exc()
        }

        # Handle the error
        error_info = error_manager.handle_error(e, error_context)

        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "return_code": 1,
            "error_handled": True,
            "error_info": error_info
        }

def get_supported_languages() -> List[str]:
    """Get a list of supported languages.

    Returns:
        A list of supported languages.
    """
    # Get the sandbox instance
    sandbox = get_sandbox()

    # Get the supported languages from the sandbox
    return sandbox.get_supported_languages()

def get_error_history(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get the error history.

    Args:
        limit: The maximum number of errors to return.
            If None, all errors are returned.

    Returns:
        A list of error entries.
    """
    # Get the error manager instance
    error_manager = get_error_manager()

    # Get the error history
    return error_manager.get_error_history(limit)

def clear_error_history() -> None:
    """Clear the error history."""
    # Get the error manager instance
    error_manager = get_error_manager()

    # Clear the error history
    error_manager.clear_error_history()
