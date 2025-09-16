import uuid
import pytest
from api.dependencies import get_graph, get_config
from langgraph.graph.state import CompiledStateGraph


class TestDependency:
    """Test dependencies functions."""

    def test_get_graph(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_graph dependency."""
        monkeypatch.setenv("LLM_MODEL", "llama2")
        graph = get_graph()

        # Ensure it is not None
        assert graph is not None, "get_graph() should not return None"
        # Ensure the type is CompiledStateGraph
        assert isinstance(
            graph,
            CompiledStateGraph,
        ), f"Expected CompiledStateGraph, but got {type(graph)}"

    @pytest.mark.parametrize(
        ("thread_id", "expected"),
        [
            ("12345", "12345"),
            (None, "is_uuid"),
            ("", "is_uuid"),
        ],
    )
    def test_get_config(self, thread_id: str | None, expected: str) -> None:
        """Test get_config dependency."""
        config = get_config(thread_id=thread_id)
        returned_thread_id = config["configurable"]["thread_id"]

        if expected == "is_uuid":
            try:
                # Check if the returned value is a valid UUID4
                uuid.UUID(returned_thread_id, version=4)
            except ValueError:
                pytest.fail(f"Expected a valid UUID4, but got '{returned_thread_id}'")
        else:
            assert returned_thread_id == expected
