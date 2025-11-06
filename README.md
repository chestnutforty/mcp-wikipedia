# MCP Wikipedia Server

An MCP (Model Context Protocol) server that provides Wikipedia search with time-travel capability. This tool allows you to search Wikipedia articles and retrieve their content as it existed at a specific point in time.

## Features

- **Time-travel search**: Retrieve Wikipedia articles as they existed before a specific date
- **Multi-language support**: Search Wikipedia in any language (default: English)
- **Async implementation**: Built on async/await for efficient performance
- **Historical accuracy**: Uses Wikipedia's revision history API

## Installation

```bash
cd mcp-wikipedia
uv pip install -e .
```

## Usage

### Running the Server

```bash
python wikipedia_server.py
```

The server will start on port **8003**.

### Environment Variables

- `WIKIPEDIA_ACCESS_TOKEN` (optional): Personal access token for higher rate limits

### API

#### `search_wikipedia`

Search Wikipedia articles as they existed at a specific point in time.

**Parameters:**
- `query` (string, required): Search query
- `end_date` (string, required): ISO format date (YYYY-MM-DD) - retrieve articles as they existed before this date
- `lang` (string, optional): Language code (default: 'en')
- `limit` (integer, optional): Maximum number of articles to retrieve (default: 2)

**Returns:** Formatted string with article titles and content

**Example:**
```python
# Search for articles about "Python programming" as they existed on January 1, 2023
result = await search_wikipedia(
    query="Python programming",
    end_date="2023-01-01",
    lang="en",
    limit=2
)
```

## Use Cases

- Historical research and fact-checking
- Training data for language models (with temporal constraints)
- Base rate and reference statistics from a specific time period
- Biographical data and timelines
- Scientific concepts and their evolution

## Architecture

- **FastMCP**: Uses the FastMCP framework for MCP protocol implementation
- **Wikipedia API**: Queries Wikipedia's MediaWiki API with revision history support
- **Async HTTP**: Uses `httpx` for async HTTP requests
- **Wikitext parsing**: Uses `wikitextparser` to clean Wikipedia markup

## Dependencies

- mcp
- fastapi>=0.116.1
- uvicorn>=0.35.0
- httpx
- wikitextparser>=0.56.4
- pandas

## License

See the main gpt-oss repository for license information.
