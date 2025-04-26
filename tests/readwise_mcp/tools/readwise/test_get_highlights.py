# Standard Library
from datetime import date, datetime
from typing import List

# Third Party
import pytest

# Internal Libraries
from readwise_mcp.tools.readwise.get_highlights import get_highlight_by_document_id, get_highlights_by_filters
from readwise_mcp.types.highlight import Highlight


@pytest.mark.asyncio
async def test_get_highlights_by_document_id_success(readwise_api_key):
    """Test retrieving highlights for an existing document ID."""

    # Call the function with a real document ID
    highlights = await get_highlight_by_document_id(readwise_api_key, 50788861)

    # Assert we got results (actual results will vary)
    assert isinstance(highlights, list)
    if highlights:
        assert isinstance(highlights[0], Highlight)
        assert highlights[0].book_id == 50788861


@pytest.mark.asyncio
async def test_get_highlights_by_document_id_empty(readwise_api_key):
    """Test retrieving highlights for a document ID with no highlights."""

    # Call the function with a document ID that likely doesn't exist
    highlights = await get_highlight_by_document_id(readwise_api_key, 1234)

    # Assert we got an empty list
    assert isinstance(highlights, list)
    assert len(highlights) == 0


@pytest.mark.asyncio
async def test_get_highlights_by_filters(readwise_api_key):
    """Test retrieving highlights by date range and tag filters."""

    # Define date range and tag
    from_date = date(2025, 4, 13)
    to_date = date(2025, 4, 20)
    tag_names = ["generative ai"]

    # Call the function with real filters
    highlights = await get_highlights_by_filters(
        readwise_api_key, from_date=from_date, to_date=to_date, tag_names=tag_names
    )

    # Assert on the structure of the results
    assert isinstance(highlights, list)

    # If any results were returned, check that they all have the specified tag
    for highlight in highlights:
        assert isinstance(highlight, Highlight)
        tag_names_list = [tag.name for tag in highlight.tags]
        assert "generative ai" in tag_names_list
