import json

from app.config import END_TEXT, SEPARATOR, STEP_ICONS


def print_separator():
    print(SEPARATOR)

def goodbye():
    print(END_TEXT)

def create_observation(tool_name, tool_input, tool_output):
    return json.dumps(
        {
            "STEP": "OBSERVE",
            "tool": tool_name,
            "INPUT": tool_input,
            "OUTPUT": tool_output,
        }
    )

def print_step(step: str, content: str, tool: str | None):
    if step == "TOOL":
        icon = STEP_ICONS.get(step, "•")
        print(f"{icon} : {tool} : {content}")

    else:
        icon = STEP_ICONS.get(step, "•")
        print(f"{icon} : {content}")
