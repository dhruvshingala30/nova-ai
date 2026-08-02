from typing import Any, Literal

from pydantic import BaseModel, Field


class OutputFormat(BaseModel):
    STEP: Literal["START", "EXPLANATION", "TOOL", "ANSWER"]
    CONTENT: str
    TOOL: str | None = None
    INPUT: dict[str, Any] | None = None


class PythonCodeInterpreter(BaseModel):
    code: str = Field(
        description="Valid Python code to execute. Write code for math calculations, symbolic math, or data processing. "
        "Assign the answer to a variable named `result` or use `print()`."
    )