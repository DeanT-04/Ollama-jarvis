#!/usr/bin/env python3
"""
Memoripy memory module for Jarvis.

This module provides a memory system using Memoripy for storing conversation history,
execution results, and long-term memories with semantic search capabilities.
"""

import os
from datetime import datetime
from typing import Dict, List, Any

from memoripy import MemoryManager, JSONStorage, InMemoryStorage
from memoripy.implemented_models import OllamaChatModel, OllamaEmbeddingModel

from jarvis.config import get_config

class MemoriyMemory:
    """Memory mechanism for storing conversation history and execution results using Memoripy."""

    def __init__(self, use_persistent_storage: bool = True) -> None:
        """Initialize the memory system.

        Args:
            use_persistent_storage: Whether to use persistent storage for memories.
        """
        self.user_id = get_config("USER_ID", "jarvis_user")
        self.use_persistent_storage = use_persistent_storage

        # Get Ollama model names from config
        self.chat_model_name = get_config("OLLAMA_MODEL", "llama3.2")
        self.embedding_model_name = get_config("OLLAMA_EMBEDDING_MODEL", self.chat_model_name)

        # Initialize storage
        if use_persistent_storage:
            storage_path = os.path.join(get_config("WORKSPACE_DIR"), "memories.json")
            self.storage = JSONStorage(storage_path)
        else:
            self.storage = InMemoryStorage()

        # Initialize Memoripy memory manager
        self.memory_manager = MemoryManager(
            OllamaChatModel(self.chat_model_name),
            OllamaEmbeddingModel(self.embedding_model_name),
            storage=self.storage
        )

        # Initialize local history for conversation tracking
        self.history: List[Dict[str, Any]] = []

        print(f"Memoripy memory system initialized with models: {self.chat_model_name} (chat), {self.embedding_model_name} (embedding)")

    def add_user_message(self, message: str) -> None:
        """Add a user message to the memory.

        Args:
            message: The user message to add.
        """
        msg = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(msg)

        # We'll store the interaction when the assistant responds

    def add_assistant_message(self, message: str) -> None:
        """Add an assistant message to the memory.

        Args:
            message: The assistant message to add.
        """
        msg = {
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(msg)

        # Get the last user message
        user_message = None
        for item in reversed(self.history[:-1]):
            if item["role"] == "user":
                user_message = item["content"]
                break

        if user_message:
            # Store the interaction in Memoripy
            combined_text = f"{user_message} {message}"
            embedding = self.memory_manager.get_embedding(combined_text)
            concepts = self.memory_manager.extract_concepts(combined_text)

            try:
                self.memory_manager.add_interaction(user_message, message, embedding, concepts)
            except Exception as e:
                print(f"Failed to add interaction to Memoripy: {e}")

    def add_execution_result(self, code: str, language: str, output: str, error: str, success: bool) -> None:
        """Add an execution result to the memory.

        Args:
            code: The code that was executed.
            language: The language of the code.
            output: The output of the execution.
            error: Any error messages from the execution.
            success: Whether the execution was successful.
        """
        content = f"Code execution ({language}):\n{code}\nSuccess: {success}\nOutput: {output}\nError: {error}"
        msg = {
            "role": "system",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "type": "execution_result",
                "language": language,
                "success": success
            }
        }
        self.history.append(msg)

        # Add a summary to long-term memory
        summary = f"Executed {language} code: {code[:50]}{'...' if len(code) > 50 else ''}. Result: {'Success' if success else 'Failure'}"
        self.add_memory(summary, memory_type="execution")

    def add_memory(self, memory_text: str, memory_type: str = "general") -> None:
        """Add a custom memory to long-term storage.

        Args:
            memory_text: The memory text to add.
            memory_type: The type of memory (e.g., "general", "execution", "search").
        """
        # We'll use the memory text directly without formatting

        # Store in Memoripy
        try:
            embedding = self.memory_manager.get_embedding(memory_text)
            concepts = self.memory_manager.extract_concepts(memory_text)
            self.memory_manager.add_interaction(
                f"Remember this {memory_type} information",
                memory_text,
                embedding,
                concepts
            )
        except Exception as e:
            print(f"Failed to add memory to Memoripy: {e}")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history in a format suitable for the Ollama API.

        Returns:
            The conversation history.
        """
        # Filter out system messages for the conversation history
        return [{
            "role": msg["role"],
            "content": msg["content"]
        } for msg in self.history if msg["role"] != "system"]

    def get_full_history(self) -> List[Dict[str, Any]]:
        """Get the full history including system messages.

        Returns:
            The full history.
        """
        return self.history

    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant memories based on the query.

        Args:
            query: The search query.
            limit: The maximum number of memories to return.

        Returns:
            A list of relevant memories.
        """
        try:
            # Load the last few interactions for context
            short_term, _ = self.memory_manager.load_history()
            last_interactions = short_term[-5:] if len(short_term) >= 5 else short_term

            # Retrieve relevant past interactions
            relevant_interactions = self.memory_manager.retrieve_relevant_interactions(
                query,
                exclude_last_n=len(last_interactions)
            )

            # Apply limit if needed
            if limit and len(relevant_interactions) > limit:
                relevant_interactions = relevant_interactions[:limit]

            # Format the results
            results = []
            for interaction in relevant_interactions:
                # Extract prompt and response
                prompt = interaction.get('prompt', '')
                response = interaction.get('response', '')

                # Create memory entry
                results.append({
                    "memory": f"User: {prompt}\nAssistant: {response}",
                    "timestamp": interaction.get("timestamp", datetime.now().isoformat()),
                    "relevance": interaction.get("relevance", 0.0)
                })

            return results
        except Exception as e:
            print(f"Failed to search memories in Memoripy: {e}")
            return []

    def generate_response_with_memory(self, prompt: str) -> str:
        """Generate a response using the memory system.

        Args:
            prompt: The user prompt.

        Returns:
            The generated response.
        """
        try:
            # Load the last 5 interactions from history (for context)
            short_term, _ = self.memory_manager.load_history()
            last_interactions = short_term[-5:] if len(short_term) >= 5 else short_term

            # Retrieve relevant past interactions, excluding the last 5
            relevant_interactions = self.memory_manager.retrieve_relevant_interactions(
                prompt,
                exclude_last_n=5
            )

            # Generate a response using the last interactions and retrieved interactions
            response = self.memory_manager.generate_response(
                prompt,
                last_interactions,
                relevant_interactions
            )

            return response
        except Exception as e:
            print(f"Failed to generate response with Memoripy: {e}")
            return "I apologize, but I'm having trouble accessing my memory at the moment."


# Global memory instance
_memory = None

def get_memory(use_persistent_storage: bool = True) -> MemoriyMemory:
    """Get the global memory instance.

    Args:
        use_persistent_storage: Whether to use persistent storage for memories.

    Returns:
        The global memory instance.
    """
    global _memory

    if _memory is None:
        _memory = MemoriyMemory(use_persistent_storage=use_persistent_storage)

    return _memory
