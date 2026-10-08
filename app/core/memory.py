"""
app/core/memory.py - SQLite Session Memory & Context Persistence Engine
Provides database persistence for chat history across terminal restarts.
"""

import re
import sqlite3
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "nova_memory.db"

class SQLiteMemory:
    """SQLite database interface for persisting conversation history and session logs."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.Connection(self.db_path)

    def _init_db(self):
        """Creates the `messages` table schema and index if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_session_id ON messages (session_id)"
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT DEFAULT 'default_user'
                )
                """
            )
            cursor.execute("PRAGMA table_info(sessions)")
            columns = [col[1] for col in cursor.fetchall()]
            if "user_id" not in columns:
                cursor.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT DEFAULT 'default_user'")
            conn.commit()

    def save_message(self, session_id: str, role: str, content: str):
        """Saves a single message into SQLite for a specific session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )
            conn.commit()

    def save_session(self, session_id: str, title: str, user_id: str = "default_user"):
        """Creates a session or updates its timestamp."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO sessions (session_id, title, user_id) VALUES (?, ?, ?) 
                ON CONFLICT(session_id) 
                DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, title, user_id),
            )
            conn.commit()

    def get_session_history(
        self, session_id: str, limit: int = 20
    ) -> list[dict[str, str]]:
        """Retrieves recent messages for a session ID in chronological order."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # FIX: Corrected invalid SQL syntax (LIMIT = ? -> LIMIT ? and ORDER BY ASC -> ORDER BY id ASC)
            cursor.execute(
                """
                SELECT role, content FROM (
                    SELECT id, role, content FROM messages
                    WHERE session_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                ) ORDER BY id ASC
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()
            return [{"role": row[0], "content": row[1]} for row in rows]

    def list_sessions(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """Returns all sessions with their human-readable titles."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute(
                    """SELECT session_id, title, created_at, updated_at 
                    FROM sessions 
                    WHERE user_id = ?
                    AND TRIM(title) != ''
                    ORDER BY updated_at DESC
                    """, (user_id,),
                )
            else:
                cursor.execute(
                    """SELECT session_id, title, created_at, updated_at 
                    FROM sessions 
                    WHERE TRIM(session_id) != ''
                    AND TRIM(title) != ''
                    ORDER BY updated_at DESC"""
                )

            rows = cursor.fetchall()
            return [
                {
                    "session_id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "updated_at": row[3],
                }
                for row in rows
            ]

    def get_session_title(self, session_id: str):
        """Returns the human-readable title for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT TITLE FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            return row[0] if row else None

    def update_session_title(self, session_id: str, title: str) -> None:
        """Updates only the title of an existing session record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sessions
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
                """,
                (title, session_id)
            )
            conn.commit()


    def generate_title_in_background(
            self, 
            client, 
            model_name: str, 
            prompt: str, 
            session_id: str, 
            on_title_generated: Callable[[str], None] | None = None,
    ) -> None :
        """Fires an asynchronous daemon thread to generate and update the session title."""
        def _worker() -> None:
            # Ask Ollama for the refined title
            refined_title = self.generate_title_from_prompt(
                client=client,
                model_name=model_name,
                prompt=prompt
            )
            # Update database record
            self.update_session_title(session_id=session_id, title=refined_title)

            # Emit callback event to notify frontend/orchestrator
            if on_title_generated:
                on_title_generated(refined_title)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def generate_title_from_prompt(self, client, model_name: str, prompt: str) -> str:
        """Generates a clean 3-to-5 word session title from the initial prompt."""
        try:
            response = client.chat(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Summarize the user prompt into a concise title (3 to 5 words max). "
                            "Correct typos/proper nouns. Output ONLY title text without quotes."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                keep_alive="30m"
            )
            
            raw_title = response.message.content.strip()
            clean_title = re.sub(r"[^\w\s-]", "", raw_title)
            return clean_title if clean_title else prompt[:30]
        except Exception:  # noqa: BLE001
            return prompt[:30].strip()
