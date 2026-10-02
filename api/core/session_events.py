"""api/core/session_events.py - Session Event Queue Manager.

Maintains in-memory asynchronous queues mapped by session ID to route
internal agent events to client-facing Server-Sent Events (SSE) streams.
"""

import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.core.event import NovaEvent


class SessionEventManager:
    """Stores and retrieves asyncio.Queue instances for active SSE sessions."""

    def __init__(self) -> None:
        # Maps session_id (str) -> asyncio.Queue containing streaming NovaEvents
        self.queues: dict[str, asyncio.Queue[NovaEvent]] = {}

    def create_queue(self, session_id: str) -> asyncio.Queue[NovaEvent]:
        """Creates and stores a fresh asyncio queue for a given session."""
        queue: asyncio.Queue[NovaEvent] = asyncio.Queue()
        self.queues[session_id] = queue
        return queue

    def get_queue(self, session_id: str) -> asyncio.Queue[NovaEvent] | None:
        """Retrieves an existing queue by session ID, or returns None if not found."""
        return self.queues.get(session_id)

    def remove_queue(self, session_id: str) -> None:
        """Deletes a session queue once streaming has concluded to prevent memory leaks."""
        self.queues.pop(session_id, None)

# Global singleton instance used across the app
session_event_manager = SessionEventManager()