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
    """Search for anime on MyAnimeList (MAL) based on various criteria.
    
    Args:
        params (AnimeSearchParams): Search parameters including query, limit,
                                  status ('airing', 'complete', 'upcoming'), 
                                  rating ('g', 'pg', 'pg13', 'r17', 'r', 'rx'),
                                  order_by ('mal_id', 'title', 'start_date', 'end_date', 'episodes', 'score', 'rank', 'popularity'),
                                  sort ('desc', 'asc'), start_date, and end_date
    
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
    """Get the top-ranked anime from MyAnimeList.
    
    Args:
        params (TopAnimeParams): Parameters for filtering top anime including
                               filter ('airing', 'upcoming', 'bypopularity', 'favorite'),
                               ratings ('g', 'pg', 'pg13', 'r17', 'r', 'rx'), limits
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
    """Get a random anime from MyAnimeList.
    
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
    """Get reviews for a specific anime by its MyAnimeList ID.
    
    Args:
        id (int): The MyAnimeList ID of the anime.
        params (AnimeReviewParams): Parameters for filtering reviews including
                                  spoilers and preliminary options. 
                                  if the anime is airing/publishing, then preliminary needs to be true.
                                  If review has spoilers, then spoilers parameter would be true.
    
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

    """Get recommendations for a specific anime by its MyAnimeList ID. 
    This tool will give you anime similar to the anime whose ID you provide.
    
    Args:
        id (int): The MyAnimeList ID of the anime.
    
    Returns:
        List[AnimeRecommendationResponse]: List of recommended anime with
                                         MAL ID and title.
    
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
    """Get news articles for a specific anime by its MyAnimeList ID.
    
    Args:
        id (int): The MyAnimeList ID of the anime.
        
    Returns:
        List[AnimeNewsResponse]: List of news articles with title, date,
                               author username, and excerpt.
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
    
    Args:
        params (SeasonalAnimeParams): Parameters containing year and season ('fall', 'winter', 'spring', 'summer').
        
    Returns:
        List[SeasonalAnimeResponse]: List of seasonal anime with detailed
                                   information including MAL ID, title, episodes, status, currently airing or not, start_date, end_date, duration,
                                rating, score, scored_by, rank, popularity, favorites, synopsis, background,
                                season, year, producer_ids list, producer_names list, studio_ids list, studio_names list,
                                genre_ids list, genre_names list
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