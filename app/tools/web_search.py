"""
app/tools/web_search.py - Real-Time Tavily Web Search Tool Integration.

Queries the web via the Tavily Search API to retrieve live news, facts,
sports schedules, and current events context for the LLM.
"""

import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

class WebSearch:
    """Tavily search engine API integration handler."""

    @staticmethod
    def search_web(query: str, time_range: str | None = None) -> dict:
        """
        Performs a live web search using Tavily with optional temporal filtering.

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

        client = TavilyClient(api_key=api_key)

        kwargs = {
            "query": query,
            "max_results": 5,
            "search_depth": "advanced",
        }
        if time_range:
            kwargs["time_range"] = time_range

        try:
            # Fetch search results optimized for LLM consumption
            response = client.search(**kwargs)

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
                    "published": r.get("published_date", ""),
                    "snippet": r.get("content", "")[:200],
                }
                for r in raw_results
            ]

            return {"success": True, "results": formatted_results}

        except Exception as e:  # noqa: BLE001
            return {
                "success": False,
                "error": f"Tavily search execution failed: {str(e)}",  # noqa: RUF010
            }
