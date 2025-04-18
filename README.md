# Jarvis CLI

A command-line interface (CLI) for an AI assistant named Jarvis, powered by a local Ollama model.

## Features

- Understands user requests via natural language
- Executes Bash or Python code within a dedicated safe workspace
- Self-corrects when code execution fails
- Maintains conversation memory

## Setup

1. Ensure you have an Ollama server running locally
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Jarvis CLI:
   ```
   python jarvis_cli.py
   ```

## Security Warning

**IMPORTANT**: This initial implementation executes code directly, which poses significant security risks. Future versions will implement proper sandboxing (e.g., using Docker).
