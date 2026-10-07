"""app/tools/workspace_inspector.py - Workspace File Inspection and Multi-Modal Analysis Tools.

Provides sandboxed, path-traversal-guarded agent utilities to explore workspace
directories, inspect tabular data (CSV/TSV), parse PDF document metadata,
and analyze visual assets using local vision LLMs.
"""

import base64
import io
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd
from ollama import Client
from openai import RateLimitError

from app.core.session_store import session_store

# Add project root (nova-ai/) to Python path dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (
    CLOUD_BASE_URL,
    CLOUD_VISION_MODEL,
    GROQ_API_KEY,
    OLLAMA_HOST,
    USE_CLOUD_LLM,
    VISION_MODEL_NAME,
    WORKSPACE_DIR,
)
from app.core.workspace_manager import workspace
from app.models import (
    InspectCSVInput,
    InspectImageInput,
    InspectPDFInput,
    ListFilesInput,
)


# ----------------------------
# Tool 1: List Workspace Files
# ----------------------------
def list_workspace_files(
        params: ListFilesInput | None = None,
        subfolder: str | None = None,
        pattern: str | None = "*"
) -> dict[str, Any]:
    """
    Lists files, sizes, and relative paths in the workspace.
    """
    if params is None:
        params = ListFilesInput(subfolder=subfolder or "" , pattern=pattern or "*")
    try:
        target_dir = workspace.resolve_safe_path(params.subfolder) # type: ignore
        if not target_dir.exists() or not target_dir.is_dir():
            return {"status": "error", "message": f"Directory '{params.subfolder}' does not exist."}

        files_info = []
        for path in target_dir.glob(params.pattern): # type: ignore
            if path.is_file():
                # Compute relative path back to root workspace for clean LLM context
                rel_path = path.relative_to(WORKSPACE_DIR)
                files_info.append({
                    "name": path.name,
                    "path": str(rel_path),
                    "size_bytes": path.stat().st_size,
                    "size_human": f"{path.stat().st_size / 1024:.1f} KB" if path.stat().st_size >= 1024 else f"{path.stat().st_size} B",
                    "extension": path.suffix.lower()
                })

        return {
            "status": "success",
            "count": len(files_info),
            "files": files_info
        }

    except PermissionError as pe:
        return {"status": "error", "message": str(pe)}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to list files: {str(e)}"}  # noqa: RUF010

 
# ---------------------------------
# Tool 2: Inspect CSV Schema & Head
# ---------------------------------
def inspect_csv_schema(
    params: InspectCSVInput | None = None,
    file_path: str = "",
    sample_rows: int = 5,
    session_id: str | None = None,
) -> dict[str, Any]:
    if params is None:
        params = InspectCSVInput(file_path=file_path, sample_rows=sample_rows)
    try:
        clean_filename = Path(params.file_path).name
        raw_bytes = None

        if session_id:
            raw_bytes = session_store.get_file(session_id, clean_filename)

        if not raw_bytes:
            safe_file_path = workspace.resolve_safe_path(
                params.file_path, session_id=session_id
            )
            if safe_file_path.exists() and safe_file_path.is_file():
                raw_bytes = safe_file_path.read_bytes()

        if not raw_bytes:
            return {
                "status": "error",
                "message": f"Dataset '{params.file_path}' not found in active session.",
            }

        sep = "\t" if clean_filename.lower().endswith(".tsv") else ","
        df_sample = pd.read_csv(
            io.BytesIO(raw_bytes), sep=sep, nrows=params.sample_rows
        )

        # Estimate rows from byte lines
        total_lines = len(raw_bytes.splitlines())
        estimated_rows = max(0, total_lines - 1)

        column_schema = [
            {"column": col, "dtype": str(df_sample[col].dtype)}
            for col in df_sample.columns
        ]

        return {
            "status": "success",
            "file_name": clean_filename,
            "total_rows_approx": estimated_rows,
            "total_columns": len(df_sample.columns),
            "columns": column_schema,
            "sample_data": df_sample.to_dict(orient="records"),
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to inspect CSV: {str(e)}"}  # noqa: RUF010


# --------------------------
# Tool 3: Inspect PDF Schema (In-Memory Stream Aware)
# --------------------------
def inspect_pdf_schema(
    params: InspectPDFInput | None = None,
    file_path: str = "",
    max_pages_to_sample: int = 2,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Inspects a PDF document from active session memory (or disk fallback) to retrieve
    total page count, metadata, and clean sample text from initial pages.
    """
    if params is None:
        params = InspectPDFInput(
            file_path=file_path,
            max_pages_to_sample=max_pages_to_sample,
            session_id=session_id,
        )

    try:
        import fitz  # PyMuPDF: C-based, resilient to stream decompression & trailer damage

        clean_filename = Path(params.file_path).name
        raw_bytes: bytes | None = None
        active_session = params.session_id or session_id

        # 1. Check session_store for in-memory uploaded PDF
        if active_session:
            raw_bytes = session_store.get_file(active_session, clean_filename)

        # 2. Disk fallback for static templates
        if not raw_bytes:
            safe_file_path = workspace.resolve_safe_path(
                params.file_path, session_id=active_session
            )
            if not safe_file_path.exists():
                safe_file_path = workspace.resolve_safe_path(
                    params.file_path, session_id=None
                )
            if safe_file_path.exists() and safe_file_path.is_file():
                raw_bytes = safe_file_path.read_bytes()

        if not raw_bytes:
            return {
                "status": "error",
                "message": f"PDF document '{params.file_path}' was not found in active session memory.",
            }

        # 3. Parse in-memory stream with fitz
        doc = fitz.open(stream=raw_bytes, filetype="pdf")
        total_pages = len(doc)

        metadata_raw = doc.metadata or {}
        metadata_summary = {
            "title": metadata_raw.get("title") or clean_filename,
            "author": metadata_raw.get("author") or "Unknown",
            "creator": metadata_raw.get("creator") or "Unknown",
        }

        # 4. Extract text sample from initial pages
        pages_to_extract = min(total_pages, params.max_pages_to_sample)
        sample_pages = []

        for page_num in range(pages_to_extract):
            page = doc[page_num]
            extracted_text = str(page.get_text("text") or "").strip()
            cleaned_text = " ".join(extracted_text.split())

            snippet = (
                cleaned_text[:400] + "..."
                if len(cleaned_text) > 400
                else cleaned_text or "[No readable text found on page]"
            )

            sample_pages.append(
                {
                    "page_number": page_num + 1,
                    "character_count": len(extracted_text),
                    "text_sample": snippet,
                }
            )

        doc.close()

        return {
            "status": "success",
            "file_name": clean_filename,
            "total_pages": total_pages,
            "metadata": metadata_summary,
            "sample_pages": sample_pages,
        }

    except Exception as e:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"Failed to inspect PDF '{params.file_path}': {str(e)}",  # noqa: RUF010
        }


# --------------------------
# Tool 4: Inspect Image / Chart (In-Memory Base64 Aware)
# --------------------------
def inspect_image(
    params: InspectImageInput | None = None,
    file_path: str = "chart.png",
    prompt: str = "Describe this image in detail.",
    base64_image: str | None = None,
    session_id: str | None = None,
) -> dict[str, str]:
    if params is None:
        params = InspectImageInput(
            file_path=file_path,
            prompt=prompt,
            base64_image=base64_image,
            session_id=session_id,
        )

    try:
        raw_b64: str | None = params.base64_image
        target_name = Path(params.file_path).name

        # 1. Resolve image from in-memory session store
        if not raw_b64 and session_id:
            visuals = session_store.get_latest_visuals(session_id)
            # Find matching visual by filename or pick the latest generated visual
            for v in reversed(visuals):
                if v.get("name") == target_name or target_name in [
                    "chart.png",
                    "image.png",
                ]:
                    raw_b64 = v.get("b64")
                    target_name = v.get("name", target_name)
                    break

            # If not in visuals, check uploaded raw files in session_store
            if not raw_b64:
                file_bytes = session_store.get_file(session_id, target_name)
                if file_bytes:
                    raw_b64 = base64.b64encode(file_bytes).decode("utf-8")

        # 2. Optional disk fallback for static/legacy template assets
        if not raw_b64:
            safe_file_path = workspace.resolve_safe_path(
                params.file_path, session_id=session_id
            )
            if not safe_file_path.exists():
                safe_file_path = workspace.resolve_safe_path(
                    params.file_path, session_id=None
                )

            if safe_file_path.exists() and safe_file_path.is_file():
                with open(safe_file_path, "rb") as img_file:
                    raw_b64 = base64.b64encode(img_file.read()).decode("utf-8").strip()

        if not raw_b64:
            return {
                "status": "error",
                "message": f"Image artifact '{params.file_path}' was not found in active session memory.",
            }

        # Normalize data URL stripping if already prefixed
        if raw_b64.startswith("data:"):
            raw_b64 = raw_b64.split(",", 1)[-1].strip()

        ext = Path(target_name).suffix.lower().lstrip(".")
        mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext or 'png'}"

        # 3. Vision Inference (Cloud Groq vs. Local Ollama)
        if USE_CLOUD_LLM:
            from openai import OpenAI

            cloud_client = OpenAI(
                api_key=GROQ_API_KEY, base_url=CLOUD_BASE_URL, timeout=30.0
            )
            max_retries = 3
            visual_analysis = "No visual description generated."

            for attempt in range(max_retries):
                try:
                    response = cloud_client.chat.completions.create(
                        model=CLOUD_VISION_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": params.prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{mime_type};base64,{raw_b64}"
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=600,
                        temperature=0.1,
                    )
                    visual_analysis = (
                        response.choices[0].message.content
                        or "No visual description generated."
                    )
                    break
                except RateLimitError:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2.0 * (attempt + 1))
        else:
            client = Client(host=OLLAMA_HOST)
            response = client.chat(
                model=VISION_MODEL_NAME,
                messages=[
                    {"role": "user", "content": params.prompt, "images": [raw_b64]}
                ],
                options={"temperature": 0.1},
                keep_alive="5m",
            )
            visual_analysis = (
                response.message.content or "No visual description generated."
            )

        return {
            "status": "success",
            "file_name": target_name,
            "prompt_asked": params.prompt,
            "visual_analysis": visual_analysis,
        }

    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to inspect image: {str(e)}"}  # noqa: RUF010


if __name__ == "__main__":
    # 1. Create a dummy test file in workspace
    dummy_csv = WORKSPACE_DIR / "users.csv"
    dummy_csv.write_text(
        "id,name,role\n1,Alice,Admin\n2,Bob,Developer\n3,Charlie,Data Scientist"
    )

    # 2. Test valid file listing
    print("--- Testing list_workspace_files ---")
    list_input = ListFilesInput()
    print(list_workspace_files(list_input))

    # 3. Test CSV inspection
    print("\n--- Testing inspect_csv_schema ---")
    inspect_input = InspectCSVInput(file_path="users.csv", sample_rows=2)
    print(inspect_csv_schema(inspect_input))

    # 4. Test Path Traversal Security Guard
    print("\n--- Testing Security Guard ---")
    malicious_input = InspectCSVInput(file_path="../../etc/passwd")
    print(inspect_csv_schema(malicious_input))
