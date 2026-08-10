import sys
from pathlib import Path

# Add project root (nova-ai/) to Python path dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from pydantic import BaseModel, Field

from app.core.workspace_manager import workspace


# ------------------------------------------------------------------
# Tool 1: List Workspace Files
# ------------------------------------------------------------------
class ListFilesInput(BaseModel):
    subfolder: str | None = Field(
        default="",
        description="Optional relative subfolder within workspace (e.g., 'data' or 'reports'). Leave empty for root.",
    )
    pattern: str | None = Field(
        default="*",
        description="Optional glob pattern to filter files, e.g., '*.csv' or '*.json'.",
    )

def list_workspace_files(
        params: ListFilesInput | None = None,
        subfolder: str | None = None,
        pattern: str | None = "*"
):
    """
    Lists files, sizes, and relative paths in the workspace.
    """
    if params is None:
        params = ListFilesInput(subfolder=subfolder or "" , pattern=pattern or "*")
    try:
        target_dir = workspace.resolve_safe_path(params.subfolder) # type: ignore
        if not target_dir.exists() or not target_dir.is_dir():
            return {"status": "error", "message": f"Directory '{params.subfolder}' does no exist."}

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


# ------------------------------------------------------------------
# Tool 2: Inspect CSV Schema & Head
# ------------------------------------------------------------------
class InspectCSVInput(BaseModel):
    file_path: str = Field(
        default=...,
        description="Relative path to the CSV file inside the workspace (e.g., 'sales_2025.csv').",
    )
    sample_rows: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of sample rows to return for preview.",
    )


def inspect_csv_schema(
        params: InspectCSVInput | None = None,
        file_path : str = "",
        sample_rows: int = 5
):
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
