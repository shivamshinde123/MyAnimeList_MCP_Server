
from pydantic import BaseModel, Field
from typing import Optional, List

class ProducerResourceParams(BaseModel):
    """Model for producer resource parameters"""
    query: str = Field("Toei Animation", description="Search term for producer/studio name", min_length=1)
    limit: Optional[int] = Field(5, description="Number of results to return", ge=1, le=25)

class ProducerResourceResponse(BaseModel):
    """Model for producer resource response"""
    about: Optional[str] = None
    titles: Optional[List[str]] = None


