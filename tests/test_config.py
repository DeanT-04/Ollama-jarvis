#!/usr/bin/env python3
"""
Tests for the configuration module.
"""

import os
import unittest
from unittest.mock import patch

from jarvis.config import load_config, get_config

class TestConfig(unittest.TestCase):
    """Test cases for the configuration module."""

    def test_default_config(self):
        """Test loading the default configuration."""
        config = load_config()

        # Check that the default values are set
        self.assertEqual(config["OLLAMA_API_BASE"], "http://localhost:11434")
        self.assertEqual(config["OLLAMA_MODEL"], "llama3.2")
        self.assertTrue(config["WEB_SEARCH_ENABLED"])
        self.assertEqual(config["WEB_SEARCH_MAX_RESULTS"], 3)

    @patch.dict(os.environ, {"OLLAMA_MODEL": "llama3"})
    def test_env_override(self):
        """Test that environment variables override default values."""
        config = load_config()

        # Check that the environment variable overrides the default
        self.assertEqual(config["OLLAMA_MODEL"], "llama3")

    @patch.dict(os.environ, {"MAX_RETRIES": "5"})
    def test_numeric_conversion(self):
        """Test that numeric strings are converted to integers."""
        config = load_config()

        # Check that the string is converted to an integer
        self.assertEqual(config["MAX_RETRIES"], 5)
        self.assertIsInstance(config["MAX_RETRIES"], int)

    @patch.dict(os.environ, {"WEB_SEARCH_ENABLED": "false"})
    def test_boolean_conversion(self):
        """Test that boolean strings are converted to booleans."""
        config = load_config()

        # Check that the string is converted to a boolean
        self.assertFalse(config["WEB_SEARCH_ENABLED"])
        self.assertIsInstance(config["WEB_SEARCH_ENABLED"], bool)

    @patch.dict(os.environ, {"OLLAMA_MODEL": "llama3"})
    def test_get_config(self):
        """Test getting a configuration value."""
        # Reset the CONFIG dictionary to force reloading
        from jarvis.config import CONFIG
        CONFIG.clear()

        # Get a value that exists
        value = get_config("OLLAMA_MODEL")
        self.assertEqual(value, "llama3")

        # Get a value with a default
        value = get_config("NONEXISTENT_KEY", "default_value")
        self.assertEqual(value, "default_value")

if __name__ == "__main__":
    unittest.main()
