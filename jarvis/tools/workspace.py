#!/usr/bin/env python3
"""
Workspace utilities for Jarvis.

This module provides functions for interacting with the Jarvis workspace.
"""

import os
import subprocess
from typing import Tuple, List, Dict, Any, Optional

from jarvis.config import get_config

def get_workspace_state(workspace_dir: Optional[str] = None) -> str:
    """Get the current state of the workspace.

    Args:
        workspace_dir: The path to the workspace directory.
            If not provided, the default workspace directory from the configuration will be used.

    Returns:
        A string containing the current state of the workspace.
    """
    workspace_dir = workspace_dir or get_config("WORKSPACE_DIR")
    
    try:
        # Run the ls -la command
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                ['dir', '/a'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=workspace_dir,
                shell=True
            )
        else:  # Unix/Linux/Mac
            process = subprocess.Popen(
                ['ls', '-la'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=workspace_dir
            )
        
        stdout, stderr = process.communicate()
        
        if stderr:
            return f"Error getting workspace state: {stderr.decode()}"
        
        return stdout.decode()
    except Exception as e:
        return f"Error getting workspace state: {e}"


def read_file(file_path: str, workspace_dir: Optional[str] = None) -> Tuple[str, bool]:
    """Read the contents of a file in the workspace.

    Args:
        file_path: The path to the file, relative to the workspace directory.
        workspace_dir: The path to the workspace directory.
            If not provided, the default workspace directory from the configuration will be used.

    Returns:
        A tuple containing the file contents and a boolean indicating success.
    """
    workspace_dir = workspace_dir or get_config("WORKSPACE_DIR")
    
    try:
        full_path = os.path.join(workspace_dir, file_path)
        
        # Check if the file exists and is within the workspace
        if not os.path.exists(full_path):
            return f"File {file_path} does not exist.", False
        
        # Check if the file is within the workspace
        if not os.path.abspath(full_path).startswith(os.path.abspath(workspace_dir)):
            return f"File {file_path} is outside the workspace.", False
        
        # Read the file
        with open(full_path, 'r') as f:
            content = f.read()
        
        return content, True
    except Exception as e:
        return f"Error reading file {file_path}: {e}", False


def write_file(file_path: str, content: str, workspace_dir: Optional[str] = None) -> Tuple[str, bool]:
    """Write content to a file in the workspace.

    Args:
        file_path: The path to the file, relative to the workspace directory.
        content: The content to write to the file.
        workspace_dir: The path to the workspace directory.
            If not provided, the default workspace directory from the configuration will be used.

    Returns:
        A tuple containing a message and a boolean indicating success.
    """
    workspace_dir = workspace_dir or get_config("WORKSPACE_DIR")
    
    try:
        full_path = os.path.join(workspace_dir, file_path)
        
        # Check if the file is within the workspace
        if not os.path.abspath(full_path).startswith(os.path.abspath(workspace_dir)):
            return f"File {file_path} is outside the workspace.", False
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write the file
        with open(full_path, 'w') as f:
            f.write(content)
        
        return f"File {file_path} written successfully.", True
    except Exception as e:
        return f"Error writing file {file_path}: {e}", False


def list_directory(dir_path: str = "", workspace_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """List the contents of a directory in the workspace.

    Args:
        dir_path: The path to the directory, relative to the workspace directory.
        workspace_dir: The path to the workspace directory.
            If not provided, the default workspace directory from the configuration will be used.

    Returns:
        A list of dictionaries containing information about the directory contents.
    """
    workspace_dir = workspace_dir or get_config("WORKSPACE_DIR")
    
    try:
        full_path = os.path.join(workspace_dir, dir_path)
        
        # Check if the directory exists and is within the workspace
        if not os.path.exists(full_path):
            return []
        
        # Check if the directory is within the workspace
        if not os.path.abspath(full_path).startswith(os.path.abspath(workspace_dir)):
            return []
        
        # List the directory
        items = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            item_info = {
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                "path": os.path.join(dir_path, item)
            }
            items.append(item_info)
        
        return items
    except Exception as e:
        print(f"Error listing directory {dir_path}: {e}")
        return []


def format_directory_listing(items: List[Dict[str, Any]]) -> str:
    """Format a directory listing as a string.

    Args:
        items: A list of dictionaries containing information about the directory contents.

    Returns:
        A formatted string containing the directory listing.
    """
    if not items:
        return "Directory is empty or does not exist."
    
    formatted_listing = "Name\t\tType\t\tSize\n"
    formatted_listing += "----\t\t----\t\t----\n"
    
    for item in items:
        name = item["name"]
        item_type = item["type"]
        size = item["size"]
        
        # Format size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.2f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.2f} MB"
        
        formatted_listing += f"{name}\t\t{item_type}\t\t{size_str}\n"
    
    return formatted_listing
