from pathlib import Path

from fastapi import APIRouter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from api.schemas.conversations import Conversation, Message
from api.services.conversation_service import conversation_service

router = APIRouter()

@router.get("/conversations", response_model=list[Conversation])
def list_conversations() -> list[Conversation]:
    """Endpoint to list all conversations."""
    return conversation_service.list_conversations() # type: ignore

@router.get("/conversations/{session_id}", response_model=list[Message])
def get_conversation(session_id: str) -> list[Message]:
    """Endpoint to retrieve a specific conversation by session ID."""
    return conversation_service.get_conversation(session_id=session_id) # type: ignore