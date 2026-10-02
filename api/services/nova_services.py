"""api/services/nova_services.py - Nova AI Orchestrator Service Layer.

Provides an application-level wrapper around the MultiAgentOrchestrator,
handling background task delegation and event collector injection.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.orchestrator import MultiAgentOrchestrator


class NovaService:
    """Wrapper around MultiAgentOrchestrator for managing individual chat sessions."""

    def __init__(self, session_id: str | None = None, event_handler = None) -> None:
        """Initializes orchestrator with an optional session ID and event collector."""
        if session_id:
            self.orchestrator = MultiAgentOrchestrator(session_id=session_id, event_handler=event_handler)
        else:
            self.orchestrator = MultiAgentOrchestrator(event_handler=event_handler)

    def chat(self, message: str) -> tuple[str, str]:
        """Executes the orchestrator pipeline for a prompt and returns (response, session_id)."""
        response = self.orchestrator.run(user_query=message)
        return response, self.orchestrator.session_id # type: ignore