# Standard Library
import asyncio
import logging
from typing import Dict, List, Optional

# Third Party
import httpx

# Internal Libraries
from readwise_mcp.types.book import BookCategory

READWISE_API_URL = "https://readwise.io/api/v2"

PAGE_SIZE = 50

DEFAULT_SLEEP_BETWEEN_REQUESTS_IN_SECONDS = 1


def to_book_category(category_str: str) -> BookCategory:
    """Convert a string to a BookCategory enum.

    Args:
        category_str (str): The string to convert to a BookCategory enum.

    Returns:
        BookCategory: The BookCategory enum.

    Raises:
        ValueError: If the category string is not a valid BookCategory.
    """
    if BookCategory.is_valid_category(category_str):
        return BookCategory(category_str)
    else:
        raise ValueError(f"Invalid category: {category_str}. Valid categories are: {BookCategory.get_valid_values()}")


async def _make_request(
    api_key: str,
    method: str,
    url: str,
    expected_statuses: tuple,
    params: Optional[Dict] = None,
    body: Optional[Dict] = None,
    retries: int = 3,
) -> Optional[Dict | List]:
    """Make an HTTP request with retry and rate-limit handling.

    Args:
        api_key: Readwise API key.
        method: HTTP method (GET, POST, PATCH, DELETE).
        url: Full API URL.
        expected_statuses: Tuple of HTTP status codes that indicate success.
        params: Optional query parameters (for GET requests).
        body: Optional JSON body (for POST/PATCH requests).
        retries: Number of retry attempts.

    Returns:
        Parsed JSON response, or None for responses with no body (e.g. 204).
    """

    for _ in range(retries):
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Token {api_key}"}
                response = await client.request(method, url, headers=headers, params=params, json=body)
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        logging.info(f"Rate limit exceeded. Retrying in {retry_after} seconds.")
                        await asyncio.sleep(int(retry_after))
                        continue
                    else:
                        logging.info("Rate limit exceeded. Retrying in 1 second.")
                        await asyncio.sleep(1)
                        continue
                if response.status_code not in expected_statuses:
                    raise Exception(f"Failed to {method} {url}: {response.status_code} {response.text}")
                if response.status_code == 204:
                    return None
                return response.json()
            except Exception as e:
                logging.error(f"Error during {method} {url}: {e}")
                continue

    raise Exception(f"Failed to {method} {url} after {retries} retries")


async def get_data(api_key: str, url: str, params: Optional[Dict] = None, retries: int = 3) -> List | Dict:
    """Get data from the API."""
    return await _make_request(api_key, "GET", url, (200,), params=params, retries=retries)


async def post_data(api_key: str, url: str, body: Dict, retries: int = 3) -> Dict:
    """Post data to the API."""
    return await _make_request(api_key, "POST", url, (200, 201), body=body, retries=retries)


async def patch_data(api_key: str, url: str, body: Dict, retries: int = 3) -> Dict:
    """Patch data on the API."""
    return await _make_request(api_key, "PATCH", url, (200,), body=body, retries=retries)


async def delete_data(api_key: str, url: str, retries: int = 3) -> None:
    """Delete data from the API."""
    await _make_request(api_key, "DELETE", url, (204,), retries=retries)
