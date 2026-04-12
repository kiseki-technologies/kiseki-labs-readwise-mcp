# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kiseki-Labs-Readwise-MCP is a Model Context Protocol (MCP) server for the Readwise API, built with FastMCP. It exposes async tools that let language models search documents, list documents by filters, and retrieve highlights from a user's Readwise library. Requires a `READWISE_API_KEY` in `.env`.

## Commands

```bash
uv sync                              # Install dependencies
uv run mcp dev server.py             # Run dev server (http://127.0.0.1:6274/)
make test                            # Run all tests (or: uv run pytest)
uv run pytest tests/path/test_x.py   # Run a single test file
uv run pytest tests/path/test_x.py::test_func  # Run a single test function
make fmt                             # Format code (black + isort, 120 char line length)
make lint                            # Lint (pylint)
make lint-ci                         # Lint with fail-under threshold (6.0)
```

## Architecture

**server.py** is the entry point. It initializes a `FastMCP` instance and registers 4 tools + 1 resource via decorators. The API key is loaded from `.env` at module level and passed explicitly into tool functions.

**readwise_mcp/tools/readwise/** — API integration layer:
- `common.py`: shared HTTP client (`get_data`) with retry logic, 429 rate-limit handling, and `Retry-After` header support. Uses `httpx.AsyncClient`.
- `get_document.py`: document search by name(s) and filtered listing by category/date range.
- `get_highlights.py`: highlight retrieval by document IDs (concurrent via `asyncio.gather`) or by date/tag filters.

**readwise_mcp/types/** — Pydantic models: `Book` (with `BookCategory` enum: books, articles, tweets, podcasts, supplementals), `Highlight`, `Tag`.

**readwise_mcp/utils/duration.py** — Parses duration expressions ("1w", "2d", "3h", "30m") into `(from_date, to_date)` tuples. Used by tools to convert shorthand into date range filters.

## Testing Conventions

- pytest only, no TestClasses — each test is a standalone function
- Tests mirror the source tree under `tests/`
- Tests are **integration tests** that hit the real Readwise API — they require `READWISE_API_KEY` in `.env` and auto-skip if it's not set
- `pytest-asyncio` for async test support
- `conftest.py` provides a session-scoped `readwise_api_key` fixture

## Code Style

- black (120 char lines, py310 target) + isort (black-compatible profile)
- isort sections: STDLIB, THIRDPARTY, FIRSTPARTY (`readwise_mcp`)
- Import headers: `# Standard Library`, `# Third Party`, `# Internal Libraries`

## Known Limitations

- **No mocked unit tests** — all tests require a live API key, making CI dependent on external service availability
- **README is slightly stale** — documents `find_readwise_document_by_name` (singular) but the actual tool is `find_readwise_documents_by_names` (plural, accepts a list); `duration_expression` parameter is also missing from README signatures
- **`get_greeting` resource** in server.py is a leftover FastMCP example, not a real feature
- **Global API key** — loaded once at module level in server.py; no runtime refresh or validation
- **Pylint threshold** is set to 6.0 (low) in CI
