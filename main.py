"""
main.py - Entry Point for NovaAI Interactive CLI Agent.

This module initializes the NovaAI agent instance and maintains an interactive
read-eval-print loop (REPL) in the terminal for user interactions.
"""

from app.agent import NovaAI
from app.config import EXIT_COMMANDS
from app.utils import goodbye, print_separator


def main():
    """
    Main loop for interacting with the NovaAI agent.

    Continuously listens for user input in the CLI, checks if the query matches
    exit commands, and triggers the agentic execution loop (`agent.run`).
    """
    # Initialize the core NovaAI agent engine
    agent = NovaAI()

    print_separator()

    while True:
        # Accept query input from user
        user_query = input("You: ")

        # Check if user wants to exit the application
        if user_query.strip().lower() in EXIT_COMMANDS:
            goodbye()
            break

        # Execute the agentic reasoning and tool execution loop
        agent.run(user_query)
        print_separator()


if __name__ == "__main__":
    main()
