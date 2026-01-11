
import asyncio
import httpx

from typing import Any, Dict, List, Tuple, Optional

from utils.logger import logger

from server import mcp, BASE_URL

from models.manga_models import (
    TopMangaParams, TopMangaResponse, RandomMangaResponse, MangaReviewParams,
    MangaReviewResponse
)

@mcp.tool()
async def get_top_manga(params: TopMangaParams):

    """Use this tool to get the top manga"""

    try:
        async with httpx.AsyncClient() as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            response = await client.get(f"{BASE_URL}/top/manga", params=query_params)

            mangalist = response.get('data', '')

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

            logger.info(f"Top Manga Fetched:\n {result[0]}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while fetching top manga: {e}")
        raise

@mcp.tool()
async def get_random_manga():

    """Use this tool to get a random manga"""
    
    try:
        async with httpx.AsyncClient() as client:

            response = await client.get(f"{BASE_URL}/random/manga")

            manga = response.json().get('data', '')

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
        logger.error(f"Error occured while fetching random manga")
        raise

@mcp.tool()
async def get_manga_reviews(id: int, params: MangaReviewParams):
    
    """
    Use this tool to get the anime reviews
    """

    try:
        async with httpx.AsyncClient() as client:

            # Convert Pydantic model to dict, excluding None values
            query_params = params.model_dump(exclude_none=True)

            response = client.get(f"{BASE_URL}/manga/{id}/reviews", params=query_params)

            data =  response.json().get('data', '')

            result = [MangaReviewResponse(
                review = item.get('review', ''),
                date = item.get('date', '')
            ) for item in data]

            logger.info(f"Reviews for the manga with MAL_ID {id} fetched: {result[0]}...")

            return result

    except Exception as e:
        logger.error(f"Error occured while getting manga review: {e}")
        raise