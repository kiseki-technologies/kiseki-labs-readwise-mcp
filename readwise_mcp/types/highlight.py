# Standard Library
from datetime import datetime
from typing import List, Optional

# Third Party
from pydantic import BaseModel, HttpUrl

# Internal Libraries
# Internal
from readwise_mcp.types.tag import Tag


class Highlight(BaseModel):
    """Represents a highlight from Readwise API."""

    id: int
    text: str
    note: str
    location: int
    location_type: str
    highlighted_at: Optional[datetime] = None
    url: Optional[HttpUrl] = None
    color: str
    updated: datetime
    book_id: int
    tags: List[Tag] = []
