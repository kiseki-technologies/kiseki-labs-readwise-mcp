# Standard Library
from unittest.mock import AsyncMock, patch

# Third Party
import httpx
import pytest

# Internal Libraries
from readwise_mcp.tools.readwise.common import get_data, to_book_category
from readwise_mcp.types.book import BookCategory


def test_to_book_category_valid():
    assert to_book_category("books") == BookCategory.BOOKS
    assert to_book_category("articles") == BookCategory.ARTICLES
    assert to_book_category("tweets") == BookCategory.TWEETS
    assert to_book_category("supplementals") == BookCategory.SUPPLEMENTALS
    assert to_book_category("podcasts") == BookCategory.PODCASTS


@pytest.mark.parametrize("invalid_category", ["book", "BOOKS", "article", "video", "", "unknown"])
def test_to_book_category_invalid(invalid_category):
    with pytest.raises(ValueError, match="Invalid category"):
        to_book_category(invalid_category)


@pytest.mark.asyncio
async def test_get_data_success():
    mock_response = httpx.Response(200, json={"results": [{"id": 1}]})
    with patch("readwise_mcp.tools.readwise.common.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await get_data("fake-key", "https://readwise.io/api/v2/books/", {"page_size": 50})

    assert result == {"results": [{"id": 1}]}
    mock_client.request.assert_called_once_with(
        "GET",
        "https://readwise.io/api/v2/books/",
        headers={"Authorization": "Token fake-key"},
        params={"page_size": 50},
        json=None,
    )


@pytest.mark.asyncio
async def test_get_data_rate_limit_then_success():
    rate_limit_response = httpx.Response(429, headers={"Retry-After": "0"}, json={})
    success_response = httpx.Response(200, json={"results": []})

    with patch("readwise_mcp.tools.readwise.common.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.side_effect = [rate_limit_response, success_response]
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await get_data("fake-key", "https://readwise.io/api/v2/books/")

    assert result == {"results": []}
    assert mock_client.request.call_count == 2


@pytest.mark.asyncio
async def test_get_data_rate_limit_no_retry_after_header():
    rate_limit_response = httpx.Response(429, json={})
    success_response = httpx.Response(200, json={"ok": True})

    with patch("readwise_mcp.tools.readwise.common.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.side_effect = [rate_limit_response, success_response]
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await get_data("fake-key", "https://readwise.io/api/v2/books/")

    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_get_data_non_200_raises():
    error_response = httpx.Response(500, text="Internal Server Error")

    with patch("readwise_mcp.tools.readwise.common.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.return_value = error_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(Exception, match="Failed to GET"):
            await get_data("fake-key", "https://readwise.io/api/v2/books/", retries=1)


@pytest.mark.asyncio
async def test_get_data_retries_exhausted():
    error_response = httpx.Response(500, text="Server Error")

    with patch("readwise_mcp.tools.readwise.common.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.request.return_value = error_response
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(Exception, match="Failed to GET.*after 2 retries"):
            await get_data("fake-key", "https://readwise.io/api/v2/books/", retries=2)
