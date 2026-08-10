"""
tools.py - Central Tool Registry.

Registers all executable tools available to NovaAI, mapping their tool names
to execution functions, Pydantic input schemas, descriptions, and parameter types.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.code_interpreter import CodeInterpreter, CodeInterpreterInput
from app.tools.weather import Weather, WeatherInput
from app.tools.web_search import WebSearch, WebSearchInput
from app.tools.workspace_tools import (
    InspectCSVInput,
    ListFilesInput,
    inspect_csv_schema,
    list_workspace_files,
)

# Central registry mapping string identifiers to tool metadata and handler methods
AVAILABLE_TOOLS = {
    "get_weather": {
        "function": Weather().get_weather,
        "schema": WeatherInput,
        "description": "Returns the current weather of cities provided by the user.",
        "parameters": {"cities": "list[str]"},
    },
    "run_python_code": {
        "function": CodeInterpreter.run_python_code,
        "schema": CodeInterpreterInput,
        "description": "Executes Python code to perform complex math, symbolic equations, data processing, or custom calculations.",
        "parameters": {"code": "str"},
    },
    "search_web": {
        "function": WebSearch.search_web,
        "schema": WebSearchInput,
        "description": "Searches the web for up-to-date information, current events, and live facts.",
        "parameters": {"query": "str"},
    },
    "list_workspace_files": {
        "function": list_workspace_files,
        "schema": ListFilesInput,
        "description": "Lists files, sizes, and relative paths in the workspace.",
        "parameters": {
            "subfolder": "str (optional)", 
            "pattern": "str (optional)",
        },
    },
    "inspect_csv_schema": {
        "function": inspect_csv_schema,
        "schema": InspectCSVInput,
        "description": "Inspects a CSV file's structure, column types, shape, and sample data without loading the whole file into LLM memory.",
        "parameters": {
            "file_path": "str", 
            "sample_rows": "int (optional)",
        },
    },
}

__all__ = ["AVAILABLE_TOOLS"]