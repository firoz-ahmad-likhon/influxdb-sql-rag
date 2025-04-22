from src.agent.state import State


class Router:
    """Route the workflow based on whether we need database or chat."""

    def __call__(self, state: State) -> str:
        """Call the class."""
        return "answer_up" if state.get("type") in ("chat", "follow-up") else "execute"
