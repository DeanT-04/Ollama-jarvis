#!/usr/bin/env python3
"""
Test script for the web search functionality in Jarvis CLI.

This script tests the basic functionality of the web search module,
including searching the web and formatting the results.
"""

from web_search import search_web, format_search_results

def main():
    """Main function to test the web search functionality."""
    print("Testing web search functionality...")
    
    # Test search query
    query = "How to install Python on Windows"
    
    # Perform the search
    print(f"Searching for: {query}")
    results = search_web(query, num_results=2)
    
    # Print the results
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Title: {result.get('title', 'No title')}")
        print(f"Body: {result.get('body', 'No content')[:100]}...")
        print(f"URL: {result.get('href', 'No URL')}")
    
    # Format the results
    formatted_results = format_search_results(results)
    
    # Print the formatted results
    print("\nFormatted results:")
    print(formatted_results)
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
