
import httpx

from src.utils.logger import logger
from src.tools.config import mcp, BASE_URL
from src.models.manga_models import (
    MangaNewsResponse, TopMangaParams, TopMangaResponse, RandomMangaResponse, MangaReviewParams,
    MangaReviewResponse, MangaSearchParams, MangaSearchResponse, SimilarMangaResponse
)

@mcp.tool()
async def search_manga(params: MangaSearchParams):

    """Search for manga on MyAnimeList based on various criteria.
    
    Args:
        params (MangaSearchParams): Search parameters including query, limit,
                                  status, order_by, sort, start_date, and end_date
    
    Returns:
        List[MangaSearchResponse]: List of manga matching search criteria with
                                 detailed information including MAL ID, title,
                                 volumes, status, currently publishing or not, start_date, end_date
                                 ,score, scored_by, rank, popularity, favorites, synopsis, background,
                                 , author_ids list, author_names list, genre_ids list, genre_names list
    
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
    """Get the top-ranked manga from MyAnimeList.
    
    Args:
        params (TopMangaParams): Parameters for filtering top manga including
                               filter, ratings, limit
    
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
    """Get a random manga from MyAnimeList.
    
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

    """Get reviews for a specific manga by its MyAnimeList ID.
    
    Args:
        id (int): The MyAnimeList ID of the manga.
        params (MangaReviewParams): Parameters for filtering reviews including
                                  spoilers and preliminary options.
                                  if the manga is airing/publishing, then preliminary needs to be true.
                                  If review has spoilers, then spoilers parameter would be true.
    
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
    """Get recommendations for a specific manga by its MyAnimeList ID. 
    This tool will give you manga similar to the manga whose ID you provide.
    
    Args:
        id (int): The MyAnimeList ID of the manga.
    
    Returns:
        List[MangaRecommendationResponse]: List of recommended manga with
                                         MAL ID and title.
    
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
    """Get news articles for a specific manga by its MyAnimeList ID.
    
    Args:
        id (int): The MyAnimeList ID of the manga.
        
    Returns:
        List[MangaNewsResponse]: List of news articles with title, date,
                               author username, and excerpt.
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