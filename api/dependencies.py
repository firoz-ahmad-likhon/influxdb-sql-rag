from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables.config import RunnableConfig
from fastapi import Header
import uuid
from src.agent.graph import Workflow
from src.utils.helper import Helper


def get_graph() -> CompiledStateGraph:
    """Graph instance."""
    return Workflow().build(checkpointer=Helper.checkpoint())


def get_config(thread_id: str | None = Header(default=None)) -> RunnableConfig:
    """Configure the rag instance to pass the thread id.

    It should return the provided thread_id if it's a non-empty string.
    Otherwise, it should generate a new UUID.
    """
    return {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}
