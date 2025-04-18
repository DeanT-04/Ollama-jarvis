#!/usr/bin/env python3
"""
Jarvis CLI with Agent Architecture - A command-line interface for an AI assistant powered by Ollama.

This script implements a CLI for interacting with an AI assistant named Jarvis,
using an agent architecture for more autonomous and capable assistance.
"""

import traceback

from jarvis.config import get_config
from jarvis.core.memory import Memory
from jarvis.core.agent import Agent
from jarvis.core.agent_executor import AgentExecutor
from jarvis.tools.workspace import get_workspace_state
from jarvis.tools.register_tools import register_all_tools

def main():
    """Main function to run the Jarvis CLI with agent architecture."""
    workspace_dir = get_config("WORKSPACE_DIR")
    ollama_model = get_config("OLLAMA_MODEL")

    print("Jarvis CLI (Agent Mode)")
    print("=======================")
    print(f"Using Ollama model: {ollama_model}")
    print(f"Workspace directory: {workspace_dir}")
    print("Type 'exit' or 'quit' to end the session.")
    print()

    # Register all tools
    register_all_tools()

    # Initialize memory
    memory = Memory()

    # Initialize agent and executor
    agent = Agent(model=ollama_model)
    executor = AgentExecutor(agent=agent, max_iterations=10)

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

            # Get workspace state for context
            workspace_state = get_workspace_state()

            # Create context from memory and workspace state
            try:
                relevant_memories = memory.search_memories(user_input, limit=3)
                memories_str = "\n".join([f"- {entry['memory']}" for entry in relevant_memories])
            except Exception as e:
                print(f"Warning: Could not retrieve memories: {e}")
                memories_str = "No relevant memories found."

            # Format conversation history
            try:
                history = memory.get_conversation_history()
                history_str = ""
                for msg in history[-6:]:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    history_str += f"{role.capitalize()}: {content}\n"
            except Exception as e:
                print(f"Warning: Could not format conversation history: {e}")
                history_str = "No conversation history available."

            context = f"""Current Workspace State:
```
{workspace_state}
```

Relevant memories:
{memories_str}

Conversation history:
{history_str}
"""

            # Run the agent executor
            result = executor.run(user_input, context=context, verbose=True)

            # Add the agent's output to memory
            memory.add_assistant_message(result["output"])

            # Print the agent's output
            print("\nJarvis:", result["output"])

            # Add memories about the agent's actions
            for action, _ in result["intermediate_steps"]:
                memory.add_memory(f"Used tool '{action.tool_name}' to help answer the user's question.")

            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
