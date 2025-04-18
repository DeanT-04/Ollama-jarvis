# Add Environment Awareness and Web Search Capabilities

## Overview
This PR enhances Jarvis CLI with two major capabilities:
1. **Environment Awareness**: Jarvis now understands its workspace state, allowing it to make more informed decisions based on existing files and directory structures.
2. **Web Search Integration**: Jarvis can now search the web for information when it lacks knowledge or encounters errors it can't solve on its own.

## Key Changes

### Web Search Functionality
- Added `web_search.py` module with DuckDuckGo search integration
- Implemented search query extraction and result formatting
- Integrated web search into the main conversation loop
- Enhanced error correction with web search capabilities

### Workspace Awareness
- Added `workspace_utils.py` module for workspace interaction
- Implemented functions to get workspace state, read files, and list directories
- Added workspace state information to the system prompt
- Allows Jarvis to reference and understand its environment

### Enhanced Error Handling
- Updated error handling to incorporate web search when needed
- Jarvis can now search for solutions to errors it encounters
- Improved self-correction loop with external knowledge

### Cross-Platform Compatibility
- Updated bash execution to work on Windows using PowerShell
- Improved platform detection and command execution

### Configuration
- Added new configuration options in .env files
- Added web search configuration parameters

## Testing
- Added test scripts for web search and workspace utilities
- Verified functionality on Windows platform

## Future Work
- Further integration with MCP SDK for tools
- Implement proper sandboxing for security
- Enhance web search with more sources and better filtering
