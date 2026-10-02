"""app/core/event_bus.py - Asynchronous Event Bus and Dispatch Bridge.

Provides the EventCollector utility to safely forward synchronous or
cross-thread agent events into an active asyncio.Queue within a running event loop.
"""

import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.core.event import NovaEvent


class EventCollector:
    def __init__(
        self, 
        queue: asyncio.Queue[NovaEvent], 
        loop: asyncio.AbstractEventLoop
    ) -> None:
        self.queue = queue
        self.loop = loop

    def __call__(self, event: NovaEvent):
        self.loop.call_soon_threadsafe(
            self.queue.put_nowait,
            event,
        )