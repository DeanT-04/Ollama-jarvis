# Jarvis CLI

A command-line interface (CLI) for an AI assistant named Jarvis, powered by a local Ollama model.

## Features

- Understands user requests via natural language
- Executes Bash or Python code within a dedicated safe workspace
- Self-corrects when code execution fails
- Maintains conversation memory using mem0ai
- Retrieves relevant memories to provide context-aware responses
- Workspace awareness: Jarvis knows the current state of its workspace
- Web search capability: Jarvis can search the web for information when needed
- MCP integration: Jarvis exposes tools and resources via the Model Context Protocol

## Setup

1. Ensure you have an Ollama server running locally
2. Create a virtual environment and install the required dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure the environment variables (optional):
   - Copy `.env.example` to `.env`
   - Modify the values as needed
   - If you're using the Mem0 platform, set your API key
4. Run the Jarvis CLI:
   ```
   python jarvis_cli.py
   ```

5. (Optional) Run the Jarvis MCP server:
   ```
   python mcp_tools.py
   ```
   This will start an MCP server that exposes Jarvis tools and resources to LLM applications.

## Security Warning

**IMPORTANT**: This initial implementation executes code directly, which poses significant security risks. Future versions will implement proper sandboxing (e.g., using Docker).
