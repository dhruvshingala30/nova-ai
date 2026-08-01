from typing import Literal

"""
Application Configuration
"""

# -------------------------------
# LLM Configuration
# -------------------------------

MODEL_NAME = "qwen2.5:7b"


# -------------------------------
# Chat Configuration
# -------------------------------

MAX_HISTORY = 20

# -------------------------------
# Application Configuration
# -------------------------------

EXIT_COMMANDS = {"exit", "quit", "bye"}

SEPARATOR = "=" * 100

END_TEXT = "👋👋👋👋👋👋 BYE !!! 👋👋👋👋👋👋"

STEP_ICONS = {
    "START": "🔥",
    "EXPLANATION": "🧠",
    "TOOL": "🛠️",
    "ANSWER": "🤖",
}

Operation = Literal[
    "addition",
    "subtraction",
    "multiplication",
    "division",
    "modulus",
    "power",
    "absolute",
    "average",
    "minimum",
    "maximum",
    "round",
    "floor",
    "ceil",
]

VALID = {
    "addition",
    "subtraction",
    "multiplication",
    "division",
    "modulus",
    "power",
    "absolute",
    "average",
    "minimum",
    "maximum",
    "round",
    "floor",
    "ceil",
}

ALIASES = {
    "add": "addition",
    "plus": "addition",
    "sum": "addition",
    "subtract": "subtraction",
    "minus": "subtraction",
    "multiply": "multiplication",
    "times": "multiplication",
    "divide": "division",
    "div": "division",
    "avg": "average",
    "mean": "average",
    "min": "minimum",
    "max": "maximum",
}