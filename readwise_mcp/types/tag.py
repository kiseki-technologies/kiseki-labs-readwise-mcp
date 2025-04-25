# Third Party
from pydantic import BaseModel


class Tag(BaseModel):
    """Represents a tag associated with a highlight."""

    id: int
    name: str
