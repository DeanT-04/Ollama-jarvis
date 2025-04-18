#!/usr/bin/env python3
"""
Agent module for Jarvis.

This module provides the Agent class, which is responsible for reasoning about
tasks and selecting appropriate tools to accomplish them.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union

from jarvis.config import get_config
from jarvis.core.ollama import OllamaClient
from jarvis.core.tool_registry import get_registry
from jarvis.core.agent_prompts import (
    AGENT_SYSTEM_PROMPT,
    AGENT_PLANNING_PROMPT,
    AGENT_TOOL_SELECTION_PROMPT,
    AGENT_TOOL_RESULT_PROMPT,
    AGENT_FINAL_ANSWER_PROMPT
)

class AgentAction:
    """An action taken by the agent."""
    
    def __init__(self, tool_name: str, tool_input: Dict[str, Any], thought: str):
        """Initialize an agent action.
        
        Args:
            tool_name: The name of the tool to use.
            tool_input: The input to the tool.
            thought: The agent's reasoning for taking this action.
        """
        self.tool_name = tool_name
        self.tool_input = tool_input
        self.thought = thought
    
    def __repr__(self) -> str:
        """Return a string representation of the action."""
        return f"AgentAction(tool_name={self.tool_name}, tool_input={self.tool_input})"

class AgentFinish:
    """The final output of the agent."""
    
    def __init__(self, output: str, thought: str):
        """Initialize an agent finish.
        
        Args:
            output: The final output of the agent.
            thought: The agent's reasoning for the final output.
        """
        self.output = output
        self.thought = thought
    
    def __repr__(self) -> str:
        """Return a string representation of the finish."""
        return f"AgentFinish(output={self.output})"

class Agent:
    """Agent for reasoning about tasks and selecting tools."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the agent.
        
        Args:
            model: The model to use for the agent.
                If not provided, the default model from the configuration will be used.
        """
        self.model = model or get_config("OLLAMA_MODEL")
        self.client = OllamaClient(model=self.model)
        self.registry = get_registry()
    
    def _extract_thinking_and_action(self, text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Extract the thinking and action from the agent's response.
        
        Args:
            text: The agent's response.
            
        Returns:
            A tuple (thinking, action), where action is either a tool call or a final answer.
        """
        # Extract thinking
        thinking_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
        thinking = thinking_match.group(1).strip() if thinking_match else ""
        
        # Extract tool call
        tool_match = re.search(r'<tool>(.*?)</tool>', text, re.DOTALL)
        if tool_match:
            tool_json = tool_match.group(1).strip()
            try:
                tool_data = json.loads(tool_json)
                return thinking, {"type": "tool", "data": tool_data}
            except json.JSONDecodeError:
                # If the JSON is invalid, treat it as a final answer
                return thinking, {"type": "answer", "data": tool_json}
        
        # Extract final answer
        answer_match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
        if answer_match:
            answer = answer_match.group(1).strip()
            return thinking, {"type": "answer", "data": answer}
        
        # If no structured output is found, treat the entire response as a final answer
        return thinking, {"type": "answer", "data": text}
    
    def plan(self, task: str, context: Optional[str] = None) -> Union[AgentAction, AgentFinish]:
        """Plan the next action for a task.
        
        Args:
            task: The task to plan for.
            context: Additional context for the task.
            
        Returns:
            Either an AgentAction to take or an AgentFinish with the final output.
        """
        # Create a prompt for the agent
        prompt = self._create_agent_prompt(task, context)
        
        # Send the prompt to the model
        response = self.client.generate(
            prompt=prompt,
            system=AGENT_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the thinking and action from the response
        thinking, action = self._extract_thinking_and_action(response.get("response", ""))
        
        # Return the appropriate action
        if action["type"] == "tool":
            tool_data = action["data"]
            return AgentAction(
                tool_name=tool_data["name"],
                tool_input=tool_data["input"],
                thought=thinking
            )
        else:
            return AgentFinish(
                output=action["data"],
                thought=thinking
            )
    
    def _create_agent_prompt(self, task: str, context: Optional[str] = None) -> str:
        """Create a prompt for the agent.
        
        Args:
            task: The task to create a prompt for.
            context: Additional context for the task.
            
        Returns:
            The agent prompt.
        """
        # Get tool descriptions
        tool_descriptions = self.registry.get_tool_descriptions()
        
        # Create the prompt
        prompt = f"""Task: {task}\n\n"""
        
        if context:
            prompt += f"""Context: {context}\n\n"""
        
        prompt += f"""Available Tools:
{tool_descriptions}

Think step by step about how to accomplish this task. You can use the available tools to help you.
"""
        
        return prompt
    
    def process_tool_result(self, task: str, tool_name: str, tool_input: Dict[str, Any], 
                           tool_result: Any) -> Union[AgentAction, AgentFinish]:
        """Process the result of a tool and determine the next action.
        
        Args:
            task: The original task.
            tool_name: The name of the tool that was used.
            tool_input: The input that was provided to the tool.
            tool_result: The result from the tool.
            
        Returns:
            Either an AgentAction to take or an AgentFinish with the final output.
        """
        # Create a prompt for processing the tool result
        prompt = f"""Task: {task}

I used the tool '{tool_name}' with the input:
{json.dumps(tool_input, indent=2)}

And got the following result:
{tool_result}

Based on this result, what should I do next? Should I use another tool or provide a final answer?
"""
        
        # Send the prompt to the model
        response = self.client.generate(
            prompt=prompt,
            system=AGENT_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the thinking and action from the response
        thinking, action = self._extract_thinking_and_action(response.get("response", ""))
        
        # Return the appropriate action
        if action["type"] == "tool":
            tool_data = action["data"]
            return AgentAction(
                tool_name=tool_data["name"],
                tool_input=tool_data["input"],
                thought=thinking
            )
        else:
            return AgentFinish(
                output=action["data"],
                thought=thinking
            )
