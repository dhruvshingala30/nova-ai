"""
api/schemas/workspace.py - Workspace API Data Schemas.
"""

from pydantic import BaseModel


class WorkspaceFileInfo(BaseModel):
    name: str
    size_bytes: int
    is_image: bool = False
    is_template: bool


class WorkspaceFileListResponse(BaseModel):
    files: list[WorkspaceFileInfo]


class WorkspaceUploadResponse(BaseModel):
    status: str
    filename: str
    message: str