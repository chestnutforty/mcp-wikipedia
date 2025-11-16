from typing import Annotated
from mcp.server.fastmcp import FastMCP
from wikipedia.search import Wikipedia
from datetime import datetime

mcp = FastMCP(
    name="wikipedia",
    instructions=r"""
Use this tool to search Wikipedia articles as they existed at a specific point in time.
This is useful for historical research, fact-checking, and getting information from a specific date.
The tool retrieves article content from Wikipedia's revision history before the specified end_date.
    """.strip(),
)


@mcp.tool(
    name="search_wikipedia",
    title="Search Wikipedia with time travel",
    description="""
Search Wikipedia and retrieve articles as they existed before a specific date.
Useful for historical timelines, biographical data, scientific concepts, reference statistics, and base rates.
    """,
    exclude_args=["cutoff_date"]
)
async def search_wikipedia(
    query: Annotated[str, "Search query string"],
    cutoff_date: Annotated[str, "ISO format date (YYYY-MM-DD) - retrieve articles as they existed before this date"] = datetime.now().strftime("%Y-%m-%d"),
    lang: Annotated[str, "Two letter language code"] = 'en',
    # limit: Annotated[int, "Maximum number of articles to retrieve"] = 1
) -> str:
    """
    Search Wikipedia articles as they existed at a specific point in time.

    Args:
        query: Search query string
        cutoff_date: ISO format date (YYYY-MM-DD) - retrieve articles as they existed before this date
        lang: Language code (default: 'en')
        limit: Maximum number of articles to retrieve (default: 2)

    Returns:
        Formatted string with article titles and content
    """
    try:
        # Parse end_date to datetime
        end_date_dt = datetime.fromisoformat(cutoff_date)

        # Initialize Wikipedia search
        wiki = Wikipedia(lang=lang, limit=1)

        # Perform search
        results = await wiki.search(query, end_date_dt)

        if not results:
            return f"No Wikipedia articles found for query: {query}"

        # Format results
        formatted_results = []
        for article in results:
            title = article['title']
            content = article['content']
            timestamp = article['timestamp']

            # Truncate very long articles
            if len(content) > 50000:
                content = content[:50000] + "\n\n[Article truncated due to length...]"

            formatted_results.append(
                f"=== {title} ===\n"
                f"Last revision before {cutoff_date}: {timestamp}\n\n"
                f"{content}\n"
            )

        return "\n\n".join(formatted_results)

    except ValueError as e:
        return f"Error parsing date '{cutoff_date}'. Please use ISO format (YYYY-MM-DD): {str(e)}"
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"
