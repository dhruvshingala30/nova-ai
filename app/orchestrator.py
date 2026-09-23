"""
app/orchestrator.py - Multi-Agent Supervisor & Orchestration Engine.

Orchestrates Phase 3.1 multi-agent workflows by:
1. Decomposing complex queries into subtasks with dependency management.
2. Dispatching subtasks to domain specialists (ResearchAgent, DataAnalystAgent, DocVisionAgent).
3. Passing artifacts and intermediate findings across the SharedContextBus.
4. Synthesizing worker outcomes into a unified, grounded final response.
"""

import re
from datetime import datetime
from pathlib import Path

from ollama import Client
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from app.agents.specialists import DataAnalystAgent, DocVisionAgent, ResearchAgent
from app.config import MAX_HISTORY, MODEL_NAME, OLLAMA_HOST
from app.core.memory import SQLiteMemory
from app.core.shared_context import SharedContextBus
from app.models import AgentRole, SubTask, SupervisorDecision
from app.prompts import SUPERVISOR_PROMPT
from app.tools.knowledge_base_search import get_indexed_documents
from app.utils import print_step


class MultiAgentOrchestrator:
    """
    Supervisor Agent responsible for multi-agent decomposition, execution, and synthesis.
    """

    def __init__(self, session_id: str | None = None) -> None:
        self.client = Client(host=OLLAMA_HOST)
        self.model = MODEL_NAME
        self.memory = SQLiteMemory()
        self.session_id = session_id
        self.context_bus = SharedContextBus()

        self.message_history: list[dict]= []
        self._get_system_context()

        if session_id:
            saved_history = self.memory.get_session_history(
                self.session_id, limit=MAX_HISTORY # type: ignore
            )
            self.message_history.extend(saved_history)

        # Initialize the specialist team
        self.workers = {
            AgentRole.RESEARCHER.value: ResearchAgent(),
            AgentRole.DATA_ANALYST.value: DataAnalystAgent(),
            AgentRole.DOC_VISION.value: DocVisionAgent(),
        }


    def _get_system_context(self):
        """Dynamically provides date context and indexed knowledge base catalog."""
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
            + SUPERVISOR_PROMPT
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
        self._get_system_context()

        response = self.client.chat(
            model=self.model,
            format=SupervisorDecision.model_json_schema(),
            messages=self.message_history,
            options={"temperature": 0.0},
        )

        raw_result = response.message.content or "{}"
        cleaned_result = self._clean_json_output(raw_result)

        self.add_message("assistant", cleaned_result)

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
            print(f"📝 New Session Title Generated: '{self.session_id}'")

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
            print_step(step="ANSWER", content=decision.FINAL_ANSWER, tool=None)
            self.memory.save_message(
                session_id=self.session_id,
                role="assistant",
                content=decision.FINAL_ANSWER,
            )
            return decision.FINAL_ANSWER

        # -------------------------------------------------------------
        # 3. EXECUTE DELEGATED SUBTASKS ACROSS SPECIALISTS
        # -------------------------------------------------------------
        subtasks: list[SubTask] = decision.SUBTASKS or []
        if decision.ACTION == "DELEGATE" and subtasks:
            print_step(
                step="PLAN",
                content=f"Supervisor Formulated Multi-Agent Plan ({len(subtasks)} Subtasks)",
                tool=None,
            )
            for st in subtasks:
                agent_icon = (
                    "🌐" if st.assigned_agent == AgentRole.RESEARCHER
                    else ("📊" if st.assigned_agent == AgentRole.DATA_ANALYST else "📄")
                )
                print(
                    f"   {st.task_id}. {agent_icon} [{st.assigned_agent.value}]: {st.instruction}"
                )

            # Execute subtasks in dependency order
            for subtask in subtasks:
                worker_agent = self.workers.get(subtask.assigned_agent.value)
                if not worker_agent:
                    continue

                print(
                    f"\n🚀 [DISPATCHING SUBTASK #{subtask.task_id}] -> {subtask.assigned_agent.value}"
                )

                # Retrieve context from completed dependency tasks
                accumulated_context = self.context_bus.format_context_for_prompt()

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
        print(
            "\n🧠 [SUPERVISOR] Synthesizing all specialist findings into final answer..."
        )
        all_findings = self.context_bus.format_context_for_prompt()

        synthesis_messages = [
            {"role": "system", "content": self._get_system_context()},
            {
                "role": "user",
                "content": (
                    f"Original User Query: {user_query}\n\n"
                    f"Team Findings:\n{all_findings}\n\n"
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

        print_step(step="ANSWER", content=final_text, tool=None)

        # Persist final conversation turn to SQLite memory
        self.memory.save_message(
            session_id=self.session_id, role="assistant", content=final_text
        )
        return final_text
