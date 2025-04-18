# Jarvis

An autonomous AI assistant powered by local Ollama models with LLM-driven action generation, automated debugging loops, dynamic knowledge acquisition via web search (Perplexica), environment awareness, and step-by-step planning.

## Features

- **LLM-Driven Action Generation**: Generates Bash commands or Python code directly within standard markdown blocks
- **Automated Debugging Loop**: Captures errors, analyzes them, and attempts to correct code automatically
- **Dynamic Knowledge Acquisition**: Uses Perplexica for web search when it lacks information
- **Environment Awareness**: Maintains awareness of its workspace state
- **Step-by-Step Planning**: Breaks down complex tasks into manageable steps
- **Memory System**: Maintains conversation history and execution results
- **MCP Integration**: Exposes tools and resources via the Model Context Protocol

## Project Structure

```
├── jarvis/              # Main package directory
│   ├── core/            # Core functionality
│   │   ├── executor.py  # Code execution
│   │   ├── memory.py    # Memory management
│   │   └── ollama.py    # Ollama client
│   ├── tools/           # Tools and integrations
│   │   ├── mcp_integration.py  # MCP integration
│   │   ├── search.py    # Web search functionality
│   │   └── workspace.py # Workspace utilities
│   └── utils/           # Utility functions
│       └── parsing.py   # Text parsing utilities
├── tests/               # Test directory
├── jarvis_workspace/    # Workspace directory
├── main.py              # Entry point script
└── mcp_server.py        # MCP server script
```

## Setup

1. Ensure you have an Ollama server running locally
2. Clone the Perplexica repository:
   ```
   git clone https://github.com/ItzCrazyKns/Perplexica.git
   ```
3. Create a virtual environment and install the required dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Configure the environment variables (optional):
   - Copy `.env.example` to `.env`
   - Modify the values as needed
   - If you're using the Mem0 platform, set your API key
5. Run the Jarvis CLI:
   ```
   python main.py
   ```

6. (Optional) Run the Jarvis MCP server:
   ```
   python mcp_server.py
   ```
   This will start an MCP server that exposes Jarvis tools and resources to LLM applications.

## Security Warning

**IMPORTANT**: This implementation executes code directly, which poses significant security risks. Future versions will implement proper sandboxing (e.g., using Docker).

## Testing

To run the tests:

```
python -m unittest discover tests
```
