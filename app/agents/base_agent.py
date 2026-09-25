"""
app/agents/base_agent.py - Base Class for Domain-Specific Specialist Agents.

Provides bounded ReAct loop reasoning and scoped tool execution for specialized worker agents.
"""

import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from ollama import Client
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.config import MODEL_NAME, OLLAMA_HOST
from app.core.event import NovaEvent
from app.models import OutputFormat, TaskResult
from app.prompts import SPECIALIST_PROMPT
from app.single_agent import NovaAI
from app.tools.knowledge_base_search import get_indexed_documents
from app.utils import create_observation


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
        event_handler: Callable[[NovaEvent], None] | None = None,
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
        self.event_handler = event_handler

        self.client = Client(host=OLLAMA_HOST)
        self.nova = NovaAI()

    def _emit(self, event: NovaEvent):
        """Emits an event to the registered event handler."""
        if self.event_handler:
            self.event_handler(event)

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

    def _get_indexed_document_context(self):
        """
        Dynamically formats indexed documents if this specialist is equipped
        with knowledge base retrieval tools.
        """
        if "search_knowledge_base" not in self.scoped_tools:
            return ""

        try:
            docs = get_indexed_documents()
        except Exception:  # noqa: BLE001
            docs = []

        if docs:
            doc_list = "\n".join(f"- {d}" for d in docs)
            return (
                "=========================================================="
                "\nINDEXED KNOWLEDGE BASED DOCUMENTS:\n"
                "=========================================================="
                f"\n{doc_list}\n"
                "- When answering questions regarding indexed literature, market concepts, "
                "or domain facts, prioritize searching these specific documents.\n"
            )
        return "\nINDEXED KNOWLEDGE BASE DOCUMENTS: (No documents currently indexed)\n"

    def _build_system_prompt(self) -> str:
        """Constructs the specialist's strict system prompt using SPECIALIST_PROMPT."""
        tools_text = self._generate_tools_prompt()
        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M:%S %p")  # noqa: DTZ005
        docs_context = self._get_indexed_document_context()

        return SPECIALIST_PROMPT.format(
            name=self.name,
            current_date_time=current_time,
            role_description=self.role_description,
            indexed_documents_context=docs_context,
            system_instructions=self.system_instructions.strip(),
            available_tools=tools_text,
        )

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
        hitl_denied = False

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
                self._emit(
                    event=NovaEvent(
                        event_type="reflection",
                        content=parsed.CONTENT or "Analysing execution error...",
                        data={
                            "agent": self.name,
                            "turn": turns,
                        }
                    )
                )
                # print_step(
                #     step="REFLECT",
                #     content=parsed.CONTENT or "Analysing execution error...",
                #     tool=None,
                # )

                messages.append(
                    {
                        "role": "user",
                        "content": "[REFLECTION ACKNOWLEDGED]: If the operation was blocked or denied by the user, immediately output STEP: ANSWER summarizing what was completed. Otherwise, summarize the error and execute a corrected tool.",
                    }
                )
                continue

            # -------------------------------------------------------------
            # Handle Tool Execution Turn
            # -------------------------------------------------------------
            if parsed.STEP == "TOOL" and parsed.TOOL:
                self._emit(
                    event=NovaEvent(
                        event_type="tool_invocation",
                        content=parsed.CONTENT or "",
                        data={
                            "agent": self.name,
                            "tool": parsed.TOOL,
                            "input": parsed.INPUT,
                        },
                    )
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
                    self._emit(
                        event=NovaEvent(
                            event_type="approval_required",
                            content="Human approval required for workspace modification.",
                            data={
                                "agent": self.name,
                                "task_id": task_id,
                                "tool": parsed.TOOL,
                                "input": parsed.INPUT,
                                "reason": reason,
                            }
                        )
                    )
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

                    if approval in ["y", "yes"]:
                        self._emit(
                            event=NovaEvent(
                                event_type="approval_granted",
                                content="Human approval granted. Continue tool execution.",
                                data={
                                    "agent": self.name,
                                    "task_id": task_id,
                                    "tool": parsed.TOOL,
                                    "input": parsed.INPUT,
                                    "decision": "approved",
                                },
                            )
                        )

                    else:
                        self._emit(
                            event=NovaEvent(
                                event_type="approval_denied",
                                content="Human approval denied. Tool execution blocked.",
                                data={
                                    "agent": self.name,
                                    "task_id": task_id,
                                    "tool": parsed.TOOL,
                                    "input": parsed.INPUT,
                                    "reason": "Human operator denied execution.",
                                    "decision": "denied",
                                }
                            )
                        )
                        print("🚫 Action denied by human operator.")
                        hitl_denied = True

                        return TaskResult(
                            task_id=task_id,
                            assigned_agent=self.name,
                            status="BLOCKED",
                            summary=f"Subtask #{task_id} execution halted: Human operator denied approval for tool '{parsed.TOOL}' ({reason}).",
                            artifacts=[],
                        )
                # ---------------------------------------------------------

                tool_output = self.execute_tool(parsed.TOOL, tool_input)
                obs_str = create_observation(parsed.TOOL, tool_input, tool_output)

                messages.append(
                    {
                        "role": "user",
                        "content": obs_str
                        + "\n\n[SYSTEM OBSERVATION RECEIVED]: Analyze whether the assigned subtask is fully satisfied. If more actions (e.g. running Python calculations) are required, execute the next `STEP: TOOL`. ONLY output `STEP: ANSWER` if all requirements of the subtask are completely finished.",
                    }
                )

                self._emit(
                    event=NovaEvent(
                        event_type="tool_result",
                        content=f"\n\n✅ [RESULT OF #{task_id} DONE BY {parsed.TOOL} -> {tool_output}]\n",
                        data={
                            "agent": self.name,
                            "tool": parsed.TOOL,
                            "output": tool_output,
                            "success": True,
                        }
                    )
                )
                continue

            # -------------------------------------------------------------
            # Handle Final Answer Step
            # -------------------------------------------------------------
            elif parsed.STEP == "ANSWER":
                # 1. Detect if the instruction demanded a saved file artifact (e.g., .png, .jpg, .csv)
                target_artifacts = re.findall(
                    r"['\"]?([\w\-_\.]+\.(?:png|jpg|jpeg|csv|json))['\"]?",
                    instruction,
                    flags=re.IGNORECASE,
                )

                # 2. Check if the demanded file actually exists in the workspace
                workspace_dir = PROJECT_ROOT / "nova_workspace"
                missing_artifacts = [
                    f for f in target_artifacts if not (workspace_dir / f).exists()
                ]

                # 3. If an artifact is missing, reject ANSWER and force the agent to generate it
                if missing_artifacts and not hitl_denied:
                    missing_str = ", ".join(f"'{m}'" for m in missing_artifacts)
                    warning_msg = (
                        f"[SYSTEM WARNING]: You were instructed to generate and save {missing_str}, "
                        f"but the file does not exist in the workspace ({workspace_dir}). "
                        "You MUST execute `STEP: TOOL` with `run_python_code` calling matplotlib/pandas "
                        f"(e.g., plt.savefig({missing_str})) to create the file before outputting `STEP: ANSWER`."
                    )
                    messages.append({"role": "user", "content": warning_msg})
                    continue

                # 4. If all checks pass (or HITL was denied), conclude the subtask cleanly
                self._emit(
                    event=NovaEvent(
                        event_type="agent_completed",
                        content=f"[{self.name} Completed Task #{task_id}] {parsed.CONTENT}",
                        data={
                            "agent": self.name,
                            "task_id": task_id,
                            "result": parsed.CONTENT,
                        }
                    )
                )
                # print_step(
                #     step="EXPLANATION",
                #     content=f"[{self.name} Completed Task #{task_id}] {parsed.CONTENT}",
                #     tool=None,
                # )
                return TaskResult(
                    task_id=task_id,
                    assigned_agent=self.name,
                    status="FAILED" if hitl_denied else "SUCCESS",
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
            status="FAILED" if hitl_denied else "SUCCESS",
            summary=f"{self.name} completed bounded turns. Latest findings: {messages[-1]['content']}",
            artifacts=detected_artifacts,
        )
