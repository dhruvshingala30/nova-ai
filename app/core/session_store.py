"""
app/core/session_store.py - Ephemeral In-Memory Store for Uploaded Tables & Media.
"""

from typing import Any


class EphemeralSessionStore:
    def __init__(self):
        # Maps session_id -> { filename: bytes / str / metadata }
        self._data: dict[str, dict[str, Any]] = {}
        # Retains latest generated image base64 strings per session for multi-turn vision
        self._latest_visuals: dict[str, list[dict[str, str]]] = {}

    def save_file(self, session_id: str, filename: str, content: bytes) -> None:
        if session_id not in self._data:
            self._data[session_id] = {}
        self._data[session_id][filename] = content

    def get_file(self, session_id: str, filename: str) -> bytes | None:
        return self._data.get(session_id, {}).get(filename)

    def get_all_session_files(self, session_id: str) -> dict[str, bytes]:
        return self._data.get(session_id, {})

    def record_visual(self, session_id: str, name: str, b64_str: str) -> None:
        if session_id not in self._latest_visuals:
            self._latest_visuals[session_id] = []
        self._latest_visuals[session_id].append({"name": name, "b64": b64_str})
        # Keep only the 3 most recent images
        self._latest_visuals[session_id] = self._latest_visuals[session_id][-3:]

    def get_latest_visuals(self, session_id: str) -> list[dict[str, str]]:
        return self._latest_visuals.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        self._data.pop(session_id, None)
        self._latest_visuals.pop(session_id, None)


session_store = EphemeralSessionStore()
