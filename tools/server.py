
import os
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

mcp = FastMCP("MAL_MCP_Server", stateless_http=True)
app = FastAPI()
app.mount("/mal_mcp", mcp.streamable_http_app())


def main():
    """Run the MCP server with streamable HTTP transport."""
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    """Entry point for running the MCP server."""
    main()