#!/usr/bin/env python3
"""
Main entry point for Jarvis.

This script provides a command-line interface for interacting with Jarvis,
an AI assistant powered by Ollama.
"""

import os
import argparse
import json
from typing import Optional, Dict, Any

from jarvis import __version__
from jarvis.cli import main as cli_main
from jarvis.cli_agent import main as cli_agent_main
from jarvis.config import get_config, load_config
from jarvis.core.memory import Memory
from jarvis.core.ollama import OllamaClient

def parse_args():
    """Parse command-line arguments.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Jarvis - An autonomous AI assistant powered by Ollama")

    # General options
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--config", type=str, help="Path to a custom configuration file")
    parser.add_argument("--workspace", type=str, help="Path to the workspace directory")
    parser.add_argument("--model", type=str, help="Ollama model to use")

    # Mode selection
    mode_group = parser.add_argument_group("Mode Selection")
    mode_group.add_argument("--interactive", action="store_true", help="Run in interactive mode (default)")
    mode_group.add_argument("--agent", action="store_true", help="Run in agent mode (using the agent architecture)")
    mode_group.add_argument("--batch", type=str, help="Run in batch mode with the specified input file")
    mode_group.add_argument("--server", action="store_true", help="Run in server mode")
    mode_group.add_argument("--execute", type=str, help="Execute a single command and exit")

    # Security options
    security_group = parser.add_argument_group("Security Options")
    security_group.add_argument("--security-level", type=str, choices=["low", "medium", "high"],
                               default="medium", help="Security level for code execution")

    # Memory options
    memory_group = parser.add_argument_group("Memory Options")
    memory_group.add_argument("--no-memory", action="store_true", help="Disable persistent memory")
    memory_group.add_argument("--disable-memory", action="store_true", help="Completely disable memory for faster responses")
    memory_group.add_argument("--memory-file", type=str, help="Path to a custom memory file")

    # Advanced options
    advanced_group = parser.add_argument_group("Advanced Options")
    advanced_group.add_argument("--temperature", type=float, help="Temperature for the Ollama model")
    advanced_group.add_argument("--max-tokens", type=int, help="Maximum number of tokens to generate")
    advanced_group.add_argument("--system-prompt", type=str, help="Custom system prompt")
    advanced_group.add_argument("--debug", action="store_true", help="Enable debug mode")

    return parser.parse_args()

def load_custom_config(config_path: str) -> Dict[str, Any]:
    """Load a custom configuration file.

    Args:
        config_path: Path to the custom configuration file.

    Returns:
        The loaded configuration.
    """
    try:
        with open(config_path, 'r') as f:
            if config_path.endswith('.json'):
                return json.load(f)
            else:
                # Assume it's a .env file
                config = {}
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    config[key] = value
                return config
    except Exception as e:
        print(f"Error loading custom configuration: {e}")
        return {}

def process_batch_file(batch_file: str, memory: Optional[Memory] = None,
                      client: Optional[OllamaClient] = None) -> None:
    """Process a batch file.

    Args:
        batch_file: Path to the batch file.
        memory: Memory instance to use.
        client: OllamaClient instance to use.
    """
    try:
        with open(batch_file, 'r') as f:
            commands = f.readlines()

        # Initialize client if not provided
        if client is None:
            client = OllamaClient()

        # Initialize memory only if not disabled and not provided
        disable_memory = str(get_config("DISABLE_MEMORY", "false")).lower() in ["true", "yes", "1"]
        if memory is None:
            if disable_memory:
                memory = None
                print("Memory disabled for faster responses.")
            else:
                memory = Memory(use_persistent_storage=not get_config("NO_MEMORY", False))

        # Process each command
        for i, command in enumerate(commands):
            command = command.strip()
            if not command or command.startswith('#'):
                continue

            print(f"\nExecuting command {i+1}/{len(commands)}: {command}")

            # Send the command to Ollama with streaming enabled for faster responses
            response = client.generate(
                prompt=command,
                temperature=get_config("TEMPERATURE", 0.7),
                max_tokens=get_config("MAX_TOKENS", 1000),
                stream=True
            )

            # Print the response
            print(f"\nJarvis: {response.get('response', '')}")

            # Add to memory if enabled
            if memory:
                # Add the command to memory
                memory.add_user_message(command)
                # Add the response to memory
                memory.add_assistant_message(response.get('response', ''))

    except Exception as e:
        print(f"Error processing batch file: {e}")

def execute_single_command(command: str) -> None:
    """Execute a single command and exit.

    Args:
        command: The command to execute.
    """
    try:
        # Initialize client
        client = OllamaClient()

        # Initialize memory only if not disabled
        disable_memory = str(get_config("DISABLE_MEMORY", "false")).lower() in ["true", "yes", "1"]
        if disable_memory:
            memory = None
            print("Memory disabled for faster response.")
        else:
            memory = Memory(use_persistent_storage=False)

        # Send the command to Ollama with streaming enabled for faster responses
        response = client.generate(
            prompt=command,
            temperature=get_config("TEMPERATURE", 0.7),
            max_tokens=get_config("MAX_TOKENS", 1000),
            stream=True
        )

        # Add to memory if enabled
        if memory:
            # Add the command to memory
            memory.add_user_message(command)
            # Add the response to memory
            memory.add_assistant_message(response.get('response', ''))

    except Exception as e:
        print(f"Error executing command: {e}")

def main():
    """Main entry point."""
    args = parse_args()

    # Show version information if requested
    if args.version:
        print(f"Jarvis v{__version__}")
        return

    # Load custom configuration if provided
    if args.config:
        custom_config = load_custom_config(args.config)
        for key, value in custom_config.items():
            os.environ[key] = str(value)

    # Reload configuration with environment variables
    load_config()

    # Override configuration with command-line arguments
    if args.workspace:
        os.environ["WORKSPACE_DIR"] = args.workspace

    if args.model:
        os.environ["OLLAMA_MODEL"] = args.model

    if args.security_level:
        os.environ["SECURITY_LEVEL"] = args.security_level

    if args.no_memory:
        os.environ["NO_MEMORY"] = "true"

    if args.disable_memory:
        os.environ["DISABLE_MEMORY"] = "true"

    if args.memory_file:
        os.environ["MEMORY_FILE"] = args.memory_file

    if args.temperature:
        os.environ["TEMPERATURE"] = str(args.temperature)

    if args.max_tokens:
        os.environ["MAX_TOKENS"] = str(args.max_tokens)

    if args.system_prompt:
        os.environ["SYSTEM_PROMPT"] = args.system_prompt

    if args.debug:
        os.environ["DEBUG"] = "true"

    # Reload configuration with updated environment variables
    load_config()

    # Determine the mode to run in
    if args.batch:
        process_batch_file(args.batch)
    elif args.execute:
        execute_single_command(args.execute)
    elif args.server:
        print("Server mode not implemented yet.")
    elif args.agent:
        # Run in agent mode
        cli_agent_main()
    else:
        # Run in interactive mode (default)
        cli_main()

if __name__ == "__main__":
    main()
