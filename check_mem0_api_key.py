#!/usr/bin/env python3
"""
Check if the Mem0 API key is set.
"""

import os

def main():
    """Check if the Mem0 API key is set."""
    # Check for MEM0_API_KEY
    mem0_api_key = os.environ.get("MEM0_API_KEY")
    if mem0_api_key:
        print(f"MEM0_API_KEY is set: {mem0_api_key[:5]}...{mem0_api_key[-5:] if len(mem0_api_key) > 10 else ''}")
    else:
        print("MEM0_API_KEY is not set.")
    
    # Check for OPENAI_API_KEY
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        print(f"OPENAI_API_KEY is set: {openai_api_key[:5]}...{openai_api_key[-5:] if len(openai_api_key) > 10 else ''}")
    else:
        print("OPENAI_API_KEY is not set.")
    
    # List all environment variables that contain "API_KEY"
    print("\nAll environment variables containing 'API_KEY':")
    for key, value in os.environ.items():
        if "API_KEY" in key:
            print(f"{key}: {value[:5]}...{value[-5:] if len(value) > 10 else ''}")

if __name__ == "__main__":
    main()
