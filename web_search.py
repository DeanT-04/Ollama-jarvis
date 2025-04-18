#!/usr/bin/env python3
"""
Web search module for Jarvis CLI.

This module provides functions for searching the web using DuckDuckGo.
"""

import re
from typing import List, Dict, Any
from duckduckgo_search import DDGS

def search_web(query: str, num_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo and return the results.
    
    Args:
        query: The search query.
        num_results: The number of results to return.
        
    Returns:
        A list of dictionaries containing the search results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
        return results
    except Exception as e:
        print(f"Error searching the web: {e}")
        return []

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
