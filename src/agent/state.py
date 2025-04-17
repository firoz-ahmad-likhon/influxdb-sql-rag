from typing import Any
from typing_extensions import TypedDict


class State(TypedDict, total=False):
    """State of the RAG system."""

    question: str
    query: str
    result: list[Any] | None
    answer: str | None
    error: str | None
    use_chat: bool  # Flag for using chat instead of database
    is_followup: bool  # Flag for follow prior conversation
