from typing import Any, Literal
from typing_extensions import TypedDict


class State(TypedDict, total=False):
    """State of the RAG system."""

    question: str
    query: str
    result: list[Any] | None
    answer: str
    error: str | None
    type: Literal["query", "chat", "follow-up"]
