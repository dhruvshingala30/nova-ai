"""
app/tools/__init__.py - Central Tool Registry.

Registers all executable tools available to NovaAI, mapping their tool names
to execution functions, Pydantic input schemas, descriptions, and parameter types.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models import (
    CodeInterpreterInput,
    InspectCSVInput,
    InspectImageInput,
    InspectPDFInput,
    ListFilesInput,
    SearchKnowledgeBaseInput,
    WeatherInput,
    WebSearchInput,
)
from app.tools.code_interpreter import CodeInterpreter
from app.tools.knowledge_base_search import search_knowledge_base
from app.tools.weather import Weather
from app.tools.web_search import WebSearch
from app.tools.workspace_tools import (
    inspect_csv_schema,
    inspect_image,
    inspect_pdf_schema,
    list_workspace_files,
)

# Central registry mapping string identifiers to tool metadata and handler methods
AVAILABLE_TOOLS = {
    "get_weather": {
        "function": Weather().get_weather,
        "schema": WeatherInput,
        "description": "Fetches live weather and temperatures. MANDATORY for all city weather inquiries.",
        "parameters": {"cities": "list[str]"},
    },
    "run_python_code": {
        "function": CodeInterpreter.run_python_code,
        "schema": CodeInterpreterInput,
        "description": "Executes Python code in a secure sandbox. MANDATORY for math, data analysis on CSVs, or plotting.",
        "parameters": {"code": "str"},
    },
    "search_web": {
        "function": WebSearch.search_web,
        "schema": WebSearchInput,
        "description": "Performs a live web search for external world events, live facts, news, and current metrics.",
        "parameters": {
            "query": "str (The search term)",
            "time_range": "str (optional) ('day', 'week', 'month', or null)",
        },
    },
    "list_workspace_files": {
        "function": list_workspace_files,
        "schema": ListFilesInput,
        "description": "Lists active files and datasets attached to the current chat session. Use ONLY when the user asks to see uploaded files.",
        "parameters": {
            "subfolder": "str (optional)",
            "pattern": "str (optional)",
        },
    },
    "inspect_csv_schema": {
        "function": inspect_csv_schema,
        "schema": InspectCSVInput,
        "description": "Inspects columns, data types, and sample rows of a session CSV/TSV before running Python code on it.",
        "parameters": {
            "file_path": "str",
            "sample_rows": "int (optional, default=5)",
        },
    },
    "inspect_pdf_schema": {
        "function": inspect_pdf_schema,
        "schema": InspectPDFInput,
        "description": "Inspects PDF structural metadata (page count, author, sample preview). DO NOT use to read or answer questions from a document.",
        "parameters": {
            "file_path": "str",
            "max_pages_to_sample": "int (optional, default=2)",
        },
    },
    "search_knowledge_base": {
        "function": search_knowledge_base,
        "schema": SearchKnowledgeBaseInput,
        "description": (
            "Performs semantic & keyword retrieval over all indexed PDFs, books, and documents. "
            "MANDATORY for answering ANY questions about concepts, facts, quotes, chapters, "
            "or topics contained within the user's indexed documents."
        ),
        "parameters": {
            "query": "str",
            "n_results": "int (optional, default=3)",
        },
    },
    "inspect_image": {
        "function": inspect_image,
        "schema": InspectImageInput,
        "description": (
            "Analyzes, describes, and extracts visual information from in-memory charts or images (.png, .jpg, .webp). "
            "MANDATORY whenever the user asks to inspect or verify a generated plot or uploaded image."
        ),
        "parameters": {
            "file_path": "str",
            "prompt": "str (optional)",
        },
    },
}

__all__ = ["AVAILABLE_TOOLS"]