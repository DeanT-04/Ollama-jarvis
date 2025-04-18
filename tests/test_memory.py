#!/usr/bin/env python3
"""
Tests for the memory module.
"""

import unittest
from unittest.mock import patch

from jarvis.core.memory import Memory, get_memory

class TestMemory(unittest.TestCase):
    """Test cases for the memory module."""

    def test_memory_class(self):
        """Test that the Memory class is a wrapper around MemoriyMemory."""
        # Import the MemoriyMemory class
        from jarvis.core.memoripy_memory import MemoriyMemory

        # Check that Memory is a subclass of MemoriyMemory
        self.assertTrue(issubclass(Memory, MemoriyMemory))

    @patch('jarvis.core.memory.Memory')
    def test_get_memory(self, mock_memory_class):
        """Test the get_memory function."""
        # Configure the mock Memory class
        mock_memory_instance = mock_memory_class.return_value

        # Call get_memory
        memory = get_memory(use_persistent_storage=True)

        # Check that the Memory class was called with the correct arguments
        mock_memory_class.assert_called_once_with(use_persistent_storage=True)

        # Check that the memory instance is the mock instance
        self.assertEqual(memory, mock_memory_instance)

        # Call get_memory again
        memory2 = get_memory(use_persistent_storage=False)

        # Check that the Memory class was not called again
        mock_memory_class.assert_called_once()

        # Check that the memory instance is the same
        self.assertEqual(memory2, memory)



if __name__ == "__main__":
    unittest.main()
