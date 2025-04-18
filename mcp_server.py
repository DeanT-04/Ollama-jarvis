#!/usr/bin/env python3
"""
MCP server for Jarvis.

This script provides a Model Context Protocol (MCP) server for Jarvis,
allowing it to expose tools and resources to LLM applications.
"""

import argparse
from jarvis.tools.mcp_integration import JarvisMCPServer

def parse_args():
    """Parse command-line arguments.
    
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Jarvis MCP Server")
    parser.add_argument("--name", default="jarvis-mcp", help="Name of the MCP server")
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Create and run the MCP server
    server = JarvisMCPServer(name=args.name)
    server.run()

if __name__ == "__main__":
    main()
