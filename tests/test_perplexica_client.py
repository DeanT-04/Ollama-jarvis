#!/usr/bin/env python3
"""
Tests for the Perplexica client module.
"""

import unittest
from unittest.mock import patch, MagicMock

from jarvis.tools.perplexica_client import PerplexicaClient, PerplexicaError

class TestPerplexicaClient(unittest.TestCase):
    """Test cases for the Perplexica client module."""

    def setUp(self):
        """Set up the test environment."""
        # Patch the requests.post method
        self.requests_post_patcher = patch("jarvis.tools.perplexica_client.requests.post")
        self.mock_post = self.requests_post_patcher.start()

        # Configure the mock response
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {
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
        self.mock_response.raise_for_status = MagicMock()
        self.mock_post.return_value = self.mock_response

        # Create a Perplexica client
        self.client = PerplexicaClient(api_url="http://test.perplexica.com")

    def tearDown(self):
        """Clean up after the tests."""
        # Stop the patcher
        self.requests_post_patcher.stop()

    def test_search(self):
        """Test searching with Perplexica."""
        # Perform a search
        result = self.client.search("test query")

        # Check that the requests.post method was called with the correct arguments
        self.mock_post.assert_called_once()
        args, kwargs = self.mock_post.call_args

        # Check the URL
        self.assertEqual(args[0], "http://test.perplexica.com/api/search")

        # Check the payload
        payload = kwargs["json"]
        self.assertEqual(payload["query"], "test query")
        self.assertEqual(payload["focusMode"], "webSearch")
        self.assertEqual(payload["chatModel"]["provider"], "openai")
        self.assertEqual(payload["chatModel"]["name"], "gpt-4o-mini")

        # Check the result
        self.assertEqual(result["message"], "Test message")
        self.assertEqual(len(result["sources"]), 1)
        self.assertEqual(result["sources"][0]["pageContent"], "Test content")

    def test_search_with_custom_parameters(self):
        """Test searching with custom parameters."""
        # Perform a search with custom parameters
        result = self.client.search(
            query="test query",
            focus_mode="academicSearch",
            chat_model_provider="ollama",
            chat_model_name="llama3",
            embedding_model_provider="ollama",
            embedding_model_name="llama3",
            optimization_mode="speed",
            system_instructions="Test instructions",
            history=[["human", "Hello"], ["assistant", "Hi"]]
        )

        # Check the payload
        payload = self.mock_post.call_args[1]["json"]
        self.assertEqual(payload["query"], "test query")
        self.assertEqual(payload["focusMode"], "academicSearch")
        self.assertEqual(payload["chatModel"]["provider"], "ollama")
        self.assertEqual(payload["chatModel"]["name"], "llama3")
        self.assertEqual(payload["embeddingModel"]["provider"], "ollama")
        self.assertEqual(payload["embeddingModel"]["name"], "llama3")
        self.assertEqual(payload["optimizationMode"], "speed")
        self.assertEqual(payload["systemInstructions"], "Test instructions")
        self.assertEqual(payload["history"], [["human", "Hello"], ["assistant", "Hi"]])

    def test_search_with_error(self):
        """Test searching with an error."""
        # Configure the mock post to raise an exception
        self.mock_post.side_effect = Exception("Test error")

        # Check that the search method raises a PerplexicaError
        with self.assertRaises(PerplexicaError):
            self.client.search("test query")

    def test_process_stream(self):
        """Test processing a streaming response."""
        # Configure the mock response for streaming
        mock_stream_response = MagicMock()
        mock_stream_response.iter_lines.return_value = [
            b'{"type":"init","data":"Stream connected"}',
            b'{"type":"sources","data":[{"pageContent":"Test content","metadata":{"title":"Test title","url":"https://example.com"}}]}',
            b'{"type":"response","data":"Test "}',
            b'{"type":"response","data":"message"}',
            b'{"type":"done"}'
        ]

        # Process the stream
        result = self.client.process_stream(mock_stream_response)

        # Check the result
        self.assertEqual(result["message"], "Test message")
        self.assertEqual(len(result["sources"]), 1)
        self.assertEqual(result["sources"][0]["pageContent"], "Test content")

    def test_process_stream_with_error(self):
        """Test processing a streaming response with an error."""
        # Configure the mock response to raise an exception
        mock_stream_response = MagicMock()
        mock_stream_response.iter_lines.side_effect = Exception("Test error")

        # Check that the process_stream method raises a PerplexicaError
        with self.assertRaises(PerplexicaError):
            self.client.process_stream(mock_stream_response)

if __name__ == "__main__":
    unittest.main()
