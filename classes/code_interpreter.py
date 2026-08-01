import contextlib
import io
import math
import traceback

import sympy


class CodeInterpreter:
    @staticmethod
    def run_python_code(code: str) -> dict:
        stdout_buffer = io.StringIO()

        safe_globals = {
            "__builtins__": {
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "len": len,
                "range": range,
                "list": list,
                "dict": dict,
                "float": float,
                "int": int,
                "str": str,
                "print": print,
                "isinstance": isinstance,
                "enumerate": enumerate,
                "zip": zip,
            },
            "math": math,
            "sympy": sympy,
        }
        safe_locals = {}

        try:
            with contextlib.redirect_stdout(stdout_buffer):
                exec(code, safe_globals, safe_locals)  # noqa: S102

            output = stdout_buffer.getvalue().strip()
            result_val = safe_locals.get("result", None)

            return {
                "success": True,
                "output": output,
                "result_variable": str(result_val) if result_val is not None else None,
            }

        except Exception as e:  # noqa: BLE001
            error_msg = traceback.format_exc()
            return {"success": False, "error": str(e), "traceback": error_msg}
