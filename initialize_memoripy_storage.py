#!/usr/bin/env python3
"""
Initialize the Memoripy storage file with the correct format.
"""

import os
import json
from jarvis.config import get_config

def main():
    """Initialize the Memoripy storage file."""
    # Get the workspace directory
    workspace_dir = get_config("WORKSPACE_DIR")
    
    # Create the storage file path
    storage_path = os.path.join(workspace_dir, "memories.json")
    
    # Create the initial storage structure
    initial_storage = {
        "short_term_memory": [],
        "long_term_memory": []
    }
    
    # Write the initial storage structure to the file
    with open(storage_path, 'w') as f:
        json.dump(initial_storage, f, indent=2)
    
    print(f"Initialized Memoripy storage file at {storage_path}")

if __name__ == "__main__":
    main()
