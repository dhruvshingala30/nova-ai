"""
app/agents/specialists.py - Domain-Specific Specialist Agents for NovaAI.

Defines the concrete workers:
1. ResearchAgent - Live web search & real-time weather metrics.
2. DataAnalystAgent - Python computations, data science, chart generation.
3. DocVisionAgent - Local RAG document search, PDF schemas, and multimodal image inspection.
"""
from collections.abc import Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.agents.base_agent import BaseSpecialistAgent
from app.core.event import NovaEvent
from app.tools import AVAILABLE_TOOLS


class ResearchAgent(BaseSpecialistAgent):
    """
    Specialist agent for gathering real-time external world information,
    weather metrics, news, and live web lookups.
    """

    def __init__(
            self,
            event_handler: Callable[[NovaEvent], None] | None = None,
    ) -> None:
        # Scoped tools: Only web search and weather tools
        scoped_tools = {
            "search_web": AVAILABLE_TOOLS["search_web"],
            "get_weather": AVAILABLE_TOOLS["get_weather"],
        }
        instructions = """
            1. LIVE WEATHER:
                - Use `get_weather` for ANY query asking about current or live or today's weather, temperature, rain, or climate in a city or ZIP code.
                - MUST use `get_weather` EVEN IF the user explicitly commands you to search on web (e.g., 'Search Google', 'Search the web', or 'Use web search'.)
                - Correct typos in city names before executing.
                - Convert slang/abbreviations into full city names (e.g., 'ahmd' -> "Ahmedabad", 'blr' -> "Bangalore", 'nyc' -> "New York", 'jpr' -> "Jaipur").
                - If an abbreviation is ambiguous (e.g., 'sfo', 'nyc', 'ldn'), resolve it to the major global city (e.g., "San Francisco", "New York", "London").
                - If the city input is too vague or unknown, keep the original name and let the tool execute.
                - Fictional locations (e.g. Wakanda, Hogwarts, Asgard, Gotham): Let `get_weather` handle or inform the user.

            2. GENERAL LIVE WEB SEARCH:
                - Use `search_web` for real-time world events, breaking news, sports scores, live metrics, tech releases, and facts not present in the local knowledge base.

                - TEMPORAL INTENT RECOGNITION:
                    1. Check if the query is TIME-SENSITIVE (e.g., asks for 'today', 'latest', 'current', 'recent', 'who won yesterday', 'this week', or specific events).
                    2. If TIME-SENSITIVE:
                       - Formulate search queries anchored with the current year or month/year from your CURRENT SYSTEM DATE to avoid stale cached indexing.
                       - When calling `search_web`, supply the appropriate `time_range` argument ('day', 'week', or 'month') if fresh results are required.
                    3. If TIME-AGNOSTIC (e.g., historical events, general knowledge, conceptual explanations):
                       - Search using pure semantic keywords without forcing current date tokens or time filters.

                - RESULT EVALUATION & STALENESS FILTERING:
                    1. Compare timestamps in search snippets against your CURRENT SYSTEM DATE.
                    2. If a query asks for current/latest status, explicitly discard or flag results that are days or weeks behind when more recent updates are expected.
                    3. If sources conflict on dates or findings, state the discrepancy clearly rather than silently merging outdated data.
                    4. Synthesize facts into concise, well-structured summaries quoting the relevant dates/timestamps discovered.
        """

        super().__init__(
            name="ResearchAgent",
            role_description="Expert in gathering real-time web news, live information, world events, and weather metrics.",
            system_instructions=instructions,
            scoped_tools=scoped_tools,
            event_handler=event_handler,
        )


class DataAnalystAgent(BaseSpecialistAgent):
    """Specialist agent for data processing, math calculations, and visual plotting."""

    def __init__(
            self,
            event_handler: Callable[[NovaEvent], None] | None = None,
    ) -> None:
        scoped_tools = {
            "run_python_code": AVAILABLE_TOOLS["run_python_code"],
            "inspect_csv_schema": AVAILABLE_TOOLS["inspect_csv_schema"],
            "list_workspace_files": AVAILABLE_TOOLS["list_workspace_files"],
        }
        instructions = """
            1. CODE EXECUTION, DATA CREATION & MATH:
                - ALL Python code generation, custom DataFrame creation, dummy data simulation, computation, calculus, symbolic math, data generation, data analysis, custom algorithms and plotting MUST be written as Python code inside `run_python_code`.
                - CRITICAL: Your final summary MUST quote the exact numeric stdout output returned by `run_python_code`. NEVER calculate or estimate numbers in your head.
                - Always use standard numeric units (e.g. 5.4e12 for 5.4 trillion) to avoid scale errors.
                - If plotting charts, always save via `plt.savefig('filename.png')`.

            2. WORKSPACE FILE OPERATIONS & PATHS:
                - Use `list_workspace_files` ONLY when the user explicitly asks to view, check, or list what files are in the workspace.
                - Always pass ONLY bare filenames (e.g. 'users.csv', NEVER './workspace/users.csv' or 'nova_workspace/users.csv').
                - For CSV analysis: Invoke `inspect_csv_schema` first to check columns, then run analysis with `run_python_code`.
        """

        super().__init__(
            name="DataAnalystAgent",
            role_description="Expert in Python code generation, mathematics, computation, calculus, symbolic math, equations, data analysis, view/list directory contents and visualization.",
            system_instructions=instructions,
            scoped_tools=scoped_tools,
            event_handler=event_handler,
        )


class DocVisionAgent(BaseSpecialistAgent):
    """Specialist agent for local knowledge base retrieval (RAG) and PDF inspection."""

    def __init__(
        self, 
        event_handler: Callable[[NovaEvent], None] | None = None,
    ) -> None:
        scoped_tools = {
            "search_knowledge_base": AVAILABLE_TOOLS["search_knowledge_base"],
            "inspect_pdf_schema": AVAILABLE_TOOLS["inspect_pdf_schema"],
            "inspect_image": AVAILABLE_TOOLS["inspect_image"],
        }
        instructions = """
            1. KNOWLEDGE BASE & DOCUMENT QUESTIONS:
                - When asked about books, PDFs, documents, market concepts, author quotes, or literature facts, invoke `search_knowledge_base` directly.
                - NEVER attempt to answer questions about indexed literature from memory without searching first.
                - NEVER use `inspect_pdf_schema` to search for answers in a book or document; `inspect_pdf_schema` is ONLY for viewing page count/metadata.

            2. IMAGES, CHARTS & VISUAL UNDERSTANDING:
                - When asked to view, explain, describe, or analyze a saved chart, image, plot, or screenshot in the workspace, invoke `inspect_image`.
                - Pass the bare image filename (e.g., "gdp_vs_happiness.png") and a descriptive prompt explaining what to look for.
        """

        super().__init__(
            name="DocVisionAgent",
            role_description="Expert in querying local documents (RAG), inspecting PDFs, and visual understanding.",
            system_instructions=instructions,
            scoped_tools=scoped_tools,
            event_handler=event_handler,
        )
