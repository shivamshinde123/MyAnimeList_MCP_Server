

from pydantic import BaseModel
from typing import Literal, Optional


class TopMangaParams(BaseModel):
    """Parameters for filtering top manga requests."""
    filter: Optional[Literal['airing', 'upcoming', 'bypopularity', 'favorite']] = 'airing'
    ratings: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = 'g'
    limit: Optional(int) = 10

class TopMangaResponse(BaseModel):
    """Response model for top manga data."""
    title: str
    type: Optional[str] = None
    volumes: Optional[int] = None
    status: Optional[str] = None
    rank: Optional[int] = None
    synopsis: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None

class RandomMangaResponse(BaseModel):
    """Response model for random manga data."""
    title: str
    type: Optional[str] = None
    volumes: Optional[int] = None
    status: Optional[str] = None
    rank: Optional[int] = None
    synopsis: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None

class MangaReviewParams(BaseModel):
    """Parameters for filtering manga review requests."""
    preliminary: Optional[bool] # if the manga is airing/publishing, then preliminary needs to be true
    spoilers: Optional[bool]

class MangaReviewResponse(BaseModel):
    """Response model for manga review data."""
    review: Optional[str]
    date: Optional[str]