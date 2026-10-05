"""
app/tools/code_interpreter.py - Dual-Mode Execution Sandbox with Session Isolation.
"""

import base64
from pathlib import Path

import docker
from docker.errors import ContainerError, DockerException

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.config import E2B_API_KEY, USE_CLOUD_LLM
from app.core.workspace_manager import workspace
from app.models import CodeInterpreterInput


class CodeInterpreter:
    @staticmethod
    def run_python_code(
        params: CodeInterpreterInput | None = None,
        code: str | None = None,
        session_id: str | None = None,
    ):
        if params is None:
            if code is None:
                return {
                    "success": False,
                    "output": None,
                    "error": "No Python code provided.",
                }
            params = CodeInterpreterInput(code=code)

        target_dir = workspace.get_workspace_dir(session_id=session_id)
        default_dir = workspace.get_workspace_dir(session_id=None)

        wrapped_code = (
            "import math, sys\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "pd.set_option('display.max_rows', 20)\n"
            "pd.set_option('display.max_columns', 8)\n"
            "pd.set_option('display.width', 120)\n"
            "import matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "try:\n"
            "    import sympy as sp\n"
            "except ImportError:\n"
            "    pass\n\n"
            f"{params.code}\n\n"
            "if 'result' in locals() and result is not None:\n"
            "    print(result)\n"
        )

        # -------------------------------------------------------------
        # CLOUD MODE: E2B Sandbox
        # -------------------------------------------------------------
        if USE_CLOUD_LLM and E2B_API_KEY:
            from e2b_code_interpreter import Sandbox

            try:
                with Sandbox.create(api_key=E2B_API_KEY) as sandbox:
                    existing_files = set()

                    # Sync baseline workspace files
                    if default_dir.exists():
                        for f in default_dir.glob("*"):
                            if f.is_file():
                                sandbox.files.write(f.name, f.read_bytes())
                                existing_files.add(f.name)

                    # Sync session-specific uploads
                    if target_dir.exists():
                        for f in target_dir.glob("*"):
                            if f.is_file():
                                sandbox.files.write(f.name, f.read_bytes())
                                existing_files.add(f.name)

                    execution = sandbox.run_code(code=wrapped_code, language="python")
                    output_text = "\n".join(
                        [str(line) for line in execution.logs.stdout]
                    )
                    error_text = (
                        "\n".join([str(err) for err in execution.logs.stderr])
                        if execution.error
                        else None
                    )

                    artifacts = []

                    # Download saved artifacts back into session directory
                    try:
                        sandbox_files = sandbox.files.list(".")
                        for s_file in sandbox_files:
                            name = s_file.name
                            if (
                                name.lower().endswith(
                                    (".png", ".jpg", ".jpeg", ".csv", ".json")
                                )
                                and name not in existing_files
                            ):
                                content = sandbox.files.read(name)
                                file_bytes = (
                                    content.encode("utf-8")
                                    if isinstance(content, str)
                                    else bytes(content)
                                )
                                out_path = workspace.resolve_safe_path(
                                    name, session_id=session_id
                                )
                                out_path.write_bytes(file_bytes)
                                if name not in artifacts:
                                    artifacts.append(name)
                    except Exception:  # noqa: BLE001, S110
                        pass

                    # Capture plots emitted without an explicit savefig call
                    if not artifacts:
                        for idx, res in enumerate(execution.results):
                            if res.png:
                                chart_name = (
                                    "chart.png" if idx == 0 else f"chart_{idx + 1}.png"
                                )
                                out_path = workspace.resolve_safe_path(
                                    chart_name, session_id=session_id
                                )
                                out_path.write_bytes(base64.b64decode(res.png))
                                artifacts.append(chart_name)

                    return {
                        "success": execution.error is None,
                        "output": output_text
                        or "Code executed successfully with no printed output.",
                        "error": str(execution.error)
                        if execution.error
                        else error_text,
                        "artifacts": artifacts,
                    }
            except Exception as e:  # noqa: BLE001
                return {
                    "success": False,
                    "output": None,
                    "error": str(e),
                    "artifacts": [],
                }

        # -------------------------------------------------------------
        # LOCAL MODE: Docker Container
        # -------------------------------------------------------------
        else:
            try:
                client = docker.from_env()
                client.ping()

                output_bytes = client.containers.run(
                    image="nova-sandbox:latest",
                    command=["python", "-c", wrapped_code],
                    volumes={
                        str(target_dir.resolve()): {"bind": "/workspace", "mode": "rw"}
                    },
                    working_dir="/workspace",
                    detach=False,
                    remove=True,
                    network_disabled=True,
                    mem_limit="512m",
                    cpu_quota=50000,
                )

                execution_output = output_bytes.decode("utf-8").strip()
                if len(execution_output) > 4000:
                    execution_output = (
                        execution_output[:4000] + "\n\n... [Output truncated]"
                    )

                return {
                    "success": True,
                    "output": execution_output
                    or "Code executed successfully with no printed output.",
                    "error": None,
                }
            except ContainerError as ce:
                stderr_msg = (
                    ce.stderr.decode("utf-8") if isinstance(ce.stderr, bytes) else str(ce)
                )
                return {
                    "success": False,
                    "output": None,
                    "error": f"Execution Runtime Error:\n{stderr_msg}",
                }
            except DockerException as de:
                return {
                    "success": False,
                    "output": None,
                    "error": f"Docker Engine Error: {str(de)}",  # noqa: RUF010
                }
            except Exception as e:  # noqa: BLE001
                return {
                    "success": False,
                    "output": None,
                    "error": f"Unexpected Error: {str(e)}",  # noqa: RUF010
                }
