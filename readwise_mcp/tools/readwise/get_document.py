# Standard Library
import logging
import time
import traceback
from datetime import date
from typing import Dict, List, Optional

# Internal Libraries
# Company Libraries
from readwise_mcp.tools.readwise.common import (
    PAGE_SIZE,
    READWISE_API_URL,
    get_data,
    to_book_category,
)
from readwise_mcp.types.book import Book, BookCategory


async def get_document_by_name(readwise_api_key: str, document_name: str, document_category: str = "") -> Book | None:
    """Get a document (aka book) from Readwise by name"""

    params = {"page_size": PAGE_SIZE}
    if document_category:
        params["category"] = document_category

    url = f"{READWISE_API_URL}/books/"

    while True:
        response = await get_data(readwise_api_key, url, params)

        books_json = response["results"]

        for book_json in books_json:
            if book_json["title"].lower() == document_name.lower():
                return Book(**book_json)

        url = response.get("next", None)
        if not url:
            break

    logging.warning(f"No book found for {document_name}")
    return None


async def list_documents_by_filters(
    readwise_api_key: str,
    document_category: str = "",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> List[Book]:
    """List all documents in Readwise based on either category or date range
    Make sure to provide at least one of the parameters.
    """

    params = {}
    if document_category:
        # Validate that the category is a valid BookCategory
        try:
            params["category"] = to_book_category(document_category).value
        except ValueError as e:
            raise ValueError(f"Invalid category: {document_category}. {str(e)}")

    url = f"{READWISE_API_URL}/books/"

    if from_date:
        from_date_str = from_date.isoformat() + "T00:00:00Z"
        params["last_highlight_at__gt"] = from_date_str

    if to_date:
        to_date_str = to_date.isoformat() + "T23:59:59Z"
        params["last_highlight_at__lt"] = to_date_str

    if not params:
        raise ValueError("At least one parameter must be provided")

    params["page_size"] = PAGE_SIZE

    books: List[Book] = []
    first_request = True

    while True:
        # Pass params only on the first request. Subsequent requests use the 'next' URL which contains all params.
        current_params = params if first_request else None
        response = await get_data(readwise_api_key, url, current_params)
        first_request = False

        books_json = response["results"]
        books.extend([Book(**book_json) for book_json in books_json])

        url = response.get("next", None)
        if not url:
            break

        logging.info(f"Fetched {len(books_json)} books. Next url: {url}")

        time.sleep(1)
    return books
