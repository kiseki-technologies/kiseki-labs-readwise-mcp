# Kiseki-Labs-Readwise-MCP

## Overview

`Kiseki-Labs-Readwise-MCP` is a Model Context Protocol (MCP) Server designed to interact with the Readwise API.

It allows language models to access and manipulate your Readwise documents and highlights programmatically. This server is developed by [Kiseki Labs](https://kisekilabs.com).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd readwise_mcp
    ```

2. **Initialise dependencies with uv**
    *(Assuming you have [uv](https://github.com/astral-sh/uv) installed)*
    ```bash
    uv sync
    ```

## Configuration

This server requires a Readwise API key to function.

1.  Obtain your API key from [Readwise](https://readwise.io/access_token).
2.  Create a `.env` file in the root directory of the project.
3.  Add your API key to the `.env` file:
    ```env
    READWISE_API_KEY=your_readwise_api_key_here
    ```
    The server uses `python-dotenv` to automatically load this variable when run.

## Available Tools

The server exposes the following tools for interaction:

*   `find_readwise_document_by_name(document_name: str) -> Book | None`: Finds a specific document in Readwise by its exact name.
*   `list_readwise_documents_by_filters(document_category: str = "", from_date: Optional[date] = None, to_date: Optional[date] = None) -> List[Book]`: Lists documents based on category (e.g., 'books', 'articles') and/or a date range. Requires at least one filter.
*   `get_readwise_highlights_by_document_ids(document_ids: List[int]) -> List[Highlight]`: Retrieves all highlights associated with a list of specific document IDs.
*   `get_readwise_highlights_by_filters(from_date: Optional[date] = None, to_date: Optional[date] = None, tag_names: List[str] = []) -> List[Highlight]`: Fetches highlights based on a date range and/or a list of tags. Requires at least one filter.

*(Note: `Book` and `Highlight` refer to the data structures defined in the `readwise_mcp.types` module.)*

## Running the Server

### Development Mode

To run the MCP server in dev mode, execute the following command from the project's root directory:

```bash
uv run mcp dev server.py
```

The dev server will start and become accessible online by default on http://127.0.0.1:6274/ if you haven't modified the host and port.


### Installing the MCP Server with Claude

On MacBook open the file below in your favourite text editor:
```
~/Library/Application\ Support/Claude/claude_desktop_config.json
```

For instance using vim open this file you can run the command:
```
vim ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Then add the appropriate entry under the `mcpServers` object, like in the example below:
```
"mcpServers": {
    "Kiseki-Labs-Readwise-MCP": {
      "command": "/Users/eddie/.pyenv/shims/uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "fastmcp",
        "run",
        "/Users/eddie/Development/AI/mcp_servers/readwise_mcp/server.py"
      ]
    }
    ...
```

Save the file with those changes.
Finally, restart Claude. After restart, the `Kiseki-Labs-Readwise-MCP` MCP Server should be available.