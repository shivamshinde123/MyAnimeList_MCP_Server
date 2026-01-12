import logging

def setup_logger(name: str = "MAL_MCPServer", log_file: str = "mal_mcp_server.log") -> logging.Logger:
    """Set up and configure a logger for the MyAnimeList MCP Server.
    
    This function creates a logger with both file and console handlers,
    configured with appropriate formatting for debugging and monitoring.
    
    Args:
        name (str): Name of the logger (default: "MAL_MCPServer")
        log_file (str): Path to the log file (default: "mal_mcp_server.log")
    
    Returns:
        logging.Logger: Configured logger instance ready for use
    
    Example:
        logger = setup_logger()
        logger.info("Server started successfully")
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers if function is called multiple times
    if logger.handlers:
        return logger
    
    # File handler with DEBUG level
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

# Configure default logger instance
logger = setup_logger()