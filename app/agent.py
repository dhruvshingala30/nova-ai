"""
agent.py - NovaAI ReAct Agent Engine Core.

Implements the central reasoning agent that communicates with Ollama, manages
chat history, formats system prompts dynamically, and orchestrates tool execution.
"""

from datetime import datetime

from ollama import Client
from pydantic import ValidationError

from app import prompts
from app.config import MAX_HISTORY, MODEL_NAME, OLLAMA_HOST, STEP_ICONS
from app.models import OutputFormat
from app.tools import AVAILABLE_TOOLS
from app.utils import create_observation, print_step


class NovaAI:
    """
    Autonomous ReAct AI Agent powered by local LLMs via Ollama.

    Attributes:
        client (Client): Ollama API client instance.
        model (str): Name of the active LLM model.
        system_prompt (str): Full formatted system prompt containing tool schemas and date context.
        message_history (list[dict]): Maintained context history of turn-by-turn messages.
    """

    def __init__(self) -> None:
        """Initializes Ollama client, builds system prompt with real-time date context, and prepares history."""
        self.client = Client(host=OLLAMA_HOST)
        self.model = MODEL_NAME

        # Inject dynamic date context into system prompt
        current_date = datetime.now().strftime("%A, %B %d, %Y")  # noqa: DTZ005
        date_context = f"\n CURRENT DATE AND TIME: TODAY is {current_date}.\n"

        # Build prompt with tools rendered into template
        self.system_prompt = date_context + prompts.SYSTEM_PROMPT.replace(
            "{{AVAILABLE_TOOLS}}", self._generate_tools_prompt()
        )

        # System message initialization
        self.message_history = [{"role": "system", "content": self.system_prompt}]

    def _generate_tools_prompt(self) -> str:
        """
        Dynamically formats registered tool specifications into text
        descriptions for injection into {{AVAILABLE_TOOLS}}.

        Returns:
            str: Formatted string list of tools and parameter descriptions.
        """
        lines = []
        for index, (name, tool) in enumerate(AVAILABLE_TOOLS.items()):
            parameter_list = [
                f"{param}: {dtype}" for param, dtype in tool["parameters"].items()
            ]
            params = ", ".join(parameter_list)
            prefix = "" if index == 0 else "\t\t"
            lines.append(
                f"{prefix}- {name}({params})\n\t\tDescription: {tool['description']}"
            )
        return "\n\n".join(lines)

    def add_message(self, role: str, content: str):
        """
        Appends a message to message_history and applies truncation if max context length is exceeded.

        Args:
            role (str): Message sender role ('user', 'assistant', or 'system').
            content (str): Raw message string content.
        """
        self.message_history.append({"role": role, "content": content})

        # Enforce history limit while retaining the root system prompt
        if len(self.message_history) > MAX_HISTORY + 1:
            self.message_history = [
                self.message_history[0],
                *self.message_history[-MAX_HISTORY:],
            ]

    def chat(self) -> OutputFormat:
        """
        Sends message history to Ollama, enforcing structured JSON output validation matching OutputFormat.

        Returns:
            OutputFormat: Parsed and validated Pydantic model response.
        """
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

    def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """
        Looks up registered tool, validates inputs against Pydantic schema, and executes handler function.

        Args:
            tool_name (str): Identifier of tool to execute.
            tool_input (dict): Parameter arguments provided by the LLM.

        Returns:
            dict: Execution results or error response dictionary.
        """
        tool = AVAILABLE_TOOLS.get(tool_name)

        # Handle unregistered tool calls gracefully
        if tool is None:
            valid_tools = list(AVAILABLE_TOOLS.keys())
            return {
                "success": False,
                "error": f"Tool '{tool_name}' does not exist. Available tools are {valid_tools}. Use 'search_web' for search/schedule queries.",
            }

        if not isinstance(tool_input, dict):
            raise TypeError(f"Tool input for '{tool_name}' must be a JSON object")

        # -------------------------------------------------------------
        # Pydantic Schema Input Validation
        # -------------------------------------------------------------
        schema = tool.get("schema")
        if schema:
            try:
                validated_input = schema.model_validate(tool_input)
                tool_input = validated_input.model_dump()
            except ValidationError as e:
                return {
                    "success": False,
                    "error": f"Invalid arguments provided for tool '{tool_name}'.",
                    "details": e.errors(),
                }

        # Execute registered tool handler
        function = tool["function"]
        return function(**tool_input)

    def observe(self, tool_name: str, tool_input: dict, tool_output: dict):
        """Passes tool execution output back into chat history as an observation message."""
        self.add_message(
            role="user",
            content=create_observation(tool_name, tool_input, tool_output),
        )

    def run(self, user_query: str):
        """
        Executes the main ReAct loop for a given user query until an 'ANSWER' step is reached.

        Args:
            user_query (str): Input prompt entered by the user.
        """
        self.add_message(role="user", content=user_query)

        while True:
            parsed_result = self.chat()

            # Process Tool Execution Request
            if parsed_result.STEP == "TOOL":
                tool_name = parsed_result.TOOL
                tool_input = parsed_result.INPUT

                # Catch empty/invalid tool parameters generated by model
                if not tool_name or tool_input is None:
                    self.observe(
                        tool_name="system",
                        tool_input={},
                        tool_output={
                            "success": False,
                            "error": "A TOOL step must specify a valid TOOL and input dictionary from AVAILABLE_TOOLS. "
                            "If no further tool execution is required, proceed to the ANSWER step.",
                        },
                    )
                    continue

                tool_output = self.execute_tool(tool_name, tool_input)
                self.observe(tool_name, tool_input, tool_output)
                print_step(
                    parsed_result.STEP, parsed_result.CONTENT, parsed_result.TOOL
                )

            # Process Intermediate Reasoning Steps or Final Answer
            elif parsed_result.STEP in STEP_ICONS:
                print_step(parsed_result.STEP, parsed_result.CONTENT or "", None)
                if parsed_result.STEP == "ANSWER":
                    break
            else:
                print(f"Unknown step: {parsed_result.STEP}")
                break
