#!/usr/bin/env python3
"""
Perplexica search module for Jarvis CLI.

This module provides functions for searching the web using Perplexica,
an open-source AI-powered search engine.
"""

import os
import re
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PERPLEXICA_URL = os.getenv("PERPLEXICA_URL", "http://localhost:3000")
PERPLEXICA_SEARCH_ENDPOINT = f"{PERPLEXICA_URL}/api/search"
DEFAULT_CHAT_MODEL_PROVIDER = os.getenv("PERPLEXICA_CHAT_MODEL_PROVIDER", "ollama")
DEFAULT_CHAT_MODEL_NAME = os.getenv("PERPLEXICA_CHAT_MODEL_NAME", "llama3")
DEFAULT_EMBEDDING_MODEL_PROVIDER = os.getenv("PERPLEXICA_EMBEDDING_MODEL_PROVIDER", "ollama")
DEFAULT_EMBEDDING_MODEL_NAME = os.getenv("PERPLEXICA_EMBEDDING_MODEL_NAME", "llama3")
DEFAULT_FOCUS_MODE = os.getenv("PERPLEXICA_FOCUS_MODE", "webSearch")
DEFAULT_OPTIMIZATION_MODE = os.getenv("PERPLEXICA_OPTIMIZATION_MODE", "balanced")


class PerplexicaClient:
    """Client for interacting with the Perplexica API."""
    
    def __init__(self, base_url: str = PERPLEXICA_URL):
        """Initialize the Perplexica client.
        
        Args:
            base_url: The base URL of the Perplexica API.
        """
        self.base_url = base_url
        self.search_endpoint = f"{base_url}/api/search"
    
    def search(
        self,
        query: str,
        focus_mode: str = DEFAULT_FOCUS_MODE,
        chat_model_provider: str = DEFAULT_CHAT_MODEL_PROVIDER,
        chat_model_name: str = DEFAULT_CHAT_MODEL_NAME,
        embedding_model_provider: str = DEFAULT_EMBEDDING_MODEL_PROVIDER,
        embedding_model_name: str = DEFAULT_EMBEDDING_MODEL_NAME,
        optimization_mode: str = DEFAULT_OPTIMIZATION_MODE,
        system_instructions: Optional[str] = None,
        history: Optional[List[List[str]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Search using the Perplexica API.
        
        Args:
            query: The search query.
            focus_mode: The focus mode to use (webSearch, academicSearch, etc.).
            chat_model_provider: The provider for the chat model.
            chat_model_name: The name of the chat model.
            embedding_model_provider: The provider for the embedding model.
            embedding_model_name: The name of the embedding model.
            optimization_mode: The optimization mode (speed, balanced).
            system_instructions: Custom instructions for the AI.
            history: Conversation history.
            stream: Whether to stream the response.
            
        Returns:
            The search results.
        """
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
        
        if system_instructions:
            payload["systemInstructions"] = system_instructions
        
        if history:
            payload["history"] = history
        
        try:
            response = requests.post(self.search_endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching with Perplexica: {e}")
            # Fallback to mock response when Perplexica is unavailable
            return self._mock_search_response(query)
    
    def _mock_search_response(self, query: str) -> Dict[str, Any]:
        """Generate a mock search response when Perplexica is unavailable.
        
        Args:
            query: The search query.
            
        Returns:
            A mock search response.
        """
        return {
            "message": f"I searched for information about '{query}', but I couldn't connect to the search service. Here's what I know from my training:\n\n"
                      f"This is a mock response because the Perplexica search service is unavailable. "
                      f"Please ensure that Perplexica is running and accessible at {self.base_url}.",
            "sources": [
                {
                    "pageContent": "This is a mock search result because Perplexica is unavailable.",
                    "metadata": {
                        "title": "Mock Search Result",
                        "url": "https://example.com/mock-result"
                    }
                }
            ]
        }
    
    def format_search_results(self, results: Dict[str, Any]) -> str:
        """Format search results as a string.
        
        Args:
            results: The search results from Perplexica.
            
        Returns:
            A formatted string containing the search results.
        """
        if not results or "message" not in results:
            return "No search results found."
        
        formatted_results = results["message"]
        
        if "sources" in results and results["sources"]:
            formatted_results += "\n\n### Sources\n\n"
            for i, source in enumerate(results["sources"], 1):
                title = source.get("metadata", {}).get("title", "No title")
                url = source.get("metadata", {}).get("url", "No URL")
                formatted_results += f"{i}. [{title}]({url})\n"
        
        return formatted_results


def search_web(query: str, num_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search the web using Perplexica and return the results.
    
    Args:
        query: The search query.
        num_results: The number of results to return.
        
    Returns:
        A list of dictionaries containing the search results.
    """
    client = PerplexicaClient()
    results = client.search(query)
    
    if "sources" not in results or not results["sources"]:
        return []
    
    # Limit the number of sources to num_results
    sources = results["sources"][:num_results]
    
    # Convert to the format expected by the existing code
    formatted_sources = []
    for source in sources:
        formatted_source = {
            "title": source.get("metadata", {}).get("title", "No title"),
            "body": source.get("pageContent", "No content"),
            "href": source.get("metadata", {}).get("url", "No URL")
        }
        formatted_sources.append(formatted_source)
    
    return formatted_sources


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format the search results as a string.
    
    Args:
        results: The search results.
        
    Returns:
        A formatted string containing the search results.
    """
    if not results:
        return "No search results found."
    
    formatted_results = "### Search Results\n\n"
    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        body = result.get("body", "No content")
        href = result.get("href", "No URL")
        
        formatted_results += f"**Result {i}: {title}**\n"
        formatted_results += f"{body}\n"
        formatted_results += f"Source: {href}\n\n"
    
    return formatted_results


def extract_search_query(text: str) -> str:
    """
    Extract a search query from text.
    
    Args:
        text: The text to extract the search query from.
        
    Returns:
        The extracted search query, or an empty string if no query is found.
    """
    pattern = r"SEARCH_WEB:\s*\"([^\"]+)\""
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return ""


def is_search_request(text: str) -> bool:
    """
    Check if the text contains a search request.
    
    Args:
        text: The text to check.
        
    Returns:
        True if the text contains a search request, False otherwise.
    """
    return "SEARCH_WEB:" in text


def get_available_focus_modes() -> List[str]:
    """
    Get a list of available focus modes.
    
    Returns:
        A list of available focus modes.
    """
    return [
        "webSearch",
        "academicSearch",
        "writingAssistant",
        "wolframAlphaSearch",
        "youtubeSearch",
        "redditSearch"
    ]


def get_focus_mode_description(focus_mode: str) -> str:
    """
    Get a description of a focus mode.
    
    Args:
        focus_mode: The focus mode.
        
    Returns:
        A description of the focus mode.
    """
    descriptions = {
        "webSearch": "Searches the entire web to find the best results.",
        "academicSearch": "Finds articles and papers, ideal for academic research.",
        "writingAssistant": "Helpful for writing tasks that do not require searching the web.",
        "wolframAlphaSearch": "Answers queries that need calculations or data analysis using Wolfram Alpha.",
        "youtubeSearch": "Finds YouTube videos based on the search query.",
        "redditSearch": "Searches Reddit for discussions and opinions related to the query."
    }
    
    return descriptions.get(focus_mode, "Unknown focus mode.")
