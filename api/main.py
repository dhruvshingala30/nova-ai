from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from api.routes.chat import router as chat_router
from api.routes.conversations import router as conversations_router

app = FastAPI(
    title="Nova AI API",
    description="API backend for NovaAI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "NovaAI is up and running"
    }

app.include_router(
    router=chat_router,
    prefix="/api",
)

app.include_router(
    router=conversations_router,
    prefix="/api",
)