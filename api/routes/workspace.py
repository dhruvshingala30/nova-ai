"""
api/routes/workspace.py - Dual-Routing In-Memory Upload Handler.
"""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, UploadFile

from app.core.session_store import session_store
from rag.ingest_pdf import (
    chunk_documents,
    extract_pdf_pages_from_bytes,
    ingest_to_chromadb,
)

router = APIRouter(prefix="/workspace", tags=["workspace"])


def _background_pdf_ingest(file_bytes: bytes, filename: str):
    try:
        pages = extract_pdf_pages_from_bytes(file_bytes, filename)
        if pages:
            chunks = chunk_documents(pages)
            count = ingest_to_chromadb(chunks)
            print(
                f"✅ [RAG] Successfully embedded {count} chunks for PDF '{filename}' into vector DB."
            )
        else:
            print(
                f"⚠️ [RAG] Skipped vector indexing for '{filename}': zero extractable text pages."
            )
    except Exception as e:  # noqa: BLE001
        print(f"❌ [RAG] Failed to embed PDF '{filename}': {e}")


@router.post("/{session_id}/upload")
async def upload_file(
    session_id: str,
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(description="File attachment")],
):
    filename = file.filename or "attachment"

    # 1. Reset stream pointer to start
    await file.seek(0)

    # 2. Read full byte array explicitly into immutable bytes
    raw_content = await file.read()
    file_bytes = bytes(
        raw_content
    )  # Create a hard copy in memory independent of request lifecycle

    print(f"📦 [Upload] Received '{filename}' - Total size: {len(file_bytes):,} bytes")

    # 3. Cache in ephemeral session memory
    session_store.save_file(
        session_id=session_id, filename=filename, content=file_bytes
    )

    # 4. Route PDF to background ingestion with independent byte buffer
    if filename.lower().endswith(".pdf"):
        background_tasks.add_task(
            _background_pdf_ingest, file_bytes=file_bytes, filename=filename
        )
        return {
            "status": "success",
            "filename": filename,
            "message": "PDF uploaded and queued for background RAG indexing.",
        }

    return {
        "status": "success",
        "filename": filename,
        "message": "File cached in session memory.",
    }


@router.get("/{session_id}/files")
def list_session_uploads(session_id: str):
    """Returns files currently cached in memory for this session."""
    cached = session_store.get_all_session_files(session_id)
    files = [
        {
            "name": name,
            "size_bytes": len(b),
            "is_image": name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")),
        }
        for name, b in cached.items()
    ]
    return {"files": files}
