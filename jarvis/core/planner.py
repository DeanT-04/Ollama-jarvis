#!/usr/bin/env python3
"""
Planner module for Jarvis.

This module provides functions for planning and breaking down complex tasks
into manageable steps.
"""

from typing import Dict, Any, Optional

from jarvis.config import get_config
from jarvis.core.ollama import OllamaClient

class Planner:
    """Planner for breaking down complex tasks into manageable steps."""

    def __init__(self, model: Optional[str] = None):
        """Initialize the planner.

        Args:
            model: The model to use for planning.
                If not provided, the default model from the configuration will be used.
        """
        self.model = model or get_config("OLLAMA_MODEL")
        self.client = OllamaClient(model=self.model)

    def create_plan(self, task: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Create a plan for a complex task.

        Args:
            task: The task to plan for.
            context: Additional context for the task.

        Returns:
            A dictionary containing the plan.
        """
        # Create a prompt for the planning
        prompt = self._create_planning_prompt(task, context)

        # Send the prompt to the model
        response = self.client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )

        # Parse the response
        plan = self._parse_planning_response(response.get("response", ""))

        return plan

    def _create_planning_prompt(self, task: str, context: Optional[str] = None) -> str:
        """Create a prompt for planning.

        Args:
            task: The task to plan for.
            context: Additional context for the task.

        Returns:
            The planning prompt.
        """
        prompt = f"""You are an AI assistant tasked with breaking down a complex task into manageable steps.

Task: {task}

"""

        if context:
            prompt += f"""
Context:
{context}

"""

        prompt += """
Please create a detailed plan for accomplishing this task. The plan should include:

1. A high-level overview of the approach
2. A list of steps, with each step including:
   - A clear description of what needs to be done
   - Any code or commands that need to be executed
   - Expected outcomes or results
3. Any potential challenges or considerations

Format your response as follows:

OVERVIEW:
[Brief overview of the approach]

STEPS:
1. [Step 1 description]
   - [Substep 1.1]
   - [Substep 1.2]
   CODE: [Any code or commands for this step, if applicable]
   EXPECTED OUTCOME: [What should happen after this step]

2. [Step 2 description]
   - [Substep 2.1]
   - [Substep 2.2]
   CODE: [Any code or commands for this step, if applicable]
   EXPECTED OUTCOME: [What should happen after this step]

... and so on

CONSIDERATIONS:
- [Consideration 1]
- [Consideration 2]
... and so on

Please be as detailed and specific as possible.
"""

        return prompt

    def _parse_planning_response(self, response: str) -> Dict[str, Any]:
        """Parse the planning response.

        Args:
            response: The response from the model.

        Returns:
            A dictionary containing the parsed plan.
        """
        # Initialize the plan
        plan = {
            "overview": "",
            "steps": [],
            "considerations": []
        }

        # Parse the overview
        if "OVERVIEW:" in response:
            overview_start = response.find("OVERVIEW:") + len("OVERVIEW:")
            overview_end = response.find("STEPS:")
            if overview_end == -1:
                overview_end = len(response)
            plan["overview"] = response[overview_start:overview_end].strip()

        # Parse the steps
        if "STEPS:" in response:
            steps_start = response.find("STEPS:") + len("STEPS:")
            steps_end = response.find("CONSIDERATIONS:")
            if steps_end == -1:
                steps_end = len(response)
            steps_text = response[steps_start:steps_end].strip()

            # Split the steps
            step_blocks = []
            current_block = ""
            for line in steps_text.split("\n"):
                if line.strip() and line.strip()[0].isdigit() and ". " in line:
                    if current_block:
                        step_blocks.append(current_block)
                    current_block = line
                else:
                    current_block += "\n" + line

            if current_block:
                step_blocks.append(current_block)

            # Parse each step
            for block in step_blocks:
                step = {
                    "description": "",
                    "substeps": [],
                    "code": "",
                    "expected_outcome": ""
                }

                # Parse the description
                lines = block.split("\n")
                if lines and lines[0].strip():
                    # Extract the step number and description
                    parts = lines[0].strip().split(". ", 1)
                    if len(parts) > 1:
                        step["description"] = parts[1].strip()

                # Parse the substeps, code, and expected outcome
                for i, line in enumerate(lines[1:]):
                    line = line.strip()
                    if line.startswith("-"):
                        step["substeps"].append(line[1:].strip())
                    elif line.startswith("CODE:"):
                        # Extract the code
                        code_text = line[len("CODE:"):].strip()
                        if not code_text:  # If the code is on the next line(s)
                            code_start = i + 1
                            code_text = ""
                            for code_line in lines[code_start + 1:]:
                                if code_line.strip().startswith("EXPECTED OUTCOME:"):
                                    break
                                code_text += code_line + "\n"
                        step["code"] = code_text.strip()
                    elif line.startswith("EXPECTED OUTCOME:"):
                        # Extract the expected outcome
                        outcome_text = line[len("EXPECTED OUTCOME:"):].strip()
                        step["expected_outcome"] = outcome_text

                plan["steps"].append(step)

        # Parse the considerations
        if "CONSIDERATIONS:" in response:
            considerations_start = response.find("CONSIDERATIONS:") + len("CONSIDERATIONS:")
            considerations_text = response[considerations_start:].strip()

            # Split the considerations
            for line in considerations_text.split("\n"):
                line = line.strip()
                if line.startswith("-"):
                    plan["considerations"].append(line[1:].strip())

        return plan

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a step in the plan.

        Args:
            step: The step to execute.

        Returns:
            A dictionary containing the result of the execution.
        """
        # This is a placeholder for now
        # In a real implementation, this would execute the code in the step
        # and return the result
        return {
            "success": True,
            "output": "Step executed successfully.",
            "error": ""
        }
