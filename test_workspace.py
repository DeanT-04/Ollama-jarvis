#!/usr/bin/env python3
"""
Test script for the workspace utilities in Jarvis CLI.

This script tests the basic functionality of the workspace utilities module,
including getting the workspace state and listing directory contents.
"""

import os
from workspace_utils import get_workspace_state, list_directory, format_directory_listing

# Configuration
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_workspace")

def main():
    """Main function to test the workspace utilities."""
    print("Testing workspace utilities...")
    
    # Ensure the workspace directory exists
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    # Create a test file in the workspace
    test_file_path = os.path.join(WORKSPACE_DIR, "test_file.txt")
    with open(test_file_path, "w") as f:
        f.write("This is a test file.")
    
    # Create a test directory in the workspace
    test_dir_path = os.path.join(WORKSPACE_DIR, "test_dir")
    os.makedirs(test_dir_path, exist_ok=True)
    
    # Get the workspace state
    print("\nWorkspace state:")
    workspace_state = get_workspace_state(WORKSPACE_DIR)
    print(workspace_state)
    
    # List the directory contents
    print("\nDirectory contents:")
    items = list_directory(WORKSPACE_DIR)
    formatted_listing = format_directory_listing(items)
    print(formatted_listing)
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
