"""
api/services/workspace_service.py - Workspace Service Layer.

Provides a service boundary over session files, template synchronization,
and automatic background RAG indexing.
"""

import shutil
from pathlib import Path
from typing import BinaryIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.core.workspace_manager import workspace
from rag.ingest_pdf import chunk_documents, extract_pdf_pages, ingest_to_chromadb


class WorkspaceService:
    """Service layer managing workspace file resolution, listings, and indexing."""

    def list_files(self, session_id: str) -> list[dict]:
        """
        Gathers all available files: global template assets first,
        followed/overridden by session-specific files.
        """
        session_dir = workspace.get_workspace_dir(session_id=session_id)
        default_dir = workspace.get_workspace_dir(session_id=None)

        files_map: dict[str, dict] = {}

        # 1. Base starter files from nova_workspace/
        if default_dir.exists():
            for item in default_dir.iterdir():
                if item.is_file() and not item.name.startswith("."):
                    files_map[item.name] = {
                        "name": item.name,
                        "size_bytes": item.stat().st_size,
                        "is_image": item.suffix.lower()
                        in [".png", ".jpg", ".jpeg", ".webp"],
                        "is_template": True,
                    }

        # 2. Session-specific files from nova_workspaces/<session_id>/
        if session_dir.exists():
            for item in session_dir.iterdir():
                if item.is_file() and not item.name.startswith("."):
                    files_map[item.name] = {
                        "name": item.name,
                        "size_bytes": item.stat().st_size,
                        "is_image": item.suffix.lower()
                        in [".png", ".jpg", ".jpeg", ".webp"],
                        "is_template": False,
                    }

        return list(files_map.values())

    def save_file(self, session_id: str, filename: str, file_stream: BinaryIO) -> Path:
        """Saves an incoming byte stream to the session's workspace directory."""
        session_dir = workspace.get_workspace_dir(session_id=session_id)
        dest_path = session_dir / filename

        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file_stream, buffer)

        return dest_path

    def get_file_path(self, session_id: str, filename: str) -> Path | None:
        """
        Resolves the path of a requested file for download.
        Checks session directory first, falling back to default workspace templates.
        """
        session_dir = workspace.get_workspace_dir(session_id=session_id)
        target = session_dir / filename

        if not target.exists():
            target = workspace.get_workspace_dir(session_id=None) / filename

        if target.exists() and target.is_file():
            return target

        return None

    def ingest_pdf(self, file_path: str | Path) -> None:
        """Ingests a PDF into ChromaDB for hybrid RAG search."""
        path_str = str(file_path)
        try:
            pages = extract_pdf_pages(file_path=path_str)
            chunks = chunk_documents(pages_data=pages)
            ingest_to_chromadb(chunks=chunks)
            print(
                f" [WorkspaceService] Ingested PDF '{Path(path_str).name}' into vector DB."
            )
        except Exception as e:  # noqa: BLE001
            print(f" [WorkspaceService] PDF indexing error for '{path_str}': {e}")


# Global singleton instance used by API route handlers
workspace_service = WorkspaceService()