# Standard Library
import asyncio
import logging
from datetime import date
from typing import List, Optional

# Internal Libraries
from readwise_mcp.tools.readwise.common import (
    DEFAULT_SLEEP_BETWEEN_REQUESTS_IN_SECONDS,
    READWISE_API_URL,
    get_data,
)
from readwise_mcp.types.highlight import Highlight


async def get_highlight_by_document_id(api_key: str, document_id: int) -> List[Highlight]:
    """Get highlights by document id."""

    url = f"{READWISE_API_URL}/highlights/"
    params = {"book_id": document_id, "page_size": 100}

    highlights: List[Highlight] = []
    first_request = True
    while True:
        # Pass params only on the first request.
        current_params = params if first_request else None
        hs = await get_data(api_key, url, current_params)
        first_request = False

        hs_results = hs["results"]

        highlights.extend([Highlight(**h) for h in hs_results])

        total_highlights = hs["count"]
        logging.info(f"Total highlights: {total_highlights}")
        url = hs.get("next", None)

        if not url:
            break

        await asyncio.sleep(DEFAULT_SLEEP_BETWEEN_REQUESTS_IN_SECONDS)

    return highlights


async def get_highlights_by_filters(
    api_key: str,
    from_date: Optional[date],
    to_date: Optional[date],
    tag_names: List[str],
) -> List[Highlight]:
    """Get highlights by filters."""

    if not from_date and not to_date and not tag_names:
        raise ValueError("At least one filter must be provided")

    url = f"{READWISE_API_URL}/highlights/"

    params = {}
    if from_date:
        # Convert date to ISO format string
        from_date_str = from_date.isoformat() + "T00:00:00Z"
        params["highlighted_at__gt"] = from_date_str

    if to_date:
        to_date_str = to_date.isoformat() + "T23:59:59Z"
        params["highlighted_at__lt"] = to_date_str

    highlights: List[Highlight] = []
    logging.info(f"Getting highlights with params: {params}")

    first_request = True
    while True:
        # Pass params only on the first request.
        current_params = params if first_request else None
        hs = await get_data(api_key, url, current_params)
        first_request = False

        hs_results = hs["results"]

        rq_highlights = [Highlight(**h) for h in hs_results]

        # Filter highlights by tags if tag_names is provided
        if tag_names and len(tag_names) > 0:
            # Create a filtered list of highlights that have at least one of the specified tags
            filtered_highlights = []
            for highlight in rq_highlights:
                # Check if any of the highlight's tags match the requested tag_names
                highlight_tags = [tag.name for tag in highlight.tags] if highlight.tags else []
                if any(tag in highlight_tags for tag in tag_names):
                    filtered_highlights.append(highlight)

            highlights.extend(filtered_highlights)
            logging.info(f"Filtered to {len(highlights)} highlights with tags: {', '.join(tag_names)}")

        url = hs.get("next", None)
        if not url:
            break

        await asyncio.sleep(DEFAULT_SLEEP_BETWEEN_REQUESTS_IN_SECONDS)

    return highlights
