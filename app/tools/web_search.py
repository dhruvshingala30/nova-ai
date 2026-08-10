"""
web_search.py - Real-Time Tavily Web Search Tool Integration.

Queries the web via the Tavily Search API to retrieve live news, facts,
sports schedules, and current events context for the LLM.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tavily import TavilyClient

load_dotenv()
class WebSearchInput(BaseModel):
    """Pydantic validation schema for search query strings."""

    query: str = Field(
        description="Concise search query optimized for real-time search engine retrieval (e.g., 'Nifty 50 today stock price' or 'The Hundred 2026 cricket schedule')."
    )


class WebSearch:
    """Tavily search engine API integration handler."""

    @staticmethod
    def search_web(query: str, max_results: int = 5) -> dict:
        """
        Executes a real-time web search query using the Tavily Client API.

        Args:
            query (str): Keyword query string.
            max_results (int): Maximum count of search result links to process.

        Returns:
            dict: Structured search status containing titles, URLs, and truncated snippet content.
        """
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "TAVILY_API_KEY environment variable is missing.",
            }

        try:
            client = TavilyClient(api_key=api_key)

            # Fetch search results optimized for LLM consumption
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
            )

            raw_results = response.get("results", [])
            if not raw_results:
                return {
                    "success": False,
                    "message": f"No search results found for query: '{query}'",
                }

            # Truncate content snippets to manage LLM context window efficiently
            formatted_results = [
                {
                    "title": r.get("title", "")[:80],
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:200],
                }
                for r in raw_results[:3]
            ]

            return {"success": True, "results": formatted_results}

        except Exception as e:  # noqa: BLE001
            return {
                "success": False,
                "error": f"Tavily search execution failed: {str(e)}",  # noqa: RUF010
            }
