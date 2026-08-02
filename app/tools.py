from classes.code_interpreter import CodeInterpreter
from classes.weather import Weather

AVAILABLE_TOOLS = {
    "get_weather": {
        "function": Weather.get_weather,
        "description": "Returns the current weather of cities provided by the user.",
        "parameters": {"cities": "list[str]"},
    },
    "run_python_code": {
        "function": CodeInterpreter.run_python_code,
        "description": "Executes Python code to perform complex math, symbolic equations, data processing, or custom calculations.",
        "parameters": {"code": "str"},
    },
}