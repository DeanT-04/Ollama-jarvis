# Search Tools

This document describes the search tools available in Jarvis.

## Perplexica Search

Jarvis integrates with [Perplexica](https://github.com/ItzCrazyKns/Perplexica), an AI-powered search engine that provides high-quality search results with source citations. Perplexica uses advanced machine learning algorithms to understand your questions and find relevant information on the web.

### Configuration

To use the Perplexica search tools, you need to configure the following settings in your environment variables or `.env` file:

```
PERPLEXICA_URL=http://localhost:3000
PERPLEXICA_CHAT_MODEL_PROVIDER=ollama
PERPLEXICA_CHAT_MODEL_NAME=llama3.2
PERPLEXICA_EMBEDDING_MODEL_PROVIDER=ollama
PERPLEXICA_EMBEDDING_MODEL_NAME=llama3.2
PERPLEXICA_FOCUS_MODE=webSearch
PERPLEXICA_OPTIMIZATION_MODE=balanced
```

### Available Search Tools

Jarvis provides several search tools that use Perplexica:

1. **Web Search**: Search the web for general information.
   ```python
   result = search_web("What is quantum computing?")
   ```

2. **Academic Search**: Search for academic papers and articles.
   ```python
   result = search_academic("Recent advances in machine learning")
   ```

3. **YouTube Search**: Search for videos on YouTube.
   ```python
   result = search_youtube("Python tutorial for beginners")
   ```

4. **Reddit Search**: Search for discussions on Reddit.
   ```python
   result = search_reddit("Best programming languages to learn in 2025")
   ```

5. **Wolfram Alpha Search**: Search for calculations and data analysis.
   ```python
   result = search_wolfram_alpha("Solve x^2 + 5x + 6 = 0")
   ```

6. **Writing Assistant**: Get writing assistance without searching the web.
   ```python
   result = writing_assistant("Write a professional email requesting a meeting")
   ```

### Search Result Format

All search tools return results in the following format:

```python
{
    "success": True,  # Whether the search was successful
    "message": "...",  # The search result text
    "sources": [  # List of sources used to generate the result
        {
            "pageContent": "...",  # Content snippet from the source
            "metadata": {
                "title": "...",  # Title of the source
                "url": "..."  # URL of the source
            }
        },
        # More sources...
    ]
}
```

If an error occurs, the result will have `"success": False` and an `"error"` field with the error message.

### Using Search Tools in Jarvis

The search tools are registered with Jarvis's Tool Registry and can be used by Jarvis to find information on the web. For example:

```python
from jarvis.core.tool_registry import get_registry

# Get the registry
registry = get_registry()

# Call the search_web tool
result = registry.call_tool("search_web", query="What is artificial intelligence?")

# Print the result
print(result["message"])

# Print the sources
for source in result["sources"]:
    print(f"Source: {source['metadata']['title']}")
    print(f"URL: {source['metadata']['url']}")
    print(f"Content: {source['pageContent']}")
    print()
```

## Setting Up Perplexica

To use the Perplexica search tools, you need to set up Perplexica. Follow these steps:

1. Clone the Perplexica repository:
   ```bash
   git clone https://github.com/ItzCrazyKns/Perplexica.git
   ```

2. Follow the installation instructions in the [Perplexica README](https://github.com/ItzCrazyKns/Perplexica#installation).

3. Start Perplexica:
   ```bash
   docker compose up -d
   ```

4. Configure Jarvis to use Perplexica by setting the `PERPLEXICA_URL` environment variable to the URL of your Perplexica instance (default: `http://localhost:3000`).

5. Test the connection by using one of the search tools in Jarvis.

## Troubleshooting

If you encounter issues with the Perplexica search tools, check the following:

1. Make sure Perplexica is running and accessible at the URL specified in the `PERPLEXICA_URL` environment variable.

2. Check the Perplexica logs for any errors:
   ```bash
   docker compose logs
   ```

3. Verify that the models specified in the configuration are available in your Perplexica instance.

4. If you're using Ollama models, make sure Ollama is running and accessible from Perplexica.

5. Check the Jarvis logs for any errors related to the Perplexica client or search tools.
