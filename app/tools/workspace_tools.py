"""app/tools/workspace_inspector.py - Workspace File Inspection and Multi-Modal Analysis Tools.

Provides sandboxed, path-traversal-guarded agent utilities to explore workspace
directories, inspect tabular data (CSV/TSV), parse PDF document metadata,
and analyze visual assets using local vision LLMs.
"""

import base64
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from ollama import Client
from pypdf import PdfReader

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
                rel_path = path.relative_to(workspace.workspace_dir)
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
        file_path : str = "",
        sample_rows: int = 5
) -> dict[str, Any]:
    """
    Inspects a CSV file's structure, column types, shape, and sample data without loading the whole file into LLM memory.
    """
    if params is None:
        params = InspectCSVInput(file_path=file_path, sample_rows=sample_rows)
    try:
        safe_file_path = workspace.resolve_safe_path(params.file_path)

        if not safe_file_path.exists():
            return {"status": "error", "message": f"File '{params.file_path}' not found."}

        if safe_file_path.suffix.lower() not in ['.csv', '.tsv']:
            return {"status": "error", "message": f"File '{params.file_path}' is not a CSV/TSV file."}
        
        # Use pandas to quickly inspect the header and schema
        sep = '\t' if safe_file_path.suffix.lower() == '.tsv' else ','

        # Read sample rows
        df_sample = pd.read_csv(safe_file_path, sep=sep, nrows=params.sample_rows)

        # Get overall row count efficiently without reading everything into RAM
        with open(safe_file_path, 'rb') as file:
            total_lines = sum(1 for _ in file)
        estimated_rows = max(0, total_lines - 1)  # Subtract 1 for header

        # Build schema summary
        column_schema = [
            {"column": col, "dtype": str(df_sample[col].dtype)}
            for col in df_sample.columns
        ]

        return {
            "status": "success",
            "file_name": safe_file_path.name,
            "total_rows_approx": estimated_rows,
            "total_columns": len(df_sample.columns),
            "columns": column_schema,
            "sample_data": df_sample.to_dict(orient="records")
        }

    except PermissionError as pe:
        return {"status": "error", "message": str(pe)}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to inspect CSV: {str(e)}"}  # noqa: RUF010


# --------------------------
# Tool 3: Inspect PDF Schema
# --------------------------
def inspect_pdf_schema(
        params: InspectPDFInput | None = None,
        file_path: str = "",
        max_pages_to_sample: int = 2,
) -> dict[str, Any]:
    """
    Inspects a PDF document in `./nova_workspace` to retrieve total page count,
    metadata, and sample text from the initial pages.
    """
    # 1. Parameter Normalization (Handles both direct kwargs and Pydantic objects)
    if params is None:
        params = InspectPDFInput(
            file_path=file_path,
            max_pages_to_sample=max_pages_to_sample
        )

    try:
        # 2. Path Security Check
        safe_file_path = workspace.resolve_safe_path(params.file_path)
        if not safe_file_path.exists():
            return {
                "status": "error",
                "message": f"File '{params.file_path}' not found in workspace.",
            }
        if safe_file_path.suffix.lower() != '.pdf':
            return {
                "status": "error",
                "message": f"File '{params.file_path}' is not a valid PDF file."
            }

        # 3. Read PDF with pypdf.PdfReader
        reader = PdfReader(safe_file_path)
        total_pages = len(reader.pages)

        # Extract basic metadata
        meta = reader.metadata
        metadata_summary = {}
        if meta:
            metadata_summary = {
                "title": meta.title or "Unknown",
                "author": meta.author or "Unknown",
                "creator": meta.creator or "Unknown",
            }

        # Extract sample text from initial pages
        pages_to_extract = min(total_pages, params.max_pages_to_sample)
        sample_pages = []
        for page_num in range(pages_to_extract):
            page = reader.pages[page_num]
            extracted_text = page.extract_text() or "[No readable text found.]"

            # Clean up excessive whitespace for scannability
            cleaned_text = " ".join(extracted_text.split())

            # Limit sample snippet length per page
            snippet = (
                cleaned_text[:400] + '...'
                if len(cleaned_text) > 400
                else cleaned_text
            )

            sample_pages.append(
                {
                    "page_number": page_num + 1,
                    "character_count": len(extracted_text),
                    "text_sample": snippet,
                }
            )

        return {
            "status": "success",
            "file_name": safe_file_path.name,
            "total_pages": total_pages,
            "metadata": metadata_summary,
            "sample_pages": sample_pages,
        }
    
    except Exception as e:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"Failed to inspect pdf '{params.file_path}': {str(e)}"  # noqa: RUF010
        }


# --------------------------
# Tool 4: Inspect Image / Chart
# --------------------------
def inspect_image(
    params: InspectImageInput | None = None,
    file_path: str = "",
    prompt: str = "Describe this image in detail.",
) -> dict[str, str]:
    """Inspects an image located in ./nova_workspace using a multimodal vision model.

    Supports both Cloud (Groq Vision) and Local (Ollama LLaVA) execution.
    """
    if params is None:
        params = InspectImageInput(file_path=file_path, prompt=prompt)

    try:
        # 1. Path Sandboxing Guardrail
        safe_file_path = workspace.resolve_safe_path(params.file_path)

        if not safe_file_path.exists():
            return {
                "status": "error",
                "message": f"File '{params.file_path}' does not exist.",
            }

        # 2. File Format Guardrail
        supported_exts = {".png", ".jpg", ".jpeg", ".webp"}
        if safe_file_path.suffix.lower() not in supported_exts:
            return {
                "status": "error",
                "message": f"File '{params.file_path}' is not a supported image format ({supported_exts})",
            }

        # 3. Encode Image to Base64
        with open(safe_file_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode("utf-8")

        # 4. Hybrid Routing: Cloud (Groq) vs Local (Ollama)
        if USE_CLOUD_LLM:
            from openai import OpenAI

            ext = safe_file_path.suffix.lower().lstrip(".")
            mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

            cloud_client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url=CLOUD_BASE_URL,
            )

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
                                    "url": f"data:{mime_type};base64,{base64_image}"
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

        else:
            client = Client(host=OLLAMA_HOST)
            response = client.chat(
                model="llava",
                messages=[
                    {
                        "role": "user",
                        "content": params.prompt,
                        "images": [base64_image],
                    }
                ],
                options={"temperature": 0.1},
                keep_alive="5m",
            )
            visual_analysis = (
                response.message.content or "No visual description generated."
            )

        return {
            "status": "success",
            "file_name": safe_file_path.name,
            "prompt_asked": params.prompt,
            "visual_analysis": visual_analysis,
        }

    except Exception as e:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"Failed to inspect image: {str(e)}",  # noqa: RUF010
        }


if __name__ == "__main__":
    # 1. Create a dummy test file in workspace
    dummy_csv = workspace.workspace_dir / "users.csv"
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
