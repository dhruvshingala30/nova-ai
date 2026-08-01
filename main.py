from app.agent import NovaAI
from app.config import EXIT_COMMANDS
from app.utils import (
    goodbye,
    print_separator,
)


def main():

    agent = NovaAI()

    print_separator()

    while True:
        user_query = input("👉 ")

        if user_query.strip().lower() in EXIT_COMMANDS:
            goodbye()
            break

        agent.run(user_query)

        print_separator()


if __name__ == "__main__":
    main()
