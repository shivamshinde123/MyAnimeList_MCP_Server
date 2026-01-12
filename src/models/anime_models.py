
from pydantic import BaseModel, Field
from typing import Literal, Optional, List


class AnimeSearchParams(BaseModel):
    """Parameters for searching anime on MyAnimeList."""
    query: str = Field(..., description="Search term for anime title or keywords", min_length=1)
    limit: Optional[int] = Field(5, description="Number of results to return", ge=1, le=25)
    status: Optional[Literal['airing', 'complete', 'upcoming']] = Field(None, description="Filter by anime status")
    rating: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = Field(None, description="Filter by content rating")
    order_by: Optional[Literal['mal_id', 'title', 'start_date', 'end_date', 'episodes', 'score', 'rank', 'popularity']] = Field('popularity', description="Sort results by this field")
    sort: Optional[Literal['desc', 'asc']] = Field('desc', description="Sort direction")
    start_date: Optional[str] = Field(None, description="Filter anime that started after this date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Filter anime that ended before this date (YYYY-MM-DD)")

class AnimeSearchResponse(BaseModel):
    """Response model for anime search results."""
    mal_id: Optional[int] = None
    title: Optional[str] = None
    episodes: Optional[int] = None
    status: Optional[str] = None
    airing: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    rating: Optional[str] = None
    score: Optional[float] = None
    scored_by: Optional[int] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    favorites: Optional[int] = None
    synopsis: Optional[str] = None
    background: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None
    producers_mal_ids: Optional[List[int]] = None
    producer_names: Optional[List[str]] = None
    studio_ids: Optional[List[int]] = None
    studio_name: Optional[List[str]] = None
    genre_ids: Optional[List[int]] = None
    genre_names: Optional[List[str]] = None

class TopAnimeParams(BaseModel):
    """Parameters for filtering top anime requests."""
    filter: Optional[Literal['airing', 'upcoming', 'bypopularity', 'favorite']] = 'airing'
    ratings: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = 'g'
    limit: Optional[int] = 10

class TopAnimeResponse(BaseModel):
    """Response model for top anime data."""
    title: Optional[str] = None
    type: Optional[str] = None
    episodes: Optional[int] = None
    status: Optional[str] = None
    rating: Optional[str] = None
    rank: Optional[int] = None
    synopsis: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None

class RandomAnimeResponse(BaseModel):
    """Response model for random anime data."""
    title: Optional[str] = None
    type: Optional[str] = None
    episodes: Optional[int] = None
    status: Optional[str] = None
    rating: Optional[str] = None
    rank: Optional[int] = None
    synopsis: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None

class AnimeReviewParams(BaseModel):
    """Parameters for filtering anime review requests."""
    preliminary: Optional[bool] = True # if the anime is airing/publishing, then preliminary needs to be true
    spoilers: Optional[bool] = False

class AnimeReviewResponse(BaseModel):
    """Response model for anime review data."""
    review: Optional[str]
    date: Optional[str]

class SimilarAnimeResponse(BaseModel):
    """Response model for anime recommendation"""
    mal_id: Optional[int] = None
    title: Optional[str] = None

class AnimeNewsResponse(BaseModel):
    """Response model for anime news"""
    title: Optional[str] = None
    date: Optional[str] = None
    author_username: Optional[str] = None
    url: Optional[str] = None
    excerpt: Optional[str] = None

class SeasonalAnimeParams(BaseModel):
    season: Optional[Literal['fall', 'winter', 'spring', 'summer']] = 'spring'
    year: Optional[int] = 2025

class SeasonalAnimeResponse(BaseModel):
    mal_id: Optional[int] = None
    title: Optional[str] = None
    episodes: Optional[int] = None
    status: Optional[str] = None
    airing: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    rating: Optional[str] = None
    score: Optional[float] = None
    scored_by: Optional[int] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    favorites: Optional[int] = None
    synopsis: Optional[str] = None
    background: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None
    producers_mal_ids: Optional[List[int]] = None
    producer_names: Optional[List[str]] = None
    studio_ids: Optional[List[int]] = None
    studio_names: Optional[List[str]] = None
    genre_ids: Optional[List[int]] = None
    genre_names: Optional[List[str]] = None