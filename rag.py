import uuid
from src.agent.graph import Workflow
from src.utils.helper import Helper


def run() -> None:
    """Run the RAG agent."""
    try:
        rag = Workflow().build(checkpointer=Helper.checkpoint())
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}

        while True:
            user_input = input("You: ")
            if user_input.lower() in {"exit", "quit"}:
                break
            response = rag.invoke({"question": user_input}, config=config)
            print(  # noqa:T201
                f"Bot: {response.get('answer', 'Sorry, I have no answer.')}",
            )
    except Exception as e:
        raise RuntimeError("Error: ", e) from e


if __name__ == "__main__":
    run()
