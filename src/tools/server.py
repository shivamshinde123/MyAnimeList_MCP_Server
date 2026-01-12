from fastapi import FastAPI
from src.tools.config import mcp

# Import tool modules to register them with the MCP server
import src.tools.anime_related_tools
import src.tools.manga_related_tools  
import src.tools.producer_related_tools

def main():
    """Run the MCP server with streamable HTTP transport."""
    # mcp.run(transport="streamable-http")
    mcp.run(transport="stdio")
