"""
app/orchestrator.py - Multi-Agent Supervisor & Orchestration Engine.

Orchestrates Phase 3.1 multi-agent workflows by:
1. Decomposing complex queries into subtasks with dependency management.
2. Dispatching subtasks to domain specialists (ResearchAgent, DataAnalystAgent, DocVisionAgent).
3. Passing artifacts and intermediate findings across the SharedContextBus.
4. Synthesizing worker outcomes into a unified, grounded final response.
"""

import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from ollama import Client
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from app.agents.specialists import DataAnalystAgent, DocVisionAgent, ResearchAgent
from app.config import MAX_HISTORY, MODEL_NAME, OLLAMA_HOST
from app.core.event import NovaEvent
from app.core.memory import SQLiteMemory
from app.core.shared_context import SharedContextBus
from app.models import AgentRole, SubTask, SupervisorDecision, TaskResult
from app.prompts import SUPERVISOR_PROMPT
from app.tools.knowledge_base_search import get_indexed_documents


class MultiAgentOrchestrator:
    """
    Supervisor Agent responsible for multi-agent decomposition, execution, and synthesis.
    """

    def __init__(
        self,
        session_id: str | None = None,
        event_handler: Callable[[NovaEvent], None] | None = None,
    ) -> None:
        self.client = Client(host=OLLAMA_HOST)
        self.model = MODEL_NAME
        self.memory = SQLiteMemory()
        self.session_id = session_id
        self.context_bus = SharedContextBus()
        self.event_handler = event_handler

        self.message_history: list[dict]= []
        self._update_system_message()

        if session_id:
            saved_history = self.memory.get_session_history(
                self.session_id, limit=MAX_HISTORY # type: ignore
            )
            self.message_history.extend(saved_history)

        # Initialize the specialist team
        self.workers = {
            AgentRole.RESEARCHER.value: ResearchAgent(event_handler=self.event_handler),
            AgentRole.DATA_ANALYST.value: DataAnalystAgent(event_handler=self.event_handler),
            AgentRole.DOC_VISION.value: DocVisionAgent(event_handler=self.event_handler),
        }


    def _emit(self, event: NovaEvent):
        """Emits an event to the registered event handler."""
        if self.session_id:
            event.data.setdefault("session_id", self.session_id)

        if self.event_handler:
            self.event_handler(event)


    def _build_supervisor_prompt(self) -> str:
        """Constructs the full supervisor system prompt with live date and doc catalog."""
        current_date = datetime.now().strftime("%A, %B %d, %Y at %I:%M:%S %p")  # noqa: DTZ005
        date_context = f"CURRENT SYSTEM DATE AND TIME: TODAY is {current_date}.\n"

        indexed_docs = get_indexed_documents()
        if indexed_docs:
            docs_list_str = "\n".join([f"  - {doc}" for doc in indexed_docs])
            kb_catalog = (
                f"CURRENTLY INDEXED KNOWLEDGE BASE DOCUMENTS:\n{docs_list_str}\n"
            )
        else:
            kb_catalog = (
                "CURRENTLY INDEXED KNOWLEDGE BASE DOCUMENTS: None currently indexed.\n"
            )

        system_banner = (
            "==========================================================\n"
            "SYSTEM RUNTIME CONTEXT:\n"
            f"- {date_context}"
            f"{kb_catalog}"
            "==========================================================\n\n"
        )
        return system_banner + SUPERVISOR_PROMPT

    def _update_system_message(self) -> None:
        """Updates or initializes the root system message in message_history."""
        full_prompt = self._build_supervisor_prompt()

        if not self.message_history:
            self.message_history.append({"role": "system", "content": full_prompt})
        else:
            self.message_history[0] = {"role": "system", "content": full_prompt}


    def _clean_json_output(self, raw_content: str) -> str:
        """Strips Markdown block tags from the supervisor response."""
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()


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

            # Clear shared blackboard for this query run
            self.context_bus.clear()

    def chat(self) -> SupervisorDecision:
        """Sends sanitized context history to Ollama and parses structured JSON output."""
        self._update_system_message()

        response = self.client.chat(
            model=self.model,
            format=SupervisorDecision.model_json_schema(),
            messages=self.message_history,
            options={"temperature": 0.0},
            keep_alive="30m"
        )

        raw_result = response.message.content or "{}"
        cleaned_result = self._clean_json_output(raw_result)

        self.add_message(
            role="assistant",
            content=cleaned_result
        )

        try:
            return SupervisorDecision.model_validate_json(cleaned_result)
        except ValidationError:
            # Fallback if unparsable
            return SupervisorDecision(
                ACTION="DIRECT_ANSWER",
                REASONING="Direct fallback",
                FINAL_ANSWER=cleaned_result,
            )


    def run(self, user_query: str) -> str:
        """
        Executes the collaborative multi-agent workflow.

        Args:
            user_query (str): The natural language query from the user.

        Returns:
            str: Final synthesized response.
        """
        # Auto-generate session title if needed
        if self.session_id is None:
            self.session_id = self.memory.generate_title_from_prompt(
                client=self.client,
                model_name=self.model,
                prompt=user_query,
            )

            self._emit(
                event=NovaEvent(
                    event_type="session_created",
                    content=f"📝 New Session Title Generated: '{self.session_id}'",
                    data={
                        "user_query": user_query,
                        "session_id": self.session_id,
                    },
                )
            )
            # print(f"📝 New Session Title Generated: '{self.session_id}'")

        # Save user query to persistent SQLite memory
        self.add_message(role="user", content=user_query)

        # -------------------------------------------------------------
        # 1. SUPERVISOR PLANNING & DELEGATION TURN
        # -------------------------------------------------------------
        decision = self.chat()

        # -------------------------------------------------------------
        # 2. HANDLE DIRECT ANSWER (No Subtasks Needed)
        # -------------------------------------------------------------
        if decision.ACTION == "DIRECT_ANSWER" and decision.FINAL_ANSWER:
            self._emit(
            event=NovaEvent(
                event_type="final_answer",
                content=decision.FINAL_ANSWER,
                data={
                    "session_id": self.session_id,
                    "user_query": user_query,
                }
            )
        )
            # print_step(step="ANSWER", content=decision.FINAL_ANSWER, tool=None)
            self.add_message(
                role="assistant",
                content=decision.FINAL_ANSWER,
            )
            return decision.FINAL_ANSWER

        # -------------------------------------------------------------
        # 3. EXECUTE DELEGATED SUBTASKS ACROSS SPECIALISTS
        # -------------------------------------------------------------
        subtasks: list[SubTask] = decision.SUBTASKS or []
        if subtasks:
            self._emit(
                event=NovaEvent(
                    event_type="plan_created",
                    content=f"Supervisor Formulated Multi-Agent Plan ({len(subtasks)} Subtasks)",
                    data={
                        "subtask_count": len(subtasks),
                        "subtasks": [st.model_dump() for st in subtasks],
                    }
                )
            )
            # print_step(
            #     step="PLAN",
            #     content=f"Supervisor Formulated Multi-Agent Plan ({len(subtasks)} Subtasks)",
            #     tool=None,
            # )
            for st in subtasks:
                agent_icon = (
                    "🌐" if st.assigned_agent == AgentRole.RESEARCHER
                    else ("📊" if st.assigned_agent == AgentRole.DATA_ANALYST else "📄")
                )

                self._emit(
                    event=NovaEvent(
                        event_type="subtask_list",
                        content=f"   {st.task_id}. {agent_icon} [{st.assigned_agent.value}]: {st.instruction}",
                        data={
                            "task_id": st.task_id,
                            "agent": f"{agent_icon} [{st.assigned_agent.value}]",
                            "instruction": st.instruction,
                        },
                    )
                )
                # print(
                #     f"   {st.task_id}. {agent_icon} [{st.assigned_agent.value}]: {st.instruction}"
                # )

            # Execute subtasks in dependency order
            for subtask in subtasks:
                worker_agent = self.workers.get(subtask.assigned_agent.value)
                if not worker_agent:
                    continue

                self._emit(
                    event=NovaEvent(
                        event_type="subtask_dispatched",
                        content=f"\n🚀 [DISPATCHING SUBTASK #{subtask.task_id}] -> {subtask.assigned_agent.value}",
                        data={
                            "task_id": subtask.task_id,
                            "agent": subtask.assigned_agent.value,
                            "task": subtask.instruction,
                        }
                    )
                )

                # print(
                #     f"\n🚀 [DISPATCHING SUBTASK #{subtask.task_id}] -> {subtask.assigned_agent.value}"
                # )

                # Retrieve context from completed dependency tasks
                accumulated_context = self.context_bus.format_context_for_prompt()

                # -------------------------------------------------------------
                # DEPENDENCY SAFEGUARD: Skip if an upstream dependency failed/was blocked
                # -------------------------------------------------------------
                dependency_failed = False
                for dep_id in (subtask.dependencies or []):
                    dep_result = self.context_bus.get_result(dep_id)
                    if dep_result and dep_result.status != "SUCCESS":
                        dependency_failed = True
                        break

                # Also check if the subtask requires an artifact that wasn't created
                if "denied due to HITL" in accumulated_context.lower():
                    dependency_failed = True

                if dependency_failed:
                    skipped_result = TaskResult(
                        task_id=subtask.task_id,
                        assigned_agent=subtask.assigned_agent.value,
                        status="SKIPPED",
                        summary=f"Subtask #{subtask.task_id} skipped because prerequisite dependency was denied or incomplete.",
                        artifacts=[],
                    )
                    self.context_bus.publish_result(result=skipped_result)
                    self._emit(
                        event=NovaEvent(
                            event_type="subtask_skipped",
                            content=f"⏭️ [SUBTASK #{subtask.task_id} SKIPPED]: Upstream dependency was denied or failed.",
                            data={
                                "task_id": subtask.task_id,
                                "agent": subtask.assigned_agent.value,
                            }
                        )
                    )
                    continue

                # Worker executes task
                task_result = worker_agent.work_on_task(
                    task_id=subtask.task_id,
                    instruction=subtask.instruction,
                    context_findings=accumulated_context,
                )

                # Publish result to shared blackboard
                self.context_bus.publish_result(task_result)

        # -------------------------------------------------------------
        # 4. FINAL SYNTHESIS TURN BY SUPERVISOR
        # -------------------------------------------------------------
        # print(
        #     "\n🧠 [SUPERVISOR] Synthesizing all specialist findings into final answer..."
        # )
        all_findings = self.context_bus.format_context_for_prompt()

        self._emit(
            event=NovaEvent(
                event_type="synthesis_started",
                content="\n💬 [SUPERVISOR] Synthesizing all specialist findings into final answer...",
                data={
                    "subtask_count": len(subtasks),
                    "agent_results": all_findings,
                }
            )
        )

        synthesis_messages = [
            {"role": "system", "content": self._build_supervisor_prompt()},
            {
                "role": "user",
                "content": (
                    f"Original User Query: {user_query}\n\n"
                    f"Team Findings:\n{all_findings}\n\n"
                    "SYNTHESIS GUIDELINES:\n"
                    "- If a subtask has status 'BLOCKED' or 'SKIPPED', explicitly report that the action (such as saving a file or plotting) was aborted/denied.\n"
                    "- NEVER state that a file was saved or created if its generation subtask was BLOCKED.\n"
                    "- Directly integrate today's date/time from SYSTEM RUNTIME CONTEXT if the user asked for it.\n\n"
                    "Provide your final ACTION: 'SYNTHESIZE' with the comprehensive 'FINAL_ANSWER'."
                ),
            },
        ]

        synthesis_response = self.client.chat(
            model=self.model,
            format=SupervisorDecision.model_json_schema(),
            messages=synthesis_messages,
            options={"temperature": 0.0},
        )

        synth_cleaned = self._clean_json_output(
            synthesis_response.message.content or "{}"
        )
        try:
            synth_decision = SupervisorDecision.model_validate_json(synth_cleaned)
            final_text = synth_decision.FINAL_ANSWER or synth_cleaned
        except ValidationError:
            final_text = synth_cleaned

        self._emit(
            event=NovaEvent(
                event_type="final_answer",
                content=final_text,
                data={
                    "session_id": self.session_id,
                    "user_query": user_query,
                }
            )
        )

        # print_step(step="ANSWER", content=final_text, tool=None)

        # Persist final conversation turn to SQLite memory
        self.add_message(
            role="assistant",
            content=final_text
        )
        return final_text
