# Jarvis CLI: Current Limitations and Perplexica Integration

## Overview

This issue addresses the current limitations of Jarvis CLI and proposes integrating Perplexica as a replacement for DuckDuckGo to enhance the web search functionality.

## Current Limitations

### Web Search Functionality
- DuckDuckGo search is unreliable and often returns poor results
- No support for other search engines
- No caching mechanism for search results
- No rate limiting or error handling for search API calls
- No support for specialized searches (academic, videos, etc.)

### LLM Integration
- No fallback mechanism to other LLM providers when Ollama is unavailable
- No support for cloud-based LLMs (OpenAI, Anthropic, etc.)
- No model selection capability - hardcoded to use a single model
- No streaming support for responses
- No parameter customization (temperature, top_p, etc.)

### Code Execution
- No sandboxing or security measures
- Limited to Python and Bash only
- No resource limits (CPU, memory, etc.)
- No timeout mechanism for long-running processes
- No proper isolation between executions

### Memory Management
- Dependency on external mem0ai service
- No persistent storage for memories
- No memory organization or categorization
- No memory search or filtering capabilities
- No memory pruning or management

## Proposed Solution: Perplexica Integration

### Why Perplexica?
- Open-source AI-powered search engine
- More reliable and feature-rich search capabilities
- Support for different search modes (web, academic, videos, etc.)
- Integration with local LLMs via Ollama
- Active development and community support

### Integration Plan
1. Set up Perplexica using Docker
2. Configure Perplexica to use Ollama for local LLM capabilities
3. Create a Perplexica client for Jarvis CLI
4. Update Jarvis CLI to use the new Perplexica client
5. Test and refine the integration

### Benefits
- More reliable and accurate search results
- Support for specialized search modes
- Better integration with local LLMs
- Improved user experience
- Foundation for future enhancements

## Additional Improvements

Beyond the Perplexica integration, we should also consider addressing the following issues:

1. **Implement proper sandboxing** for code execution using Docker or similar technology
2. **Add support for multiple LLM providers** and model selection
3. **Implement streaming responses** for better user experience
4. **Enhance memory management** with persistent storage and better organization
5. **Improve error handling and recovery** throughout the codebase

## Next Steps

1. Review and approve this proposal
2. Create a detailed implementation plan
3. Implement the Perplexica integration
4. Test and refine the implementation
5. Document the new functionality
6. Release a new version of Jarvis CLI

## References
- [Perplexica GitHub Repository](https://github.com/ItzCrazyKns/Perplexica)
- [Perplexica API Documentation](https://github.com/ItzCrazyKns/Perplexica/tree/master/docs/API/SEARCH.md)
- [Ollama GitHub Repository](https://github.com/ollama/ollama)
