
from pydantic import BaseModel
from typing import Optional, List

class ProducerResourceParams(BaseModel):
    """Model for producer resource parameters"""
    query: Optional[str] = "Toei Animation"
    limit: Optional[int] = 5

class ProducerResourceResponse(BaseModel):
    """Model for producer resource response"""
    about: Optional[str] = None
    titles: Optional[List[str]] = None


