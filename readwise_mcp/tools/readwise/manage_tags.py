# Standard Library
from typing import List, Literal, Optional

# Internal Libraries
from readwise_mcp.tools.readwise.common import (
    READWISE_API_URL,
    delete_data,
    get_data,
    patch_data,
    post_data,
)
from readwise_mcp.types.tag import Tag

EntityType = Literal["highlights", "books"]


def _tags_url(entity_type: EntityType, entity_id: int, tag_id: Optional[int] = None) -> str:
    """Build the tags URL for a given entity."""
    base = f"{READWISE_API_URL}/{entity_type}/{entity_id}/tags"
    if tag_id is not None:
        return f"{base}/{tag_id}"
    return base


async def get_tags(api_key: str, entity_type: EntityType, entity_id: int) -> List[Tag]:
    """Get all tags for a highlight or book.

    The book tags endpoint returns a plain list, while the highlight tags
    endpoint returns a paginated response with a ``results`` key.

    Args:
        api_key: Readwise API key.
        entity_type: Either "highlights" or "books".
        entity_id: The ID of the highlight or book.

    Returns:
        List of Tag objects.
    """
    url = _tags_url(entity_type, entity_id)
    data = await get_data(api_key, url)
    tag_list = data["results"] if isinstance(data, dict) else data
    return [Tag(**tag) for tag in tag_list]


async def add_tag(api_key: str, entity_type: EntityType, entity_id: int, tag_name: str) -> Tag:
    """Add a tag to a highlight or book.

    Args:
        api_key: Readwise API key.
        entity_type: Either "highlights" or "books".
        entity_id: The ID of the highlight or book.
        tag_name: The name of the tag to add.

    Returns:
        The created Tag object.
    """
    url = _tags_url(entity_type, entity_id)
    data = await post_data(api_key, url, {"name": tag_name})
    return Tag(**data)


async def update_tag(api_key: str, entity_type: EntityType, entity_id: int, tag_id: int, new_name: str) -> Tag:
    """Rename a tag on a highlight or book.

    Args:
        api_key: Readwise API key.
        entity_type: Either "highlights" or "books".
        entity_id: The ID of the highlight or book.
        tag_id: The ID of the tag to rename.
        new_name: The new name for the tag.

    Returns:
        The updated Tag object.
    """
    url = _tags_url(entity_type, entity_id, tag_id)
    data = await patch_data(api_key, url, {"name": new_name})
    return Tag(**data)


async def delete_tag(api_key: str, entity_type: EntityType, entity_id: int, tag_id: int) -> None:
    """Remove a tag from a highlight or book.

    Args:
        api_key: Readwise API key.
        entity_type: Either "highlights" or "books".
        entity_id: The ID of the highlight or book.
        tag_id: The ID of the tag to remove.
    """
    url = _tags_url(entity_type, entity_id, tag_id)
    await delete_data(api_key, url)
