# api/core/hitl_manager.py
import threading


class HITLManager:
    """Manages thread-safe approval handshakes between BaseAgent and FastAPI."""

    def __init__(self):
        # Maps session_id to (threading.Event, dict_containing_decision)
        self._pending: dict[str, tuple[threading.Event, dict]] = {}

    def wait_for_decision(self, session_id: str, timeout: float = 300.0) -> bool:
        """Called by BaseSpecialistAgent thread to block until UI responds."""
        event = threading.Event()
        result_holder = {"approved": False}
        self._pending[session_id] = (event, result_holder)

        # Wait until /approve endpoint signals or times out (5 min)
        signaled = event.wait(timeout=timeout)
        self._pending.pop(session_id, None)

        if not signaled:
            return False  # Timed out -> auto-deny
        return result_holder["approved"]

    def submit_decision(self, session_id: str, approved: bool) -> bool:
        """Called by FastAPI /approve endpoint when user clicks Approve/Deny."""
        if session_id in self._pending:
            event, result_holder = self._pending[session_id]
            result_holder["approved"] = approved
            event.set()
            return True
        return False


hitl_manager = HITLManager()
