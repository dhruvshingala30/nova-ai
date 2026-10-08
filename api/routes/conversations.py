"""api/routers/conversations.py - Conversation History Route Handlers.

Exposes endpoints for querying historical sessions and retrieving past
message logs from persistent memory.
"""

from pathlib import Path

from fastapi import APIRouter, Header

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from api.schemas.conversations import Conversation, Message
from api.services.conversation_service import conversation_service

# Create isolated router instance
router = APIRouter()

# ---------------------------------------------------------------------------
# GET /conversations - List All Saved Chat Sessions
# ---------------------------------------------------------------------------
@router.get("/conversations", response_model=list[Conversation])
def list_conversations(x_user_id: str | None = Header(default=None)) -> list[Conversation]:
    """Endpoint to list all conversations from persistent storage for sidebar display."""
    return conversation_service.list_conversations(x_user_id=x_user_id) # type: ignore

# ---------------------------------------------------------------------------
# GET /conversations/{session_id} - Fetch Messages for Specific Session
# ---------------------------------------------------------------------------
@router.get("/conversations/{session_id}", response_model=list[Message])
def get_conversation(session_id: str) -> list[Message]:
    """Endpoint to retrieve the full chat message history for a given session ID."""
    return conversation_service.get_conversation(session_id=session_id) # type: ignore