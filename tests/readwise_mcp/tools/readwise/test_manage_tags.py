# Third Party
import pytest
import pytest_asyncio

# Internal Libraries
from readwise_mcp.tools.readwise.get_highlights import get_highlight_by_document_id
from readwise_mcp.tools.readwise.manage_tags import add_tag, delete_tag, get_tags, update_tag
from readwise_mcp.types.tag import Tag

# Known document ID used in other integration tests
TEST_BOOK_ID = 50788861


@pytest_asyncio.fixture()
async def highlight_id(readwise_api_key):
    """Fetch a real highlight ID from the test book."""
    highlights = await get_highlight_by_document_id(readwise_api_key, TEST_BOOK_ID)
    assert highlights, f"No highlights found for book {TEST_BOOK_ID}"
    return highlights[0].id


# --- Book tag tests ---


@pytest.mark.asyncio
async def test_get_tags_for_book(readwise_api_key):
    """Test listing tags on a book."""
    tags = await get_tags(readwise_api_key, "books", TEST_BOOK_ID)
    assert isinstance(tags, list)
    for tag in tags:
        assert isinstance(tag, Tag)


@pytest.mark.asyncio
async def test_add_and_delete_tag_on_book(readwise_api_key):
    """Test adding a tag to a book and then removing it."""
    tag_name = "mcp-integration-test"

    created_tag = await add_tag(readwise_api_key, "books", TEST_BOOK_ID, tag_name)
    try:
        assert isinstance(created_tag, Tag)
        assert created_tag.name == tag_name

        tags = await get_tags(readwise_api_key, "books", TEST_BOOK_ID)
        tag_ids = [t.id for t in tags]
        assert created_tag.id in tag_ids
    finally:
        await delete_tag(readwise_api_key, "books", TEST_BOOK_ID, created_tag.id)

    tags_after = await get_tags(readwise_api_key, "books", TEST_BOOK_ID)
    tag_ids_after = [t.id for t in tags_after]
    assert created_tag.id not in tag_ids_after


@pytest.mark.asyncio
async def test_update_tag_on_book(readwise_api_key):
    """Test renaming a tag on a book."""
    original_name = "mcp-rename-test"
    new_name = "mcp-renamed-test"

    created_tag = await add_tag(readwise_api_key, "books", TEST_BOOK_ID, original_name)
    try:
        updated_tag = await update_tag(readwise_api_key, "books", TEST_BOOK_ID, created_tag.id, new_name)
        assert isinstance(updated_tag, Tag)
        assert updated_tag.name == new_name
        assert updated_tag.id == created_tag.id
    finally:
        await delete_tag(readwise_api_key, "books", TEST_BOOK_ID, created_tag.id)


# --- Highlight tag tests ---


@pytest.mark.asyncio
async def test_get_tags_for_highlight(readwise_api_key, highlight_id):
    """Test listing tags on a highlight."""
    tags = await get_tags(readwise_api_key, "highlights", highlight_id)
    assert isinstance(tags, list)
    for tag in tags:
        assert isinstance(tag, Tag)


@pytest.mark.asyncio
async def test_add_and_delete_tag_on_highlight(readwise_api_key, highlight_id):
    """Test adding a tag to a highlight and then removing it."""
    tag_name = "mcp-highlight-test"

    created_tag = await add_tag(readwise_api_key, "highlights", highlight_id, tag_name)
    try:
        assert isinstance(created_tag, Tag)
        assert created_tag.name == tag_name

        tags = await get_tags(readwise_api_key, "highlights", highlight_id)
        tag_ids = [t.id for t in tags]
        assert created_tag.id in tag_ids
    finally:
        await delete_tag(readwise_api_key, "highlights", highlight_id, created_tag.id)

    tags_after = await get_tags(readwise_api_key, "highlights", highlight_id)
    tag_ids_after = [t.id for t in tags_after]
    assert created_tag.id not in tag_ids_after
