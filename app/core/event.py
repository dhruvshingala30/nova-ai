from dataclasses import dataclass, field
from typing import Any


@dataclass
class NovaEvent:
    """Base class for all events in the Nova framework."""

    event_type: str
    content: str
    data: dict[str, Any] = field(default_factory=dict)