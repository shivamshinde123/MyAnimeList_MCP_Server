

from pydantic import BaseModel
from typing import Literal, Optional, List

class MangaSearchParams(BaseModel):
    """Parameters for searching manga on MyAnimeList."""
    query: Optional[str] = None
    limit: Optional[int] = 5
    status: Optional[Literal['airing', 'complete', 'uncoming']] = 'complete'
    order_by: Optional[Literal['mal_id', 'title', 'start_date', 'end_date', 'volumes', 'score', 'rank', 'popularity']] = 'popularity'
    sort: Optional[Literal['desc', 'asc']] = 'desc'
    start_date: Optional[str] = None
    end_date: Optional[str] = None

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
    filter: Optional[Literal['airing', 'upcoming', 'bypopularity', 'favorite']] = 'airing'
    ratings: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = 'g'
    limit: Optional[int] = 10

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
    preliminary: Optional[bool] = True # if the manga is airing/publishing, then preliminary needs to be true
    spoilers: Optional[bool] = False

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


