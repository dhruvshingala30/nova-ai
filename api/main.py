"""api/main.py - FastAPI Application Entry Point.

Initializes the core FastAPI app, configures global CORS middleware,
registers domain routers, and sets up health check endpoints.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from api.routes.chat import router as chat_router
from api.routes.conversations import router as conversations_router

# Initialize the main FastAPI application instance
app = FastAPI(
    title="Nova AI API",
    description="API backend for NovaAI",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Middleware Configuration
# ---------------------------------------------------------------------------
# Allow frontend clients running on localhost:3000 (e.g. Next.js / React)
# to make cross-origin requests to this server without getting blocked by the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP verbs (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ---------------------------------------------------------------------------
# Base Health Check Route
# ---------------------------------------------------------------------------
@app.get("/")
def root() -> dict[str, str]:
    """Simple health-check endpoint to verify the server is running."""
    return {
        "message": "NovaAI is up and running"
    }

# ---------------------------------------------------------------------------
# Router Registration
# ---------------------------------------------------------------------------
# Mount both chat and conversation routes under the shared '/api' prefix
# Example: /chat becomes /api/chat, /conversations becomes /api/conversations
app.include_router(
    router=chat_router,
    prefix="/api",
)

app.include_router(
    router=conversations_router,
    prefix="/api",
)