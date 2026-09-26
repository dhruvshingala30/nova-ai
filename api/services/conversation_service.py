from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.core.memory import SQLiteMemory


class ConversationService:
    def __init__(self):
        self.memory = SQLiteMemory()

    def list_conversations(self) -> list[dict[str, str]]:
        """Retrieves all conversations from memory."""
        sessions = self.memory.list_sessions()
        return [
            {
                "session_id": session_id
            }
            for session_id in sessions
        ]

    def get_conversation(self, session_id: str) -> list[dict[str, str]]:
        """Retrieves a specific conversation by session ID."""
        return self.memory.get_session_history(session_id=session_id)


conversation_service = ConversationService()