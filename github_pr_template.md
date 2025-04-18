# Integrate Perplexica for Enhanced Web Search Capabilities

## Overview

This PR replaces the current DuckDuckGo search implementation with Perplexica, an open-source AI-powered search engine. This change significantly enhances Jarvis CLI's web search capabilities, providing more reliable and feature-rich search functionality.

## Key Changes

### New Features
- **Perplexica Integration**: Replaced DuckDuckGo with Perplexica for web search
- **Multiple Search Modes**: Added support for different search modes (web, academic, videos, etc.)
- **Better Source Attribution**: Improved source attribution in search results
- **Enhanced Error Handling**: Added better error handling for search operations
- **Ollama Integration**: Configured Perplexica to use Ollama for local LLM capabilities

### Technical Changes
- Created a new `perplexica_search.py` module to replace `web_search.py`
- Implemented a `PerplexicaClient` class for interacting with the Perplexica API
- Updated `jarvis_cli.py` to use the new Perplexica client
- Added configuration options for Perplexica in `.env.example`
- Updated documentation to reflect the new search capabilities

## Implementation Details

### Perplexica Setup
- Perplexica is set up using Docker for easy deployment
- Configured to use Ollama for local LLM capabilities
- API endpoint is configurable via environment variables

### Search Functionality
- Implemented support for different search modes:
  - Web Search (default)
  - Academic Search
  - YouTube Search
  - Reddit Search
  - Wolfram Alpha Search
  - Writing Assistant Mode
- Added better formatting for search results
- Improved source attribution

### Error Handling
- Added proper error handling for Perplexica API calls
- Implemented fallback mechanisms for when Perplexica is unavailable
- Added better error reporting for search operations

## Testing

The following tests were performed to verify the integration:

1. **Basic Search**: Tested basic web search functionality
2. **Different Search Modes**: Tested each search mode to ensure they work correctly
3. **Error Handling**: Tested error handling by simulating API failures
4. **Performance**: Measured search performance compared to the previous implementation

## Documentation

Updated documentation to reflect the new search capabilities:

- Added information about Perplexica integration in the README
- Updated the `.env.example` file with Perplexica configuration options
- Added comments in the code to explain the new functionality

## Future Work

While this PR significantly enhances Jarvis CLI's web search capabilities, there are still areas for improvement:

1. **Caching**: Implement caching for search results to improve performance
2. **Rate Limiting**: Add rate limiting for Perplexica API calls
3. **User Preferences**: Allow users to set default search modes and other preferences
4. **Advanced Search Options**: Add support for more advanced search options

## Related Issues

This PR addresses the limitations identified in issue #XX (Jarvis CLI: Current Limitations and Perplexica Integration).

## Screenshots

[Include screenshots of the new search functionality in action]
