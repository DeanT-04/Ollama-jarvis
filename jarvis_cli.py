#!/usr/bin/env python3
"""
Jarvis CLI - A command-line interface for an AI assistant powered by Ollama.

This script implements a basic CLI for interacting with an AI assistant named Jarvis.
Jarvis can understand user requests, generate and execute code, and attempt to
correct itself when code execution fails.

SECURITY WARNING: This initial implementation executes code directly, which poses
significant security risks. Future versions will implement proper sandboxing.
"""

import os
import sys
import json
import subprocess
import tempfile
import requests
from typing import Dict, List, Tuple, Optional, Any
import re

# Configuration
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_workspace")
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # Change to your preferred model
MAX_RETRIES = 2

# Ensure workspace directory exists
os.makedirs(WORKSPACE_DIR, exist_ok=True)

class Memory:
    """Simple memory mechanism to store conversation history."""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the memory."""
        self.history.append({
            "role": "user",
            "content": message
        })
    
    def add_assistant_message(self, message: str) -> None:
        """Add an assistant message to the memory."""
        self.history.append({
            "role": "assistant",
            "content": message
        })
    
    def add_execution_result(self, code: str, language: str, output: str, error: str, success: bool) -> None:
        """Add an execution result to the memory."""
        self.history.append({
            "role": "system",
            "content": f"Code execution ({language}):\n{code}\nSuccess: {success}\nOutput: {output}\nError: {error}"
        })
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history in a format suitable for the Ollama API."""
        # Filter out system messages for the conversation history
        return [msg for msg in self.history if msg["role"] != "system"]
    
    def get_full_history(self) -> List[Dict[str, str]]:
        """Get the full history including system messages."""
        return self.history


def send_to_ollama(prompt: str, memory: Memory, system_prompt: Optional[str] = None) -> str:
    """Send a prompt to the Ollama API and return the response."""
    if system_prompt is None:
        system_prompt = """You are Jarvis, an AI assistant operating within a dedicated workspace.
Your goal is to help the user by generating Bash commands or Python code snippets.
If you need to run code, generate the complete code block needed for the immediate step.
If you can answer directly without code, do so.
Always output code clearly marked within markdown code blocks (e.g., ```bash ... ``` or ```python ... ```).
Remember that all code you generate will be executed in a specific workspace directory.
"""
    
    # Prepare the conversation history
    messages = memory.get_conversation_history()
    
    # Add the current prompt
    current_message = {"role": "user", "content": prompt}
    
    # Prepare the payload
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages + [current_message],
        "stream": False,
        "system": system_prompt
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return f"I'm sorry, I encountered an error while trying to process your request: {e}"


def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
    """Extract code blocks from the text.
    
    Returns a list of tuples (language, code).
    """
    pattern = r"```(\w+)\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def execute_bash(code: str) -> Tuple[str, str, int]:
    """Execute a Bash command in the workspace directory.
    
    Returns a tuple (stdout, stderr, return_code).
    """
    try:
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR, suffix='.sh', delete=False) as f:
            f.write(code.encode())
            script_path = f.name
        
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Execute the script
        process = subprocess.Popen(
            ['/bin/bash', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=WORKSPACE_DIR
        )
        stdout, stderr = process.communicate()
        
        # Clean up
        os.unlink(script_path)
        
        return stdout.decode(), stderr.decode(), process.returncode
    except Exception as e:
        return "", str(e), 1


def execute_python(code: str) -> Tuple[str, str, int]:
    """Execute a Python code snippet in the workspace directory.
    
    Returns a tuple (stdout, stderr, return_code).
    """
    try:
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(dir=WORKSPACE_DIR, suffix='.py', delete=False) as f:
            f.write(code.encode())
            script_path = f.name
        
        # Execute the script
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=WORKSPACE_DIR
        )
        stdout, stderr = process.communicate()
        
        # Clean up
        os.unlink(script_path)
        
        return stdout.decode(), stderr.decode(), process.returncode
    except Exception as e:
        return "", str(e), 1


def handle_code_execution(code: str, language: str, memory: Memory, retries: int = 0) -> Tuple[str, bool]:
    """Handle the execution of code and potential retries.
    
    Returns a tuple (response_text, success).
    """
    print(f"\nExecuting {language} code...")
    
    # Execute the code
    if language.lower() in ["bash", "shell", "sh"]:
        stdout, stderr, return_code = execute_bash(code)
    elif language.lower() in ["python", "py"]:
        stdout, stderr, return_code = execute_python(code)
    else:
        return f"I don't know how to execute code in {language}.", False
    
    # Check if execution was successful
    if return_code == 0 and not stderr:
        memory.add_execution_result(code, language, stdout, stderr, True)
        return f"Execution successful:\n\n{stdout}", True
    
    # If we've reached the maximum number of retries, give up
    if retries >= MAX_RETRIES:
        memory.add_execution_result(code, language, stdout, stderr, False)
        return f"I've tried {MAX_RETRIES + 1} times, but I'm still encountering errors:\n\n{stderr}\n\nPlease provide more guidance.", False
    
    print(f"Execution failed. Analyzing error and retrying ({retries + 1}/{MAX_RETRIES})...")
    
    # Prepare a prompt for self-correction
    correction_prompt = f"""I tried to execute the following {language} code:

```{language}
{code}
```

But I encountered this error:

```
{stderr}
```

Please analyze the error and provide a corrected version of the code."""
    
    # Add the failed execution to memory
    memory.add_execution_result(code, language, stdout, stderr, False)
    
    # Get a corrected version of the code
    correction_response = send_to_ollama(correction_prompt, memory)
    memory.add_assistant_message(correction_response)
    
    # Extract the corrected code
    corrected_code_blocks = extract_code_blocks(correction_response)
    
    if not corrected_code_blocks:
        return f"I couldn't generate a corrected version of the code. Here's the error I encountered:\n\n{stderr}", False
    
    # Use the first code block of the correct language
    for corrected_language, corrected_code in corrected_code_blocks:
        if corrected_language.lower() in [language.lower(), "bash", "shell", "sh", "python", "py"]:
            # Recursively try to execute the corrected code
            return handle_code_execution(corrected_code, corrected_language, memory, retries + 1)
    
    return f"I couldn't generate a corrected version of the code in {language}. Here's the error I encountered:\n\n{stderr}", False


def main():
    """Main function to run the Jarvis CLI."""
    print("Jarvis CLI")
    print("==========")
    print(f"Using Ollama model: {OLLAMA_MODEL}")
    print(f"Workspace directory: {WORKSPACE_DIR}")
    print("Type 'exit' or 'quit' to end the session.")
    print()
    
    memory = Memory()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ")
            
            # Check if the user wants to exit
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Add the user input to memory
            memory.add_user_message(user_input)
            
            # Send the user input to Ollama
            response = send_to_ollama(user_input, memory)
            
            # Add the response to memory
            memory.add_assistant_message(response)
            
            # Print the response
            print("\nJarvis:", response.split("```")[0].strip())
            
            # Extract and execute code blocks
            code_blocks = extract_code_blocks(response)
            
            if code_blocks:
                for language, code in code_blocks:
                    execution_result, success = handle_code_execution(code, language, memory)
                    print(f"\nExecution Result: {execution_result}")
            
            print()
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
