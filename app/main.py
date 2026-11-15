
from app.services.agent import HardwareAgent


def main():
    print("\n" + "=" * 55)
    print("          LOCAL LINUX HARDWARE ASSISTANT")
    print("=" * 55)
    print("Ask questions about your computer hardware.")
    print("Type 'exit' to close the assistant.\n")

    agent = HardwareAgent()

    while True:
        try:
            question = input("You: ").strip()

            if question.lower() in ("exit", "quit"):
                print("Assistant: Goodbye!")
                break

            if not question:
                continue

            answer = agent.ask(question)

            print("\nAssistant:", answer, "\n")

        except KeyboardInterrupt:
            print("\nAssistant: Goodbye!")
            break


if __name__ == "__main__":
    main()
