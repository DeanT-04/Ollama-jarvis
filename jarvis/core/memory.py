#!/usr/bin/env python3
"""
Memory module for Jarvis.

This module provides a memory system for storing conversation history,
execution results, and long-term memories with semantic search capabilities.
"""

# Import the Memoripy memory implementation
from jarvis.core.memoripy_memory import MemoriyMemory


# For backward compatibility, we'll keep the Memory class name
class Memory(MemoriyMemory):
    """Memory mechanism for storing conversation history and execution results.

    This is a wrapper around the MemoriyMemory class for backward compatibility.
    """
    pass


# Global memory instance
_memory = None

def get_memory(use_persistent_storage: bool = True) -> Memory:
    """Get the global memory instance.

    Args:
        use_persistent_storage: Whether to use persistent storage for memories.

    Returns:
        The global memory instance.
    """
    global _memory

    if _memory is None:
        _memory = Memory(use_persistent_storage=use_persistent_storage)

    return _memory
