# Perplexica Integration Plan for Jarvis CLI

## Overview

This document outlines the plan for integrating Perplexica as a replacement for DuckDuckGo in the Jarvis CLI web search functionality. Perplexica offers more reliable and feature-rich search capabilities, which will enhance Jarvis CLI's ability to find and process information.

## Integration Steps

### 1. Setup Perplexica

#### 1.1 Install and Configure Perplexica
- Set up Perplexica using Docker (recommended approach)
- Configure Perplexica to use Ollama for local LLM capabilities
- Ensure Perplexica is accessible via its API

#### 1.2 Test Perplexica API
- Verify that Perplexica API is working correctly
- Test different search modes and parameters
- Document API usage patterns for integration

### 2. Create Perplexica Client for Jarvis CLI

#### 2.1 Develop Perplexica API Client
- Create a new module `perplexica_search.py` to replace `web_search.py`
- Implement functions to interact with Perplexica API
- Support different search modes (web, academic, etc.)
- Handle API responses and error conditions

#### 2.2 Implement Search Result Processing
- Parse and format search results from Perplexica
- Extract relevant information from search results
- Format results for presentation to the user

### 3. Integrate with Jarvis CLI

#### 3.1 Update Jarvis CLI to Use Perplexica
- Modify `jarvis_cli.py` to use the new Perplexica client
- Update the search request handling logic
- Implement support for different search modes

#### 3.2 Enhance User Experience
- Add support for selecting search modes
- Improve result presentation
- Add progress indicators for search operations

### 4. Test and Refine

#### 4.1 Test Integration
- Test basic search functionality
- Test different search modes
- Test error handling and recovery
- Test performance and reliability

#### 4.2 Refine Implementation
- Address any issues identified during testing
- Optimize performance
- Improve error handling
- Enhance user experience

## Implementation Details

### Perplexica API Client

```python
# perplexica_search.py

import requests
from typing import List, Dict, Any, Optional

class PerplexicaClient:
    """Client for interacting with the Perplexica API."""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        """Initialize the Perplexica client.
        
        Args:
            base_url: The base URL of the Perplexica API.
        """
        self.base_url = base_url
        self.search_endpoint = f"{base_url}/api/search"
    
    def search(
        self,
        query: str,
        focus_mode: str = "webSearch",
        chat_model_provider: str = "ollama",
        chat_model_name: str = "llama3",
        embedding_model_provider: str = "ollama",
        embedding_model_name: str = "llama3",
        optimization_mode: str = "balanced",
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
            return {
                "message": f"Error searching with Perplexica: {e}",
                "sources": []
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
    import re
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
```

### Integration with Jarvis CLI

The integration with Jarvis CLI will involve updating the imports and function calls in `jarvis_cli.py` to use the new Perplexica client instead of the DuckDuckGo search functionality.

## Conclusion

Integrating Perplexica as a replacement for DuckDuckGo will significantly enhance Jarvis CLI's web search capabilities. Perplexica offers more reliable and feature-rich search, which will improve the quality of information Jarvis can provide to users. This integration is a key step in addressing the limitations identified in the current implementation of Jarvis CLI.
