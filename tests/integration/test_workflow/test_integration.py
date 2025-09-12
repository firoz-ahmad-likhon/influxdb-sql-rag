import pytest
from langgraph.graph.state import CompiledStateGraph


class TestWorkflowConversation:
    """Integration test simulating full chat flow."""

    @pytest.fixture(autouse=True)
    def setup_method(self, graph: CompiledStateGraph, thread_id: str) -> None:
        """Initialize the test class."""
        self.graph = graph
        self.thread_id = thread_id

    def test_chat_flow(self) -> None:
        """Test the chat flow."""
        config = {"configurable": {"thread_id": self.thread_id}}

        conversation = [
            {"question": "Hi", "expected_type": "chat"},
            {
                "question": "Give me latest 5 rows from air sensors.",
                "expected_type": "query",
            },
            {
                "question": "Display the prior result in tabular form.",
                "expected_type": "follow-up",
            },
        ]

        for i, turn in enumerate(conversation):
            response = self.graph.invoke({"question": turn["question"]}, config=config)

            # Assertions
            assert response is not None, f"Step {i+1}: No response returned"
            assert isinstance(response, dict), f"Step {i+1}: Response is not a dict"
            assert "answer" in response, f"Step {i+1}: Missing 'answer' key"
            assert isinstance(
                response["answer"],
                str,
            ), f"Step {i+1}: 'answer' is not a string"
            assert len(response["answer"]) > 0, f"Step {i+1}: 'answer' is empty"
            assert response.get("type") == turn["expected_type"], (
                f"Step {i+1}: Expected type '{turn['expected_type']}', "
                f"got '{response.get('type')}'"
            )
