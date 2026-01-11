
from pydantic import BaseModel
from typing import Literal, Optional, List


class AnimeSearchParams(BaseModel):
    """Parameters for searching anime on MyAnimeList."""
    query: str
    limit: Optional[int] = 5
    status: Optional[Literal['airing', 'complete', 'uncoming']] = 'airing'
    rating: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = 'g'
    order_by: Optional[Literal['mal_id', 'title', 'start_date', 'end_date', 'episodes', 'score', 'rank', 'popularity']] = 'popularity'
    sort: Optional[Literal['desc', 'asc']] = 'desc'
    start_date: Optional[str] 
    end_date: Optional[str]

class AnimeSearchResponse(BaseModel):
    """Response model for anime search results."""
    mal_id: int
    title: str
    episodes: int
    status: str
    airing: bool
    start_date: str
    end_date: str
    duration: str
    rating: str
    score: float
    scored_by: int
    rank: int
    popularity: int
    favorites: int
    synopsis: str
    background: str
    season: str
    year: int
    producers_mal_ids: List[int]
    producer_names: List[str]
    studio_ids: List[int]
    studio_name: List[str]
    genre_ids: List[int]
    genre_names: List[str]


class TopAnimeParams(BaseModel):
    """Parameters for filtering top anime requests."""
    filter: Optional[Literal['airing', 'upcoming', 'bypopularity', 'favorite']] = 'airing'
    ratings: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = 'g'
    limit: Optional(int) = 10

class TopAnimeResponse(BaseModel):
    """Response model for top anime data."""
    title: str
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
    title: str
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
    preliminary: Optional[bool] # if the anime is airing/publishing, then preliminary needs to be true
    spoilers: Optional[bool]

class AnimeReviewResponse(BaseModel):
    """Response model for anime review data."""
    review: Optional[str]
    date: Optional[str]

