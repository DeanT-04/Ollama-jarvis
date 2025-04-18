#!/usr/bin/env python3
"""
Web search module for Jarvis CLI.

This module provides functions for searching the web using a simple mock implementation.
"""

import re
from typing import List, Dict, Any

def search_web(query: str, num_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search the web and return the results (mock implementation).

    Args:
        query: The search query.
        num_results: The number of results to return.

    Returns:
        A list of dictionaries containing the search results.
    """
    # Mock implementation for testing
    results = [
        {
            "title": f"Result 1 for {query}",
            "body": f"This is a mock search result for the query: {query}. It contains some information that might be relevant to the user's question.",
            "href": "https://example.com/result1"
        },
        {
            "title": f"Result 2 for {query}",
            "body": f"Another mock search result with different information about {query}. This could help answer the user's question.",
            "href": "https://example.com/result2"
        },
        {
            "title": f"Result 3 for {query}",
            "body": f"A third mock result with additional details about {query}. This provides more context for the user.",
            "href": "https://example.com/result3"
        }
    ]
    return results[:num_results]

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
