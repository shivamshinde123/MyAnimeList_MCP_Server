import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
mcp = FastMCP("MAL_MCP_Server")