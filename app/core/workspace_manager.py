from pathlib import Path


class WorkspaceManager:
    def __init__(self, workspace_dir: str  = "nova_workspace") -> None:
        if workspace_dir is None:
            # 1. Calculates project root (nova-ai/)
            PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
            # 2. Points directly to nova-ai/nova_workspace
            self.workspace_dir = (PROJECT_ROOT / workspace_dir).resolve()
        else:
            self.workspace_dir = Path(workspace_dir).resolve()

        # 3. Auto-creates the folder on root if it doesn't exist yet
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def resolve_safe_path(self, relative_path: str) -> Path:
        """
        Resolves a relative path against the workspace directory and ensures
        it does not escape the sandbox (prevents path traversal attacks).
        """
        # Remove leading slashes to prevent root-anchoring issues
        clean_rel = relative_path.lstrip("/\\")

        # Strip accidental prefix aliases the LLM might hallucinate
        for prefix in ("nova_workspace/", "workspace/", "./nova_workspace/", "./workspace/"):
            clean_rel = clean_rel.removeprefix(prefix)

        target_path = (self.workspace_dir / clean_rel).resolve()

        if not target_path.is_relative_to(self.workspace_dir):
            raise PermissionError(
                f"Security Error: Access denied to path '{relative_path}'."
                f"Paths must stay inside '{self.workspace_dir}'."
            )
        return target_path

# Global singleton instance
workspace = WorkspaceManager()