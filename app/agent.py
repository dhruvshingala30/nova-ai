from ollama import Client

from app import prompts
from app.config import MAX_HISTORY, MODEL_NAME, STEP_ICONS
from app.models import OutputFormat
from app.tools import AVAILABLE_TOOLS
from app.utils import create_observation, print_step
from classes.calculator import Calculator

NORMALIZERS = {
    "basic_calculator": Calculator.normalize_calculator, 
}


class NovaAI:
    def __init__(self) -> None:
        self.client = Client()
        self.model = MODEL_NAME

        self.system_prompt = prompts.SYSTEM_PROMPT.replace(
                    "{{AVAILABLE_TOOLS}}", 
                    self._generate_tools_prompt()
                )
        
        self.message_history = [
            {"role": "system", "content": self.system_prompt}
        ]


    def _generate_tools_prompt(self):
        lines = []

        for index, (name, tool) in enumerate(AVAILABLE_TOOLS.items()):
            parameter_list = []

            for parameter, data_type in tool["parameters"].items():
                parameter_list.append(f"{parameter}: {data_type}")

            params = ", ".join(parameter_list)

            prefix = "" if index == 0 else "\t\t"
            lines.append(f"{prefix}- {name}({params})\n  \t\tDescription: {tool['description']}")

        return "\n\n".join(lines)


    def add_message(self, role: str, content: str):
        self.message_history.append(
            {
                "role": role,
                "content": content
            }
        )

        if len(self.message_history) > MAX_HISTORY + 1:
             self.message_history = [
                  self.message_history[0], 
                  *self.message_history[-MAX_HISTORY:], 
             ]


    def chat(self):
        response = self.client.chat(
            model=self.model,
            format=OutputFormat.model_json_schema(),
            messages=self.message_history,
        )

        raw_result = response.message.content or "[]"
        self.add_message("assistant", raw_result)

        try:
            return OutputFormat.model_validate_json(raw_result)

        except Exception:
            print(raw_result)
            raise


    def execute_tool(self, tool_name, tool_input):
        tool = AVAILABLE_TOOLS.get(tool_name)

        if tool is None:
            raise ValueError(f"Unknown tool requested: {tool_name}")

        if not isinstance(tool_input, dict):
            raise TypeError(f"Tool input for '{tool_name}' must be a JSON object")

        normalizer = NORMALIZERS.get(tool_name)
        if normalizer:
            tool_input = normalizer(tool_input)

        function = tool["function"]
        return function(**tool_input)


    def observe(self, tool_name, tool_input, tool_output):
        self.add_message(
            role="user",
            content=create_observation(
                    tool_name,
                    tool_input,
                    tool_output
                ),
        )


    def run(self, user_query):
        self.add_message(
        role="user",
        content=user_query
        )

        while True:
            parsed_result = self.chat()

            if parsed_result.STEP == "TOOL":
                tool_name = parsed_result.TOOL
                tool_input = parsed_result.INPUT

                if not tool_name or tool_input is None:
                    raise ValueError("A TOOL step must include TOOL and INPUT values")

                tool_output = self.execute_tool(
                    tool_name, 
                    tool_input
                )

                self.observe(
                    tool_name, 
                    tool_input, 
                    tool_output
                )

                print_step(
                    parsed_result.STEP,
                    parsed_result.CONTENT,
                    parsed_result.TOOL,
                )
            
            elif parsed_result.STEP in STEP_ICONS:
                print_step(
                    parsed_result.STEP,
                    parsed_result.CONTENT or "", 
                    None
                )

                if parsed_result.STEP == "ANSWER":
                    break

            else:
                print(f"Unknown step: {parsed_result.STEP}")
                break
