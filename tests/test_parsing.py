#!/usr/bin/env python3
"""
Tests for the parsing utilities.
"""

import unittest
from jarvis.utils.parsing import extract_code_blocks, extract_search_query, is_search_request, extract_focus_mode

class TestParsing(unittest.TestCase):
    """Test cases for the parsing utilities."""

    def test_extract_code_blocks(self):
        """Test extracting code blocks from text."""
        text = """
        Here's a Python script:

        ```python
        print("Hello, world!")
        ```

        And here's a Bash script:

        ```bash
        echo "Hello, world!"
        ```
        """

        code_blocks = extract_code_blocks(text)
        self.assertEqual(len(code_blocks), 2)
        self.assertEqual(code_blocks[0][0], "python")
        self.assertEqual(code_blocks[0][1], 'print("Hello, world!")')
        self.assertEqual(code_blocks[1][0], "bash")
        self.assertEqual(code_blocks[1][1], 'echo "Hello, world!"')

    def test_extract_search_query(self):
        """Test extracting a search query from text."""
        text = 'I need to search for information about climate change. SEARCH_WEB: "latest climate change findings"'
        query = extract_search_query(text)
        self.assertEqual(query, "latest climate change findings")

        # Test with no search query
        text = "This text doesn't contain a search query."
        query = extract_search_query(text)
        self.assertEqual(query, "")

    def test_is_search_request(self):
        """Test checking if text contains a search request."""
        text = 'I need to search for information about climate change. SEARCH_WEB: "latest climate change findings"'
        self.assertTrue(is_search_request(text))

        # Test with no search request
        text = "This text doesn't contain a search request."
        self.assertFalse(is_search_request(text))

    def test_extract_focus_mode(self):
        """Test extracting a focus mode from text."""
        text = 'I need to search for academic papers. SEARCH_WEB: "quantum computing" FOCUS_MODE: academicSearch'
        focus_mode = extract_focus_mode(text)
        self.assertEqual(focus_mode, "academicSearch")

        # Test with no focus mode
        text = 'I need to search for information. SEARCH_WEB: "quantum computing"'
        focus_mode = extract_focus_mode(text)
        self.assertIsNone(focus_mode)

if __name__ == "__main__":
    unittest.main()
