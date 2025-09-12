import uuid
import pytest
from src.agent.graph import Workflow
from src.utils.helper import Helper
from langgraph.graph.state import CompiledStateGraph


@pytest.fixture(scope="class")
def graph() -> CompiledStateGraph:
    """Compile the LangGraph workflow once per test class."""
    return Workflow().build(checkpointer=Helper.checkpoint())


@pytest.fixture(scope="class")
def thread_id() -> str:
    """Generate a consistent thread ID for all messages."""
    return str(uuid.uuid4())
