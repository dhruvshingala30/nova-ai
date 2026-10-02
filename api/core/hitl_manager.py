"""api/core/hitl_manager.py - Human-In-The-Loop (HITL) Concurrency Manager.

Coordinates cross-thread synchronization between blocking specialist agents
and asynchronous API approval endpoints using threading events.
"""

import threading


class HITLManager:
    """Manages thread-safe approval handshakes between BaseAgent and FastAPI."""

    def __init__(self):
        # Maps session_id to a tuple: (threading.Event, dict_containing_decision)
        # The Event pauses/unpauses the agent thread.
        # The dict holds the boolean approval result.
        self._pending: dict[str, tuple[threading.Event, dict]] = {}

    def wait_for_decision(self, session_id: str, timeout: float = 300.0) -> bool:
        """Called by the agent worker thread to pause execution until the user approves or denies.

        Args:
            session_id: Target session identifier.
            timeout: Maximum seconds to wait before defaulting to denial (default 5 min).
        """
        event = threading.Event()
        result_holder = {"approved": False}
        self._pending[session_id] = (event, result_holder)

        # Block the current thread until submit_decision calls event.set() or timeout expires
        signaled = event.wait(timeout=timeout)

        # Clean up pending state after resuming
        self._pending.pop(session_id, None)

        if not signaled:
            return False  # Timed out -> auto-deny
        return result_holder["approved"]

    def submit_decision(self, session_id: str, approved: bool) -> bool:
        """Called by the FastAPI /approve endpoint when a user clicks Approve or Deny in the UI.

        Args:
            session_id: Target session identifier.
            approved: True if user approved, False if denied.

        Returns:
            True if there was a waiting agent thread, False if no request was pending.
        """
        if session_id in self._pending:
            event, result_holder = self._pending[session_id]
            result_holder["approved"] = approved  # Save user choice
            event.set()  # Unblock the waiting agent thread
            return True
        return False

# Global singleton instance used across routes and agent threads
hitl_manager = HITLManager()
