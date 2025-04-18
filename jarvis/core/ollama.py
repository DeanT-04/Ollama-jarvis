#!/usr/bin/env python3
"""
Ollama client module for Jarvis.

This module provides a client for interacting with the Ollama API.
"""

import json
import requests
from typing import Dict, List, Any, Optional

from jarvis.config import get_config

class OllamaClient:
    """Client for interacting with the Ollama API."""

    def __init__(self, model: Optional[str] = None, api_base: Optional[str] = None):
        """Initialize the Ollama client.

        Args:
            model: The model to use for chat and completions.
            api_base: The base URL for the Ollama API.
        """
        self.model = model or get_config("OLLAMA_MODEL")
        self.api_base = api_base or get_config("OLLAMA_API_BASE")
        self.chat_api_url = f"{self.api_base}/api/chat"
        self.generate_api_url = f"{self.api_base}/api/generate"

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        stream: bool = False,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send a chat request to the Ollama API.

        Args:
            messages: The messages to send to the API.
            system: The system message to use.
            temperature: The temperature to use for generation.
            top_p: The top_p value to use for generation.
            top_k: The top_k value to use for generation.
            stream: Whether to stream the response.
            max_tokens: The maximum number of tokens to generate.

        Returns:
            The response from the API.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k
            }
        }

        if system:
            payload["system"] = system

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            if stream:
                return self._stream_chat(payload, messages)
            else:
                response = requests.post(self.chat_api_url, json=payload)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return self._mock_chat_response(messages)

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        stream: bool = False,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send a generate request to the Ollama API.

        Args:
            prompt: The prompt to send to the API.
            system: The system message to use.
            temperature: The temperature to use for generation.
            top_p: The top_p value to use for generation.
            top_k: The top_k value to use for generation.
            stream: Whether to stream the response.
            max_tokens: The maximum number of tokens to generate.

        Returns:
            The response from the API.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k
            }
        }

        if system:
            payload["system"] = system

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            if stream:
                return self._stream_generate(payload)
            else:
                response = requests.post(self.generate_api_url, json=payload)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return self._mock_generate_response(prompt)

    def _stream_chat(self, payload: Dict[str, Any], messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Stream a chat request to the Ollama API.

        Args:
            payload: The payload to send to the API.
            messages: The messages sent to the API.

        Returns:
            The combined response from the API.
        """
        try:
            response_text = ""
            with requests.post(self.chat_api_url, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        response_text += content
                        # Print the chunk to give immediate feedback
                        print(content, end="", flush=True)

            # Add a newline at the end for better formatting
            print()

            # Return the combined response
            return {
                "model": self.model,
                "created_at": "2023-01-01T00:00:00.000000Z",
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "done": True
            }
        except requests.exceptions.RequestException as e:
            print(f"\nError streaming chat response from Ollama: {e}")
            return self._mock_chat_response(messages)

    def _stream_generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Stream a generate request to the Ollama API.

        Args:
            payload: The payload to send to the API.

        Returns:
            The combined response from the API.
        """
        try:
            response_text = ""
            with requests.post(self.generate_api_url, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        response_text += chunk.get("response", "")
                        # Print the chunk to give immediate feedback
                        print(chunk.get("response", ""), end="", flush=True)

            # Add a newline at the end for better formatting
            print()

            # Return the combined response
            return {"response": response_text}
        except requests.exceptions.RequestException as e:
            print(f"\nError streaming response from Ollama: {e}")
            return self._mock_generate_response(payload.get("prompt", ""))

    def _mock_chat_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate a mock chat response when Ollama is unavailable.

        Args:
            messages: The messages sent to the API.

        Returns:
            A mock chat response.
        """
        last_message = messages[-1]["content"] if messages else ""

        return {
            "model": self.model,
            "created_at": "2023-01-01T00:00:00.000000Z",
            "message": {
                "role": "assistant",
                "content": f"I'm sorry, I couldn't connect to the Ollama API. Here's a mock response to your message: '{last_message}'. Please ensure that Ollama is running and accessible."
            },
            "done": True
        }

    def _mock_generate_response(self, prompt: str) -> Dict[str, Any]:
        """Generate a mock generate response when Ollama is unavailable.

        Args:
            prompt: The prompt sent to the API.

        Returns:
            A mock generate response.
        """
        return {
            "model": self.model,
            "created_at": "2023-01-01T00:00:00.000000Z",
            "response": f"I'm sorry, I couldn't connect to the Ollama API. Here's a mock response to your prompt: '{prompt}'. Please ensure that Ollama is running and accessible.",
            "done": True
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List the available models.

        Returns:
            A list of available models.
        """
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.exceptions.RequestException as e:
            print(f"Error listing models: {e}")
            return []

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a model.

        Args:
            model: The model to get information about.

        Returns:
            Information about the model.
        """
        try:
            response = requests.post(f"{self.api_base}/api/show", json={"model": model})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting model info: {e}")
            return {}


def format_chat_history(history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Format the chat history for the Ollama API.

    Args:
        history: The chat history.

    Returns:
        The formatted chat history.
    """
    formatted_history = []

    for message in history:
        role = message.get("role", "user")
        content = message.get("content", "")

        # Skip system messages
        if role == "system":
            continue

        formatted_history.append({
            "role": role,
            "content": content
        })

    return formatted_history
