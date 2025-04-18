#!/usr/bin/env python3
"""
Perplexica client for Jarvis.

This module provides a client for interacting with the Perplexica API.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union

import requests

from jarvis.config import get_config

# Set up logging
logger = logging.getLogger(__name__)

class PerplexicaClient:
    """Client for interacting with the Perplexica API."""

    def __init__(self, api_url: Optional[str] = None):
        """Initialize the Perplexica client.

        Args:
            api_url: The URL of the Perplexica API. If not provided, it will be
                loaded from the configuration.
        """
        self.api_url = api_url or get_config("PERPLEXICA_URL", "http://localhost:3000")
        self.search_endpoint = f"{self.api_url}/api/search"

    def search(self,
               query: str,
               focus_mode: str = "webSearch",
               chat_model_provider: str = "openai",
               chat_model_name: str = "gpt-4o-mini",
               embedding_model_provider: str = "openai",
               embedding_model_name: str = "text-embedding-3-large",
               optimization_mode: str = "balanced",
               system_instructions: Optional[str] = None,
               history: Optional[List[List[str]]] = None,
               stream: bool = False) -> Dict[str, Any]:
        """Search for information using Perplexica.

        Args:
            query: The search query.
            focus_mode: The focus mode to use. Available modes: webSearch, academicSearch,
                writingAssistant, wolframAlphaSearch, youtubeSearch, redditSearch.
            chat_model_provider: The provider for the chat model (e.g., openai, ollama).
            chat_model_name: The specific model from the chosen provider.
            embedding_model_provider: The provider for the embedding model.
            embedding_model_name: The specific embedding model.
            optimization_mode: The optimization mode (speed or balanced).
            system_instructions: Custom instructions to guide the AI's response.
            history: An array of message pairs representing the conversation history.
            stream: Whether to enable streaming responses.

        Returns:
            A dictionary containing the search results.

        Raises:
            PerplexicaError: If an error occurs during the search.
        """
        # Prepare the request payload
        payload = {
            "chatModel": {
                "provider": chat_model_provider,
                "name": chat_model_name
            },
            "embeddingModel": {
                "provider": embedding_model_provider,
                "name": embedding_model_name
            },
            "optimizationMode": optimization_mode,
            "focusMode": focus_mode,
            "query": query,
            "stream": stream
        }

        # Add optional parameters if provided
        if system_instructions:
            payload["systemInstructions"] = system_instructions

        if history:
            payload["history"] = history

        # Make the request
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.search_endpoint, json=payload, headers=headers)

            # Check if the request was successful
            response.raise_for_status()

            # If streaming is enabled, return the response object
            if stream:
                return {"stream": response}

            # Parse the response
            return response.json()

        except Exception as e:
            logger.error(f"Error searching with Perplexica: {str(e)}")
            raise PerplexicaError(f"Error searching with Perplexica: {str(e)}")

    def process_stream(self, stream_response: requests.Response) -> Dict[str, Any]:
        """Process a streaming response from Perplexica.

        Args:
            stream_response: The streaming response from Perplexica.

        Returns:
            A dictionary containing the processed response.

        Raises:
            PerplexicaError: If an error occurs while processing the stream.
        """
        try:
            # Initialize variables to store the response
            message = ""
            sources = []

            # Process each line in the stream
            for line in stream_response.iter_lines():
                if not line:
                    continue

                # Decode the line and parse the JSON
                data = json.loads(line.decode("utf-8"))

                # Process the data based on its type
                if data["type"] == "response":
                    message += data["data"]
                elif data["type"] == "sources":
                    sources = data["data"]
                elif data["type"] == "done":
                    break

            # Return the processed response
            return {
                "message": message,
                "sources": sources
            }

        except Exception as e:
            logger.error(f"Error processing Perplexica stream: {str(e)}")
            raise PerplexicaError(f"Error processing Perplexica stream: {str(e)}")


class PerplexicaError(Exception):
    """Exception raised for errors in the Perplexica client."""
    pass
