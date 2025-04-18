#!/usr/bin/env python3
"""
Tests for the search tools module.
"""

import unittest
from unittest.mock import patch, MagicMock

from jarvis.tools.search_tools import (
    get_perplexica_client,
    search_web,
    search_academic,
    search_youtube,
    search_reddit,
    search_wolfram_alpha,
    writing_assistant
)

class TestSearchTools(unittest.TestCase):
    """Test cases for the search tools module."""
    
    def setUp(self):
        """Set up the test environment."""
        # Patch the PerplexicaClient class
        self.perplexica_client_patcher = patch("jarvis.tools.search_tools.PerplexicaClient")
        self.mock_perplexica_client_class = self.perplexica_client_patcher.start()
        
        # Configure the mock PerplexicaClient instance
        self.mock_perplexica_client = MagicMock()
        self.mock_perplexica_client_class.return_value = self.mock_perplexica_client
        
        # Configure the mock search method
        self.mock_perplexica_client.search.return_value = {
            "message": "Test message",
            "sources": [
                {
                    "pageContent": "Test content",
                    "metadata": {
                        "title": "Test title",
                        "url": "https://example.com"
                    }
                }
            ]
        }
        
        # Reset the global Perplexica client instance
        import jarvis.tools.search_tools
        jarvis.tools.search_tools._perplexica_client = None
    
    def tearDown(self):
        """Clean up after the tests."""
        # Stop the patcher
        self.perplexica_client_patcher.stop()
    
    def test_get_perplexica_client(self):
        """Test getting the Perplexica client instance."""
        # Get the Perplexica client instance
        client = get_perplexica_client()
        
        # Check that the PerplexicaClient class was called
        self.mock_perplexica_client_class.assert_called_once()
        
        # Check that the client instance is the mock instance
        self.assertEqual(client, self.mock_perplexica_client)
        
        # Get the client instance again
        client2 = get_perplexica_client()
        
        # Check that the PerplexicaClient class was not called again
        self.mock_perplexica_client_class.assert_called_once()
        
        # Check that the client instance is the same
        self.assertEqual(client2, client)
    
    def test_search_web(self):
        """Test searching the web."""
        # Search the web
        result = search_web("test query")
        
        # Check that the search method was called with the correct arguments
        self.mock_perplexica_client.search.assert_called_once_with(
            query="test query",
            focus_mode="webSearch"
        )
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Test message")
        self.assertEqual(len(result["sources"]), 1)
        self.assertEqual(result["sources"][0]["pageContent"], "Test content")
    
    def test_search_web_with_error(self):
        """Test searching the web with an error."""
        # Configure the mock search method to raise an exception
        self.mock_perplexica_client.search.side_effect = Exception("Test error")
        
        # Search the web
        result = search_web("test query")
        
        # Check the result
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Unexpected error: Test error")
    
    def test_search_academic(self):
        """Test searching for academic information."""
        # Search for academic information
        result = search_academic("test query")
        
        # Check that the search method was called with the correct arguments
        self.mock_perplexica_client.search.assert_called_once_with(
            query="test query",
            focus_mode="academicSearch"
        )
        
        # Check the result
        self.assertTrue(result["success"])
    
    def test_search_youtube(self):
        """Test searching YouTube."""
        # Search YouTube
        result = search_youtube("test query")
        
        # Check that the search method was called with the correct arguments
        self.mock_perplexica_client.search.assert_called_once_with(
            query="test query",
            focus_mode="youtubeSearch"
        )
        
        # Check the result
        self.assertTrue(result["success"])
    
    def test_search_reddit(self):
        """Test searching Reddit."""
        # Search Reddit
        result = search_reddit("test query")
        
        # Check that the search method was called with the correct arguments
        self.mock_perplexica_client.search.assert_called_once_with(
            query="test query",
            focus_mode="redditSearch"
        )
        
        # Check the result
        self.assertTrue(result["success"])
    
    def test_search_wolfram_alpha(self):
        """Test searching Wolfram Alpha."""
        # Search Wolfram Alpha
        result = search_wolfram_alpha("test query")
        
        # Check that the search method was called with the correct arguments
        self.mock_perplexica_client.search.assert_called_once_with(
            query="test query",
            focus_mode="wolframAlphaSearch"
        )
        
        # Check the result
        self.assertTrue(result["success"])
    
    def test_writing_assistant(self):
        """Test using the writing assistant."""
        # Use the writing assistant
        result = writing_assistant("test query")
        
        # Check that the search method was called with the correct arguments
        self.mock_perplexica_client.search.assert_called_once_with(
            query="test query",
            focus_mode="writingAssistant"
        )
        
        # Check the result
        self.assertTrue(result["success"])

if __name__ == "__main__":
    unittest.main()
