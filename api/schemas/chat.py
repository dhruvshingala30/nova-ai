"""api/schemas/chat.py - Chat API Data Schemas.

Defines Pydantic request and response models for primary chat interactions
and session-level query payloads.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Payload sent by client to send a message to the agent."""
    message: str  # User's prompt/query
    session_id: str | None = None   # Optional existing session ID (generates new one if omitted)

class ChatResponse(BaseModel):
    """Synchronous response model returned after processing chat."""
    response: str  # Final reply from agent
    session_id: str  # Confirmed session ID