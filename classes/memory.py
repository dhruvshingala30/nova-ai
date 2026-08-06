"""
memory.py - SQLite Session Memory & Context Persistence Engine
Provides database persistence for chat history across terminal restarts.
"""

import re
import sqlite3


class SQLiteMemory:
    """SQLite database interface for persisting conversation history and session logs."""

    def __init__(self, db_path: str = "nova_memory.db"):
        self.db_path = db_path
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

    def list_sessions(self) -> list[str]:
        """Returns a list of all unique session IDs stored in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT session_id FROM messages")
            rows = cursor.fetchall()
            return [row[0] for row in rows]

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
            )
            raw_title = response.message.content.strip()
            clean_title = re.sub(r"[^\w\s-]", "", raw_title)
            return clean_title if clean_title else prompt[:30]
        except Exception:  # noqa: BLE001
            return prompt[:30].strip()
