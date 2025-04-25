# Third Party
import pytest

# Internal Libraries
from readwise_mcp.tools.readwise.get_document import get_documents_by_names
from readwise_mcp.types.book import Book


@pytest.mark.asyncio
async def test_get_single_existing_document(readwise_api_key):
    """Test retrieving a single known document by name."""
    doc_name = "GPT 4.1 Prompting Guide | OpenAI Cookbook"
    results = await get_documents_by_names(readwise_api_key, [doc_name])

    assert len(results) == 1
    assert doc_name in results
    book = results[doc_name]
    assert isinstance(book, Book)
    assert book.title == doc_name
    assert book.category == "articles"  # Example assertion, adjust if needed


@pytest.mark.asyncio
async def test_get_multiple_existing_documents(readwise_api_key):
    """Test retrieving multiple known documents by names."""
    doc_names = ["GPT 4.1 Prompting Guide | OpenAI Cookbook", "Questions About the Future of AI"]
    results = await get_documents_by_names(readwise_api_key, doc_names)

    assert len(results) == 2
    for name in doc_names:
        assert name in results
        book = results[name]
        assert isinstance(book, Book)
        assert book.title == name


@pytest.mark.asyncio
async def test_get_mixed_existing_and_non_existing(readwise_api_key):
    """Test retrieving a mix of existing and non-existing documents."""
    doc_names = ["GPT 4.1 Prompting Guide | OpenAI Cookbook", "This Also Does Not Exist 67890"]
    results = await get_documents_by_names(readwise_api_key, doc_names)

    assert len(results) == 2

    # Check existing document
    existing_name = "GPT 4.1 Prompting Guide | OpenAI Cookbook"
    assert existing_name in results
    book = results[existing_name]
    assert isinstance(book, Book)
    assert book.title == existing_name

    # Check non-existing document
    non_existing_name = "This Also Does Not Exist 67890"
    assert non_existing_name in results
    assert results[non_existing_name] is None
