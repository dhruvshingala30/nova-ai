from typing import Any, Literal

from pydantic import BaseModel


class OutputFormat(BaseModel):
    STEP: Literal["START", "EXPLANATION", "TOOL", "ANSWER"]
    CONTENT: str
    TOOL: str | None = None
    INPUT: dict[str, Any] | None = None