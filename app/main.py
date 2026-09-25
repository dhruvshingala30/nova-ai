"""
app/main.py - Entry Point for NovaAI Interactive Multi-Agent CLI.

Initializes the MultiAgentOrchestrator and manages the REPL loop
with background workspace monitoring.
"""

from config import EXIT_COMMANDS
from core.event import NovaEvent
from core.workspace_manager import workspace
from core.workspace_watcher import start_workspace_watcher
from orchestrator import MultiAgentOrchestrator
from utils import goodbye, print_separator, print_step, welcome


def main():
    """
    Main loop for interacting with the Multi-Agent NovaAI framework.
    """

    def cli_event_handler(event: NovaEvent):
        """
        Handles events emitted by the MultiAgentOrchestrator and its agents.
        """
        match event.event_type:
            case "final_answer":
                output = print_step(
                    step="ANSWER",
                    content=event.content,
                    tool=None
                )
                print(output)

            case "reflection":
                output = print_step(
                    step="REFLECT",
                    content=event.content,
                    tool=None
                )
                print(output)

            case "plan_created":
                output = print_step(
                    step="PLAN",
                    content=event.content,
                    tool=None
                )
                print(output)

            case "tool_invocation":
                output = print_step(
                    step="TOOL",
                    content=f"[{event.data['agent']}] {event.content}",
                    tool=event.data['tool']
                )
                print(output)

            case "tool_result":
                output = print_step(
                    step="RESULT",
                    content=f"`{event.data['tool']}` has done with it's findings.",
                    tool=None
                )
                print(output)

            case "agent_completed":
                output = print_step(
                    step="EXPLANATION",
                    content=event.content,
                    tool=None
                )
                print(output)

            case "approval_required" | "approval_granted" | "approval_denied":
                pass

            case _:
                print(event.content)

    # Initialize the Multi-Agent Orchestrator (Supervisor)
    orchestrator = MultiAgentOrchestrator(event_handler=cli_event_handler)

    print_separator()
    welcome()
    print("🤝 NovaAI Multi-Agent Collaboration Engine Active (Phase 3.1)")
    print_separator()

    # Start the workspace watcher for automatic PDF/CSV ingestion
    watcher_observer = start_workspace_watcher(str(workspace.workspace_dir))
    print_separator()
 
    while True:
        try:
            # Prompt user for natural language input
            user_query = input("👉 ")

            # Input Validation and flow control guard
            if not user_query.strip():
                continue

            # Check for predefined exit commands
            if user_query.strip().lower() in EXIT_COMMANDS:
                goodbye()
                break

            # Execute the multi-agent reasoning and delegation pipeline
            orchestrator.run(user_query)
            print_separator()

        except (KeyboardInterrupt, EOFError):
            goodbye()
            break

    # Gracefully shut down background observer thread on exit
    watcher_observer.stop()
    watcher_observer.join()


if __name__ == "__main__":
    main()
