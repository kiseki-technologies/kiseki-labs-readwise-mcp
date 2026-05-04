# Standard Library
from datetime import date
from unittest.mock import AsyncMock, patch

# Third Party
import pytest

# Internal Libraries
from readwise_mcp.types.book import Book
from readwise_mcp.types.highlight import Highlight


@pytest.mark.asyncio
async def test_list_documents_rejects_duration_with_date():
    """duration_expression and from_date/to_date are mutually exclusive."""
    # Import inside test to avoid server.py side effects at module level
    # Internal Libraries
    from server import list_readwise_documents_by_filters

    with pytest.raises(ValueError, match="Cannot provide both duration_expression and from_date or to_date"):
        await list_readwise_documents_by_filters(duration_expression="1w", from_date=date(2024, 1, 1))


@pytest.mark.asyncio
async def test_list_documents_rejects_duration_with_to_date():
    # Internal Libraries
    from server import list_readwise_documents_by_filters

    with pytest.raises(ValueError, match="Cannot provide both duration_expression and from_date or to_date"):
        await list_readwise_documents_by_filters(duration_expression="1w", to_date=date(2024, 1, 31))


@pytest.mark.asyncio
async def test_list_documents_parses_duration():
    # Internal Libraries
    from server import list_readwise_documents_by_filters

    with patch("server.list_documents_by_filters", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        with patch("server.parse_duration", return_value=(date(2024, 1, 8), date(2024, 1, 15))):
            result = await list_readwise_documents_by_filters(duration_expression="1w")

    assert result == []
    _, call_kwargs = mock_list.call_args
    # Verify the parsed dates were passed through
    assert call_kwargs.get("from_date") is not None or mock_list.call_args[0][2] == date(2024, 1, 8)


@pytest.mark.asyncio
async def test_get_highlights_rejects_empty_document_ids():
    # Internal Libraries
    from server import get_readwise_highlights_by_document_ids

    with pytest.raises(ValueError, match="No document IDs provided"):
        await get_readwise_highlights_by_document_ids(document_ids=[])


@pytest.mark.asyncio
async def test_get_highlights_by_filters_rejects_duration_with_date():
    # Internal Libraries
    from server import get_readwise_highlights_by_filters

    with pytest.raises(ValueError, match="Cannot provide both duration_expression and from_date or to_date"):
        await get_readwise_highlights_by_filters(duration_expression="1w", from_date=date(2024, 1, 1))


@pytest.mark.asyncio
async def test_get_highlights_concurrent_gather():
    """Highlights for multiple document IDs are fetched concurrently."""
    # Internal Libraries
    from server import get_readwise_highlights_by_document_ids

    highlight_json = {
        "id": 1,
        "text": "hi",
        "note": "",
        "location": 1,
        "location_type": "order",
        "highlighted_at": "2024-01-15T10:00:00Z",
        "url": None,
        "color": "yellow",
        "updated": "2024-01-15T10:00:00Z",
        "book_id": 101,
        "tags": [],
    }
    highlight_json_2 = {**highlight_json, "id": 2, "book_id": 202}

    with patch("server.get_highlight_by_document_id", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [
            [Highlight(**highlight_json)],
            [Highlight(**highlight_json_2)],
        ]
        result = await get_readwise_highlights_by_document_ids(document_ids=[101, 202])

    assert len(result) == 2
    assert mock_get.call_count == 2
    book_ids = {h.book_id for h in result}
    assert book_ids == {101, 202}
