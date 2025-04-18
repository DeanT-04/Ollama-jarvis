#!/usr/bin/env python3
"""
Test script for the mem0ai integration in Jarvis CLI.

This script tests the basic functionality of the mem0ai integration,
including adding and retrieving memories.
"""

import os
from dotenv import load_dotenv
from mem0 import Memory

# Load environment variables
load_dotenv()

def main():
    """Main function to test the mem0ai integration."""
    print("Testing mem0ai integration...")
    
    # Initialize memory
    memory = Memory()
    user_id = "test_user"
    
    # Add some test messages
    print("Adding test messages...")
    memory.add([{"role": "user", "content": "What's the weather like today?"}], user_id=user_id)
    memory.add([{"role": "assistant", "content": "I don't have real-time weather data, but I can help you find that information."}], user_id=user_id)
    memory.add([{"role": "user", "content": "What's my favorite color?"}], user_id=user_id)
    memory.add([{"role": "assistant", "content": "I don't know your favorite color yet. Would you like to tell me?"}], user_id=user_id)
    memory.add([{"role": "user", "content": "My favorite color is blue."}], user_id=user_id)
    memory.add([{"role": "assistant", "content": "Thanks for letting me know! I'll remember that your favorite color is blue."}], user_id=user_id)
    
    # Search for memories
    print("\nSearching for memories about favorite color...")
    results = memory.search("What is my favorite color?", user_id=user_id, limit=3)
    
    # Print the results
    print("\nRelevant memories:")
    for i, result in enumerate(results.get("results", [])):
        print(f"{i+1}. {result.get('memory', '')}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
