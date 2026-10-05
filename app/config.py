"""
app/config.py - Global Application & Runtime Configurations.

Centralized configuration file storing environment variables, timeouts,
UI icons, and chat memory limits for the NovaAI Agent.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Mode switch
USE_CLOUD_LLM = os.getenv(key="USE_CLOUD_LLM", default="false").lower() == "true"

# -------------------------------
# Cloud inference (Groq / OpenRouter)
# -------------------------------
GROQ_API_KEY = os.getenv(key="GROQ_API_KEY", default="")
CLOUD_MODEL_NAME = os.getenv(key="CLOUD_MODEL_NAME", default="llama-3.3-70b-versatile")
CLOUD_BASE_URL = os.getenv(key="CLOUD_BASE_URL", default="https://api.groq.com/openai/v1")
CLOUD_VISION_MODEL = os.getenv(key="CLOUD_VISION_MODEL", default="llama-3.2-11b-vision-preview")

# -------------------------------
# Local Ollama fallback
# -------------------------------
OLLAMA_HOST = os.getenv(key="OLLAMA_HOST", default="http://localhost:11434")
MODEL_NAME = os.getenv(key="MODEL_NAME", default="qwen2.5:7b-instruct-q8_0")
VISION_MODEL_NAME = os.getenv(key="VISION_MODEL_NAME", default="llava")

# Sandbox
E2B_API_KEY = os.getenv(key="E2B_API_KEY", default="")

# Workspace & Database
WORKSPACE_DIR = Path(os.getenv(key="WORKSPACE_DIR", default=str(PROJECT_ROOT / "nova_workspace")))
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = Path(os.getenv(key="DATABASE_PATH", default=str(PROJECT_ROOT / "data" / "nova.db")))
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# -------------------------------
# Agent Chat Memory Configuration
# -------------------------------
# Maximum number of past conversation messages retained in active LLM context
MAX_HISTORY = int(os.getenv(key="MAX_HISTORY", default="20"))

# Request timeout limit (in seconds) for external HTTP requests
TIME_OUT = 10

# -------------------------------
# Agent Chat Memory Configuration
# -------------------------------
MAX_RETRIES = 3

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
    "PLAN": "📋",
    "REFLECT": "🔄",
    "EXPLANATION": "📦",
    "TOOL": "🛠️",
    "RESULT": "✅",
    "ANSWER": "🤖",
}
