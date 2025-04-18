#!/usr/bin/env python3
"""
Test script for the Mem0 client.
"""

import os
from mem0 import MemoryClient

def main():
    """Test the Mem0 client."""
    # Get the Mem0 API key
    mem0_api_key = os.environ.get("MEM0_API_KEY", "")
    print(f"Using Mem0 API key: {mem0_api_key[:5]}...{mem0_api_key[-5:] if len(mem0_api_key) > 10 else ''}")

    try:
        # Initialize the Mem0 client
        client = MemoryClient(api_key=mem0_api_key)
        print("Mem0 client initialized successfully.")

        # Store messages
        messages = [
            {"role": "user", "content": "Hello, I'm testing Mem0!"},
            {"role": "assistant", "content": "Hello! I'm here to help with your Mem0 test."}
        ]

        result = client.add(messages, user_id="test_user")
        print(f"Added messages: {result}")

        # Search memories
        query = "What do you know about me?"
        related_memories = client.search(query, user_id="test_user")
        print(f"Search results: {related_memories}")

        # Get all memories
        all_memories = client.get_all(user_id="test_user")
        print(f"All memories: {all_memories}")

    except Exception as e:
        print(f"Error testing Mem0 client: {e}")

if __name__ == "__main__":
    main()
