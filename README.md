# Jarvis CLI

A command-line interface (CLI) for an AI assistant named Jarvis, powered by a local Ollama model.

## Features

- Understands user requests via natural language
- Executes Bash or Python code within a dedicated safe workspace
- Self-corrects when code execution fails
- Maintains conversation memory using mem0ai
- Retrieves relevant memories to provide context-aware responses

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

## Security Warning

**IMPORTANT**: This initial implementation executes code directly, which poses significant security risks. Future versions will implement proper sandboxing (e.g., using Docker).
