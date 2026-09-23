"""
app/agents/base_agent.py - Base Class for Domain-Specific Specialist Agents.

Provides bounded ReAct loop reasoning and scoped tool execution for specialized worker agents.
"""

import re
from pathlib import Path
from typing import Any

from ollama import Client
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.config import MODEL_NAME, OLLAMA_HOST
from app.models import OutputFormat, TaskResult
from app.single_agent import NovaAI
from app.utils import create_observation, print_step


class BaseSpecialistAgent:
    """
    Abstract base class providing LLM reasoning and scoped tool execution for specialist agents.
    """

    def __init__(
        self,
        name: str,
        role_description: str,
        system_instructions: str,
        scoped_tools: dict[str, Any],
        model: str = MODEL_NAME,
        max_turns: int = 5,
    ) -> None:
        """
        Args:
            name: Agent identifier (e.g., 'ResearchAgent').
            role_description: Short capability statement used by the Supervisor.
            system_instructions: Domain-specific prompt constraints and guidelines.
            scoped_tools: Subset of tools this specific specialist is allowed to execute.
            model: Ollama model name to use for reasoning.
            max_turns: Maximum internal ReAct iterations before forcing a conclusion.
        """
        self.name = name
        self.role_description = role_description
        self.system_instructions = system_instructions
        self.scoped_tools = scoped_tools
        self.model = model
        self.max_turns = max_turns
        self.client = Client(host=OLLAMA_HOST)
        self.nova = NovaAI()

    def _generate_tools_prompt(self) -> str:
        """Formats only the scoped tools available to this specialist."""
        if not self.scoped_tools:
            return "No external tools assigned. Rely strictly on text analysis."

        lines = []
        for name, tool in self.scoped_tools.items():
            param_list = [f"{p}: {dtype}" for p, dtype in tool["parameters"].items()]
            params_str = ", ".join(param_list)
            lines.append(
                f"- {name}({params_str})\n\tDescription: {tool['description']}"
            )
        return "\n\n".join(lines)

    def _build_system_prompt(self) -> str:
        """Constructs the specialist's strict system prompt."""
        tools_text = self._generate_tools_prompt()
        return f"""You are {self.name}, a specialized worker agent within NovaAI.
ROLE: {self.role_description}

SPECIFIC INSTRUCTIONS:
{self.system_instructions}

==========================================================
AVAILABLE SCOPED TOOLS:
{tools_text}

CLOSED-WORLD RULE: You are ONLY allowed to use the tools listed above.
==========================================================
JSON RESPONSE PROTOCOL:
You MUST respond with exactly ONE valid JSON object matching this schema:
{{
  "STEP": "TOOL" | "ANSWER" | "REFLECT" | "EXPLANATION",
  "CONTENT": "<reasoning or final summary of findings>",
  "TOOL": "<tool_name>" | null,
  "INPUT": {{ <arguments> }} | null
}}
When you have collected the required information, output `STEP: ANSWER` with a comprehensive summary in `CONTENT`.
"""

    def _clean_json(self, raw: str) -> str:
        """Strips Markdown wrappers from LLM outputs."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()


    def execute_tool(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Validates and runs an assigned tool from the scoped inventory."""
        tool = self.scoped_tools.get(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' is not in {self.name}'s scoped toolset. Valid: {list(self.scoped_tools.keys())}",
            }

        schema = tool.get("schema")
        if schema and isinstance(tool_input, dict):
            try:
                validated = schema.model_validate(tool_input)
                tool_input = validated.model_dump()
            except ValidationError as e:
                return {
                    "success": False,
                    "error": f"Invalid arguments for tool '{tool_name}': {e.errors()}",
                }

        # Invoke the underlying python tool function
        handler = tool["function"]
        return handler(**tool_input)

    def work_on_task(
        self,
        task_id: int,
        instruction: str,
        context_findings: str,
    ) -> TaskResult:
        """
        Executes an assigned subtask using an internal bounded ReAct loop.

        Args:
            task_id: Numeric task ID from the supervisor.
            instruction: Clear instructions for what needs to be accomplished.
            context_findings: Text containing findings from preceding tasks.

        Returns:
            TaskResult: Formatted outcome to send back to the supervisor.
        """
        system_prompt = self._build_system_prompt()
        user_message = (
            f"Assigned Subtask #{task_id}:\n"
            f"Instruction: {instruction}\n\n"
            f"Context from preceding tasks (if relevant):\n{context_findings}\n\n"
            "Please begin reasoning and invoke tools if necessary to complete this task."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        turns = 0
        detected_artifacts: list[str] = []

        while turns < self.max_turns:
            turns += 1

            # Query the local LLM
            response = self.client.chat(
                model=self.model,
                format=OutputFormat.model_json_schema(),
                messages=messages,
                options={"temperature": 0.0},
            )

            raw_content = response.message.content or "{}"
            cleaned = self._clean_json(raw_content)
            messages.append({"role": "assistant", "content": cleaned})

            try:
                parsed = OutputFormat.model_validate_json(cleaned)
            except ValidationError:
                parsed = OutputFormat(
                    STEP="ANSWER",
                    CONTENT=cleaned,
                    TOOL=None,
                    INPUT=None,
                )

            # ---------------------------------------------------------
            # 2. REFLECTION & SELF-CORRECTION STEP
            # ---------------------------------------------------------
            if parsed.STEP == "REFLECT":
                print_step(
                    step="REFLECT",
                    content=parsed.CONTENT or "Analysing execution error...",
                    tool=None,
                )

                messages.append(
                    {
                        "role": "user",
                        "content": "[REFLECTION ACKNOWLEDGED]: Now summarize the error and either correct the tool invocation or provide a final answer.",
                    }
                )
                continue

            # -------------------------------------------------------------
            # Handle Tool Execution Turn
            # -------------------------------------------------------------
            if parsed.STEP == "TOOL" and parsed.TOOL:
                print_step(
                    step="TOOL",
                    content=f"[{self.name}] {parsed.CONTENT or ''}",
                    tool=parsed.TOOL,
                )

                tool_input = parsed.INPUT or {}
                # Scan for generated image or CSV artifacts (e.g. 'chart.png')
                if "code" in tool_input:
                    matches = re.findall(
                        r"['\"]([\w\-_]+\.(?:png|jpg|csv|json))['\"]",
                        tool_input["code"],
                    )
                    for match in matches:
                        if match not in detected_artifacts:
                            detected_artifacts.append(match)

                # ---------------------------------------------------------
                # DYNAMIC HITL SAFEGUARD
                # ---------------------------------------------------------
                requires_approval, reason = self.nova.assess_hitl_risk(
                    parsed.TOOL, tool_input
                )

                if requires_approval:
                    print("\n ⚠️  [HITL SAFEGUARD - HUMAN APPROVAL REQUIRED]")
                    print(f"   Reason: {reason}")
                    print(f"   Tool: {parsed.TOOL}")
                    if "code" in tool_input:
                        print("   --- Code Preview ---")
                        for line in tool_input["code"].strip().split("\n"):
                            print(f"   | {line}")
                        print("   --------------------")

                    approval = (
                        input("👉 Approve this workspace modification? (y/n): ")
                        .strip()
                        .lower()
                    )

                    if approval not in ["y", "yes"]:
                        print("🚫 Action denied by human operator.")
                        guidance = (
                            "\n\n[SYSTEM ALERT - TOOL EXECUTION FAILED]: The tool execution encountered an error. "
                            "Analyze the error message/traceback above. Your NEXT turn MUST be `STEP: REFLECT` diagnosing "
                            "the root cause, followed either by a corrected `STEP: TOOL` action OR `STEP: ANSWER` if the operation is forbidden or impossible. "
                            "Do NOT repeat the exact same failing command."
                        )
                        obs_str = create_observation(
                            parsed.TOOL,
                            tool_input,
                            {
                                "success": False,
                                "error": "HITL safeguard denied execution.",
                            },
                        )
                        messages.append(
                            {
                                "role": "user",
                                "content": guidance + "\n\n" + obs_str,
                            }
                        )
                        continue
                # ---------------------------------------------------------

                tool_output = self.execute_tool(parsed.TOOL, tool_input)
                obs_str = create_observation(parsed.TOOL, tool_input, tool_output)

                messages.append(
                    {
                        "role": "user",
                        "content": obs_str
                        + "\n\n[SYSTEM]: Review the result. If complete, output STEP: ANSWER.",
                    }
                )
                continue

            # -------------------------------------------------------------
            # Handle Final Answer Step
            # -------------------------------------------------------------
            elif parsed.STEP == "ANSWER":
                print_step(
                    step="EXPLANATION",
                    content=f"[{self.name} Completed Task #{task_id}] {parsed.CONTENT}",
                    tool=None,
                )
                return TaskResult(
                    task_id=task_id,
                    assigned_agent=self.name,
                    status="SUCCESS",
                    summary=parsed.CONTENT,
                    artifacts=detected_artifacts,
                )

            # Handle Reflect / Explanation
            else:
                messages.append(
                    {
                        "role": "user",
                        "content": "[SYSTEM]: Proceed to execute required tool or provide STEP: ANSWER.",
                    }
                )

        # Fallback if loop exceeded max_turns
        return TaskResult(
            task_id=task_id,
            assigned_agent=self.name,
            status="SUCCESS",
            summary=f"{self.name} completed bounded turns. Latest findings: {messages[-1]['content']}",
            artifacts=detected_artifacts,
        )
