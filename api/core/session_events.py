import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.core.event import NovaEvent


class SessionEventManager:
    def __init__(self) -> None:
        self.queues: dict[str, asyncio.Queue[NovaEvent]] = {}

    def create_queue(self, session_id: str) -> asyncio.Queue[NovaEvent]:
        queue: asyncio.Queue[NovaEvent] = asyncio.Queue()
        self.queues[session_id] = queue
        return queue

    def get_queue(self, session_id: str) -> asyncio.Queue[NovaEvent] | None:
        return self.queues.get(session_id)

    def remove_queue(self, session_id: str) -> None:
        self.queues.pop(session_id, None)


session_event_manager = SessionEventManager()