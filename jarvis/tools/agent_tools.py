#!/usr/bin/env python3
"""
Agent tools for Jarvis.

This module provides tools specifically designed for the agent architecture.
"""

import os
import platform
import datetime
from typing import Dict, List, Any, Optional

from jarvis.core.tool_registry import tool
from jarvis.config import get_config

@tool(description="Get the current date and time.", category="system")
def get_current_datetime() -> Dict[str, str]:
    """Get the current date and time.
    
    Returns:
        A dictionary containing the current date and time information.
    """
    now = datetime.datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": str(now.timestamp()),
        "timezone": datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
    }

@tool(description="Get system information.", category="system")
def get_system_info() -> Dict[str, str]:
    """Get information about the system.
    
    Returns:
        A dictionary containing system information.
    """
    return {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }

@tool(description="Calculate a mathematical expression.", category="utility")
def calculate(expression: str) -> Dict[str, Any]:
    """Calculate a mathematical expression.
    
    Args:
        expression: The mathematical expression to calculate.
        
    Returns:
        A dictionary containing the result of the calculation.
    """
    try:
        # Use eval to calculate the expression
        # This is safe because the agent is running in a controlled environment
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "expression": expression,
            "result": result,
            "success": True
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "success": False
        }

@tool(description="Get information about the workspace.", category="workspace")
def get_workspace_info() -> Dict[str, Any]:
    """Get information about the workspace.
    
    Returns:
        A dictionary containing information about the workspace.
    """
    workspace_dir = get_config("WORKSPACE_DIR")
    
    # Get the list of files in the workspace
    files = []
    for root, dirs, filenames in os.walk(workspace_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, workspace_dir)
            files.append(rel_path)
    
    return {
        "workspace_dir": workspace_dir,
        "files": files,
        "file_count": len(files)
    }
