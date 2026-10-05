"""
app/orchestrator.py - Multi-Agent Supervisor & Orchestration Engine.

Orchestrates Phase 3.1 multi-agent workflows by:
1. Decomposing complex queries into subtasks with dependency management.
2. Dispatching subtasks to domain specialists (ResearchAgent, DataAnalystAgent, DocVisionAgent).
3. Passing artifacts and intermediate findings across the SharedContextBus.
4. Synthesizing worker outcomes into a unified, grounded final response.
"""

import re
import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from ollama import Client

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from app.agents.specialists import DataAnalystAgent, DocVisionAgent, ResearchAgent
from app.config import MAX_HISTORY, MODEL_NAME, OLLAMA_HOST
from app.core.event import NovaEvent
from app.core.memory import SQLiteMemory
from app.core.shared_context import SharedContextBus
from app.models import AgentRole, SubTask, SupervisorDecision, TaskResult
from app.prompts import SUPERVISOR_PROMPT, SYNTHESIS_SYSTEM_PROMPT
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
        self.session_title: str | None = None
        self.context_bus = SharedContextBus()
        self.event_handler = event_handler

        self._cached_supervisor_prompt: str = self._build_supervisor_prompt()

        self.message_history: list[dict]= [
            {"role": "system", "content": self._cached_supervisor_prompt}
        ]

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
        """Keeps static prompt first for 100% KV-cache hit rate."""
        current_date = datetime.now().strftime("%A, %B %d, %Y")  # noqa: DTZ005

        indexed_docs = get_indexed_documents()
        docs_list_str = "\n".join([f"  - {doc}" for doc in indexed_docs])

        runtime_context = (
            "\n\n==========================================================\n"
            "SYSTEM RUNTIME CONTEXT (DYNAMIC):\n"
            f"- CURRENT SYSTEM DATE: {current_date}\n"
            f"- CURRENTLY INDEXED DOCUMENTS:\n{docs_list_str if indexed_docs else '  - No indexed documents found.'}"
            "\n=========================================================="
        )
        return SUPERVISOR_PROMPT + runtime_context

    def _update_system_message(self) -> None:
        """Ensures the root system message remains intact without invalidating KV cache."""

        if not self.message_history:
            self.message_history.append({"role": "system", "content": self._cached_supervisor_prompt})
        else:
            self.message_history[0] = {"role": "system", "content": self._cached_supervisor_prompt}


    def _clean_json_output(self, raw_content: str) -> str:
        """Strips Markdown block tags from the supervisor response."""
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()


    def _build_planner_messages(self, max_recent_turns: int = 2) -> list[dict]:
        """
        Builds a compact message list specifically for planning.
        Keeps system rules and the current query, summarizing older turns
        to minimize prompt evaluation time (prefill latency).
        """
        # Ensure root system message is current
        self._update_system_message()
        system_msg = self.message_history[0]

        # Extract non-system conversation history (excluding the current user message)
        history = [m for m in self.message_history[1:-1] if m.get("content")]
        current_user_msg = self.message_history[-1]

        # If conversation just started, only send system prompt + current prompt
        if not history:
            return [system_msg, current_user_msg]

        # Extract the most recent N turns for direct short-term context
        recent_history = history[-(max_recent_turns * 2) :]

        # Build a brief rolling recap for older turns (if any exist)
        older_history = history[: -(max_recent_turns * 2)]
        planner_messages = [system_msg]

        if older_history:
            recap_snippets = []
            for msg in older_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                # Truncate content to 120 chars to prevent token bloat
                snippet = msg["content"].replace("\n", " ").strip()[:120]
                recap_snippets.append(f"- {role}: {snippet}")

            recap_text = (
                "CONTEXT RECAP (Previous conversation overview):\n"
                + "\n".join(recap_snippets)
            )
            planner_messages.append({"role": "system", "content": recap_text})

        # Append recent raw turns (truncated slightly to guarantee no tool bloat)
        for msg in recent_history:
            content = msg["content"]
            # Cap previous assistant messages so past large outputs don't flood the planner
            if msg["role"] == "assistant" and len(content) > 300:
                content = content[:300] + "... [prior findings summarized]"
            planner_messages.append({"role": msg["role"], "content": content})

        # Append the actual new user query
        planner_messages.append(current_user_msg)
        return planner_messages


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
        options = {
            "temperature": 0.0,  # Low temperature reduces branching & deliberation
            "num_predict": 1024,  # Strict token ceiling (plans never exceed ~400 tokens)
            "num_ctx": 4096,  # Avoid unnecessarily bloated 16k/32k buffers for planner
        }

        planner_messages = self._build_planner_messages(max_recent_turns=2)

        response = self.client.chat(
            model=self.model,
            format="json",
            messages=planner_messages,
            options=options,
            keep_alive="30m"
        )

        raw_result = response.message.content or "{}"
        cleaned_result = self._clean_json_output(raw_result)

        # Ensure we capture bracket boundaries if any pre/post text leaked
        match = re.search(r"\{.*\}", cleaned_result, re.DOTALL)
        if match:
            cleaned_result = match.group(0)

        try:
            return SupervisorDecision.model_validate_json(cleaned_result)
        except Exception as e:  # noqa: BLE001
            # If the supervisor output is completely malformed, formulate a safe direct reply
            # instead of exposing raw internal JSON to the end-user.
            return SupervisorDecision(
                ACTION="DIRECT_ANSWER",
                REASONING=f"Failed to parse planning plan: {e}",
                FINAL_ANSWER="I encountered and issue planning this multi-step task. " \
                "Please try rephrasing your request or breaking it into smaller parts.",
            )


    def run(self, user_query: str) -> str:
        """
        Executes the collaborative multi-agent workflow.

        Args:
            user_query (str): The natural language query from the user.

        Returns:
            str: Final synthesized response.
        """
        # Auto-generate session id if needed
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())

        session_title = self.memory.get_session_title(session_id=self.session_id)

        if session_title is None:
            # 1. Instantly use a lightweight slice as the placeholder title (0ms delay!)
            fallback_title = user_query.strip().split("\n")[0][:30].strip()
            session_title = fallback_title

            self.memory.save_session(
                session_id=self.session_id,
                title=session_title,
            )

            self._emit(
                event=NovaEvent(
                    event_type="session_created",
                    content="🆕 New Session Title Generated\n"
                            f"🆔: {self.session_id}\n"
                            f"Title: {session_title}",
                    data={
                        "user_query": user_query,
                        "session_id": self.session_id,
                        "session_title": fallback_title,
                    },
                )
            )

            # 2. Fire the LLM title generation in a background thread
            def _on_refined_title(new_title: str):
                self._emit(
                    event=NovaEvent(
                        event_type="session_updated",
                        content=f"Updated session to | `{new_title}`",
                        data={
                            "session_id": self.session_id,
                            "session_title": new_title,
                        },
                    )
                )
            # print(f"📝 New Session Title Generated: '{self.session_id}'")

            self.memory.generate_title_in_background(
                client=self.client,
                model_name=self.model,
                prompt=user_query,
                session_id=self.session_id,
                on_title_generated=_on_refined_title,
            )
        else:
            self.session_title = session_title

        # Proceed directly to planning without waiting for title LLM!
        self.add_message(role="user", content=user_query)

        self._emit(
            event=NovaEvent(
                event_type="plan_started",
                content="Analyzing user request and drafting execution plan...",
                data={
                    "session_id": self.session_id,
                    "user_query": user_query,
                },
            )
        )

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
            plan_lines = []
            for st in subtasks:
                agent_icon = (
                    "🌐" if st.assigned_agent == AgentRole.RESEARCHER
                    else ("📊" if st.assigned_agent == AgentRole.DATA_ANALYST else "📄")
                )
                plan_lines.append(f"   {st.task_id}. {agent_icon} [{st.assigned_agent.value}]: {st.instruction}")

            self._emit(
                event=NovaEvent(
                    event_type="subtask_list",
                    content="\n".join(plan_lines),
                    data={
                        "subtasks": [st.model_dump() for st in subtasks],
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
                        content=f"🚀 [DISPATCHING SUBTASK #{subtask.task_id}] -> {subtask.assigned_agent.value}",
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
                    session_id=self.session_id
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
                content="💬 [SUPERVISOR] Synthesizing all specialist findings into final answer...",
                data={
                    "subtask_count": len(subtasks),
                    "agent_results": all_findings,
                }
            )
        )

        synthesis_messages = [
            {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Original User Query: {user_query}\n\n"
                    f"Team Findings:\n{all_findings}\n\n"
                ),
            },
        ]

        stream = self.client.chat(
            model=self.model,
            messages=synthesis_messages,
            options={
                "temperature": 0.2,
                "num_predict": 1024,
            },
            keep_alive="30m",
            stream=True,
        )

        collected_chunks = []
        for chunk in stream:
            content = chunk.message.content or ""
            collected_chunks.append(content)
            self._emit(
                event=NovaEvent(
                    event_type="synthesis_chunk",
                    content=content,
                    data={
                        "session_id": self.session_id,
                        "user_query": user_query,
                    },
                )
            )

        final_text = "".join(collected_chunks).strip()

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
