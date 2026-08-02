import contextlib
import io
import math
import traceback

import numpy as np
import sympy

# List of modules that are strictly forbidden from being imported
BLOCKED_MODULES = {
    "os",
    "sys",
    "subprocess",
    "shutil",
    "pathlib",
    "builtins",
    "socket",
    "requests",
}


def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Custom import hook to block system and file access modules."""
    root_module = name.split(".")[0]
    if root_module in BLOCKED_MODULES:
        raise ImportError(
            f"Importing '{root_module}' is restricted for security reasons."
        )
    return __import__(name, globals, locals, fromlist, level)


class CodeInterpreter:
    @staticmethod
    def run_python_code(code: str) -> dict:
        """Executes Python code in a safe execution environment pre-loaded with

        math and sympy functions.
        """
        stdout_buffer = io.StringIO()

        # 1. Inject commonly used math/sympy functions directly into builtins/globals
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
                "__import__": safe_import,
            },
            # Libraries
            "math": math,
            "sympy": sympy,
            "sp": sympy,
            "numpy": np,
            "np": np,

            # Common math functions directly accessible without prefix
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,

            # SymPy shortcuts
            "Symbol": sympy.Symbol,
            "Symbols": sympy.symbols,
            "Eq": sympy.Eq,
            "solve": sympy.solve,
            "diff": sympy.diff,
            "integrate": sympy.integrate,
            "limit": sympy.limit,
            "Matrix": sympy.Matrix,
            "factor": sympy.factor,
        }
        safe_locals = {}

        try:
            with contextlib.redirect_stdout(stdout_buffer):
                exec(code, safe_globals, safe_locals)  # noqa: S102

            output = stdout_buffer.getvalue().strip()
            result_val = safe_locals.get("result", None)

            # If no print statement was run, but result variable exists, use result_val
            if not output and result_val is not None:
                output = str(result_val)

            return {
                "success": True,
                "output": output,
                "result_variable": (
                    str(result_val) if result_val is not None else None
                ),
            }

        except Exception as e:  # noqa: BLE001
            error_msg = traceback.format_exc()
            # Printing error locally helps you debug in terminal
            print(f"\n[CodeInterpreter Exec Error]: {e}\n")
            return {"success": False, "error": str(e), "traceback": error_msg}
