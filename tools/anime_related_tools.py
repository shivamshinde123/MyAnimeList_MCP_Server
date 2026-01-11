
import asyncio
import httpx

from typing import Any, Dict, List, Tuple, Optional

from utils.logger import logger

from server import mcp, BASE_URL

from models.anime_models import (
AnimeReviewParams, AnimeReviewResponse, RandomAnimeResponse, TopAnimeParams, TopAnimeResponse
)

@mcp.tool()
async def get_top_anime(params: TopAnimeParams):

    """
    Use this tool to get the top anime list
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
                episodes = anime.get('episodes', ''),
                status = anime.get('status', ''),
                rating = anime.get('rating', ''),
                rank = anime.get('rank', ''),
                synopsis = anime.get('synopsis', ''),
                season = anime.get('season', ''),
                year = anime.get('year', '')
            ) for anime in animelist]

            logger.info(f"Top Anime Fetched:\n {result[0]}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching top anime: {e}")
        raise 

@mcp.tool()
async def get_random_anime():

    """Use this tool to get a random anime"""

    try:
        async with httpx.AsyncClient() as client:

            response = client.get(f"{BASE_URL}/random/anime")

            anime = response.json().get('data', '')

            result = RandomAnimeResponse(
                title = anime.get('title_english', ''),
                type = anime.get('type', ''),
                episodes = anime.get('episodes', ''),
                status = anime.get('status', ''),
                rating = anime.get('rating', ''),
                rank = anime.get('rank', ''),
                synopsis = anime.get('synopsis', ''),
                season = anime.get('season', ''),
                year = anime.get('year', '')
            )

            logger.info(f"A random anime Fetched:\n {result}")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching a random anime: {e}")
        raise

@mcp.tool()
async def get_anime_reviews(id: int, params: AnimeReviewParams):
    
    """
    Use this tool to get the anime reviews
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







