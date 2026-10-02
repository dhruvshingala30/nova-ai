"""api/services/conversation_service.py - Conversation Memory Service Layer.

Provides a service boundary over persistent SQLite storage for managing
and querying saved chat sessions and audit trails.
"""

from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.core.memory import SQLiteMemory


class ConversationService:
    """Service layer for fetching conversation session records and message logs."""

    def __init__(self):
        # Establish connection/interface to SQLite storage
        self.memory = SQLiteMemory()

    def list_conversations(self) -> list[dict[str, Any]]:
        """Retrieves all conversation metadata records from database memory."""
        return self.memory.list_sessions()

    def get_conversation(self, session_id: str) -> list[dict[str, str]]:
        """Retrieves full message turn history (user & assistant) for a session ID."""
        return self.memory.get_session_history(session_id=session_id)

# Global singleton instance used by API route handlers
conversation_service = ConversationService()