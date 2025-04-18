#!/usr/bin/env python3
"""
Test script for the memory system.
"""

import os
from jarvis.core.memory import Memory

# Set the OpenAI API key for Mem0
os.environ["OPENAI_API_KEY"] = os.environ.get("MEM0_API_KEY", "")

def main():
    """Test the memory system."""
    # Initialize the memory system
    memory = Memory()

    # Add a test memory
    memory.add_memory("This is a test memory")

    # Add a user message
    memory.add_user_message("Hello, Jarvis!")

    # Add an assistant message
    memory.add_assistant_message("Hello! How can I help you today?")

    # Search for memories
    results = memory.search_memories("test")

    # Print the results
    print("Search results:")
    for result in results:
        print(f"- {result}")

    # Get the conversation history
    history = memory.get_conversation_history()

    # Print the history
    print("\nConversation history:")
    for msg in history:
        print(f"- {msg['role']}: {msg['content']}")

if __name__ == "__main__":
    main()
