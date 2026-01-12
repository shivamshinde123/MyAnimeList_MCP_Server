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
    
    Args:
        params (TopAnimeParams): Filtering parameters including:
            - filter (str): Ranking category - 'airing' (currently airing), 'upcoming' (not yet aired), 'bypopularity' (most popular), 'favorite' (most favorited)
            - ratings (str): Content rating filter - 'g' (General), 'pg' (Parental Guidance), 'pg13' (13+), 'r17' (17+), 'r' (Restricted), 'rx' (Hentai)
            - limit (int): Number of results to return (default: 10, max: 500)
    
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
    
    This tool fetches user-written reviews for a specific anime. You need the
    anime's MAL ID (which you can get from search_anime or other tools).
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the anime (e.g., 16498 for Attack on Titan)
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
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the anime to find similar titles for
                 (e.g., 16498 for Attack on Titan, 11061 for Hunter x Hunter)
    
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
    
    Args:
        id (int): REQUIRED - The MyAnimeList ID of the anime to get news for
                 (e.g., 16498 for Attack on Titan news)
        
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
    """Get anime from a specific season and year (seasonal anime listings).
    
    This tool retrieves all anime that aired or are scheduled to air during
    a specific season of a given year. Great for discovering what was popular
    in a particular time period.
    
    Args:
        params (SeasonalAnimeParams): Season and year parameters including:
            - season (str): The season - 'spring' (Apr-Jun), 'summer' (Jul-Sep), 'fall' (Oct-Dec), 'winter' (Jan-Mar)
            - year (int): The year (e.g., 2024, 2023, 2025) - defaults to 2025
        
    Returns:
        List[SeasonalAnimeResponse]: List of seasonal anime with detailed
                                   information including MAL ID, title, episodes, status, currently airing or not, start_date, end_date, duration,
                                rating, score, scored_by, rank, popularity, favorites, synopsis, background,
                                season, year, producer_ids list, producer_names list, studio_ids list, studio_names list,
                                genre_ids list, genre_names list
    
    Raises:
        Exception: If there's an error fetching seasonal anime from the API.
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