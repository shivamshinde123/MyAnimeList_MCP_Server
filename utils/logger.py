import logging
import sys

# configure logging 
logger = logging.geLogger("MAL_MCPServer")
logger.setLevel(logging.DEBUG)

# File handler with DEBUG level
file_handler = logging.FileHandler("mal_mcp_server.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.addHandler(file_handler)

# console handler with INFO level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.addHandler(console_handler)