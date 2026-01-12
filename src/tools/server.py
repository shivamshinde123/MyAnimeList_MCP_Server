from fastapi import FastAPI
from src.tools.config import mcp
from src.utils.logger import logger

# Import tool modules to register them with the MCP server
import src.tools.anime_related_tools
import src.tools.manga_related_tools  
import src.tools.producer_related_tools

def main() -> None:
    """Run the MyAnimeList MCP server with stdio transport.
    
    This function starts the MyAnimeList MCP server that provides comprehensive
    access to MyAnimeList data through the Jikan API. The server includes tools
    for anime search, manga search, reviews, recommendations, news, and producer
    information.
    
    The server runs with stdio transport for compatibility with MCP clients
    like Claude Desktop, VS Code extensions, and other MCP-compatible applications.
    
    Available Tools:
        - search_anime: Search for anime with filters
        - get_top_anime: Get top-ranked anime
        - get_random_anime: Get random anime recommendations
        - get_anime_reviews: Get user reviews for anime
        - get_similar_anime: Get anime recommendations
        - get_anime_news: Get latest anime news
        - get_seasonal_anime: Get anime from specific seasons
        - search_manga: Search for manga with filters
        - get_top_manga: Get top-ranked manga
        - get_random_manga: Get random manga recommendations
        - get_manga_reviews: Get user reviews for manga
        - get_similar_manga: Get manga recommendations
        - get_manga_news: Get latest manga news
        - get_producer_details: Get information about anime producers/studios
    
    Raises:
        Exception: If there's an error starting the server
    
    Example:
        # Run the server
        main()
    """
    logger.info("Starting MyAnimeList MCP Server...")
    logger.info("Available tools: anime search, manga search, reviews, recommendations, news, and more")
    
    try:
        # Run with stdio transport for MCP client compatibility
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        raise
