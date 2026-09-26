from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.orchestrator import MultiAgentOrchestrator


class NovaService:
    def __init__(self, session_id: str | None = None, event_handler = None) -> None:
        if session_id:
            self.orchestrator = MultiAgentOrchestrator(session_id=session_id, event_handler=event_handler)
        else:
            self.orchestrator = MultiAgentOrchestrator(event_handler=event_handler)

    def chat(self, message: str) -> tuple[str, str]:
        """Handles a chat message by passing it to the orchestrator."""
        response = self.orchestrator.run(user_query=message)
        return response, self.orchestrator.session_id # type: ignore