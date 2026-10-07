"""
app/tools/code_interpreter.py - Pure In-Memory Execution Sandbox.
"""

import base64
import re
from pathlib import Path
from typing import Any

from app.config import E2B_API_KEY, USE_CLOUD_LLM
from app.core.session_store import session_store
from app.models import CodeInterpreterInput


class CodeInterpreter:
    @staticmethod
    def run_python_code(
        params: CodeInterpreterInput | None = None,
        code: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        if params is None:
            if code is None:
                return {
                    "success": False,
                    "output": None,
                    "error": "No Python code provided.",
                }
            params = CodeInterpreterInput(code=code)

        # -------------------------------------------------------------
        # SHARED: Detect requested filename from code (e.g. plt.savefig('sales_trend.png'))
        # -------------------------------------------------------------
        detected_chart_name = "chart.png"
        img_name_match = re.search(
            r"plt\.savefig\s*\(\s*['\"]([^'\"]+\.(?:png|jpg|jpeg|webp))['\"]",
            params.code,
            re.IGNORECASE,
        )
        if img_name_match:
            detected_chart_name = Path(img_name_match.group(1)).name

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
            f"{params.code}\n\n"
            "if 'result' in locals() and result is not None:\n"
            "    print(result)\n"
        )

        artifacts: list[dict[str, Any]] = []

        # -------------------------------------------------------------
        # CLOUD MODE: E2B Sandbox
        # -------------------------------------------------------------
        if USE_CLOUD_LLM and E2B_API_KEY:
            from e2b_code_interpreter import Sandbox

            try:
                with Sandbox.create(api_key=E2B_API_KEY) as sandbox:
                    # 1. Preload any session-uploaded CSVs into E2B memory
                    if session_id:
                        session_files = session_store.get_all_session_files(session_id)
                        for fname, fbytes in session_files.items():
                            sandbox.files.write(fname, fbytes)

                    # 2. Execute Code
                    execution = sandbox.run_code(code=wrapped_code, language="python")
                    output_text = "\n".join(
                        [str(line) for line in execution.logs.stdout]
                    )
                    error_text = (
                        "\n".join([str(err) for err in execution.logs.stderr])
                        if execution.error
                        else None
                    )

                    # 3. Capture plots using detected filename
                    for idx, res in enumerate(execution.results):
                        if res.png:
                            chart_name = (
                                detected_chart_name
                                if idx == 0
                                else f"{Path(detected_chart_name).stem}_{idx + 1}.png"
                            )
                            artifacts.append(
                                {
                                    "filename": chart_name,
                                    "mime_type": "image/png",
                                    "base64": res.png,
                                }
                            )
                            if session_id:
                                session_store.record_visual(
                                    session_id, chart_name, res.png
                                )

                    # 4. Check if code created/modified CSV or text files in sandbox
                    try:
                        for s_file in sandbox.files.list("."):
                            if s_file.name.lower().endswith(
                                (".csv", ".tsv", ".json", ".txt")
                            ):
                                content = sandbox.files.read(
                                    s_file.name, format="bytes"
                                )
                                b64_str = base64.b64encode(bytes(content)).decode(
                                    "utf-8"
                                )
                                artifacts.append(
                                    {
                                        "filename": s_file.name,
                                        "mime_type": "text/csv"
                                        if s_file.name.endswith(".csv")
                                        else "text/plain",
                                        "base64": b64_str,
                                    }
                                )
                                if session_id:
                                    session_store.save_file(
                                        session_id, s_file.name, bytes(content)
                                    )
                    except Exception as e:  # noqa: BLE001
                        print(f"⚠️ Artifact collection note: {e}")

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
        # LOCAL MODE: Secure Docker Container (In-Memory Base64 Capture)
        # -------------------------------------------------------------
        else:
            import json

            import docker
            from docker.errors import ContainerError, DockerException

            client = docker.from_env()
            client.ping()
            try:
                # Append in-container capture logic using detected_chart_name
                in_container_code = (
                    wrapped_code
                    + "\n"
                    + "import io, os, base64, json\n"
                    + "import matplotlib.pyplot as plt\n"
                    + "# Capture in-memory plot if generated\n"
                    + "if plt.get_fignums():\n"
                    + "    __buf = io.BytesIO()\n"
                    + "    plt.savefig(__buf, format='png', bbox_inches='tight')\n"
                    + "    __b64 = base64.b64encode(__buf.getvalue()).decode('utf-8')\n"
                    + f"    print(f'\\n__NOVA_IMAGE_BASE64__{detected_chart_name}::{{__b64}}__END_NOVA_IMAGE__')\n"
                    + "\n"
                    + "# Capture any generated data/text files (.csv, .tsv, .json, .txt)\n"
                    + "__allowed_exts = ('.csv', '.tsv', '.json', '.txt')\n"
                    + "__found_files = []\n"
                    + "for __fname in os.listdir('.'):\n"
                    + "    if __fname.lower().endswith(__allowed_exts) and os.path.isfile(__fname):\n"
                    + "        try:\n"
                    + "            with open(__fname, 'rb') as __f:\n"
                    + "                __f_bytes = __f.read()\n"
                    + "                if len(__f_bytes) > 0:\n"
                    + "                    __found_files.append({\n"
                    + "                        'filename': __fname,\n"
                    + "                        'mime_type': 'text/csv' if __fname.endswith('.csv') else ('application/json' if __fname.endswith('.json') else 'text/plain'),\n"
                    + "                        'base64': base64.b64encode(__f_bytes).decode('utf-8')\n"
                    + "                    })\n"
                    + "        except Exception:\n"
                    + "            pass\n"
                    + "if __found_files:\n"
                    + "    print(f'\\n__NOVA_FILES_PAYLOAD__{json.dumps(__found_files)}__END_NOVA_FILES__')\n"
                )

                output_bytes = client.containers.run(
                    image="nova-sandbox:latest",
                    command=["python", "-c", in_container_code],
                    detach=False,
                    remove=True,
                    network_disabled=True,
                    mem_limit="512m",
                    cpu_quota=50000,
                )

                execution_output = output_bytes.decode("utf-8").strip()
                artifacts: list[dict[str, Any]] = []

                # Extract generated image with dynamic filename
                img_match = re.search(
                    r"__NOVA_IMAGE_BASE64__(.*?)::(.*?)__END_NOVA_IMAGE__",
                    execution_output,
                    re.DOTALL,
                )
                if img_match:
                    chart_filename = img_match.group(1).strip()
                    b64_data = img_match.group(2).strip()
                    artifacts.append(
                        {
                            "filename": chart_filename,
                            "mime_type": "image/png",
                            "base64": b64_data,
                        }
                    )
                    if session_id:
                        session_store.record_visual(
                            session_id, chart_filename, b64_data
                        )

                    execution_output = re.sub(
                        r"__NOVA_IMAGE_BASE64__.*?__END_NOVA_IMAGE__",
                        "",
                        execution_output,
                        flags=re.DOTALL,
                    ).strip()

                # Extract generated data files (.csv, .tsv, .json, .txt)
                files_match = re.search(
                    r"__NOVA_FILES_PAYLOAD__(.*?)__END_NOVA_FILES__",
                    execution_output,
                    re.DOTALL,
                )
                if files_match:
                    try:
                        parsed_files = json.loads(files_match.group(1).strip())
                        for pf in parsed_files:
                            artifacts.append(pf)
                            if session_id:
                                raw_bytes = base64.b64decode(pf["base64"])
                                session_store.save_file(
                                    session_id, pf["filename"], raw_bytes
                                )
                    except Exception as parse_err:  # noqa: BLE001
                        print(
                            f"⚠️ [CodeInterpreter] Failed to parse generated files payload: {parse_err}"
                        )

                    execution_output = re.sub(
                        r"__NOVA_FILES_PAYLOAD__.*?__END_NOVA_FILES__",
                        "",
                        execution_output,
                        flags=re.DOTALL,
                    ).strip()

                if len(execution_output) > 4000:
                    execution_output = (
                        execution_output[:4000] + "\n\n... [Output truncated]"
                    )

                return {
                    "success": True,
                    "output": execution_output
                    or "Code executed successfully with no printed output.",
                    "error": None,
                    "artifacts": artifacts,
                }

            except ContainerError as ce:
                stderr_msg = (
                    ce.stderr.decode("utf-8")
                    if isinstance(ce.stderr, bytes)
                    else str(ce)
                )
                return {
                    "success": False,
                    "output": None,
                    "error": f"Execution Runtime Error:\n{stderr_msg}",
                    "artifacts": [],
                }
            except DockerException as de:
                return {
                    "success": False,
                    "output": None,
                    "error": f"Docker Engine Error: {str(de)}",  # noqa: RUF010
                    "artifacts": [],
                }
            except Exception as e:  # noqa: BLE001
                return {
                    "success": False,
                    "output": None,
                    "error": f"Unexpected Error: {str(e)}",  # noqa: RUF010
                    "artifacts": [],
                }
