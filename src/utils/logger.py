import logging

# configure logging 
logger = logging.getLogger("MAL_MCPServer")
logger.setLevel(logging.DEBUG)

# File handler with DEBUG level
file_handler = logging.FileHandler("mal_mcp_server.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)