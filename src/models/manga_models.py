

from pydantic import BaseModel, Field
from typing import Literal, Optional, List

class MangaSearchParams(BaseModel):
    """Parameters for searching manga on MyAnimeList."""
    query: str = Field(..., description="Search term for manga title or keywords", min_length=1)
    limit: Optional[int] = Field(5, description="Number of results to return", ge=1, le=25)
    status: Optional[Literal['airing', 'complete', 'upcoming']] = Field(None, description="Filter by manga status - 'airing' (currently publishing), 'complete' (finished), 'upcoming' (not yet published)")
    order_by: Optional[Literal['mal_id', 'title', 'start_date', 'end_date', 'volumes', 'score', 'rank', 'popularity']] = Field('popularity', description="Sort results by this field")
    sort: Optional[Literal['desc', 'asc']] = Field('desc', description="Sort direction")
    start_date: Optional[str] = Field(None, description="Filter manga that started after this date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Filter manga that ended before this date (YYYY-MM-DD)")

class MangaSearchResponse(BaseModel):
    """Response model for manga search results."""
    mal_id: Optional[int] = None
    title: Optional[str] = None
    volumes: Optional[int] = None
    status: Optional[str] = None
    publishing: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    score: Optional[float] = None
    scored_by: Optional[int] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    favorites: Optional[int] = None
    synopsis: Optional[str] = None
    background: Optional[str] = None
    authors_mal_ids: Optional[List[int]] = None
    authors_names: Optional[List[str]] = None
    genre_ids: Optional[List[int]] = None
    genre_names: Optional[List[str]] = None

class TopMangaParams(BaseModel):
    """Parameters for filtering top manga requests."""
    filter: Optional[Literal['airing', 'upcoming', 'bypopularity', 'favorite']] = Field('airing', description="Ranking category - 'airing' (currently publishing), 'upcoming' (not yet published), 'bypopularity' (most popular), 'favorite' (most favorited)")
    ratings: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = Field('g', description="Content rating filter")
    limit: Optional[int] = Field(10, description="Number of results to return", ge=1, le=500)

class TopMangaResponse(BaseModel):
    """Response model for top manga data."""
    title: Optional[str]
    type: Optional[str] = None
    volumes: Optional[int] = None
    status: Optional[str] = None
    rank: Optional[int] = None
    synopsis: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None

class RandomMangaResponse(BaseModel):
    """Response model for random manga data."""
    title: Optional[str] = None
    type: Optional[str] = None
    volumes: Optional[int] = None
    status: Optional[str] = None
    rank: Optional[int] = None
    synopsis: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None

class MangaReviewParams(BaseModel):
    """Parameters for filtering manga review requests."""
    preliminary: Optional[bool] = Field(True, description="Include preliminary reviews - set to True if manga is still publishing")
    spoilers: Optional[bool] = Field(False, description="Include reviews with spoilers - set to True to include spoiler reviews")

class MangaReviewResponse(BaseModel):
    """Response model for manga review data."""
    review: Optional[str]
    date: Optional[str]

class SimilarMangaResponse(BaseModel):
    """Response model for manga recommendations"""
    mal_id: Optional[int] = None
    title: Optional[str] = None

class MangaNewsResponse(BaseModel):
    """Response model for manga news"""
    title: Optional[str] = None
    date: Optional[str] = None
    author_username: Optional[str] = None
    url: Optional[str] = None
    excerpt: Optional[str] = None


