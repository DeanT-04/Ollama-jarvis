#!/usr/bin/env python3
"""
Agent executor module for Jarvis.

This module provides the AgentExecutor class, which is responsible for executing
the agent's actions and managing the agent loop.
"""

import time
from typing import Dict, List, Any, Optional, Tuple, Union

from jarvis.config import get_config
from jarvis.core.agent import Agent, AgentAction, AgentFinish
from jarvis.core.tool_registry import get_registry

class AgentExecutor:
    """Executor for running the agent loop."""
    
    def __init__(self, agent: Optional[Agent] = None, max_iterations: int = 10):
        """Initialize the agent executor.
        
        Args:
            agent: The agent to use. If not provided, a new agent will be created.
            max_iterations: The maximum number of iterations to run.
        """
        self.agent = agent or Agent()
        self.registry = get_registry()
        self.max_iterations = max_iterations
    
    def run(self, task: str, context: Optional[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """Run the agent on a task.
        
        Args:
            task: The task to run the agent on.
            context: Additional context for the task.
            verbose: Whether to print verbose output.
            
        Returns:
            A dictionary containing the result of the agent run.
        """
        # Initialize the agent run
        iterations = 0
        start_time = time.time()
        intermediate_steps = []
        
        if verbose:
            print(f"Starting agent run for task: {task}")
        
        # Run the agent loop
        while iterations < self.max_iterations:
            iterations += 1
            
            if verbose:
                print(f"\nIteration {iterations}/{self.max_iterations}")
            
            # Get the next action from the agent
            if not intermediate_steps:
                # First iteration
                action = self.agent.plan(task, context)
            else:
                # Process the result of the previous action
                last_action, last_result = intermediate_steps[-1]
                action = self.agent.process_tool_result(
                    task,
                    last_action.tool_name,
                    last_action.tool_input,
                    last_result
                )
            
            # Check if the agent is done
            if isinstance(action, AgentFinish):
                if verbose:
                    print(f"Agent finished with output: {action.output}")
                
                return {
                    "output": action.output,
                    "intermediate_steps": intermediate_steps,
                    "iterations": iterations,
                    "time_taken": time.time() - start_time,
                    "thought": action.thought
                }
            
            # Execute the action
            if verbose:
                print(f"Executing action: {action.tool_name} with input: {action.tool_input}")
                print(f"Thought: {action.thought}")
            
            try:
                # Call the tool
                result = self.registry.call_tool(action.tool_name, **action.tool_input)
                
                if verbose:
                    print(f"Tool result: {result}")
                
                # Add the action and result to the intermediate steps
                intermediate_steps.append((action, result))
            except Exception as e:
                if verbose:
                    print(f"Error executing action: {e}")
                
                # Add the action and error to the intermediate steps
                error_result = {"error": str(e)}
                intermediate_steps.append((action, error_result))
        
        # If we reach here, we've hit the maximum number of iterations
        if verbose:
            print(f"Reached maximum number of iterations ({self.max_iterations})")
        
        # Get a final answer from the agent
        final_prompt = f"""Task: {task}

I've taken the following steps:
"""
        
        for i, (action, result) in enumerate(intermediate_steps):
            final_prompt += f"""
Step {i+1}:
- Tool: {action.tool_name}
- Input: {action.tool_input}
- Result: {result}
"""
        
        final_prompt += """
I've reached the maximum number of iterations. Based on the steps I've taken so far,
what's the best answer I can provide to the original task?
"""
        
        # Send the prompt to the agent
        final_action = self.agent.plan(final_prompt, context)
        
        if isinstance(final_action, AgentFinish):
            final_output = final_action.output
            final_thought = final_action.thought
        else:
            # If the agent still wants to take an action, just use its thought as the output
            final_output = f"I wasn't able to complete the task within {self.max_iterations} iterations. Here's what I know so far: {final_action.thought}"
            final_thought = final_action.thought
        
        return {
            "output": final_output,
            "intermediate_steps": intermediate_steps,
            "iterations": iterations,
            "time_taken": time.time() - start_time,
            "thought": final_thought
        }
