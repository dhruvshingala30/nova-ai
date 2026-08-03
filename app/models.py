"""
models.py - Agent Output Data Contracts & Schemas.

Defines the Pydantic data structure used for strict JSON response parsing
from the local LLM.
"""

from typing import Any, Literal

from pydantic import BaseModel


class OutputFormat(BaseModel):
    """
    Data contract enforcing the ReAct protocol step structure expected
    from the LLM's JSON response.

    Attributes:
        STEP (Literal): Current execution phase ("START", "EXPLANATION", "TOOL", or "ANSWER").
        CONTENT (str): Human-readable explanation or summary of the current step.
        TOOL (str | None): Name of the tool to invoke (only populated when STEP == "TOOL").
        INPUT (dict[str, Any] | None): Dictionary of arguments to pass to the tool function.
    """

    STEP: Literal["START", "EXPLANATION", "TOOL", "ANSWER"]
    CONTENT: str
    TOOL: str | None = None
    INPUT: dict[str, Any] | None = None
