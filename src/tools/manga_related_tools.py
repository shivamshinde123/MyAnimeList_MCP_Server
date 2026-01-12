
import httpx

from src.utils.logger import logger
from src.tools.config import mcp, BASE_URL
from src.models.manga_models import (
    MangaNewsResponse, TopMangaParams, TopMangaResponse, RandomMangaResponse, MangaReviewParams,
    MangaReviewResponse, MangaSearchParams, MangaSearchResponse, SimilarMangaResponse
)

@mcp.tool()
async def search_manga(params: MangaSearchParams):
    """Search for manga on MyAnimeList based on a query string and optional filters.
    
    This tool searches for manga using the provided query and applies optional filters
    like status, ordering, and date ranges. The query parameter is required.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - This API is UNRELIABLE and often returns incorrect or irrelevant results
    - DO NOT use this tool to find MAL IDs for other tools (get_similar_manga, get_manga_reviews, get_manga_news)
    - For finding MAL IDs: ALWAYS use web_search("{manga_name} MyAnimeList ID") instead
    
    When to Use This Tool:
      Searching for manga by keywords/themes (e.g., "fantasy manga", "horror manga")
      Exploring manga by genre, author, or other filters
      Finding manga you don't know the exact name of
    
    When not to Use This Tool
      Getting MAL IDs for other tools (use web_search instead)
      Finding specific well-known manga (use web_search instead)
    
    Example:
      User asks: "Find manga about samurai"
      CORRECT: search_manga(params={"query": "samurai"})
      
      User asks: "Find manga similar to Berserk"
      WRONG: search_manga("Berserk") then get_similar_manga(result)
      CORRECT: web_search("Berserk MyAnimeList ID") → get_similar_manga(id)
    
    Args:
        params (MangaSearchParams): Search parameters including:
            - query (str): REQUIRED - The search term (manga title or keywords)
            - limit (int): Number of results to return (default: 5, max: 25)
            - status (str): Filter by manga status - 'airing' (currently publishing), 'complete' (finished), 'upcoming' (not yet published)
            - order_by (str): Sort results by - 'mal_id', 'title', 'start_date', 'end_date', 'volumes', 'score', 'rank', 'popularity'
            - sort (str): Sort direction - 'desc' or 'asc'
            - start_date (str): Filter manga that started after this date (YYYY-MM-DD)
            - end_date (str): Filter manga that ended before this date (YYYY-MM-DD)
    
    Returns:
        List[MangaSearchResponse]: List of manga matching search criteria with
                                 detailed information including MAL ID, title,
                                 volumes, status, currently publishing or not, start_date, end_date,
                                 score, scored_by, rank, popularity, favorites, synopsis, background,
                                 author_ids list, author_names list, genre_ids list, genre_names list
    
    Raises:
        Exception: If there's an error fetching search results from the API.
    """

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            # convert pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            try:
                response = await client.get(f"{BASE_URL}/manga", params=query_params)
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/manga timed out")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error occurred while requesting {e.request.url}: {e}")
                raise

            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from API: {e}")

            mangalist = response_data.get('data', [])

            if not isinstance(mangalist, list):
                logger.error(f"Expected 'data' to be a list, got {type(mangalist)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [MangaSearchResponse(
                mal_id = manga.get('mal_id', 0),
                title = manga.get('title_english', ''),
                volumes = manga.get('volumes', 0),
                status = manga.get('status', ''),
                publishing = manga.get('publishing', False),
                start_date = manga.get('published', {}).get('from', ''),
                end_date = manga.get('published', {}).get('to', ''),
                score = manga.get('score', 0.0),
                scored_by = manga.get('scored_by', 0),
                rank = manga.get('rank', 0),
                popularity = manga.get('popularity', 0),
                favorites = manga.get('favorites', 0),
                synopsis = manga.get('synopsis', ''),
                background = manga.get('background', ''),
                authors_mal_ids = [
                    author.get('mal_id', 0) 
                    for author in manga.get('authors', []) 
                    if isinstance(author, dict)
                ],
                authors_names = [
                    author.get('name', '') 
                    for author in manga.get('authors', []) 
                    if isinstance(author, dict)
                ],
                genre_ids = [
                    genre.get('mal_id', 0) 
                    for genre in manga.get('genres', []) 
                    if isinstance(genre, dict)
                ],
                genre_names = [
                    genre.get('name', '') 
                    for genre in manga.get('genres', []) 
                    if isinstance(genre, dict)
                ],
            ) for manga in mangalist]

            return result

    except Exception as e:
        logger.error(f"Error occured while searching for a manga: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_top_manga(params: TopMangaParams):
    """Get the top-ranked manga from MyAnimeList with optional filtering.
    
    This tool retrieves the highest-rated manga from MyAnimeList's rankings.
    You can filter by different categories and content ratings.
    
    TOOL SELECTION PRIORITY:
    - Use THIS tool for ranking/popularity queries (e.g., "top manga", "most popular", "best rated")
    - DO NOT use search_manga for ranking queries
    - This is a specialized tool optimized for curated ranking data
    
    When to Use This Tool:
      "What are the top manga?"
      "Show me the most popular manga"
      "Best manga of all time"
      "What's currently publishing and popular?"
      "Most favorited manga"
      "Top upcoming manga"
      DO NOT use search_manga with keywords like "popular" or "top"
    
    Args:
        params (TopMangaParams): Filtering parameters including:
            - filter (str): Ranking category - 'airing' (currently publishing), 'upcoming' (not yet published), 'bypopularity' (most popular), 'favorite' (most favorited)
            - ratings (str): Content rating filter - 'g' (General), 'pg' (Parental Guidance), 'pg13' (13+), 'r17' (17+), 'r' (Restricted), 'rx' (Hentai)
            - limit (int): Number of results to return (default: 10, max: 500)
    
    Filter Examples:
      "Top currently publishing manga" → filter='airing'
      "Most popular manga" → filter='bypopularity'
      "Most favorited manga" → filter='favorite'
      "Best upcoming manga" → filter='upcoming'
    
    Returns:
        List[TopMangaResponse]: List of top manga with title, type, volumes,
                              status, rank, synopsis, season, and year.
    
    Raises:
        Exception: If there's an error fetching data from the API.
    """

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            try:
                response = await client.get(f"{BASE_URL}/top/manga", params=query_params)
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/top/manga timed out")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error occurred while requesting {e.request.url}: {e}")
                raise

            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from API: {e}")

            mangalist = response_data.get('data', [])

            if not isinstance(mangalist, list):
                logger.error(f"Expected 'data' to be a list, got {type(mangalist)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [TopMangaResponse(
                title = manga.get('title_english', ''),
                type = manga.get('type', ''),
                volumes = manga.get('volumes', 0),
                status =  manga.get('status', ''),
                rank = manga.get('rank', 0),
                synopsis = manga.get('synopsis', ''),
                season = manga.get('season', ''),
                year = manga.get('year', 0)

            ) for manga in mangalist]

            logger.info(f"Top Manga Fetched:\n {result}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching top manga: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_random_manga():
    """Get a completely random manga recommendation from MyAnimeList.
    
    This tool fetches a single random manga from MyAnimeList's database.
    No parameters are needed - it returns a surprise manga recommendation.
    
    TOOL SELECTION PRIORITY:
    - Use THIS tool when users want random/surprise manga recommendations
    - DO NOT use search_manga for random recommendations
    - This is a specialized tool that provides truly random selections
    
    When to Use This Tool:
      "Give me a random manga"
      "Surprise me with a manga"
      "Pick something random for me to read"
      "I don't know what manga to read, choose for me"
    
    DO NOT use search_manga or get_top_manga instead
    
    Returns:
        RandomMangaResponse: A random manga with title, type, volumes,
                           status, rank, synopsis, season, and year.
    
    Raises:
        Exception: If there's an error fetching data from the API.
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            try:
                response = await client.get(f"{BASE_URL}/random/manga")
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/random/manga timed out")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error occurred while requesting {e.request.url}: {e}")
                raise

            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from API: {e}")

            manga = response_data.get('data', {})

            if not isinstance(manga, dict):
                logger.error(f"Expected 'data' to be a dict, got {type(manga)}")
                raise ValueError("Invalid API response format: 'data' is not a dict")

            result = RandomMangaResponse(
                title = manga.get('title_english', ''),
                type = manga.get('type', ''),
                volumes = manga.get('volumes', 0),
                status =  manga.get('status', ''),
                rank = manga.get('rank', 0),
                synopsis = manga.get('synopsis', ''),
                season = manga.get('season', ''),
                year = manga.get('year', 0)
            )

            logger.info(f"A random manga Fetched:\n {result}")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching random manga", exc_info=True)
        raise

@mcp.tool()
async def get_manga_reviews(id: int, params: MangaReviewParams):
    """Get user reviews for a specific manga by its MyAnimeList ID.
    
    This tool fetches user-written reviews for a specific manga.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - This tool REQUIRES a numeric MAL ID
    - NEVER use search_manga to get MAL IDs (it returns incorrect results)
    - If you don't have the MAL ID, you MUST follow this workflow:
      1. Use web_search with query: "{manga_name} MyAnimeList ID"
      2. Extract the numeric ID from the search results
      3. Then call this function with that ID
    
    Example Workflow:
      User asks: "What do people think about Berserk?"
      WRONG: search_manga("Berserk") then get_manga_reviews(result)
      CORRECT: web_search("Berserk MyAnimeList ID") → Extract ID: 2 → get_manga_reviews(2, params)
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the manga
                 Example IDs: Berserk=2, One Piece=13, Naruto=11, Monster=1
        params (MangaReviewParams): Review filtering parameters including:
            - preliminary (bool): Include preliminary reviews (default: True) - Set to True if manga is still publishing
            - spoilers (bool): Include reviews with spoilers (default: False) - Set to True to include spoiler reviews
    
    Returns:
        List[MangaReviewResponse]: List of manga reviews with review text and date.
    
    Raises:
        Exception: If there's an error fetching reviews from the API.
    """

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            try:
                response = await client.get(f"{BASE_URL}/manga/{id}/reviews", params=query_params)
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/manga/{id}/reviews timed out")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error occurred while requesting {e.request.url}: {e}")
                raise

            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from API: {e}")

            data = response_data.get('data', [])

            if not isinstance(data, list):
                logger.error(f"Expected 'data' to be a list, got {type(data)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [MangaReviewResponse(
                review = item.get('review', ''),
                date = item.get('date', '')
            ) for item in data]

            logger.info(f"Reviews for the manga with MAL_ID {id} fetched: {result}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while getting manga review: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_similar_manga(id: int):
    """Get manga recommendations similar to a specific manga by its MyAnimeList ID.
    
    This tool finds manga that are similar to the one you specify. Perfect for
    discovering new manga based on something you already know or like.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - This tool REQUIRES a numeric MAL ID
    - NEVER use search_manga to get MAL IDs (it returns incorrect results)
    - If you don't have the MAL ID, you MUST follow this workflow:
      1. Use web_search with query: "{manga_name} MyAnimeList ID"
      2. Extract the numeric ID from the search results
      3. Then call this function with that ID
    
    Example Workflow:
      User asks: "Find manga similar to Berserk"
      WRONG: search_manga("Berserk") then get_similar_manga(result)
      CORRECT: web_search("Berserk MyAnimeList ID") → Extract ID: 2 → get_similar_manga(2)
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the manga to find similar titles for
                 Example IDs: Berserk=2, One Piece=13, Naruto=11, Attack on Titan=53390,
                             Vagabond=656, Monster=1
    
    Returns:
        List[SimilarMangaResponse]: List of recommended similar manga with
                                   MAL ID and title for each recommendation.
    
    Raises:
        Exception: If there's an error fetching recommendations from the API.
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            try:
                response = await client.get(f"{BASE_URL}/manga/{id}/recommendations")
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/manga/{id}/recommendations timed out")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error occurred while requesting {e.request.url}: {e}")
                raise

            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from API: {e}")

            mangalist = response_data.get('data', [])

            if not isinstance(mangalist, list):
                logger.error(f"Expected 'data' to be a list, got {type(mangalist)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [SimilarMangaResponse(
                mal_id = manga.get('entry', {}).get('mal_id', 0),
                title = manga.get('entry', {}).get('title', '')
            ) for manga in mangalist]

            return result

    except Exception as e:
        logger.error(f"Error occured while getting the manga recommendations: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_manga_news(id: int):
    """Get the latest news articles for a specific manga by its MyAnimeList ID.
    
    This tool fetches recent news articles, announcements, and updates
    related to a specific manga title.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - This tool REQUIRES a numeric MAL ID
    - NEVER use search_manga to get MAL IDs (it returns incorrect results)
    - If you don't have the MAL ID, you MUST follow this workflow:
      1. Use web_search with query: "{manga_name} MyAnimeList ID"
      2. Extract the numeric ID from the search results
      3. Then call this function with that ID
    
    Example Workflow:
      User asks: "What's the latest news about Berserk?"
      WRONG: search_manga("Berserk") then get_manga_news(result)
      CORRECT: web_search("Berserk MyAnimeList ID") → Extract ID: 2 → get_manga_news(2)
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the manga to get news for
                 Example IDs: Berserk=2, One Piece=13, Naruto=11, Attack on Titan=53390
        
    Returns:
        List[MangaNewsResponse]: List of news articles with title, publication date,
                               author username, article URL, and excerpt.
    
    Raises:
        Exception: If there's an error fetching news from the API.
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            try:
                response = await client.get(f"{BASE_URL}/manga/{id}/news")
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/manga/{id}/news timed out")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error occurred while requesting {e.request.url}: {e}")
                raise

            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from API: {e}")

            news_list = response_data.get('data', [])

            if not isinstance(news_list, list):
                logger.error(f"Expected 'data' to be a list, got {type(news_list)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [MangaNewsResponse(
                title = news.get('title', ''),
                date = news.get('date', ''),
                author_username = news.get('author_username', ''),
                url = news.get('url', ''),
                excerpt = news.get('excerpt', '')
            ) for news in news_list]

            return result

    except Exception as e:
        logger.error(f"Error occured while getting manga news: {e}", exc_info=True)
        raise