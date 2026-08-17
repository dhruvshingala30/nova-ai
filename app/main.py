"""
main.py - Entry Point for NovaAI Interactive CLI Agent.

This module initializes the NovaAI agent instance and maintains an interactive
read-eval-print loop (REPL) in the terminal for user interactions.
"""

from agent import NovaAI
from config import EXIT_COMMANDS
from core.workspace_manager import workspace
from core.workspace_watcher import start_workspace_watcher
from utils import goodbye, print_separator, welcome


def main():
    """
    Main loop for interacting with NovaAI.

    Creates a new agent instance with lazy session creation (title auto-generated
    on prompt #1) and processes continuous user inputs.
    """
    # Initialize the core NovaAI agent engine
    agent = NovaAI()

    print_separator()
    welcome()
    print_separator()

    # Start the background workspace watcher
    watcher_observer = start_workspace_watcher(str(workspace.workspace_dir))
    print_separator()

    while True:
        try:
            # Accept query input from user
            user_query = input("👉 ")

            # Check for empty input
            if not user_query.strip():
                continue
            
            # Check if user wants to exit the application
            if user_query.strip().lower() in EXIT_COMMANDS:
                goodbye()
                break

            # Execute the agentic reasoning and tool execution loop
            agent.run(user_query)
            print_separator()

        except (KeyboardInterrupt, EOFError):
            goodbye()
            break

    # Gracefully stop the watcher thread on exit
    watcher_observer.stop()
    watcher_observer.join()


if __name__ == "__main__":
    main()
