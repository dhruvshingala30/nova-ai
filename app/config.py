import os

"""
Application Configuration
"""

# -------------------------------
# LLM Configuration
# -------------------------------

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")

# -------------------------------
# Chat Configuration
# -------------------------------

MAX_HISTORY = 20
TIME_OUT = 10

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