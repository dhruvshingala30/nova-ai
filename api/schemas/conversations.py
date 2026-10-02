"""api/schemas/conversations.py - Conversation and History Data Schemas.

Defines Pydantic models for structured chat history, conversation sessions,
and message persistence records.
"""

from pydantic import BaseModel


class Conversation(BaseModel):
    """Metadata representing a saved chat session."""
    session_id: str  # Unique conversation identifier
    title: str  # Display title (e.g. summary of first query)
    created_at: str  # ISO timestamp when session was created
    updated_at: str  # ISO timestamp when session was last modified


class Message(BaseModel):
    """A single chat message exchange in conversation history."""
    role: str  # 'user', 'assistant', or 'system'
    content: str  # The text content of the messa