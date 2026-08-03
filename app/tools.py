"""
tools.py - Central Tool Registry.

Registers all executable tools available to NovaAI, mapping their tool names
to execution functions, Pydantic input schemas, descriptions, and parameter types.
"""

from classes.code_interpreter import CodeInterpreter, CodeInterpreterInput
from classes.weather import Weather, WeatherInput
from classes.web_search import WebSearch, WebSearchInput

# Central registry mapping string identifiers to tool metadata and handler methods
AVAILABLE_TOOLS = {
    "get_weather": {
        "function": Weather.get_weather,
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
}
