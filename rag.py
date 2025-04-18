from src.agent.workflow import dag
from src.agent.state import State


def run() -> None:
    """Run the RAG agent."""
    try:
        rag = dag()

        while True:
            user_input = input("You: ")
            if user_input.lower() in {"exit", "quit"}:
                break

            # Create initial state with user's question
            initial_state: State = {"question": user_input}
            # Run through the graph
            final_state: State = rag.invoke(initial_state)
            # Print the final answer
            print(  # noqa:T201
                f"Bot: {final_state.get('answer', 'Sorry, I have no answer.')}",
            )
    except Exception as e:
        raise RuntimeError("Error: ", e) from e


if __name__ == "__main__":
    run()
