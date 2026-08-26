"""
specialists.py - Domain-Specific Specialist Agents for NovaAI.

Defines the concrete workers:
1. ResearchAgent - Live web search & real-time weather metrics.
2. DataAnalystAgent - Python computations, data science, chart generation.
3. DocVisionAgent - Local RAG document search, PDF schemas, and multimodal image inspection.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.agents.base_agent import BaseSpecialistAgent
from app.tools import AVAILABLE_TOOLS


class ResearchAgent(BaseSpecialistAgent):
    """
    Specialist agent for gathering real-time external world information,
    weather metrics, news, and live web lookups.
    """

    def __init__(self) -> None:
        # Scoped tools: Only web search and weather tools[cite: 1]
        scoped_tools = {
            "search_web": AVAILABLE_TOOLS["search_web"],
            "get_weather": AVAILABLE_TOOLS["get_weather"],
        }
        instructions = (
            "- Use `search_web` for recent news, live facts, and online inquiries.\n"
            "- Use `get_weather` for city weather and temperature reports.\n"
            "- Extract key factual metrics and present clear, concise bullet-point summaries."
        )
        super().__init__(
            name="ResearchAgent",
            role_description="Expert in gathering real-time web news, live information, and city weather data.",
            system_instructions=instructions,
            scoped_tools=scoped_tools,
        )


class DataAnalystAgent(BaseSpecialistAgent):
    """Specialist agent for data processing, math calculations, and visual plotting."""

    def __init__(self) -> None:
        scoped_tools = {
            "run_python_code": AVAILABLE_TOOLS["run_python_code"],
            "inspect_csv_schema": AVAILABLE_TOOLS["inspect_csv_schema"],
            "list_workspace_files": AVAILABLE_TOOLS["list_workspace_files"],
        }
        instructions = (
            "- MANDATORY: For ANY arithmetic, summation, percentage, or data calculation, "
            "you MUST write and execute Python code using `run_python_code`.\n"
            "- CRITICAL: Your final summary MUST quote the exact numeric stdout output returned "
            "by `run_python_code`. NEVER calculate or estimate numbers in your head.\n"
            "- Always use standard numeric units (e.g. 5.4e12 for 5.4 trillion) to avoid scale errors.\n"
            "- If plotting charts, always save via `plt.savefig('filename.png')`."
        )
        super().__init__(
            name="DataAnalystAgent",
            role_description="Expert in Python computation, mathematics, data analysis, and visualization.",
            system_instructions=instructions,
            scoped_tools=scoped_tools,
        )


class DocVisionAgent(BaseSpecialistAgent):
    """Specialist agent for local knowledge base retrieval (RAG) and PDF inspection."""

    def __init__(self) -> None:
        scoped_tools = {
            "search_knowledge_base": AVAILABLE_TOOLS["search_knowledge_base"],
            "inspect_pdf_schema": AVAILABLE_TOOLS["inspect_pdf_schema"],
            "inspect_image": AVAILABLE_TOOLS["inspect_image"],
        }
        instructions = (
            "- When searching for specific statistics, percentages, or quotes, formulate targeted queries "
            "(e.g., 'trader failure rate percentage 95 percent lose money') and set `n_results=5`.\n"
            "- Quote literature text directly from the retrieved context chunks.\n"
            "- Use `inspect_image` when analyzing visual charts or workspace images."
        )
        super().__init__(
            name="DocVisionAgent",
            role_description="Expert in querying local documents (RAG), inspecting PDFs, and visual understanding.",
            system_instructions=instructions,
            scoped_tools=scoped_tools,
        )
