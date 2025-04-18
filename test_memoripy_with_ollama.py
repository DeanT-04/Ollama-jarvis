#!/usr/bin/env python3
"""
Test script for the Memoripy memory system with Ollama.
"""

from jarvis.core.memory import get_memory

def main():
    """Test the Memoripy memory system with Ollama."""
    # Initialize the memory system
    memory = get_memory()
    print("Memory system initialized.")
    
    # Add a test memory
    memory.add_memory("Python is a high-level, interpreted programming language known for its readability and simplicity.")
    print("Added memory about Python.")
    
    # Add a conversation
    memory.add_user_message("Hello, Jarvis!")
    memory.add_assistant_message("Hello! How can I help you today?")
    memory.add_user_message("What do you know about Python?")
    
    # Generate a response using the memory system
    response = memory.generate_response_with_memory("What do you know about Python?")
    print("\nGenerated response:")
    print(response)
    
    # Search for memories about Python
    results = memory.search_memories("Python programming")
    print("\nSearch results for 'Python programming':")
    for result in results:
        print(f"- {result['memory']}")
        print(f"  Relevance: {result.get('relevance', 'N/A')}")
        print()

if __name__ == "__main__":
    main()
