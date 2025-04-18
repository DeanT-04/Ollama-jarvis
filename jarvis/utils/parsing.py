#!/usr/bin/env python3
"""
Parsing utilities for Jarvis.

This module provides functions for parsing text, extracting code blocks,
and handling search requests.
"""

import re
from typing import List, Tuple, Optional

def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
    """Extract code blocks from the text.

    Args:
        text: The text to extract code blocks from.

    Returns:
        A list of tuples (language, code).
    """
    pattern = r"```(\w+)\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    # Clean up the code blocks by stripping leading/trailing whitespace
    cleaned_matches = []
    for language, code in matches:
        # Strip leading/trailing whitespace from each line and join
        cleaned_code = "\n".join([line.strip() for line in code.strip().split("\n")])
        cleaned_matches.append((language, cleaned_code))

    return cleaned_matches


def extract_search_query(text: str) -> str:
    """Extract a search query from text.

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
    """Check if the text contains a search request.

    Args:
        text: The text to check.

    Returns:
        True if the text contains a search request, False otherwise.
    """
    return "SEARCH_WEB:" in text


def extract_focus_mode(text: str) -> Optional[str]:
    """Extract a focus mode from text.

    Args:
        text: The text to extract the focus mode from.

    Returns:
        The extracted focus mode, or None if no focus mode is found.
    """
    pattern = r"FOCUS_MODE:\s*([\w]+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None
