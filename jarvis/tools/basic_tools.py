#!/usr/bin/env python3
"""
Basic tools for Jarvis.

This module provides basic tools that can be used by Jarvis.
"""

import os
import sys
import platform
import datetime
import json
import subprocess
from typing import Dict, List, Any, Optional

from jarvis.core.tool_registry import tool
from jarvis.config import get_config

@tool(description="Get the current date and time.", category="system", required=True)
def get_datetime() -> Dict[str, Any]:
    """Get the current date and time.
    
    Returns:
        A dictionary containing the current date and time information.
    """
    now = datetime.datetime.now()
    
    return {
        "iso": now.isoformat(),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "microsecond": now.microsecond,
        "timestamp": now.timestamp(),
        "timezone": str(datetime.datetime.now().astimezone().tzinfo)
    }

@tool(description="Get information about the system.", category="system", required=True)
def get_system_info() -> Dict[str, Any]:
    """Get information about the system.
    
    Returns:
        A dictionary containing system information.
    """
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_compiler": platform.python_compiler()
    }

@tool(description="Get environment variables.", category="system")
def get_environment_variables(variables: Optional[List[str]] = None) -> Dict[str, str]:
    """Get environment variables.
    
    Args:
        variables: A list of environment variables to get.
            If None, all environment variables are returned.
            
    Returns:
        A dictionary of environment variables.
    """
    if variables:
        return {var: os.environ.get(var, "") for var in variables}
    return dict(os.environ)

@tool(description="List files in a directory.", category="filesystem", required=True)
def list_files(directory: str = ".", recursive: bool = False) -> List[Dict[str, Any]]:
    """List files in a directory.
    
    Args:
        directory: The directory to list files in.
        recursive: Whether to list files recursively.
            
    Returns:
        A list of dictionaries containing file information.
    """
    # Get the workspace directory
    workspace_dir = get_config("WORKSPACE_DIR")
    
    # Resolve the directory path
    if directory == ".":
        directory = workspace_dir
    elif not os.path.isabs(directory):
        directory = os.path.join(workspace_dir, directory)
    
    # Check if the directory exists
    if not os.path.exists(directory):
        return []
    
    # Check if the directory is within the workspace
    if not os.path.abspath(directory).startswith(os.path.abspath(workspace_dir)):
        return []
    
    # List the files
    files = []
    
    if recursive:
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(_get_file_info(file_path, workspace_dir))
    else:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            files.append(_get_file_info(item_path, workspace_dir))
    
    return files

@tool(description="Read a file.", category="filesystem", required=True)
def read_file(file_path: str) -> Dict[str, Any]:
    """Read a file.
    
    Args:
        file_path: The path to the file to read.
            
    Returns:
        A dictionary containing the file content and information.
    """
    # Get the workspace directory
    workspace_dir = get_config("WORKSPACE_DIR")
    
    # Resolve the file path
    if not os.path.isabs(file_path):
        file_path = os.path.join(workspace_dir, file_path)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File {file_path} does not exist."
        }
    
    # Check if the file is within the workspace
    if not os.path.abspath(file_path).startswith(os.path.abspath(workspace_dir)):
        return {
            "success": False,
            "error": f"File {file_path} is outside the workspace."
        }
    
    # Check if the file is a directory
    if os.path.isdir(file_path):
        return {
            "success": False,
            "error": f"{file_path} is a directory, not a file."
        }
    
    # Read the file
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "info": _get_file_info(file_path, workspace_dir)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading file {file_path}: {str(e)}"
        }

@tool(description="Write to a file.", category="filesystem", required=True)
def write_file(file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
    """Write to a file.
    
    Args:
        file_path: The path to the file to write to.
        content: The content to write to the file.
        append: Whether to append to the file instead of overwriting it.
            
    Returns:
        A dictionary containing the result of the operation.
    """
    # Get the workspace directory
    workspace_dir = get_config("WORKSPACE_DIR")
    
    # Resolve the file path
    if not os.path.isabs(file_path):
        file_path = os.path.join(workspace_dir, file_path)
    
    # Check if the file is within the workspace
    if not os.path.abspath(file_path).startswith(os.path.abspath(workspace_dir)):
        return {
            "success": False,
            "error": f"File {file_path} is outside the workspace."
        }
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write to the file
    try:
        mode = 'a' if append else 'w'
        with open(file_path, mode) as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"File {file_path} written successfully.",
            "info": _get_file_info(file_path, workspace_dir)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error writing to file {file_path}: {str(e)}"
        }

@tool(description="Delete a file.", category="filesystem")
def delete_file(file_path: str) -> Dict[str, Any]:
    """Delete a file.
    
    Args:
        file_path: The path to the file to delete.
            
    Returns:
        A dictionary containing the result of the operation.
    """
    # Get the workspace directory
    workspace_dir = get_config("WORKSPACE_DIR")
    
    # Resolve the file path
    if not os.path.isabs(file_path):
        file_path = os.path.join(workspace_dir, file_path)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File {file_path} does not exist."
        }
    
    # Check if the file is within the workspace
    if not os.path.abspath(file_path).startswith(os.path.abspath(workspace_dir)):
        return {
            "success": False,
            "error": f"File {file_path} is outside the workspace."
        }
    
    # Delete the file
    try:
        if os.path.isdir(file_path):
            os.rmdir(file_path)
        else:
            os.remove(file_path)
        
        return {
            "success": True,
            "message": f"File {file_path} deleted successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error deleting file {file_path}: {str(e)}"
        }

@tool(description="Create a directory.", category="filesystem")
def create_directory(directory_path: str) -> Dict[str, Any]:
    """Create a directory.
    
    Args:
        directory_path: The path to the directory to create.
            
    Returns:
        A dictionary containing the result of the operation.
    """
    # Get the workspace directory
    workspace_dir = get_config("WORKSPACE_DIR")
    
    # Resolve the directory path
    if not os.path.isabs(directory_path):
        directory_path = os.path.join(workspace_dir, directory_path)
    
    # Check if the directory is within the workspace
    if not os.path.abspath(directory_path).startswith(os.path.abspath(workspace_dir)):
        return {
            "success": False,
            "error": f"Directory {directory_path} is outside the workspace."
        }
    
    # Create the directory
    try:
        os.makedirs(directory_path, exist_ok=True)
        
        return {
            "success": True,
            "message": f"Directory {directory_path} created successfully.",
            "info": _get_file_info(directory_path, workspace_dir)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating directory {directory_path}: {str(e)}"
        }

@tool(description="Run a shell command.", category="system")
def run_shell_command(command: str, timeout: int = 30) -> Dict[str, Any]:
    """Run a shell command.
    
    Args:
        command: The command to run.
        timeout: The timeout in seconds.
            
    Returns:
        A dictionary containing the result of the operation.
    """
    # Get the workspace directory
    workspace_dir = get_config("WORKSPACE_DIR")
    
    # Check if shell commands are allowed
    security_level = get_config("SECURITY_LEVEL", "medium")
    if security_level == "high":
        return {
            "success": False,
            "error": "Shell commands are not allowed in high security mode."
        }
    
    # Check for potentially dangerous commands
    dangerous_commands = [
        "rm -rf", "mkfs", "dd", ">", ">>", 
        "chmod", "chown", "sudo", "su", 
        "apt", "yum", "dnf", "pacman", "brew"
    ]
    
    for dangerous_command in dangerous_commands:
        if dangerous_command in command:
            return {
                "success": False,
                "error": f"Potentially dangerous command '{dangerous_command}' detected."
            }
    
    # Run the command
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=workspace_dir
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": process.returncode
            }
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds.",
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": -1
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error running command: {str(e)}"
        }

@tool(description="Parse JSON.", category="data", required=True)
def parse_json(json_string: str) -> Dict[str, Any]:
    """Parse a JSON string.
    
    Args:
        json_string: The JSON string to parse.
            
    Returns:
        A dictionary containing the parsed JSON.
    """
    try:
        return {
            "success": True,
            "data": json.loads(json_string)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error parsing JSON: {str(e)}"
        }

@tool(description="Stringify JSON.", category="data", required=True)
def stringify_json(data: Any, indent: int = None) -> Dict[str, Any]:
    """Convert a Python object to a JSON string.
    
    Args:
        data: The Python object to convert.
        indent: The indentation level.
            
    Returns:
        A dictionary containing the JSON string.
    """
    try:
        return {
            "success": True,
            "json": json.dumps(data, indent=indent)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error converting to JSON: {str(e)}"
        }

def _get_file_info(file_path: str, workspace_dir: str) -> Dict[str, Any]:
    """Get information about a file.
    
    Args:
        file_path: The path to the file.
        workspace_dir: The workspace directory.
            
    Returns:
        A dictionary containing file information.
    """
    # Get the relative path
    rel_path = os.path.relpath(file_path, workspace_dir)
    
    # Get the file stats
    stats = os.stat(file_path)
    
    # Determine the file type
    if os.path.isdir(file_path):
        file_type = "directory"
    elif os.path.islink(file_path):
        file_type = "link"
    else:
        file_type = "file"
    
    # Get the file extension
    _, ext = os.path.splitext(file_path)
    
    return {
        "name": os.path.basename(file_path),
        "path": file_path,
        "relative_path": rel_path,
        "type": file_type,
        "size": stats.st_size,
        "created": stats.st_ctime,
        "modified": stats.st_mtime,
        "accessed": stats.st_atime,
        "extension": ext[1:] if ext else ""
    }
