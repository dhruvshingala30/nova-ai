"""
api/routes/workspace.py - Workspace Route Handlers.
Exposes endpoints for listing, uploading, and retrieving workspace assets.
"""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from api.schemas.workspace import WorkspaceFileListResponse, WorkspaceUploadResponse
from api.services.workspace_service import workspace_service

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/{session_id}/files", response_model=WorkspaceFileListResponse)
def list_workspace_files(session_id: str):
    """Lists all files accessible within the requested session."""
    files = workspace_service.list_files(session_id=session_id)
    return {"files": files}


@router.post("/{session_id}/upload", response_model=WorkspaceUploadResponse)
async def upload_file(
    session_id: str,
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(description="The file to upload")],
):
    """Uploads a file to the session workspace and queues PDFs for background RAG indexing."""
    filename = file.filename or "uploaded_file"
    saved_path = workspace_service.save_file(
        session_id=session_id,
        filename=filename,
        file_stream=file.file,
    )

    if filename.lower().endswith(".pdf"):
        background_tasks.add_task(workspace_service.ingest_pdf, file_path=saved_path)

    return {
        "status": "success",
        "filename": filename,
        "message": "File uploaded successfully.",
    }


@router.get("/{session_id}/files/{filename}")
def download_file(session_id: str, filename: str):
    """Streams a workspace file to the browser."""
    file_path = workspace_service.get_file_path(
        session_id=session_id, filename=filename
    )

    if not file_path:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

    return FileResponse(path=file_path, filename=filename)
