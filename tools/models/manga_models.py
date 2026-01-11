

from pydantic import BaseModel
from typing import Literal, Optional


class TopMangaParams(BaseModel):
    filter: Optional[Literal['airing', 'upcoming', 'bypopularity', 'favorite']] = 'airing'
    ratings: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = 'g'
    limit: Optional(int) = 10

class TopMangaResponse(BaseModel):
    title: str
    type: Optional[str] = None
    volumes: Optional[int] = None
    status: Optional[str] = None
    rank: Optional[int] = None
    synopsis: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None

class RandomMangaResponse(BaseModel):
    title: str
    type: Optional[str] = None
    volumes: Optional[int] = None
    status: Optional[str] = None
    rank: Optional[int] = None
    synopsis: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None

class MangaReviewParams(BaseModel):
    preliminary: Optional[bool] # if the manga is airing/publishing, then preliminary needs to be true
    spoliers: Optional[bool]

class MangaReviewResponse(BaseModel):
    review: Optional[str]
    date: Optional[str]