#!/usr/bin/env python3
"""
Asynchronous Executor module for Jarvis.

This module provides an asynchronous execution environment for running code
and other tasks.
"""

import os
import sys
import time
import asyncio
import threading
import uuid
from typing import Dict, List, Any, Optional, Callable, Tuple, Union

from jarvis.config import get_config
from jarvis.core.sandbox import Sandbox
from jarvis.core.error_manager import ErrorManager

class AsyncExecutor:
    """Asynchronous executor for running code and other tasks."""
    
    def __init__(self):
        """Initialize the asynchronous executor."""
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.results: Dict[str, Dict[str, Any]] = {}
        self.sandbox = Sandbox()
        self.error_manager = ErrorManager()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
    
    def _run_event_loop(self) -> None:
        """Run the event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def execute_code(self, code: str, language: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute code asynchronously.
        
        Args:
            code: The code to execute.
            language: The language of the code.
            task_id: The task ID. If not provided, a new ID will be generated.
            
        Returns:
            A dictionary containing the task ID and status.
        """
        # Generate a task ID if not provided
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        # Create a task for the code execution
        task = asyncio.run_coroutine_threadsafe(
            self._execute_code(task_id, code, language),
            self.loop
        )
        
        # Store the task
        self.tasks[task_id] = {
            "task": task,
            "type": "code_execution",
            "code": code,
            "language": language,
            "status": "running",
            "created_at": time.time()
        }
        
        # Return the task ID and status
        return {
            "task_id": task_id,
            "status": "running"
        }
    
    async def _execute_code(self, task_id: str, code: str, language: str) -> None:
        """Execute code asynchronously.
        
        Args:
            task_id: The task ID.
            code: The code to execute.
            language: The language of the code.
        """
        try:
            # Execute the code in the sandbox
            stdout, stderr, return_code = self.sandbox.execute_code(code, language)
            
            # Check if the execution was successful
            if return_code == 0 and not stderr:
                # Store the result
                self.results[task_id] = {
                    "success": True,
                    "stdout": stdout,
                    "stderr": stderr,
                    "return_code": return_code,
                    "error_handled": False,
                    "error_info": None,
                    "status": "completed",
                    "completed_at": time.time()
                }
            else:
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
                error_info = self.error_manager.handle_error(error, error_context)
                
                # Store the result
                self.results[task_id] = {
                    "success": False,
                    "stdout": stdout,
                    "stderr": stderr,
                    "return_code": return_code,
                    "error_handled": True,
                    "error_info": error_info,
                    "status": "completed",
                    "completed_at": time.time()
                }
        except Exception as e:
            # If an exception was raised during execution, handle it
            error_context = {
                "code": code,
                "language": language,
                "exception": str(e)
            }
            
            # Handle the error
            error_info = self.error_manager.handle_error(e, error_context)
            
            # Store the result
            self.results[task_id] = {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": 1,
                "error_handled": True,
                "error_info": error_info,
                "status": "completed",
                "completed_at": time.time()
            }
        
        # Update the task status
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "completed"
    
    def execute_function(self, func: Callable, args: List[Any] = None, kwargs: Dict[str, Any] = None, 
                        task_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a function asynchronously.
        
        Args:
            func: The function to execute.
            args: The positional arguments to pass to the function.
            kwargs: The keyword arguments to pass to the function.
            task_id: The task ID. If not provided, a new ID will be generated.
            
        Returns:
            A dictionary containing the task ID and status.
        """
        # Generate a task ID if not provided
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        # Default args and kwargs to empty if not provided
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        # Create a task for the function execution
        task = asyncio.run_coroutine_threadsafe(
            self._execute_function(task_id, func, args, kwargs),
            self.loop
        )
        
        # Store the task
        self.tasks[task_id] = {
            "task": task,
            "type": "function_execution",
            "function": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "status": "running",
            "created_at": time.time()
        }
        
        # Return the task ID and status
        return {
            "task_id": task_id,
            "status": "running"
        }
    
    async def _execute_function(self, task_id: str, func: Callable, args: List[Any], kwargs: Dict[str, Any]) -> None:
        """Execute a function asynchronously.
        
        Args:
            task_id: The task ID.
            func: The function to execute.
            args: The positional arguments to pass to the function.
            kwargs: The keyword arguments to pass to the function.
        """
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                # If the function is a coroutine function, await it
                result = await func(*args, **kwargs)
            else:
                # If the function is a regular function, run it in a thread
                result = await asyncio.to_thread(func, *args, **kwargs)
            
            # Store the result
            self.results[task_id] = {
                "success": True,
                "result": result,
                "error": None,
                "status": "completed",
                "completed_at": time.time()
            }
        except Exception as e:
            # If an exception was raised during execution, handle it
            error_context = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs,
                "exception": str(e)
            }
            
            # Handle the error
            error_info = self.error_manager.handle_error(e, error_context)
            
            # Store the result
            self.results[task_id] = {
                "success": False,
                "result": None,
                "error": str(e),
                "error_info": error_info,
                "status": "completed",
                "completed_at": time.time()
            }
        
        # Update the task status
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "completed"
    
    def get_result(self, task_id: str) -> Dict[str, Any]:
        """Get the result of a task.
        
        Args:
            task_id: The task ID.
            
        Returns:
            A dictionary containing the result of the task.
        """
        # Check if the task exists
        if task_id not in self.tasks:
            return {
                "task_id": task_id,
                "status": "not_found"
            }
        
        # Check if the task is completed
        if task_id in self.results:
            return self.results[task_id]
        
        # Check if the task is running
        if self.tasks[task_id]["status"] == "running":
            return {
                "task_id": task_id,
                "status": "running"
            }
        
        # If the task is not running and not completed, it must have failed
        return {
            "task_id": task_id,
            "status": "failed"
        }
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for a task to complete.
        
        Args:
            task_id: The task ID.
            timeout: The timeout in seconds. If None, wait indefinitely.
            
        Returns:
            A dictionary containing the result of the task.
        """
        # Check if the task exists
        if task_id not in self.tasks:
            return {
                "task_id": task_id,
                "status": "not_found"
            }
        
        # Check if the task is already completed
        if task_id in self.results:
            return self.results[task_id]
        
        # Get the task
        task = self.tasks[task_id]["task"]
        
        try:
            # Wait for the task to complete
            task.result(timeout=timeout)
            
            # Return the result
            return self.results[task_id]
        except asyncio.TimeoutError:
            # If the task timed out, return a timeout status
            return {
                "task_id": task_id,
                "status": "timeout"
            }
        except Exception as e:
            # If an exception was raised, return an error status
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a task.
        
        Args:
            task_id: The task ID.
            
        Returns:
            A dictionary containing the result of the cancellation.
        """
        # Check if the task exists
        if task_id not in self.tasks:
            return {
                "task_id": task_id,
                "status": "not_found"
            }
        
        # Check if the task is already completed
        if task_id in self.results:
            return {
                "task_id": task_id,
                "status": "already_completed"
            }
        
        # Get the task
        task = self.tasks[task_id]["task"]
        
        # Cancel the task
        task.cancel()
        
        # Update the task status
        self.tasks[task_id]["status"] = "cancelled"
        
        # Store the result
        self.results[task_id] = {
            "task_id": task_id,
            "status": "cancelled",
            "cancelled_at": time.time()
        }
        
        return {
            "task_id": task_id,
            "status": "cancelled"
        }
    
    def list_tasks(self, status: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """List tasks, optionally filtered by status.
        
        Args:
            status: The status to filter by.
            
        Returns:
            A dictionary containing lists of tasks grouped by status.
        """
        # Initialize the result
        result: Dict[str, List[Dict[str, Any]]] = {
            "running": [],
            "completed": [],
            "cancelled": [],
            "failed": []
        }
        
        # Group tasks by status
        for task_id, task_info in self.tasks.items():
            task_status = task_info["status"]
            
            # Skip tasks that don't match the requested status
            if status is not None and task_status != status:
                continue
            
            # Create a copy of the task info without the task object
            task_info_copy = task_info.copy()
            task_info_copy.pop("task", None)
            
            # Add the task ID
            task_info_copy["task_id"] = task_id
            
            # Add the result if available
            if task_id in self.results:
                result_copy = self.results[task_id].copy()
                result_copy.pop("status", None)
                task_info_copy.update(result_copy)
            
            # Add the task to the appropriate list
            if task_status in result:
                result[task_status].append(task_info_copy)
        
        return result
    
    def cleanup_tasks(self, max_age: float = 3600.0) -> int:
        """Clean up old tasks.
        
        Args:
            max_age: The maximum age of tasks to keep, in seconds.
            
        Returns:
            The number of tasks cleaned up.
        """
        # Get the current time
        now = time.time()
        
        # Find tasks to clean up
        tasks_to_cleanup = []
        
        for task_id, task_info in self.tasks.items():
            # Skip running tasks
            if task_info["status"] == "running":
                continue
            
            # Check if the task is old enough to clean up
            created_at = task_info.get("created_at", 0)
            if now - created_at > max_age:
                tasks_to_cleanup.append(task_id)
        
        # Clean up the tasks
        for task_id in tasks_to_cleanup:
            self.tasks.pop(task_id, None)
            self.results.pop(task_id, None)
        
        return len(tasks_to_cleanup)
    
    def shutdown(self) -> None:
        """Shut down the executor."""
        # Cancel all running tasks
        for task_id, task_info in self.tasks.items():
            if task_info["status"] == "running":
                task = task_info["task"]
                task.cancel()
        
        # Stop the event loop
        self.loop.call_soon_threadsafe(self.loop.stop)
        
        # Wait for the thread to finish
        self.thread.join(timeout=5.0)
        
        # Close the event loop
        self.loop.close()


# Global async executor instance
_async_executor = None

def get_async_executor() -> AsyncExecutor:
    """Get the global async executor instance.
    
    Returns:
        The global async executor instance.
    """
    global _async_executor
    
    if _async_executor is None:
        _async_executor = AsyncExecutor()
    
    return _async_executor
