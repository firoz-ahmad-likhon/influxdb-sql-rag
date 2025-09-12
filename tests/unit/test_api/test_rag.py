import pytest
from fastapi.testclient import TestClient
from api.rag import app
from langchain_core.runnables.config import RunnableConfig
from http import HTTPStatus


class TestRAGAPI:
    """Test RAG API."""

    @pytest.fixture(autouse=True)
    def setup_method(self) -> None:
        """Initialize test."""
        self.client = TestClient(app)

    def test_root(self) -> None:
        """Test root endpoint."""
        response = self.client.get("/api/")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "Welcome to the InfluxDB RAG API."}

    def test_chat_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test chat endpoint with successful response."""

        def mock_invoke(
            inputs: dict[str, str],
            config: RunnableConfig = None,
        ) -> dict[str, str]:
            """Mock function for invoke."""
            assert (
                inputs["question"] == "What is the average temperature?"
            )  # Assert correct input
            return {"answer": "Mocked answer"}

        # Monkeypatch the invoke method to return the mocked response
        monkeypatch.setattr("api.rag.rag.invoke", mock_invoke)

        # Make the API call
        response = self.client.post(
            "/api/chat",
            json={"question": "What is the average temperature?"},
        )

        # Check that the status code and the response match the expected output
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"answer": "Mocked answer"}

    def test_chat_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test chat endpoint with failure response."""

        def mock_invoke(inputs: dict[str, str], config: RunnableConfig = None) -> None:
            """Mock function for invoke that raises an exception."""
            raise ValueError("Simulated failure")

        # Monkeypatch the invoke method to simulate an error
        monkeypatch.setattr("api.rag.rag.invoke", mock_invoke)

        # Make the API call
        response = self.client.post("/api/chat", json={"question": "Trigger error"})

        assert response.status_code == HTTPStatus.OK
        assert "error" in response.json()
        assert response.json()["error"] == "Simulated failure"
