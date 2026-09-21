"""
app/core/shared_context.py - Inter-Agent Blackboard & Shared Workspace Memory Bus.

Allows specialist worker agents to publish artifacts (charts, cleaned CSVs, search findings)
and enables downstream agents to consume preceding task results without context contamination.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from app.models import TaskResult


class SharedContextBus:
    """
    Central blackboard memory store for collaborative multi-agent execution.
    """

    def __init__(self) -> None:
        # Dictionary mapping task_id (int) to TaskResult object
        self._task_results: dict[int, TaskResult] = {}
        # Track generated file artifacts (e.g., 'sales_chart.png')
        self._artifacts: list[str] = []

    def publish_result(self, result: TaskResult) -> None:
        """
        Stores the structured outcome of a completed subtask.

        Args:
            result (TaskResult): The outcome payload from a worker agent.
        """
        self._task_results[result.task_id] = result
        # Collect any artifacts declared by the worker
        for artifact in result.artifacts:
            if artifact not in self._artifacts:
                self._artifacts.append(artifact)

    def get_result(self, task_id: int) -> TaskResult | None:
        """Retrieves a specific subtask result by its ID."""
        return self._task_results.get(task_id)

    def get_all_results(self) -> list[TaskResult]:
        """Returns all completed task results ordered by task_id."""
        return [self._task_results[k] for k in sorted(self._task_results.keys())]

    def format_context_for_prompt(self) -> str:
        """
        Builds a readable summary of all completed subtasks to inject into downstream agent prompts.
        """
        if not self._task_results:
            return "No previous subtask results available yet."

        lines = ["=== COMPLETED SUBTASK FINDINGS & ARTIFACTS ==="]
        for task_id in sorted(self._task_results.keys()):
            res = self._task_results[task_id]
            status_symbol = "✅" if res.status == "SUCCESS" else "❌"
            lines.append(
                f"[Task #{res.task_id}] ({res.assigned_agent}) {status_symbol}:\n"
                f"Summary: {res.summary}"
            )
            if res.artifacts:
                lines.append(f"Generated Files: {', '.join(res.artifacts)}")
            if res.error_message:
                lines.append(f"Error Log: {res.error_message}")
            lines.append("-" * 40)

        return "\n".join(lines)

    def clear(self) -> None:
        """Resets the context bus for a new conversation turn."""
        self._task_results.clear()
        self._artifacts.clear()
