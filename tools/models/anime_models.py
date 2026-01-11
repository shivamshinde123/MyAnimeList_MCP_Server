
from pydantic import BaseModel
from typing import Literal, Optional


class TopAnimeParams(BaseModel):
    filter: Optional[Literal['airing', 'upcoming', 'bypopularity', 'favorite']] = 'airing'
    ratings: Optional[Literal['g', 'pg', 'pg13', 'r17', 'r', 'rx']] = 'g'
    limit: Optional(int) = 10

class TopAnimeResponse(BaseModel):
    title: str
    type: Optional[str]
    episodes: Optional[int]
    status: Optional[str]
    rating: Optional[str]
    rank: Optional[int]
    synopsis: Optional[str]
    season: Optional[str]
    year: Optional[int]

class RandomAnimeResponse(BaseModel):
    title: str
    type: Optional[str]
    episodes: Optional[int]
    status: Optional[str]
    rating: Optional[str]
    rank: Optional[int]
    synopsis: Optional[str]
    season: Optional[str]
    year: Optional[int]

class AnimeReviewParams(BaseModel):
    preliminary: Optional[bool] # if the anime is airing/publishing, then preliminary needs to be true
    spoliers: Optional[bool]

class AnimeReviewResponse(BaseModel):
    review: Optional[str]
    date: Optional[str]

