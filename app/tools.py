from classes.calculator import Calculator
from classes.weather import Weather

AVAILABLE_TOOLS = {
    "get_weather": {
        "function": Weather.get_weather,
        "description": "Returns the current weather of cities provided by the user.",
        "parameters": {"cities": "list[str]"},
    },
    "basic_calculator": {
        "function": Calculator.basic_calculator,
        "description": "Performs basic arithmetic operations.",
        "parameters": {
            "operation": "Literal",
            "numbers": "list[float]",
            "decimals": "int | None",
        },
    },
}