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
from app.config import MODEL_NAME, OLLAMA_HOST
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

        # Initialize the specialist team
        self.workers = {
            AgentRole.RESEARCHER.value: ResearchAgent(),
            AgentRole.DATA_ANALYST.value: DataAnalystAgent(),
            AgentRole.DOC_VISION.value: DocVisionAgent(),
        }

    def _clean_json_output(self, raw_content: str) -> str:
        """Strips Markdown block tags from the supervisor response."""
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def _get_system_context(self) -> str:
        """Dynamically provides date context and indexed knowledge base catalog."""
        # Get current system date for context in supervisor prompt
        current_date = datetime.now().strftime("%A, %B %d, %Y")  # noqa: DTZ005
        date_str = f"CURRENT SYSTEM DATE: {current_date}\n"

        # List currently indexed documents in the knowledge base for context
        indexed_docs = get_indexed_documents()
        if indexed_docs:
            docs_str = "CURRENTLY INDEXED DOCUMENTS IN KNOWLEDGE BASE:\n" + "\n".join(
                [f"  - {d}" for d in indexed_docs]
            )
        else:
            docs_str = "CURRENTLY INDEXED DOCUMENTS: None currently indexed."

        return f"{date_str}\n{docs_str}\n\n{SUPERVISOR_PROMPT}"

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
            print(f"📝 Session Title: '{self.session_id}'")

        # Save user query to persistent SQLite memory
        self.memory.save_message(
            session_id=self.session_id, role="user", content=user_query
        )

        # Clear shared blackboard for this query run
        self.context_bus.clear()

        # -------------------------------------------------------------
        # 1. SUPERVISOR PLANNING & DELEGATION TURN
        # -------------------------------------------------------------
        system_prompt = self._get_system_context()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Query: {user_query}"},
        ]

        response = self.client.chat(
            model=self.model,
            format=SupervisorDecision.model_json_schema(),
            messages=messages,
            options={"temperature": 0.0},
        )

        cleaned_json = self._clean_json_output(response.message.content or "{}")
        try:
            decision = SupervisorDecision.model_validate_json(cleaned_json)
        except ValidationError:
            # Fallback if unparsable
            decision = SupervisorDecision(
                ACTION="DIRECT_ANSWER",
                REASONING="Direct fallback",
                FINAL_ANSWER=cleaned_json,
            )

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
            {"role": "system", "content": system_prompt},
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
