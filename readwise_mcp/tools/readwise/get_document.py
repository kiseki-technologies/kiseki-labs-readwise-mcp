# Standard Library
import asyncio
import logging
from datetime import date
from typing import Dict, List, Optional

# Internal Libraries
from readwise_mcp.tools.readwise.common import (
    DEFAULT_SLEEP_BETWEEN_REQUESTS_IN_SECONDS,
    PAGE_SIZE,
    READWISE_API_URL,
    get_data,
    to_book_category,
)
from readwise_mcp.types.book import Book


async def get_documents_by_names(
    readwise_api_key: str, document_names: List[str], document_category: str = ""
) -> Dict[str, Optional[Book]]:
    """Get documents (aka books) from Readwise by a list of names"""

    # Create a mapping from lowercase name to original name for lookup
    name_map = {name.lower(): name for name in document_names}
    # Initialize results with None for all requested original names
    results: Dict[str, Optional[Book]] = {name: None for name in document_names}
    found_names_lower = set()

    params = {"page_size": PAGE_SIZE}
    if document_category:
        try:
            params["category"] = to_book_category(document_category).value
        except ValueError as e:
            raise ValueError(f"Invalid category: {document_category}. {str(e)}")

    url = f"{READWISE_API_URL}/books/"
    first_request = True

    logging.debug(f"Searching for documents in {url} with params: {params}")

    while True:
        # Pass params only on the first request. Subsequent requests use the 'next' URL.
        current_params = params if first_request else None
        response = await get_data(readwise_api_key, url, current_params)
        first_request = False

        logging.info(f"Response: {response}")

        books_json = response["results"]

        for book_json in books_json:
            book_title_lower = book_json["title"].lower()
            # Check if this book title matches one of the requested names (case-insensitive)
            # and we haven't found it yet.
            if book_title_lower in name_map and book_title_lower not in found_names_lower:
                original_name = name_map[book_title_lower]
                logging.info(f"Found document: {book_json} (requested as {original_name})")
                results[original_name] = Book(**book_json)
                found_names_lower.add(book_title_lower)

        # Check if all requested documents have been found
        if len(found_names_lower) == len(document_names):
            logging.info("Found all requested documents.")
            break

        url = response.get("next", None)
        if not url:
            logging.info("No more pages to fetch from Readwise API.")
            break

        logging.info(
            f"Fetched page, found {len(found_names_lower)}/{len(document_names)} requested documents so far. Next url: {url is not None}"
        )
        await asyncio.sleep(DEFAULT_SLEEP_BETWEEN_REQUESTS_IN_SECONDS)  # Small delay between requests

    # Log any names that were not found
    not_found_names = [name for name, book in results.items() if book is None]
    if not_found_names:
        logging.warning(f"Could not find the following documents: {', '.join(not_found_names)}")

    return results


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

        await asyncio.sleep(DEFAULT_SLEEP_BETWEEN_REQUESTS_IN_SECONDS)
    return books
