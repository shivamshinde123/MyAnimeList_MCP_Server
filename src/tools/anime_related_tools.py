import httpx

from src.utils.logger import logger
from src.tools.config import mcp, BASE_URL
from src.models.anime_models import (
    AnimeNewsResponse, AnimeReviewParams, AnimeReviewResponse, AnimeSearchResponse, 
    RandomAnimeResponse, SeasonalAnimeParams, TopAnimeParams, TopAnimeResponse,
    AnimeSearchParams, SimilarAnimeResponse, SeasonalAnimeResponse
)

@mcp.tool()
async def search_anime(params: AnimeSearchParams):
    """Search for anime on MyAnimeList based on a query string and optional filters.
    
    This tool searches for anime using the provided query and applies optional filters
    like status, rating, ordering, and date ranges. The query parameter is required.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - This API is UNRELIABLE and often returns incorrect or irrelevant results
    - DO NOT use this tool to find MAL IDs for other tools (get_similar_anime, get_anime_reviews, get_anime_news)
    - For finding MAL IDs: ALWAYS use web_search("{anime_name} MyAnimeList ID") instead
    
    When to Use This Tool:
      Searching for anime by keywords/themes (e.g., "mecha anime", "slice of life")
      Exploring anime by genre, studio, or other filters
      Finding anime you don't know the exact name of
    
    When not to Use This Tool
      Getting MAL IDs for other tools (use web_search instead)
      Finding specific well-known anime (use web_search instead)
    
    Example:
      User asks: "Find anime about pirates"
      CORRECT: search_anime(params={"query": "pirates"})
      
      User asks: "Find anime similar to One Piece"
      WRONG: search_anime("One Piece") then get_similar_anime(result)
      CORRECT: web_search("One Piece MyAnimeList ID") → get_similar_anime(id)
    
    Args:
        params (AnimeSearchParams): Search parameters including:
            - query (str): REQUIRED - The search term (anime title or keywords)
            - limit (int): Number of results to return (default: 5, max: 25)
            - status (str): Filter by anime status - 'airing', 'complete', or 'upcoming'
            - rating (str): Filter by content rating - 'g', 'pg', 'pg13', 'r17', 'r', 'rx'
            - order_by (str): Sort results by - 'mal_id', 'title', 'start_date', 'end_date', 'episodes', 'score', 'rank', 'popularity'
            - sort (str): Sort direction - 'desc' or 'asc'
            - start_date (str): Filter anime that started after this date (YYYY-MM-DD)
            - end_date (str): Filter anime that ended before this date (YYYY-MM-DD)
    
    Returns:
        List[AnimeSearchResponse]: List of anime matching search criteria with
                                 detailed information including MAL ID, title,
                                 episodes, status, currently airing or not, start_date, end_date, duration,
                                 rating, score, scored_by, rank, popularity, favorites, synopsis, background,
                                 season, year, producer_ids list, producer_names list, studio_ids list, studio_names list,
                                 genre_ids list, genre_names list
    
    Raises:
        httpx.TimeoutException: If the request times out
        httpx.HTTPStatusError: If the API returns a 4xx/5xx status code
        httpx.RequestError: If there's a network error
        ValueError: If the API response is invalid or malformed
    """
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            logger.info(f"Searching anime with params: {query_params}")

            try:

                response = await client.get(f"{BASE_URL}/anime", params=query_params)
                response.raise_for_status()

            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/anime timed out")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occured: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error occured while requesting {e.request.url} : {e}")
                raise

            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from API: {e}")


            animelist = response_data.get('data', [])

            if not isinstance(animelist, list):
                logger.error(f"Expected 'data' to be a list, got {type(animelist)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            logger.info(f"Retrieved {len(animelist)} anime entries")


            logger.info(f"anime list: {animelist}")


            result = list()

            for idx, anime in enumerate(animelist):

                try:
                    if not isinstance(anime, dict):
                        logger.warning(f"Skipping anime at index {idx}: not a dict")
                        continue

                    anime_response = AnimeSearchResponse(
                    mal_id=anime.get('mal_id', 0),
                    title=anime.get('title', ''),
                    episodes=anime.get('episodes', 0),
                    status=anime.get('status', ''),
                    airing=anime.get('airing', False),
                    start_date=anime.get('aired', {}).get('from', ''),
                    end_date=anime.get('aired', {}).get('to', ''),
                    duration=anime.get('duration', ''),
                    rating=anime.get('rating', ''),
                    score=anime.get('score', 0.0),
                    scored_by=anime.get('scored_by', 0),
                    rank=anime.get('rank', 0),
                    popularity=anime.get('popularity', 0),
                    favorites=anime.get('favorites', 0),
                    synopsis=anime.get('synopsis', ''),
                    background=anime.get('background', ''),
                    season=anime.get('season', ''),
                    year=anime.get('year', 0),
                    producer_mal_ids=[
                        producer.get('mal_id', 0) 
                        for producer in anime.get('producers', []) 
                        if isinstance(producer, dict)
                    ],
                    producer_names=[
                        producer.get('name', '') 
                        for producer in anime.get('producers', []) 
                        if isinstance(producer, dict)
                    ],
                    studio_ids=[
                        studio.get('mal_id', 0) 
                        for studio in anime.get('studios', []) 
                        if isinstance(studio, dict)
                    ],
                    studio_names=[
                        studio.get('name', '') 
                        for studio in anime.get('studios', []) 
                        if isinstance(studio, dict)
                    ],
                    genre_ids=[
                        genre.get('mal_id', 0) 
                        for genre in anime.get('genres', []) 
                        if isinstance(genre, dict)
                    ],
                    genre_names=[
                        genre.get('name', '') 
                        for genre in anime.get('genres', []) 
                        if isinstance(genre, dict)
                    ]
                    )

                    result.append(anime_response)

                except Exception as e:
                    logger.warning(f"Failed to process anime at index {idx} (mal_id: {anime.get('mal_id', 'unknown')}) : {e} ")
                    continue

            logger.info(f"Successfully processed {len(result)} out of {len(animelist)} anime entries")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching anime information: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_top_anime(params: TopAnimeParams):
    """Get the top-ranked anime from MyAnimeList with optional filtering.
    
    This tool retrieves the highest-rated anime from MyAnimeList's rankings.
    You can filter by different categories and content ratings.
    
    TOOL SELECTION PRIORITY:
    - Use THIS tool for ranking/popularity queries (e.g., "top anime", "most popular", "best rated")
    - DO NOT use search_anime for ranking queries
    - This is a specialized tool optimized for curated ranking data
    
    When to Use This Tool:
      "What are the top anime?"
      "Show me the most popular anime"
      "Best anime of all time"
      "What's currently airing and popular?"
      "Most favorited anime"
      "Top upcoming anime"
      DO NOT use search_anime with keywords like "popular" or "top"
    
    Args:
        params (TopAnimeParams): Filtering parameters including:
            - filter (str): Ranking category - 'airing' (currently airing), 'upcoming' (not yet aired), 'bypopularity' (most popular), 'favorite' (most favorited)
            - ratings (str): Content rating filter - 'g' (General), 'pg' (Parental Guidance), 'pg13' (13+), 'r17' (17+), 'r' (Restricted), 'rx' (Hentai)
            - limit (int): Number of results to return (default: 10, max: 500)
    
    Filter Examples:
      "Top airing anime" → filter='airing'
      "Most popular anime" → filter='bypopularity'
      "Most favorited anime" → filter='favorite'
      "Best upcoming anime" → filter='upcoming'
    
    Returns:
        List[TopAnimeResponse]: List of top anime with title, type, episodes,
                              status, rating, rank, synopsis, season, and year.
    
    Raises:
        Exception: If there's an error fetching data from the API.
    """

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            logger.info(f"params: {query_params}")

            try:
                response = await client.get(f"{BASE_URL}/top/anime", params=query_params)
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/top/anime timed out")
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

            animelist = response_data.get('data', [])

            if not isinstance(animelist, list):
                logger.error(f"Expected 'data' to be a list, got {type(animelist)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [TopAnimeResponse(
                title = anime.get('title_english', ''),
                type = anime.get('type', ''),
                episodes = anime.get('episodes', 0),
                status = anime.get('status', ''),
                rating = anime.get('rating', ''),
                rank = anime.get('rank', 0),
                synopsis = anime.get('synopsis', ''),
                season = anime.get('season', ''),
                year = anime.get('year', 0)
            ) for anime in animelist]

            logger.info(f"Top Anime Fetched:\n {result}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching top anime: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_random_anime():
    """Get a completely random anime recommendation from MyAnimeList.
    
    This tool fetches a single random anime from MyAnimeList's database.
    No parameters are needed - it returns a surprise anime recommendation.
    
    TOOL SELECTION PRIORITY:
    - Use THIS tool when users want random/surprise recommendations
    - DO NOT use search_anime for random recommendations
    - This is a specialized tool that provides truly random selections
    
    When to Use This Tool:
      "Give me a random anime"
      "Surprise me with an anime"
      "Pick something random for me to watch"
      "I don't know what to watch, choose for me"
      DO NOT use search_anime or get_top_anime instead
    
    Returns:
        RandomAnimeResponse: A random anime with title, type, episodes,
                           status, rating, rank, synopsis, season, and year.
    
    Raises:
        Exception: If there's an error fetching data from the API.
    """

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            try:
                response = await client.get(f"{BASE_URL}/random/anime")
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/random/anime timed out")
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

            anime = response_data.get('data', {})

            if not isinstance(anime, dict):
                logger.error(f"Expected 'data' to be a dict, got {type(anime)}")
                raise ValueError("Invalid API response format: 'data' is not a dict")

            result = RandomAnimeResponse(
                title = anime.get('title_english', ''),
                type = anime.get('type', ''),
                episodes = anime.get('episodes', 0),
                status = anime.get('status', ''),
                rating = anime.get('rating', ''),
                rank = anime.get('rank', 0),
                synopsis = anime.get('synopsis', ''),
                season = anime.get('season', ''),
                year = anime.get('year', 0)
            )

            logger.info(f"A random anime Fetched:\n {result}")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching a random anime: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_anime_reviews(id: int, params: AnimeReviewParams):
    """Get user reviews for a specific anime by its MyAnimeList ID.
    
    This tool fetches user-written reviews for a specific anime.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - This tool REQUIRES a numeric MAL ID
    - NEVER use search_anime to get MAL IDs (it returns incorrect results)
    - If you don't have the MAL ID, you MUST follow this workflow:
      1. Use web_search with query: "{anime_name} MyAnimeList ID"
      2. Extract the numeric ID from the search results
      3. Then call this function with that ID
    
    Example Workflow:
      User asks: "What do people think about Trigun?"
      WRONG: search_anime("Trigun") then get_anime_reviews(result)
      CORRECT: web_search("Trigun MyAnimeList ID") → Extract ID: 6 → get_anime_reviews(6, params)
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the anime
                 Example IDs: Attack on Titan=16498, Trigun=6, Cowboy Bebop=1
        params (AnimeReviewParams): Review filtering parameters including:
            - preliminary (bool): Include preliminary reviews (default: True) - Set to True if anime is still airing
            - spoilers (bool): Include reviews with spoilers (default: False) - Set to True to include spoiler reviews
    
    Returns:
        List[AnimeReviewResponse]: List of anime reviews with review text and date.
    
    Raises:
        Exception: If there's an error fetching reviews from the API.
    """

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            try:
                response = await client.get(f"{BASE_URL}/anime/{id}/reviews", params=query_params)
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/anime/{id}/reviews timed out")
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

            result = [AnimeReviewResponse(
                review = item.get('review', ''),
                date = item.get('date', '')
            ) for item in data]

            logger.info(f"Reviews for the anime with MAL_ID {id} fetched: {result}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching anime review: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_similar_anime(id: int):
    """Get anime recommendations similar to a specific anime by its MyAnimeList ID.
    
    This tool finds anime that are similar to the one you specify. Perfect for
    discovering new anime based on something you already know or like.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - This tool REQUIRES a numeric MAL ID
    - NEVER use search_anime to get MAL IDs (it returns incorrect results)
    - If you don't have the MAL ID, you MUST follow this workflow:
      1. Use web_search with query: "{anime_name} MyAnimeList ID"
      2. Extract the numeric ID from the search results
      3. Then call this function with that ID
    
    Example Workflow:
      User asks: "Find anime similar to Trigun"
      WRONG: search_anime("Trigun") then get_similar_anime(result)
      CORRECT: web_search("Trigun MyAnimeList ID") → Extract ID: 6 → get_similar_anime(6)
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the anime to find similar titles for
                 Example IDs: Trigun=6, Attack on Titan=16498, Hunter x Hunter=11061,
                             Cowboy Bebop=1, Fullmetal Alchemist: Brotherhood=5114
    
    Returns:
        List[SimilarAnimeResponse]: List of recommended similar anime with
                                   MAL ID and title for each recommendation.
    
    Raises:
        Exception: If there's an error fetching recommendations from the API.
    """

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            try:
                response = await client.get(f"{BASE_URL}/anime/{id}/recommendations")
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/anime/{id}/recommendations timed out")
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

            anime_recommendations = response_data.get('data', [])

            if not isinstance(anime_recommendations, list):
                logger.error(f"Expected 'data' to be a list, got {type(anime_recommendations)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [SimilarAnimeResponse(
                mal_id = recommendation.get('entry', {}).get('mal_id', 0),
                title = recommendation.get('entry', {}).get('title', '')
            ) for recommendation in anime_recommendations]

            return result

    except Exception as e:
        logger.error(f"Error occured while getting anime recommendations: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_anime_news(id: int):
    """Get the latest news articles for a specific anime by its MyAnimeList ID.
    
    This tool fetches recent news articles, announcements, and updates
    related to a specific anime title.
    
    CRITICAL INSTRUCTIONS FOR LLM:
    - This tool REQUIRES a numeric MAL ID
    - NEVER use search_anime to get MAL IDs (it returns incorrect results)
    - If you don't have the MAL ID, you MUST follow this workflow:
      1. Use web_search with query: "{anime_name} MyAnimeList ID"
      2. Extract the numeric ID from the search results
      3. Then call this function with that ID
    
    Example Workflow:
      User asks: "What's the latest news about Trigun?"
      WRONG: search_anime("Trigun") then get_anime_news(result)
      CORRECT: web_search("Trigun MyAnimeList ID") → Extract ID: 6 → get_anime_news(6)
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the anime to get news for
                 Example IDs: Attack on Titan=16498, Trigun=6, Cowboy Bebop=1
        
    Returns:
        List[AnimeNewsResponse]: List of news articles with title, publication date,
                               author username, article URL, and excerpt.
    
    Raises:
        Exception: If there's an error fetching news from the API.
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            try:
                response = await client.get(f"{BASE_URL}/anime/{id}/news")
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/anime/{id}/news timed out")
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

            result = [AnimeNewsResponse(
                title = news.get('title', ''),
                date = news.get('date', ''),
                author_username = news.get('author_username', ''),
                url = news.get('url', ''),
                excerpt = news.get('excerpt', '')
            ) for news in news_list]

            return result

    except Exception as e:
        logger.error(f"Error occured while getting anime news: {e}", exc_info=True)
        raise

@mcp.tool()
async def get_seasonal_anime(params: SeasonalAnimeParams):
    """Get anime from a specific season and year.
    
    Use this tool when users ask about anime from a particular season and year.
    This retrieves all anime that aired during that time period.
    
    TOOL SELECTION PRIORITY:
    - Use THIS tool for seasonal queries (e.g., "fall 2024 anime", "winter season")
    - DO NOT use search_anime for seasonal queries
    - This is a specialized tool optimized for seasonal data
    
    When to Use This Tool:
      "What anime aired in fall 2024?"
      "Show me winter 2023 anime"
      "What's airing this season?"
      "Summer anime recommendations"
      DO NOT use search_anime with season keywords instead
    
    Args:
        params (SeasonalAnimeParams):
            - season (str): REQUIRED. Must be exactly one of: 'winter', 'spring', 'summer', 'fall' (lowercase only)
                * winter = January-March
                * spring = April-June  
                * summer = July-September
                * fall = October-December
            - year (int): REQUIRED. Four-digit year (e.g., 2024, 2025, 2026)
    
    PARAMETER MAPPING EXAMPLES:
    User says "fall 2025" → season='fall', year=2025
    User says "winter 2024 anime" → season='winter', year=2024
    User says "what aired in spring 2023" → season='spring', year=2023
    User says "summer anime" → season='summer', year=2026 (current year)
    User says "this season" → season='winter', year=2026 (current: January 2026)
    
    Returns:
        List[SeasonalAnimeResponse]: List of anime with MAL ID, title, episodes, 
        status, airing status, dates, duration, rating, score, rank, popularity,
        synopsis, producers, studios, and genres.
    
    Raises:
        Exception: If there's an error fetching data from the MyAnimeList API.
    """

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            try:
                response = await client.get(f"{BASE_URL}/seasons/{params.year}/{params.season}")
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.error(f"Request to {BASE_URL}/seasons/{params.year}/{params.season} timed out")
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

            animelist = response_data.get('data', [])

            if not isinstance(animelist, list):
                logger.error(f"Expected 'data' to be a list, got {type(animelist)}")
                raise ValueError("Invalid API response format: 'data' is not a list")

            result = [SeasonalAnimeResponse(
                mal_id = anime.get('mal_id', 0),
                title = anime.get('title', ''),
                episodes = anime.get('episodes', 0),
                status = anime.get('status', ''),
                airing = anime.get('airing', False),
                start_date = anime.get('aired', {}).get('from', ''),
                end_date = anime.get('aired', {}).get('to',''),
                duration = anime.get('duration', ''),
                rating = anime.get('rating', ''),
                score = anime.get('score', 0.0), 
                scored_by = anime.get('scored_by', 0),
                rank = anime.get('rank', 0),
                popularity = anime.get('popularity', 0),
                favorites = anime.get('favorites', 0),
                synopsis = anime.get('synopsis', ''),
                background = anime.get('background', ''),
                season = anime.get('season', ''),
                year = anime.get('year', 0),
                producers_mal_ids = [
                    producer.get('mal_id', 0) 
                    for producer in anime.get('producers', []) 
                    if isinstance(producer, dict)
                ],
                producer_names = [
                    producer.get('name', '') 
                    for producer in anime.get('producers', []) 
                    if isinstance(producer, dict)
                ],
                studio_ids = [
                    studio.get('mal_id', 0) 
                    for studio in anime.get('studios', []) 
                    if isinstance(studio, dict)
                ],
                studio_names = [
                    studio.get('name', '') 
                    for studio in anime.get('studios', []) 
                    if isinstance(studio, dict)
                ],
                genre_ids = [
                    genre.get('mal_id', 0) 
                    for genre in anime.get('genres', []) 
                    if isinstance(genre, dict)
                ],
                genre_names = [
                    genre.get('name', '') 
                    for genre in anime.get('genres', []) 
                    if isinstance(genre, dict)
                ]
            ) for anime in animelist]

            return result


    except Exception as e:
        logger.error(f"Error occured while fetching seasonal anime: {e}", exc_info=True)
        raise