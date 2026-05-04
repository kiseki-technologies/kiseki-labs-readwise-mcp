# Standard Library
from datetime import date
from unittest.mock import AsyncMock, patch

# Third Party
import pytest

# Internal Libraries
from readwise_mcp.tools.readwise.get_document import get_documents_by_names, list_documents_by_filters
from readwise_mcp.types.book import Book

FAKE_API_KEY = "fake-key"

SAMPLE_BOOK_JSON = {
    "id": 101,
    "title": "Test Book",
    "author": "Author A",
    "category": "books",
    "source": "kindle",
    "num_highlights": 5,
    "last_highlight_at": "2024-01-15T10:00:00Z",
    "updated": "2024-01-15T10:00:00Z",
    "cover_image_url": "https://example.com/cover.jpg",
    "highlights_url": "https://readwise.io/api/v2/highlights/?book_id=101",
    "source_url": None,
    "asin": None,
    "tags": [],
    "document_note": "",
}

SAMPLE_ARTICLE_JSON = {
    **SAMPLE_BOOK_JSON,
    "id": 102,
    "title": "Test Article",
    "category": "articles",
}


def _api_response(results, next_url=None):
    return {"results": results, "next": next_url}


@pytest.mark.asyncio
async def test_get_documents_by_names_single_found():
    with patch("readwise_mcp.tools.readwise.get_document.get_data", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _api_response([SAMPLE_BOOK_JSON])
        result = await get_documents_by_names(FAKE_API_KEY, ["Test Book"])

    assert "Test Book" in result
    assert isinstance(result["Test Book"], Book)
    assert result["Test Book"].id == 101


@pytest.mark.asyncio
async def test_get_documents_by_names_not_found():
    with patch("readwise_mcp.tools.readwise.get_document.get_data", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _api_response([SAMPLE_BOOK_JSON])
        result = await get_documents_by_names(FAKE_API_KEY, ["Nonexistent Book"])

    assert result["Nonexistent Book"] is None


@pytest.mark.asyncio
async def test_get_documents_by_names_case_insensitive():
    with patch("readwise_mcp.tools.readwise.get_document.get_data", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _api_response([SAMPLE_BOOK_JSON])
        result = await get_documents_by_names(FAKE_API_KEY, ["test book"])

    assert isinstance(result["test book"], Book)
    assert result["test book"].title == "Test Book"


@pytest.mark.asyncio
async def test_get_documents_by_names_multiple_pages():
    """Test pagination: document found on the second page."""
    with patch("readwise_mcp.tools.readwise.get_document.get_data", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [
            _api_response([], next_url="https://readwise.io/api/v2/books/?page=2"),
            _api_response([SAMPLE_BOOK_JSON]),
        ]
        result = await get_documents_by_names(FAKE_API_KEY, ["Test Book"])

    assert isinstance(result["Test Book"], Book)
    assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_get_documents_by_names_stops_when_all_found():
    """Should stop paginating once all requested documents are found."""
    with patch("readwise_mcp.tools.readwise.get_document.get_data", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _api_response(
            [SAMPLE_BOOK_JSON, SAMPLE_ARTICLE_JSON], next_url="https://readwise.io/api/v2/books/?page=2"
        )
        result = await get_documents_by_names(FAKE_API_KEY, ["Test Book", "Test Article"])

    assert mock_get.call_count == 1
    assert isinstance(result["Test Book"], Book)
    assert isinstance(result["Test Article"], Book)


@pytest.mark.asyncio
async def test_get_documents_by_names_invalid_category():
    with pytest.raises(ValueError, match="Invalid category"):
        await get_documents_by_names(FAKE_API_KEY, ["Test Book"], document_category="invalid")


@pytest.mark.asyncio
async def test_list_documents_by_filters_by_category():
    with patch("readwise_mcp.tools.readwise.get_document.get_data", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _api_response([SAMPLE_BOOK_JSON])
        result = await list_documents_by_filters(FAKE_API_KEY, document_category="books")

    assert len(result) == 1
    assert isinstance(result[0], Book)
    mock_get.assert_called_once()
    call_params = mock_get.call_args[0][2]
    assert call_params["category"] == "books"


@pytest.mark.asyncio
async def test_list_documents_by_filters_by_date_range():
    with patch("readwise_mcp.tools.readwise.get_document.get_data", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _api_response([SAMPLE_ARTICLE_JSON])
        result = await list_documents_by_filters(FAKE_API_KEY, from_date=date(2024, 1, 1), to_date=date(2024, 1, 31))

    assert len(result) == 1
    call_params = mock_get.call_args[0][2]
    assert "last_highlight_at__gt" in call_params
    assert "last_highlight_at__lt" in call_params


@pytest.mark.asyncio
async def test_list_documents_by_filters_pagination():
    with patch("readwise_mcp.tools.readwise.get_document.get_data", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [
            _api_response([SAMPLE_BOOK_JSON], next_url="https://readwise.io/api/v2/books/?page=2"),
            _api_response([SAMPLE_ARTICLE_JSON]),
        ]
        result = await list_documents_by_filters(FAKE_API_KEY, document_category="books")

    assert len(result) == 2
    assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_list_documents_by_filters_no_filters_raises():
    with pytest.raises(ValueError, match="At least one parameter must be provided"):
        await list_documents_by_filters(FAKE_API_KEY)


@pytest.mark.asyncio
async def test_list_documents_by_filters_invalid_category():
    with pytest.raises(ValueError, match="Invalid category"):
        await list_documents_by_filters(FAKE_API_KEY, document_category="invalid")
