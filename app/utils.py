"""
utils.py - Utility Functions & Logging Helpers.

Provides helper routines for printing formatted output steps, observations,
and application exit texts.
"""

import json

from app.config import END_TEXT, SEPARATOR, STEP_ICONS, WELCOME_TEXT


def welcome():
    print(WELCOME_TEXT)

def print_separator():
    """Prints a visual separator line in the terminal console."""
    print(SEPARATOR)


def goodbye():
    """Displays the shutdown goodbye message."""
    print(END_TEXT)


def create_observation(tool_name: str, tool_input: dict, tool_output: dict) -> str:
    """
    Serializes tool execution results into a JSON observation string
    formatted for the LLM context.

    Args:
        tool_name (str): The name of the tool executed.
        tool_input (dict): The inputs supplied to the tool.
        tool_output (dict): The output dictionary returned by the tool execution.

    Returns:
        str: JSON-encoded observation string.
    """
    return json.dumps(
        {
            "STEP": "OBSERVE",
            "tool": tool_name,
            "INPUT": tool_input,
            "OUTPUT": tool_output,
        }
    )


def print_step(step: str, content: str, tool: str | None):
    """
    Prints a formatted, emoji-iconized execution step to the terminal.

    Args:
        step (str): The current protocol step type (e.g. "START", "TOOL").
        content (str): Explanation text or description.
        tool (str | None): The name of the tool being called (if applicable).
    """
    if step == "TOOL":
        icon = STEP_ICONS.get(step, "🛠️")
        print(f"{icon} : {tool} : {content}")
    else:
        icon = STEP_ICONS.get(step, "❓")
        print(f"{icon} : {content}")
