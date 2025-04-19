# Standard Library
import logging
from typing import Dict, List, Optional, Tuple
from datetime import date
import dateparser

# Third Party
import httpx

# Internal Libraries
from readwise_mcp.types.book import BookCategory

READWISE_API_URL = "https://readwise.io/api/v2"

PAGE_SIZE = 50


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
        raise ValueError(
            f"Invalid category: {category_str}. Valid categories are: {BookCategory.get_valid_values()}"
        )


def get_date_range_from_date_expression(date_expression: str) -> Tuple[date, date]:
    """Get the start and end dates from a date expression.

    Args:
        date_expression (str): The date expression to parse.

    Returns:
        Tuple[date, date]: The start and end dates.
    """

    from_dt = dateparser.parse(date_expression)

    if not from_dt:
        raise ValueError(f"Could not parse date expression: {date_expression}")

    from_date = from_dt.date()
    to_date = date.today()

    return (from_date, to_date)


async def get_data(
    api_key: str, url: str, params: Optional[Dict] = None, retries: int = 3
) -> List | Dict:

    for _ in range(retries):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, headers={"Authorization": f"Token {api_key}"}, params=params
                )
                return response.json()
            except Exception as e:
                logging.error(f"Error getting data from {url}: {e}")
                continue

    raise Exception(f"Failed to get data from {url} after {retries} retries")
