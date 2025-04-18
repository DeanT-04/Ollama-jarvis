#!/usr/bin/env python3
"""
Search tools for Jarvis.

This module provides tools for searching the web and other sources.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from jarvis.core.tool_registry import tool
from jarvis.tools.perplexica_client import PerplexicaClient, PerplexicaError

# Set up logging
logger = logging.getLogger(__name__)

# Global Perplexica client instance
_perplexica_client = None

def get_perplexica_client() -> PerplexicaClient:
    """Get the Perplexica client instance.
    
    Returns:
        The Perplexica client instance.
    """
    global _perplexica_client
    
    if _perplexica_client is None:
        _perplexica_client = PerplexicaClient()
    
    return _perplexica_client

@tool(description="Search the web for information.", category="search", required=False)
def search_web(query: str, focus_mode: str = "webSearch") -> Dict[str, Any]:
    """Search the web for information using Perplexica.
    
    Args:
        query: The search query.
        focus_mode: The focus mode to use. Available modes: webSearch, academicSearch,
            writingAssistant, wolframAlphaSearch, youtubeSearch, redditSearch.
            
    Returns:
        A dictionary containing the search results.
    """
    try:
        # Get the Perplexica client
        client = get_perplexica_client()
        
        # Perform the search
        result = client.search(query=query, focus_mode=focus_mode)
        
        return {
            "success": True,
            "message": result.get("message", ""),
            "sources": result.get("sources", [])
        }
    except PerplexicaError as e:
        logger.error(f"Error searching the web: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error searching the web: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

@tool(description="Search for academic information.", category="search", required=False)
def search_academic(query: str) -> Dict[str, Any]:
    """Search for academic information using Perplexica.
    
    Args:
        query: The search query.
            
    Returns:
        A dictionary containing the search results.
    """
    return search_web(query, focus_mode="academicSearch")

@tool(description="Search YouTube for videos.", category="search", required=False)
def search_youtube(query: str) -> Dict[str, Any]:
    """Search YouTube for videos using Perplexica.
    
    Args:
        query: The search query.
            
    Returns:
        A dictionary containing the search results.
    """
    return search_web(query, focus_mode="youtubeSearch")

@tool(description="Search Reddit for discussions.", category="search", required=False)
def search_reddit(query: str) -> Dict[str, Any]:
    """Search Reddit for discussions using Perplexica.
    
    Args:
        query: The search query.
            
    Returns:
        A dictionary containing the search results.
    """
    return search_web(query, focus_mode="redditSearch")

@tool(description="Search Wolfram Alpha for calculations and data analysis.", category="search", required=False)
def search_wolfram_alpha(query: str) -> Dict[str, Any]:
    """Search Wolfram Alpha for calculations and data analysis using Perplexica.
    
    Args:
        query: The search query.
            
    Returns:
        A dictionary containing the search results.
    """
    return search_web(query, focus_mode="wolframAlphaSearch")

@tool(description="Get writing assistance without searching the web.", category="search", required=False)
def writing_assistant(query: str) -> Dict[str, Any]:
    """Get writing assistance without searching the web using Perplexica.
    
    Args:
        query: The writing prompt or question.
            
    Returns:
        A dictionary containing the results.
    """
    return search_web(query, focus_mode="writingAssistant")
