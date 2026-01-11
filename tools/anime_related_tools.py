
import asyncio
import httpx

from typing import Any, Dict, List, Tuple, Optional

from utils.logger import logger

from server import mcp, BASE_URL

from models.anime_models import (
AnimeReviewParams, AnimeReviewResponse, AnimeSearchResponse, RandomAnimeResponse, TopAnimeParams, TopAnimeResponse,
AnimeSearchParams
)

@mcp.tool()
async def search_anime(params: AnimeSearchParams):
    """Search for anime on MyAnimeList based on various criteria.
    
    Args:
        params (AnimeSearchParams): Search parameters including query, limit,
                                  status, rating, order_by, sort, start_date, and end_date
    
    Returns:
        List[AnimeSearchResponse]: List of anime matching search criteria with
                                 detailed information including MAL ID, title,
                                 episodes, status, currently airing or not, start_date, end_date, duration,
                                 rating, score, scored_by, rank, popularity, favorites, synopsis, background,
                                 season, year, producer_ids list, producer_names list, studio_ids list, studio_names list,
                                 genre_ids list, genre_names list
    
    Raises:
        Exception: If there's an error fetching search results from the API.
    """
    
    try:
        async with httpx.AsyncClient() as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            response = await client.get(f"{BASE_URL}/anime", params=query_params)

            animelist = response.json().get('data', '')

            result = [AnimeSearchResponse(
                mal_id = anime.get('mal_id', 0),
                title = anime.get('title', ''),
                episodes = anime.get('episodes', 0),
                status = anime.get('status', ''),
                airing = anime.get('airing', False),
                start_date = anime.get('aired', '').get('from', ''),
                end_date = anime.get('aired','').get('to','') if not anime.get('airing','') else '',
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
                producer_mal_ids = [producer.get('mal_id', 0) for producer in anime.get('producers', [])],
                producer_names = [producer.get('name', '') for producer in anime.get('producers', [])],
                studio_ids = [studio.get('mal_id', 0) for studio in anime.get('studios', [])],
                studio_names = [studio.get('name', '') for studio in anime.get('studios', [])],
                genre_ids = [genre.get('mal_id', 0) for genre in anime.get('genres', [])],
                genre_names = [genre.get('name', '') for genre in anime.get('genres', [])],
            ) for anime in animelist]

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching an anime information: {e}")
        raise

@mcp.tool()
async def get_top_anime(params: TopAnimeParams):
    """Get the top-ranked anime from MyAnimeList.
    
    Args:
        params (TopAnimeParams): Parameters for filtering top anime including
                               filter, ratings, limits
    Returns:
        List[TopAnimeResponse]: List of top anime with title, type, episodes,
                              status, rating, rank, synopsis, season, and year.
    
    Raises:
        Exception: If there's an error fetching data from the API.
    """

    try:
        async with httpx.AsyncClient() as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            response = await client.get(f"{BASE_URL}/top/anime", params=query_params)

            animelist = response.get('data', '')

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

            logger.info(f"Top Anime Fetched:\n {result[0]}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching top anime: {e}")
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
        async with httpx.AsyncClient() as client:

            response = client.get(f"{BASE_URL}/random/anime")

            anime = response.json().get('data', '')

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
        logger.error(f"Error occured while fetching a random anime: {e}")
        raise

@mcp.tool()
async def get_anime_reviews(id: int, params: AnimeReviewParams):
    """Get reviews for a specific anime by its MyAnimeList ID.
    
    Args:
        id (int): The MyAnimeList ID of the anime.
        params (AnimeReviewParams): Parameters for filtering reviews including
                                  spoilers and preliminary options.
    
    Returns:
        List[AnimeReviewResponse]: List of anime reviews with review text and date.
    
    Raises:
        Exception: If there's an error fetching reviews from the API.
    """

    try:
        async with httpx.AsyncClient() as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            response = client.get(f"{BASE_URL}/anime/{id}/reviews", params=query_params)

            data =  response.json().get('data', '')

            result = [AnimeReviewResponse(
                review = item.get('review', ''),
                date = item.get('date', '')
            ) for item in data]

            logger.info(f"Reviews for the anime with MAL_ID {id} fetched: {result[0]}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching anime review: {e}")
        raise





