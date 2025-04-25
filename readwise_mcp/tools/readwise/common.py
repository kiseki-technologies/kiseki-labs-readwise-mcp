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


async def get_data(api_key: str, url: str, params: Optional[Dict] = None, retries: int = 3) -> List | Dict:
    """Get data from the API."""

    for _ in range(retries):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers={"Authorization": f"Token {api_key}"}, params=params)
                # Check whether we got a 429 HTTP error
                if response.status_code == 429:
                    # Extract the Retry-After header
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        logging.info(f"Rate limit exceeded. Retrying in {retry_after} seconds.")
                        await asyncio.sleep(int(retry_after))
                        continue
                    else:
                        logging.info("Rate limit exceeded. Retrying in 1 second.")
                        await asyncio.sleep(1)
                        continue
                if response.status_code != 200:
                    raise Exception(f"Failed to get data from {url}: {response.status_code} {response.text}")
                return response.json()
            except Exception as e:
                logging.error(f"Error getting data from {url}: {e}")
                continue

    raise Exception(f"Failed to get data from {url} with params {params} after {retries} retries")
