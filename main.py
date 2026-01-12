"""MyAnimeList MCP Server Entry Point.

This module serves as the main entry point for the MyAnimeList MCP Server.
It imports and runs the server configuration from src.tools.server.

Usage:
    python main.py
    
Or with uv:
    uv run main.py

The server provides comprehensive access to MyAnimeList data through
the Jikan API via Model Context Protocol (MCP) tools.
"""

import asyncio
import httpx
from src.tools.server import main

def run_server() -> None:
    """Run the MyAnimeList MCP Server.
    
    This function serves as the entry point for starting the MCP server.
    It delegates to the main() function in src.tools.server which handles
    the actual server initialization and startup.
    
    The server runs with stdio transport for compatibility with MCP clients
    like Claude Desktop, VS Code extensions, and other MCP-compatible tools.
    
    Raises:
        Exception: If there's an error starting the server
    """
    main()

if __name__ == "__main__":
    """Execute server startup when script is run directly.
    
    This block ensures the server only starts when the script is executed
    directly (not when imported as a module).
    """
    run_server()
