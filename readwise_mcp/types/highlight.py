# Standard Library
from datetime import datetime
from typing import List, Optional

# Third Party
from pydantic import BaseModel, HttpUrl


class Tag(BaseModel):
    """Represents a tag associated with a highlight."""

    id: int
    name: str


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
