"""
config.py - Global Application & Runtime Configurations.

Centralized configuration file storing environment variables, timeouts,
UI icons, and chat memory limits for the NovaAI Agent.
"""

import os

# -------------------------------
# LLM & Host Configuration
# -------------------------------
# Host address for the local Ollama instance
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Local LLM model identifier used for agent reasoning
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")

# -------------------------------
# Agent Chat Memory Configuration
# -------------------------------
# Maximum number of past conversation messages retained in active LLM context
MAX_HISTORY = 20

# Request timeout limit (in seconds) for external HTTP requests
TIME_OUT = 10

# -------------------------------
# Application UI & Output Formatting
# -------------------------------
# Welcome message displayed upon entry
WELCOME_TEXT = "🤖 Welcome to NovaAI"

# Commands that trigger application shutdown
EXIT_COMMANDS = {"exit", "quit", "bye"}

# Divider line string for visual separation in terminal logs
SEPARATOR = "=" * 100

# Goodbye message displayed upon exit
END_TEXT = "\n  🤖 BYE !!!👋👋  \n"

# Emojis/Icons mapped to each step in the ReAct execution protocol
STEP_ICONS = {
    "START": "🔥",
    "EXPLANATION": "🧠",
    "TOOL": "🛠️",
    "ANSWER": "🤖",
}
