# Standard Library
import asyncio
import logging
import os
from datetime import date
from typing import Dict, List, Optional

# Third Party
from dotenv import load_dotenv
from fastmcp import FastMCP

# Internal Libraries
from readwise_mcp.tools.readwise.get_document import (
    get_documents_by_names,
    list_documents_by_filters,
)
from readwise_mcp.tools.readwise.get_highlights import (
    get_highlight_by_document_id,
    get_highlights_by_filters,
)
from readwise_mcp.types.book import Book
from readwise_mcp.types.highlight import Highlight
from readwise_mcp.utils.duration import parse_duration

load_dotenv()

READWISE_API_KEY = os.getenv("READWISE_API_KEY")


# Create an MCP server
mcp = FastMCP("Kiseki-Labs-Readwise-MCP")


@mcp.tool()
async def find_readwise_documents_by_names(
    document_names: List[str],
) -> Dict[str, Optional[Book]]:
    """Find documents in Readwise by a list of names.

    Args:
        document_names (List[str]): The names of the documents to search for in Readwise.

    Returns:
        Dict[str, Optional[Book]]: A dictionary where keys are the requested document names
        and values are the corresponding Book objects if found, or None otherwise.
    """

    logging.info(f"*** Searching for documents: {', '.join(document_names)}")
    docs_dict = await get_documents_by_names(READWISE_API_KEY, document_names)

    found_count = sum(1 for doc in docs_dict.values() if doc is not None)
    logging.info(f"*** Found {found_count}/{len(document_names)} documents.")
    for name, doc in docs_dict.items():
        if doc is None:
            logging.info(f"***   - '{name}': Not found")

    return docs_dict


@mcp.tool()
async def list_readwise_documents_by_filters(
    document_category: str = "",
    duration_expression: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> List[Book]:
    """List all documents in Readwise based on either category or date range
    At least one filter must be provided.

    Args:
        document_category (str, optional): The category of the documents to list in Readwise.
            Allowed values are 'books', 'articles', 'tweets', 'podcasts', 'supplementals',
            or simply empty string '' if no category is specified. Defaults to "".
        duration_expression (Optional[str]): A duration expression to filter documents by creation date.
            Valid formats: "1w", "2h", "30m", etc.
        from_date (Optional[date]): The start date to filter documents (inclusive).
            Documents created on or after this date will be returned.
        to_date (Optional[date]): The end date to filter documents (inclusive).
            Documents created on or before this date will be returned.

    Returns:
        List[Book]: A list of Book objects containing the documents from the specified category.

    Raises:
        ValueError: If no filters are provided (all parameters are None or empty).
    """

    if duration_expression and (from_date or to_date):
        raise ValueError("Cannot provide both duration_expression and from_date or to_date")

    if duration_expression:
        from_date, to_date = parse_duration(duration_expression)

    documents = await list_documents_by_filters(READWISE_API_KEY, document_category, from_date, to_date)
    return documents


@mcp.tool()
async def get_readwise_highlights_by_document_ids(
    document_ids: List[int],
) -> List[Highlight]:
    """
    Get highlights from Readwise by document ids.

    Args:
        document_ids (List[int]): The IDs of the documents to retrieve highlights for.

    Returns:
        List[Highlight]: A list of Highlight objects containing the highlights from the specified document.

    Raises:
        ValueError: If no document IDs are provided.
    """

    if not document_ids:
        raise ValueError("No document IDs provided")

    # Create a list of tasks (co-routines), one for each document ID
    tasks = [get_highlight_by_document_id(READWISE_API_KEY, doc_id) for doc_id in document_ids]

    # Execute all tasks concurrently and gather the results
    results = await asyncio.gather(*tasks)

    highlights: List[Highlight] = []

    # Flatten the list of lists into a single list of highlights
    for doc_highlights in results:
        highlights.extend(doc_highlights)

    return highlights


@mcp.tool()
async def get_readwise_highlights_by_filters(
    duration_expression: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    tag_names: List[str] = [],
) -> List[Highlight]:
    """
    Get highlights from Readwise by filters.

    This function retrieves highlights from Readwise based on date range and/or tags.
    At least one filter (from_date, to_date, or tag_names) must be provided.

    Args:
        duration_expression (Optional[str]): A duration expression to filter highlights by creation date.
            Valid formats: "1w", "2h", "30m", etc.
        from_date (Optional[date]): The start date to filter highlights (inclusive).
            Highlights created on or after this date will be returned.
        to_date (Optional[date]): The end date to filter highlights (inclusive).
            Highlights created on or before this date will be returned.
        tag_names (List[str]): List of tag names to filter highlights by.
            Only highlights with at least one of these tags will be returned.

    Returns:
        List[Highlight]: A list of Highlight objects matching the specified filters.

    Raises:
        ValueError: If no filters are provided (all parameters are None or empty).
    """

    if duration_expression and (from_date or to_date):
        raise ValueError("Cannot provide both duration_expression and from_date or to_date")

    if duration_expression:
        from_date, to_date = parse_duration(duration_expression)

    highlights = await get_highlights_by_filters(READWISE_API_KEY, from_date, to_date, tag_names)
    return highlights


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
