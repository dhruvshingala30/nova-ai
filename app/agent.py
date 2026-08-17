"""
agent.py - NovaAI ReAct Agent Engine Core.
Implements the central reasoning agent, manages Ollama communication,
sanitizes history, and orchestrates tool execution.
"""

import re
from datetime import datetime

from config import MAX_HISTORY, MODEL_NAME, OLLAMA_HOST, STEP_ICONS
from core.memory import SQLiteMemory
from models import OutputFormat
from ollama import Client
from prompts import SYSTEM_PROMPT
from pydantic import ValidationError
from tools import AVAILABLE_TOOLS
from tools.knowledge_base_search import get_indexed_documents
from utils import create_observation, print_step


class NovaAI:
    """Autonomous ReAct AI Agent powered by local LLMs via Ollama."""

    def __init__(self, session_id: str | None = None) -> None:
        self.client = Client(host=OLLAMA_HOST)
        self.model = MODEL_NAME
        self.memory = SQLiteMemory()
        self.session_id = session_id

        self.message_history: list[dict]= []
        self._refresh_system_prompt()

        if session_id:
            saved_history = self.memory.get_session_history(
                self.session_id, limit=MAX_HISTORY # type: ignore
            )
            self.message_history.extend(saved_history)

    def _refresh_system_prompt(self):
        """
        Constructs system prompt with live tools and dynamic knowledge base catalog.
        """
        current_date = datetime.now().strftime("%A, %B %d, %Y")  # noqa: DTZ005
        date_context = f"\nCURRENT SYSTEM DATE AND TIME: TODAY is {current_date}.\n"

        # Dynamically discover indexed documents
        indexed_docs = get_indexed_documents()
        if indexed_docs:
            docs_list_str = "\n".join([f"  - {doc}" for doc in indexed_docs])
            kb_catalog = f"\nCURRENTLY INDEXED KNOWLEDGE BASE DOCUMENTS:\n{docs_list_str}\n"

        else:
            kb_catalog = "\nCURRENTLY INDEXED KNOWLEDGE BASE DOCUMENTS: None currently indexed.\n"

        full_prompt = (
            date_context
            + kb_catalog
            + SYSTEM_PROMPT.replace("{{AVAILABLE_TOOLS}}", self._generate_tools_prompt())
        )

        if not self.message_history:
            self.message_history.append(
                {
                    "role": "system",
                    "content": full_prompt
                }
            )

        else:
            self.message_history[0] = {
                "role": "system",
                "content": full_prompt
            }

    def _generate_tools_prompt(self) -> str:
        """Formats registered tools into structured text for system prompt injection."""
        lines = []
        for index, (name, tool) in enumerate(AVAILABLE_TOOLS.items()):
            param_list = [f"{p}: {dtype}" for p, dtype in tool["parameters"].items()]
            params_str = ", ".join(param_list)
            prefix = "" if index == 0 else "\t\t"
            lines.append(
                f"{prefix}- {name}({params_str})\n\t\tDescription: {tool['description']}"
            )
        return "\n\n".join(lines)

    def add_message(self, role: str, content: str, save_to_db: bool = True):
        """Appends a message to context history and persists to SQLite."""
        self.message_history.append({"role": role, "content": content})

        if save_to_db and role != "system" and self.session_id:
            self.memory.save_message(
                session_id=self.session_id,
                role=role,
                content=content,
            )

        # Retain root system prompt while capping memory window
        if len(self.message_history) > MAX_HISTORY + 1:
            self.message_history = [
                self.message_history[0],
                *self.message_history[-MAX_HISTORY:],
            ]

    def _clean_json_output(self, raw_content: str) -> str:
        """Strips Markdown code block wrappers from LLM response strings if present."""
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def chat(self) -> OutputFormat:
        """Sends sanitized context history to Ollama and parses structured JSON output."""
        self._refresh_system_prompt()

        response = self.client.chat(
            model=self.model,
            format=OutputFormat.model_json_schema(),
            messages=self.message_history,
            options={"temperature": 0.0},
        )

        raw_result = response.message.content or "{}"
        cleaned_result = self._clean_json_output(raw_result)

        self.add_message("assistant", cleaned_result)

        try:
            return OutputFormat.model_validate_json(cleaned_result)
        except ValidationError:
            print(f"[RAW LLM UNPARSED OUTPUT]: {raw_result}")
            raise


    def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """Validates tool parameters against Pydantic schema and executes handler."""
        tool = AVAILABLE_TOOLS.get(tool_name)
        if tool is None:
            valid_tools = list(AVAILABLE_TOOLS.keys())
            return {
                "success": False,
                "error": f"Tool '{tool_name}' does not exist. Valid tools: {valid_tools}.",
            }

        if not isinstance(tool_input, dict):
            return {
                "success": False,
                "error": f"Input for '{tool_name}' must be a JSON object.",
            }

        schema = tool.get("schema")
        if schema:
            try:
                validated_input = schema.model_validate(tool_input)
                tool_input = validated_input.model_dump()
            except ValidationError as e:
                return {
                    "success": False,
                    "error": f"Invalid arguments for tool '{tool_name}'.",
                    "details": e.errors(),
                }

        function = tool["function"]
        tool_output =  function(**tool_input)

        # -------------------------------------------------------------------------
        # INTERCEPT RESTRICTED ERRORS & INJECT SYSTEM GUIDANCE
        # -------------------------------------------------------------------------
        if (
            isinstance(tool_output, dict)
            and not tool_output.get("success")
            and "restricted for security reasons" in str(tool_output.get("error"))
        ):
            tool_output["system_guidance"] = (
                "CRITICAL: Code execution is sandboxed and cannot access external networks. "
                "Select a registered data retrieval tool instead."
            )
        return tool_output

    def observe(self, tool_name: str, tool_input: dict, tool_output: dict):
        """Passes formatted observation payload with an unfulfilled subtask check back to chat history."""
        observation_json = create_observation(tool_name, tool_input, tool_output)

        # Inject an unfulfilled subtask check inside the observation prompt
        subtask_reminder = (
            "\n\n[SYSTEM CHECK]: Review the user's query. If the observation above provides "
            "all the information requested by the user, your NEXT step MUST be `STEP: ANSWER`. "
            "Do NOT trigger additional tools unless explicitly requested by the prompt."
        )

        self.add_message(
            role="user",
            content=observation_json + subtask_reminder,
        )

    def run(self, user_query: str):
        """Main ReAct execution loop handling multi-step reasoning and subtasks."""
        if self.session_id is None:
            self.session_id = self.memory.generate_title_from_prompt(
                client=self.client,
                model_name=self.model,
                prompt=user_query,
            )
            print(f"📝 New Session Title Generated: '{self.session_id}'")

        self.add_message(role="user", content=user_query)

        while True:
            parsed_result = self.chat()

            if parsed_result.STEP == "TOOL":
                tool_name = parsed_result.TOOL
                tool_input = parsed_result.INPUT

                if not tool_name or tool_input is None:
                    self.observe(
                        tool_name="system",
                        tool_input={},
                        tool_output={
                            "success": False,
                            "error": "STEP 'TOOL' requires a valid 'TOOL' and 'INPUT' object.",
                        },
                    )
                    continue

                print_step(
                    parsed_result.STEP, 
                    parsed_result.CONTENT or "", 
                    parsed_result.TOOL
                )
                
                tool_output = self.execute_tool(tool_name, tool_input)

                # PRINT INSTANT DEBUG LOG IF TOOL EXECUTION FAILS
                if isinstance(tool_output, dict) and tool_output.get("success") is False:
                    print(f"❌ [TOOL EXECUTION ERROR]: {tool_output.get('error')}")

                self.observe(tool_name, tool_input, tool_output)


            elif parsed_result.STEP in STEP_ICONS:
                print_step(parsed_result.STEP, parsed_result.CONTENT or "", None)

                if parsed_result.STEP == "ANSWER":
                    break

            else:
                print(f"Unknown execution step: {parsed_result.STEP}")
                break
