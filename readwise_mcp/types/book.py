# Standard Library
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Set

# Third Party
from pydantic import BaseModel, HttpUrl

# Internal Libraries
# Internal
from readwise_mcp.types.tag import Tag


class BookCategory(str, Enum):
    """Enumeration of valid book categories in Readwise."""

    BOOKS = "books"
    ARTICLES = "articles"
    TWEETS = "tweets"
    SUPPLEMENTALS = "supplementals"
    PODCASTS = "podcasts"

    @classmethod
    def get_valid_values(cls) -> Set[str]:
        """Returns a set of all valid category string values."""
        return {category.value for category in cls}

    @classmethod
    def is_valid_category(cls, category_str: str) -> bool:
        """Check if the given string is a valid book category."""
        return category_str in cls.get_valid_values()


class Book(BaseModel):
    """Represents a document from Readwise API."""

    id: int
    title: str
    author: str
    category: str
    source: str
    num_highlights: int
    last_highlight_at: datetime
    updated: datetime
    cover_image_url: HttpUrl
    highlights_url: str
    source_url: Optional[HttpUrl] = None
    asin: Optional[str] = None
    tags: List[str | Tag] = []
    document_note: str = ""
