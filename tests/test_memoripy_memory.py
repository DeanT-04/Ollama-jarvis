#!/usr/bin/env python3
"""
Tests for the Memoripy memory module.
"""

import unittest
from unittest.mock import patch, MagicMock

from jarvis.core.memoripy_memory import MemoriyMemory

class TestMemoriyMemory(unittest.TestCase):
    """Test cases for the Memoripy memory module."""

    def setUp(self):
        """Set up the test environment."""
        # Patch the MemoryManager class
        self.memory_manager_patcher = patch("jarvis.core.memoripy_memory.MemoryManager")
        self.mock_memory_manager_class = self.memory_manager_patcher.start()

        # Configure the mock MemoryManager instance
        self.mock_memory_manager = MagicMock()
        self.mock_memory_manager_class.return_value = self.mock_memory_manager

        # Configure the mock get_embedding method
        self.mock_memory_manager.get_embedding.return_value = [0.1, 0.2, 0.3]

        # Configure the mock extract_concepts method
        self.mock_memory_manager.extract_concepts.return_value = ["concept1", "concept2"]

        # Configure the mock load_history method
        self.mock_memory_manager.load_history.return_value = ([], [])

        # Configure the mock retrieve_relevant_interactions method
        self.mock_memory_manager.retrieve_relevant_interactions.return_value = []

        # Configure the mock generate_response method
        self.mock_memory_manager.generate_response.return_value = "Test response"

        # Patch the JSONStorage class
        self.json_storage_patcher = patch("jarvis.core.memoripy_memory.JSONStorage")
        self.mock_json_storage_class = self.json_storage_patcher.start()

        # Configure the mock JSONStorage instance
        self.mock_json_storage = MagicMock()
        self.mock_json_storage_class.return_value = self.mock_json_storage

        # Patch the InMemoryStorage class
        self.in_memory_storage_patcher = patch("jarvis.core.memoripy_memory.InMemoryStorage")
        self.mock_in_memory_storage_class = self.in_memory_storage_patcher.start()

        # Configure the mock InMemoryStorage instance
        self.mock_in_memory_storage = MagicMock()
        self.mock_in_memory_storage_class.return_value = self.mock_in_memory_storage

        # Patch the get_config function
        self.get_config_patcher = patch("jarvis.core.memoripy_memory.get_config")
        self.mock_get_config = self.get_config_patcher.start()
        self.mock_get_config.side_effect = lambda key, default=None: {
            "USER_ID": "test_user",
            "WORKSPACE_DIR": "/test/workspace",
            "OLLAMA_MODEL": "llama3.2",
            "OLLAMA_EMBEDDING_MODEL": "llama3.2"
        }.get(key, default)

        # Create a MemoriyMemory instance
        self.memory = MemoriyMemory(use_persistent_storage=True)

    def tearDown(self):
        """Clean up after the tests."""
        # Stop the patchers
        self.memory_manager_patcher.stop()
        self.json_storage_patcher.stop()
        self.in_memory_storage_patcher.stop()
        self.get_config_patcher.stop()

    def test_initialization(self):
        """Test initializing the memory system."""
        # Check that the JSONStorage class was called
        self.mock_json_storage_class.assert_called_once()

        # Check that the path argument contains the expected components
        path_arg = self.mock_json_storage_class.call_args[0][0]
        self.assertIn("memories.json", path_arg)
        self.assertIn("workspace", path_arg)

        # Check that the MemoryManager class was called with the correct arguments
        self.mock_memory_manager_class.assert_called_once()

        # Check that the memory instance has the correct attributes
        self.assertEqual(self.memory.user_id, "test_user")
        self.assertEqual(self.memory.chat_model_name, "llama3.2")
        self.assertEqual(self.memory.embedding_model_name, "llama3.2")
        self.assertEqual(self.memory.storage, self.mock_json_storage)
        self.assertEqual(self.memory.memory_manager, self.mock_memory_manager)
        self.assertEqual(self.memory.history, [])

    def test_add_user_message(self):
        """Test adding a user message to the memory."""
        # Add a user message
        self.memory.add_user_message("Hello, Jarvis!")

        # Check that the message was added to the history
        self.assertEqual(len(self.memory.history), 1)
        self.assertEqual(self.memory.history[0]["role"], "user")
        self.assertEqual(self.memory.history[0]["content"], "Hello, Jarvis!")
        self.assertIn("timestamp", self.memory.history[0])

    def test_add_assistant_message(self):
        """Test adding an assistant message to the memory."""
        # Add a user message first
        self.memory.add_user_message("Hello, Jarvis!")

        # Add an assistant message
        self.memory.add_assistant_message("Hello! How can I help you today?")

        # Check that the message was added to the history
        self.assertEqual(len(self.memory.history), 2)
        self.assertEqual(self.memory.history[1]["role"], "assistant")
        self.assertEqual(self.memory.history[1]["content"], "Hello! How can I help you today?")
        self.assertIn("timestamp", self.memory.history[1])

        # Check that the memory manager's methods were called
        self.mock_memory_manager.get_embedding.assert_called_once()
        self.mock_memory_manager.extract_concepts.assert_called_once()
        self.mock_memory_manager.add_interaction.assert_called_once_with(
            "Hello, Jarvis!",
            "Hello! How can I help you today?",
            [0.1, 0.2, 0.3],
            ["concept1", "concept2"]
        )

    def test_add_execution_result(self):
        """Test adding an execution result to the memory."""
        # Add an execution result
        self.memory.add_execution_result(
            code="print('Hello, world!')",
            language="python",
            output="Hello, world!",
            error="",
            success=True
        )

        # Check that the execution result was added to the history
        self.assertEqual(len(self.memory.history), 1)
        self.assertEqual(self.memory.history[0]["role"], "system")
        self.assertIn("Code execution (python):", self.memory.history[0]["content"])
        self.assertIn("print('Hello, world!')", self.memory.history[0]["content"])
        self.assertIn("Success: True", self.memory.history[0]["content"])
        self.assertIn("Output: Hello, world!", self.memory.history[0]["content"])
        self.assertIn("timestamp", self.memory.history[0])
        self.assertEqual(self.memory.history[0]["metadata"]["type"], "execution_result")
        self.assertEqual(self.memory.history[0]["metadata"]["language"], "python")
        self.assertEqual(self.memory.history[0]["metadata"]["success"], True)

    def test_add_memory(self):
        """Test adding a custom memory to long-term storage."""
        # Add a memory
        self.memory.add_memory("This is a test memory", memory_type="test")

        # Check that the memory manager's methods were called
        self.mock_memory_manager.get_embedding.assert_called_once_with("This is a test memory")
        self.mock_memory_manager.extract_concepts.assert_called_once_with("This is a test memory")
        self.mock_memory_manager.add_interaction.assert_called_once_with(
            "Remember this test information",
            "This is a test memory",
            [0.1, 0.2, 0.3],
            ["concept1", "concept2"]
        )

    def test_get_conversation_history(self):
        """Test getting the conversation history."""
        # Add some messages to the history
        self.memory.add_user_message("Hello, Jarvis!")
        self.memory.add_assistant_message("Hello! How can I help you today?")
        self.memory.add_execution_result(
            code="print('Hello, world!')",
            language="python",
            output="Hello, world!",
            error="",
            success=True
        )

        # Get the conversation history
        history = self.memory.get_conversation_history()

        # Check that the history contains only user and assistant messages
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello, Jarvis!")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hello! How can I help you today?")

    def test_get_full_history(self):
        """Test getting the full history."""
        # Add some messages to the history
        self.memory.add_user_message("Hello, Jarvis!")
        self.memory.add_assistant_message("Hello! How can I help you today?")
        self.memory.add_execution_result(
            code="print('Hello, world!')",
            language="python",
            output="Hello, world!",
            error="",
            success=True
        )

        # Get the full history
        history = self.memory.get_full_history()

        # Check that the history contains all messages
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello, Jarvis!")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hello! How can I help you today?")
        self.assertEqual(history[2]["role"], "system")
        self.assertIn("Code execution (python):", history[2]["content"])

    def test_search_memories(self):
        """Test searching for relevant memories."""
        # Configure the mock retrieve_relevant_interactions method
        self.mock_memory_manager.retrieve_relevant_interactions.return_value = [
            {
                "prompt": "What is Python?",
                "response": "Python is a programming language.",
                "timestamp": "2023-01-01T00:00:00.000000",
                "relevance": 0.9
            },
            {
                "prompt": "How do I install Python?",
                "response": "You can download Python from python.org.",
                "timestamp": "2023-01-02T00:00:00.000000",
                "relevance": 0.8
            }
        ]

        # Search for memories
        results = self.memory.search_memories("Python programming")

        # Check that the memory manager's retrieve_relevant_interactions method was called
        self.mock_memory_manager.retrieve_relevant_interactions.assert_called_once_with(
            "Python programming",
            exclude_last_n=0,
            limit=5
        )

        # Check the results
        self.assertEqual(len(results), 2)
        self.assertIn("User: What is Python?", results[0]["memory"])
        self.assertIn("Assistant: Python is a programming language.", results[0]["memory"])
        self.assertEqual(results[0]["timestamp"], "2023-01-01T00:00:00.000000")
        self.assertEqual(results[0]["relevance"], 0.9)
        self.assertIn("User: How do I install Python?", results[1]["memory"])
        self.assertIn("Assistant: You can download Python from python.org.", results[1]["memory"])
        self.assertEqual(results[1]["timestamp"], "2023-01-02T00:00:00.000000")
        self.assertEqual(results[1]["relevance"], 0.8)

    def test_generate_response_with_memory(self):
        """Test generating a response using the memory system."""
        # Configure the mock load_history method
        self.mock_memory_manager.load_history.return_value = (
            [
                {"prompt": "Hello", "response": "Hi"},
                {"prompt": "How are you?", "response": "I'm good"}
            ],
            []
        )

        # Configure the mock retrieve_relevant_interactions method
        self.mock_memory_manager.retrieve_relevant_interactions.return_value = [
            {"prompt": "What is Python?", "response": "Python is a programming language."}
        ]

        # Generate a response
        response = self.memory.generate_response_with_memory("Tell me about Python")

        # Check that the memory manager's methods were called
        self.mock_memory_manager.load_history.assert_called_once()
        self.mock_memory_manager.retrieve_relevant_interactions.assert_called_once_with(
            "Tell me about Python",
            exclude_last_n=5
        )
        self.mock_memory_manager.generate_response.assert_called_once_with(
            "Tell me about Python",
            [
                {"prompt": "Hello", "response": "Hi"},
                {"prompt": "How are you?", "response": "I'm good"}
            ],
            [
                {"prompt": "What is Python?", "response": "Python is a programming language."}
            ]
        )

        # Check the response
        self.assertEqual(response, "Test response")

if __name__ == "__main__":
    unittest.main()
