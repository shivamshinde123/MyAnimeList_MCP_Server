import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

def load_environment_config() -> tuple[str, FastMCP]:
    """Load environment configuration and initialize MCP server.
    
    This function loads environment variables from .env file and creates
    a FastMCP server instance for the MyAnimeList MCP Server.
    
    Returns:
        tuple[str, FastMCP]: A tuple containing:
            - BASE_URL (str): The Jikan API base URL from environment variables
            - mcp (FastMCP): Configured FastMCP server instance
    
    Raises:
        ValueError: If BASE_URL environment variable is not set
    
    Example:
        base_url, server = load_environment_config()
    """
    load_dotenv()
    
    base_url = os.getenv("BASE_URL")
    if not base_url:
        raise ValueError("BASE_URL environment variable is required")
    
    mcp_server = FastMCP("MAL_MCP_Server")
    
    return base_url, mcp_server

# Load configuration
BASE_URL, mcp = load_environment_config()