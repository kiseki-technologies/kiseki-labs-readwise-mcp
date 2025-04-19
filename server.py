# Standard Library
import asyncio
import logging
import os
from datetime import date
from typing import List, Optional

# Third Party
from dotenv import load_dotenv
from fastmcp import FastMCP

# Internal Libraries
from readwise_mcp.tools.readwise.get_document import (
    get_document_by_name,
    list_documents_by_filters,
)
from readwise_mcp.tools.readwise.get_highlights import (
    get_highlight_by_document_id,
    get_highlights_by_filters,
)
from readwise_mcp.types.book import Book
from readwise_mcp.types.highlight import Highlight

load_dotenv()

READWISE_API_KEY = os.getenv("READWISE_API_KEY")


# Create an MCP server
mcp = FastMCP("Kiseki-Labs-Readwise-MCP")


@mcp.tool()
async def find_readwise_document_by_name(
    document_name: str,
) -> Book | None:
    """Find a document in Readwise by name

    Args:
        document_name (str): The name of the document to search for in Readwise.
        document_category (str, optional): The category of the document to search for in Readwise.
            Allowed values are 'books', 'articles', 'tweets', 'podcasts', 'supplementals',
            or simply empty string '' if no category is specified. Defaults to "".

    Returns:
        A Book object if found, None otherwise.
    """

    logging.info(f"*** Searching for document: {document_name}")
    doc = await get_document_by_name(READWISE_API_KEY, document_name)
    if doc:
        return doc

    logging.info(f"*** No document found for {document_name}. Returning None")
    return None


@mcp.tool()
async def list_readwise_documents_by_filters(
    document_category: str = "",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> List[Book]:
    """List all documents in Readwise based on either category or date range
    At least one filter must be provided.

    Args:
        document_category (str, optional): The category of the documents to list in Readwise.
            Allowed values are 'books', 'articles', 'tweets', 'podcasts', 'supplementals',
            or simply empty string '' if no category is specified. Defaults to "".
        from_date (Optional[date]): The start date to filter documents (inclusive).
            Documents created on or after this date will be returned.
        to_date (Optional[date]): The end date to filter documents (inclusive).
            Documents created on or before this date will be returned.

    Returns:
        List[Book]: A list of Book objects containing the documents from the specified category.

    Raises:
        ValueError: If no filters are provided (all parameters are None or empty).
    """
    documents = await list_documents_by_filters(
        READWISE_API_KEY, document_category, from_date, to_date
    )
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
    tasks = [
        get_highlight_by_document_id(READWISE_API_KEY, doc_id)
        for doc_id in document_ids
    ]

    # Execute all tasks concurrently and gather the results
    results = await asyncio.gather(*tasks)

    highlights: List[Highlight] = []

    # Flatten the list of lists into a single list of highlights
    for doc_highlights in results:
        highlights.extend(doc_highlights)

    return highlights


@mcp.tool()
async def get_readwise_highlights_by_filters(
    date_expression: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    tag_names: List[str] = [],
) -> List[Highlight]:
    """
    Get highlights from Readwise by filters.

    This function retrieves highlights from Readwise based on date range and/or tags.
    At least one filter (date_expression, from_date, to_date, or tag_names) must be provided.

    Args:
        date_expression (Optional[str]): A date expression to filter highlights by.
            This is a string that can be parsed by the `dateparser` library.
            If provided, highlights created on or after this date will be returned.
        from_date (Optional[date]): The start date to filter highlights (inclusive).
            Highlights created on or after this date will be returned.
        to_date (Optional[date]): The end date to filter highlights (inclusive).
            Highlights created on or before this date will be returned.
        tag_names (List[str]): List of tag names to filter highlights by.
            This list is made up of strings that should only contain the name of the tags, not the tag ids.
            Only highlights with at least one of these tags will be returned.

    Returns:
        List[Highlight]: A list of Highlight objects matching the specified filters.

    Raises:
        ValueError: If no filters are provided (all parameters are None or empty).
    """
    highlights = await get_highlights_by_filters(
        READWISE_API_KEY, date_expression, from_date, to_date, tag_names
    )
    return highlights


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
