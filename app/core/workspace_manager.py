"""
app/core/workspace_manager.py - Session-Aware Path Scoping and Traversal Guard.
"""

from pathlib import Path

from app.config import PROJECT_ROOT, WORKSPACE_DIR


class WorkspaceManager:
    def __init__(self) -> None:
        self.default_workspace_dir = WORKSPACE_DIR
        self.default_workspace_dir.mkdir(parents=True, exist_ok=True)
        self.base_sessions_dir = PROJECT_ROOT / "nova_workspaces"
        self.base_sessions_dir.mkdir(parents=True, exist_ok=True)

    def get_workspace_dir(self, session_id: str | None = None) -> Path:
        """Returns the isolated workspace directory for a session or default local workspace."""
        if session_id:
            session_dir = self.base_sessions_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            return session_dir
        return self.default_workspace_dir

    def resolve_safe_path(
        self, relative_path: str, session_id: str | None = None
    ) -> Path:
        """Resolves relative paths, preventing directory traversal while respecting active session."""
        target_dir = self.get_workspace_dir(session_id)
        clean_rel = relative_path.lstrip("/\\")

        # Strip accidental prefix aliases the LLM might output
        for prefix in (
            "./nova_workspace/",
            "./workspace/",
            "nova_workspace/",
            "workspace/",
            "./nova_workspace",
            "./workspace",
            "nova_workspace",
            "workspace",
        ):
            if clean_rel == prefix or clean_rel == prefix.rstrip("/"):
                return target_dir
            clean_rel = clean_rel.removeprefix(prefix)

        target_path = (target_dir / clean_rel).resolve()

        if not target_path.is_relative_to(target_dir):
            raise PermissionError(
                f"Security Error: Access denied to path '{relative_path}'. "
                f"Paths must stay inside '{target_dir}'."
            )
        return target_path


workspace = WorkspaceManager()
